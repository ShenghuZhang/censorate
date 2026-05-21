"""Agent that pushes generated code to GitHub."""
from typing import List
from app.models.generated_file import GeneratedFile
from app.models.generation_project import GenerationProject
from app.models.github_repo import GitHubRepo
from app.services.github_service import GitHubService
from app.core.config import Settings


class GitHubPushAgent:
    """Creates GitHub repository and pushes generated code."""

    def __init__(self, settings: Settings):
        self.github = GitHubService(settings)
        self.settings = settings
        self.username = settings.GITHUB_USERNAME
        self.token = settings.GITHUB_ACCESS_TOKEN

    def create_repo_and_push(
        self,
        project: GenerationProject,
        files: List[GeneratedFile],
        repo_name: str,
        is_private: bool = False,
    ) -> GitHubRepo:
        """Create a GitHub repo and push all generated files."""
        # Create the repository
        repo_data = self.github.create_repository(
            name=repo_name,
            private=is_private,
            description=project.description or project.name,
        )

        owner = repo_data["owner"]["login"]
        repo_full_name = repo_data["full_name"]
        html_url = repo_data["html_url"]
        default_branch = repo_data.get("default_branch", "main")

        # Push files using Git Trees API
        commit_result = self.github.push_files(
            owner=owner,
            repo=repo_name,
            files=files,
            branch=default_branch,
            commit_message=f"Initial commit: {project.name}",
        )

        return GitHubRepo(
            project_id=project.id,
            repo_name=repo_name,
            owner=owner,
            url=html_url,
            default_branch=default_branch,
            is_private=is_private,
            push_status="completed",
            commit_sha=commit_result.get("sha", ""),
        )
