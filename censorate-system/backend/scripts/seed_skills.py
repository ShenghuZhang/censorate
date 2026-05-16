import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.skill import Skill
from app.schemas.skill import SkillCreate
from app.services import get_skill_service

def _build_skill_md(name: str, description: str, version: str, category: str, tags: list, body: str = "") -> bytes:
    """Build a SKILL.md with Hermes-compatible YAML frontmatter."""
    tags_yaml = ", ".join(tags)
    return (
        f"---\n"
        f"name: {name}\n"
        f"description: {description}\n"
        f"version: {version}\n"
        f"category: {category}\n"
        f"metadata:\n"
        f"  hermes:\n"
        f"    tags: [{tags_yaml}]\n"
        f"---\n\n"
        f"{body}\n"
    ).encode("utf-8")


def seed_skills():
    db = SessionLocal()
    skill_service = get_skill_service()
    try:
        print("=" * 60)
        print("Seeding sample skills...")
        print("=" * 60)

        # First, delete existing skills we are about to re-seed
        mock_slugs = [
            "req-analyzer", "architecture-diagrammer", "hermes-code-reviewer",
            "react-component-gen", "unit-test-generator", "jira-sync", "notion-knowledge"
        ]

        from sqlalchemy import text
        slugs_tuple = tuple(mock_slugs)

        # Clear FK latest_version_id and delete related data (order matters for FK constraints)
        db.execute(text("UPDATE skills SET latest_version_id = NULL WHERE slug IN :slugs"), {"slugs": slugs_tuple})
        db.execute(text("DELETE FROM skill_downloads WHERE version_id IN (SELECT id FROM skill_versions WHERE skill_id IN (SELECT id FROM skills WHERE slug IN :slugs))"), {"slugs": slugs_tuple})
        db.execute(text("DELETE FROM skill_files WHERE version_id IN (SELECT id FROM skill_versions WHERE skill_id IN (SELECT id FROM skills WHERE slug IN :slugs))"), {"slugs": slugs_tuple})
        db.execute(text("DELETE FROM skill_versions WHERE skill_id IN (SELECT id FROM skills WHERE slug IN :slugs)"), {"slugs": slugs_tuple})
        db.execute(text("DELETE FROM skills WHERE slug IN :slugs"), {"slugs": slugs_tuple})
        db.commit()

        skills_data = [
            # 1. ANALYSIS CATEGORY
            {
                "slug": "req-analyzer",
                "name": "Requirements Analyzer",
                "description": "Analyzes product requirements for completeness, contradictions, and clarity. Helps identify edge cases early.",
                "category": "analysis",
                "tags": ["requirements", "product", "nlp"],
                "version": "1.2.0",
                "body": "Automatically parses user stories and PRDs to extract structured requirements, identify ambiguities, and suggest clarifications.",
                "files": [
                    {"path": "prompts/analysis.txt", "content": b"You are a senior product manager. Analyze the following requirement..."},
                    {"path": "schema/output.json", "content": b'{"type": "object", "properties": {"ambiguities": {"type": "array"}}}'}
                ]
            },
            # 2. DESIGN CATEGORY
            {
                "slug": "architecture-diagrammer",
                "name": "Architecture Diagram Generator",
                "description": "Converts plain text descriptions of system architecture into Mermaid.js diagrams automatically.",
                "category": "design",
                "tags": ["architecture", "mermaid", "visualization"],
                "version": "0.9.0",
                "body": "Generates Mermaid.js diagram code from natural language descriptions of system architecture, data flows, and deployment topologies.",
                "files": [
                    {"path": "tools/mermaid_generator.py", "content": b"def generate_mermaid(text):\n    return 'graph TD;'"}
                ]
            },
            # 3. DEVELOPMENT CATEGORY
            {
                "slug": "hermes-code-reviewer",
                "name": "Hermes Code Reviewer",
                "description": "An advanced skill for Hermes Agent that automatically reviews code snippets, finds bugs, and suggests optimizations based on best practices.",
                "category": "development",
                "tags": ["code-review", "python", "javascript", "optimization"],
                "version": "2.0.0",
                "body": "Perform deep code analysis: detect bugs, security vulnerabilities, performance issues, and style violations. Suggest concrete fixes with before/after code examples.",
                "files": [
                    {"path": "prompts/system.txt", "content": b"You are an expert code reviewer..."},
                    {"path": "config.yaml", "content": b"max_lines: 1000\nstrict_mode: true"}
                ]
            },
            {
                "slug": "react-component-gen",
                "name": "React Component Generator",
                "description": "Generates production-ready React/Tailwind components based on UI descriptions.",
                "category": "development",
                "tags": ["react", "tailwind", "frontend", "ui"],
                "version": "1.5.2",
                "body": "Builds TypeScript React components with Tailwind CSS styling from natural language UI descriptions. Includes accessibility, responsive design, and best practices.",
                "files": [
                    {"path": "templates/base.txt", "content": b"import React from 'react';\n\nexport const Component = () => <div />;"}
                ]
            },
            # 4. TESTING CATEGORY
            {
                "slug": "unit-test-generator",
                "name": "Jest/PyTest Generator",
                "description": "Automatically writes comprehensive unit tests for given functions, covering edge cases and mocking dependencies.",
                "category": "testing",
                "tags": ["testing", "jest", "pytest", "tdd"],
                "version": "3.1.0",
                "body": "Supports Python (pytest) and JavaScript/TypeScript (jest). Targets 100% branch coverage. Generates mocks, fixtures, edge case tests, and snapshot tests automatically.",
                "files": [
                    {"path": "prompts/test_gen.txt", "content": b"Write tests using 100% branch coverage target."}
                ]
            },
            # 5. MANAGEMENT CATEGORY
            {
                "slug": "jira-sync",
                "name": "Jira Task Synchronizer",
                "description": "Allows the agent to bidirectionally sync requirements and tasks between Censorate and Jira.",
                "category": "management",
                "tags": ["jira", "sync", "project-management"],
                "version": "2.1.0",
                "body": "Bidirectionally synchronize issues, tasks, and requirements between Censorate and Jira. Maps custom fields, handles attachments, and maintains sync status.",
                "files": [
                    {"path": "api_client.py", "content": b"def sync_issues():\n    pass"}
                ]
            },
            # 6. KNOWLEDGE/CUSTOM CATEGORY
            {
                "slug": "notion-knowledge",
                "name": "Notion Knowledge Base",
                "description": "Grants the agent read access to your Notion workspaces to answer questions based on your company's internal documentation.",
                "category": "custom",
                "tags": ["notion", "rag", "knowledge"],
                "version": "0.9.5",
                "body": "RAG integration for Notion workspaces. Indexes pages, databases, and comments. Answers questions grounded in your company's internal documentation.",
                "files": [
                    {"path": "manifest.json", "content": b'{"name": "notion-kb"}'}
                ]
            }
        ]

        for data in skills_data:
            skill = db.query(Skill).filter(Skill.slug == data["slug"]).first()
            if not skill:
                # Use official skill_service to handle DB + Local File Storage
                skill_create = SkillCreate(
                    name=data["name"],
                    description=data["description"],
                    category=data["category"],
                    tags=data["tags"]
                )
                
                # Build SKILL.md with Hermes-compatible YAML frontmatter
                skill_md = _build_skill_md(
                    name=data["name"],
                    description=data["description"],
                    version=data["version"],
                    category=data["category"],
                    tags=data["tags"],
                    body=data["body"]
                )
                all_files = [{"path": "SKILL.md", "content": skill_md}] + data["files"]

                new_skill = skill_service.create_skill(
                    db=db,
                    data=skill_create,
                    files=all_files,
                    owner_id=None
                )
                
                # Update slug back to requested mock slug
                new_skill.slug = data["slug"]
                new_skill.is_published = True
                new_skill.moderation_status = "approved"
                
                # Update version name
                latest_ver = skill_service.version_repo.get(db, new_skill.latest_version_id)
                latest_ver.version = data["version"]
                
                db.commit()
                print(f"Created skill: {new_skill.name}")
            else:
                print(f"Skill {skill.name} already exists.")

        print("✅ Skills successfully seeded using SkillService!")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding skills: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_skills()
