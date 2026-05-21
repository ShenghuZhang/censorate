"""Central pipeline orchestrator tying all agents together."""
import json
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from app.core.config import Settings
from app.core.database import SessionLocal
from app.core.logger import get_logger
from app.models.generation_project import GenerationProject
from app.models.generated_file import GeneratedFile
from app.models.pipeline_step import PipelineStep
from app.models.github_repo import GitHubRepo
from app.models.template import Template
from app.state_machine.generation_state_machine import GenerationState
from app.services.claude_service import ClaudeService
from app.agents_v2 import (
    RequirementAnalysisAgent,
    ArchitectAgent,
    CodeGeneratorAgent,
    CodeReviewAgent,
    GitHubPushAgent,
)

logger = get_logger(__name__)


def _get_session():
    """Create a new DB session for background task isolation."""
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise


def _get_project(db: Session, project_id: str) -> Optional[GenerationProject]:
    return db.query(GenerationProject).filter(GenerationProject.id == project_id).first()


class PipelineOrchestrator:
    """Orchestrates the code generation pipeline steps."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.claude = ClaudeService(settings)
        self.analysis_agent = RequirementAnalysisAgent(self.claude)
        self.architect_agent = ArchitectAgent(self.claude)
        self.code_gen_agent = CodeGeneratorAgent(self.claude)
        self.review_agent = CodeReviewAgent(self.claude)
        self.push_agent = GitHubPushAgent(settings)

    # --- Internal helpers ---

    def _create_step(self, db: Session, project_id: str, step_type: str) -> PipelineStep:
        step = PipelineStep(
            project_id=project_id,
            step_type=step_type,
            status="running",
            started_at=datetime.now(timezone.utc),
        )
        db.add(step)
        db.commit()
        return step

    def _complete_step(self, db: Session, step: PipelineStep, result: dict = None):
        step.status = "completed"
        step.completed_at = datetime.now(timezone.utc)
        if result:
            step.result = result
        db.commit()

    def _fail_step(self, db: Session, step: PipelineStep, error: str):
        step.status = "failed"
        step.completed_at = datetime.now(timezone.utc)
        step.error = str(error)[:2000]
        db.commit()

    def _set_status(self, db: Session, project: GenerationProject, status: str, error: str = None):
        project.status = status
        if error:
            project.error_message = str(error)[:2000]
        else:
            project.error_message = None
        db.commit()

    # --- Pipeline steps ---

    def run_analysis(self, project_id: str):
        """Run requirement analysis: user_story -> PRD."""
        db = _get_session()
        try:
            project = _get_project(db, project_id)
            if not project:
                logger.error(f"Project {project_id} not found for analysis")
                return

            step = self._create_step(db, project_id, "analysis")
            template = db.query(Template).filter(Template.id == project.template_id).first()
            template_desc = template.description if template else ""

            prd = self.analysis_agent.analyze(project.user_story, template_desc)
            project.prd_content = json.loads(prd.model_dump_json())
            self._set_status(db, project, GenerationState.CONFIRMED)
            self._complete_step(db, step, {"prd_summary": prd.project_name})
        except Exception as e:
            logger.exception(f"Analysis failed for project {project_id}")
            if step:
                self._fail_step(db, step, str(e))
            project = _get_project(db, project_id)
            if project:
                self._set_status(db, project, GenerationState.FAILED, str(e))
        finally:
            db.close()

    def run_architecture(self, project_id: str):
        """Run architecture design: PRD -> file tree + deps."""
        db = _get_session()
        step = None
        try:
            project = _get_project(db, project_id)
            if not project or not project.prd_content:
                logger.error(f"Project {project_id} not found or missing PRD")
                return

            step = self._create_step(db, project_id, "architecture")
            template = db.query(Template).filter(Template.id == project.template_id).first()

            from app.schemas.prd import PRDOutput
            prd = PRDOutput.model_validate(project.prd_content)
            template_config = template.config if template else {}

            arch = self.architect_agent.design(prd, template_config)
            project.architecture_design = json.loads(arch.model_dump_json())
            self._set_status(db, project, GenerationState.DESIGNING)
            self._complete_step(db, step, {"file_count": len(arch.file_tree)})
        except Exception as e:
            logger.exception(f"Architecture failed for project {project_id}")
            if step:
                self._fail_step(db, step, str(e))
            project = _get_project(db, project_id)
            if project:
                self._set_status(db, project, GenerationState.FAILED, str(e))
        finally:
            db.close()

    def run_code_generation(self, project_id: str):
        """Generate all code files from architecture design."""
        db = _get_session()
        step = None
        try:
            project = _get_project(db, project_id)
            if not project or not project.architecture_design:
                logger.error(f"Project {project_id} not found or missing architecture")
                return

            step = self._create_step(db, project_id, "code_generation")

            from app.schemas.prd import PRDOutput
            from app.schemas.architecture import ArchitectureOutput

            prd = PRDOutput.model_validate(project.prd_content)
            arch = ArchitectureOutput.model_validate(project.architecture_design)
            existing_files_context = ""

            for file_spec in arch.file_tree:
                content = self.code_gen_agent.generate_file(
                    file_spec, arch, prd, existing_files_context
                )
                generated = GeneratedFile(
                    project_id=project_id,
                    file_path=file_spec.path,
                    content=content,
                    language=file_spec.language or "text",
                    step="generation",
                    status="generated",
                )
                db.add(generated)
                db.commit()
                existing_files_context += f"\n--- {file_spec.path} ---\n{content[:500]}\n"

            self._set_status(db, project, GenerationState.REVIEWING)

            # Auto-run review after generation
            self._run_review(db, project_id, arch, prd)
        except Exception as e:
            logger.exception(f"Code generation failed for project {project_id}")
            if step:
                self._fail_step(db, step, str(e))
            project = _get_project(db, project_id)
            if project:
                self._set_status(db, project, GenerationState.FAILED, str(e))
        finally:
            db.close()

    def _run_review(self, db: Session, project_id: str, arch=None, prd=None):
        """Run code review on all generated files."""
        step = None
        try:
            step = self._create_step(db, project_id, "code_review")
            files = db.query(GeneratedFile).filter(
                GeneratedFile.project_id == project_id,
                GeneratedFile.status == "generated",
            ).all()

            if arch and prd:
                project_context = f"Project: {arch.project_name}, Files: {len(arch.file_tree)}"
            else:
                project_context = ""

            all_passed = True
            for gf in files:
                review = self.review_agent.review_file(gf.file_path, gf.content, project_context)
                if review.passed:
                    gf.status = "approved"
                elif review.issues and any(i.severity == "error" for i in review.issues):
                    # Try auto-fix for errors
                    fixed = self.review_agent.fix_file(gf.content, review)
                    gf.content = fixed
                    gf.status = "auto_fixed"
                    all_passed = False
                else:
                    gf.status = "needs_review"
                    all_passed = False
                db.commit()

            if all_passed:
                self._set_status(db, _get_project(db, project_id), GenerationState.READY)
                self._complete_step(db, step, {"files_reviewed": len(files), "all_passed": True})
            else:
                self._set_status(db, _get_project(db, project_id), GenerationState.READY)
                self._complete_step(db, step, {"files_reviewed": len(files), "all_passed": False})
        except Exception as e:
            logger.exception(f"Code review failed for project {project_id}")
            if step:
                self._fail_step(db, step, str(e))
            project = _get_project(db, project_id)
            if project:
                self._set_status(db, project, GenerationState.FAILED, str(e))

    def run_push(self, project_id: str):
        """Push generated code to GitHub."""
        db = _get_session()
        step = None
        try:
            project = _get_project(db, project_id)
            if not project:
                logger.error(f"Project {project_id} not found for push")
                return

            step = self._create_step(db, project_id, "github_push")
            files = db.query(GeneratedFile).filter(
                GeneratedFile.project_id == project_id,
            ).all()

            if not files:
                raise ValueError("No files to push")

            repo_name = project.name.lower().replace(" ", "-").replace("_", "-")[:100]
            github_repo = self.push_agent.create_repo_and_push(
                project=project,
                files=files,
                repo_name=repo_name,
                is_private=False,
            )

            github_repo.project_id = project_id
            db.add(github_repo)
            project.repo_url = github_repo.url
            self._set_status(db, project, GenerationState.COMPLETED)
            self._complete_step(db, step, {"repo_url": github_repo.url})
        except Exception as e:
            logger.exception(f"GitHub push failed for project {project_id}")
            if step:
                self._fail_step(db, step, str(e))
            project = _get_project(db, project_id)
            if project:
                self._set_status(db, project, GenerationState.FAILED, str(e))
        finally:
            db.close()

    def retry_pipeline(self, project_id: str, failed_step_type: str):
        """Retry from a specific failed step."""
        retry_map = {
            "analysis": self.run_analysis,
            "architecture": self.run_architecture,
            "code_generation": self.run_code_generation,
            "code_review": self.run_code_generation,  # re-run code gen then review
            "github_push": self.run_push,
        }
        handler = retry_map.get(failed_step_type)
        if handler:
            # Increment retry count on the project
            db = _get_session()
            try:
                project = _get_project(db, project_id)
                if project:
                    failed_step = (
                        db.query(PipelineStep)
                        .filter(
                            PipelineStep.project_id == project_id,
                            PipelineStep.step_type == failed_step_type,
                        )
                        .order_by(PipelineStep.started_at.desc())
                        .first()
                    )
                    if failed_step:
                        failed_step.retry_count = (failed_step.retry_count or 0) + 1
                    db.commit()
            finally:
                db.close()

            handler(project_id)
        else:
            logger.error(f"No retry handler for step type: {failed_step_type}")
