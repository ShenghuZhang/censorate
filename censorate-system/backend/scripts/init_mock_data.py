#!/usr/bin/env python
"""Initialize mock data for Censorate system."""

import sys
import os
import uuid
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import Base, engine, SessionLocal
from app.core.security import get_password_hash
from app.core.config import Settings
from app.models.user import User
from app.models.project import Project
from app.models.team_member import TeamMember
from app.models.requirement import Requirement
from app.models.skill import Skill, SkillVersion, SkillFile
from app.models.task import Task
from pathlib import Path


def init_mock_data():
    """Initialize mock data."""
    print("========================================")
    print("Censorate Mock Data Initialization")
    print("========================================")
    print()

    # Create tables
    print("📦 Creating database tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # ========================================
        # 1. Create Users
        # ========================================
        print()
        print("👤 Creating users...")

        users_data = [
            {
                "email": "admin@stratos.com",
                "name": "Admin User",
                "password": "admin123",
                "is_superuser": True
            },
            {
                "email": "test@stratos.com",
                "name": "Test User",
                "password": "test123",
                "is_superuser": False
            },
            {
                "email": "alice@stratos.com",
                "name": "Alice Wang",
                "password": "alice123",
                "is_superuser": False
            },
            {
                "email": "bob@stratos.com",
                "name": "Bob Chen",
                "password": "bob123",
                "is_superuser": False
            }
        ]

        created_users = []
        for user_data in users_data:
            existing = db.query(User).filter(User.email == user_data["email"]).first()
            if not existing:
                user = User(
                    id=str(uuid.uuid4()),
                    email=user_data["email"],
                    name=user_data["name"],
                    hashed_password=get_password_hash(user_data["password"]),
                    is_active=True,
                    is_superuser=user_data["is_superuser"]
                )
                db.add(user)
                db.flush()
                created_users.append(user)
                print(f"  ✅ Created {user.name} ({user.email})")
            else:
                created_users.append(existing)
                print(f"  ℹ️  {existing.name} already exists")

        db.commit()

        # ========================================
        # 2. Create Projects
        # ========================================
        print()
        print("📋 Creating projects...")

        projects_data = [
            {
                "name": "AI Assistant Platform",
                "slug": "ai-assistant-platform",
                "description": "Building an intelligent AI assistant platform with multiple agents",
                "project_type": "technical",
                "created_by": "admin@stratos.com"
            },
            {
                "name": "E-commerce Website",
                "slug": "ecommerce-website",
                "description": "Full-stack e-commerce solution with payment integration",
                "project_type": "non_technical",
                "created_by": "alice@stratos.com"
            },
            {
                "name": "Mobile Banking App",
                "slug": "mobile-banking-app",
                "description": "Secure mobile banking application with biometric authentication",
                "project_type": "technical",
                "created_by": "bob@stratos.com"
            }
        ]

        created_projects = []
        for project_data in projects_data:
            existing = db.query(Project).filter(Project.slug == project_data["slug"]).first()
            if not existing:
                project = Project(
                    id=str(uuid.uuid4()),
                    name=project_data["name"],
                    slug=project_data["slug"],
                    description=project_data["description"],
                    project_type=project_data["project_type"],
                    created_by=project_data["created_by"],
                    settings={}
                )
                db.add(project)
                db.flush()
                created_projects.append(project)
                print(f"  ✅ Created {project.name}")
            else:
                created_projects.append(existing)
                print(f"  ℹ️  {existing.name} already exists")

        db.commit()

        # ========================================
        # 3. Create Team Members (Humans + AI Agents)
        # ========================================
        print()
        print("👥 Creating team members...")

        # AI agents template
        ai_agents_template = [
            {
                "name": "Analysis Agent",
                "nickname": "Alex",
                "role": "analysis_agent",
                "skills": ["requirements_analysis", "stakeholder_interview", "risk_identification"],
                "type": "ai"
            },
            {
                "name": "Design Agent",
                "nickname": "Diana",
                "role": "design_agent",
                "skills": ["system_design", "architecture", "prototyping"],
                "type": "ai"
            },
            {
                "name": "Development Agent",
                "nickname": "Devon",
                "role": "development_agent",
                "skills": ["coding", "code_review", "testing"],
                "type": "ai"
            },
            {
                "name": "Testing Agent",
                "nickname": "Tina",
                "role": "testing_agent",
                "skills": ["test_design", "quality_assurance", "bug_reporting"],
                "type": "ai"
            }
        ]

        # Human team members
        human_members_template = [
            {
                "name": "Alice Wang",
                "nickname": "Alice",
                "email": "alice@stratos.com",
                "role": "product_manager",
                "type": "human"
            },
            {
                "name": "Bob Chen",
                "nickname": "Bob",
                "email": "bob@stratos.com",
                "role": "tech_lead",
                "type": "human"
            },
            {
                "name": "Carol Li",
                "nickname": "Carol",
                "email": "carol@stratos.com",
                "role": "designer",
                "type": "human"
            }
        ]

        for project in created_projects:
            # Get existing members for this project
            existing_members = db.query(TeamMember).filter(TeamMember.project_id == project.id).all()
            existing_roles = {m.role for m in existing_members}
            existing_nicknames = {m.nickname for m in existing_members}

            # Add AI agents
            for agent_data in ai_agents_template:
                if agent_data["role"] not in existing_roles:
                    agent = TeamMember(
                        id=str(uuid.uuid4()),
                        project_id=project.id,
                        name=agent_data["name"],
                        nickname=agent_data["nickname"],
                        role=agent_data["role"],
                        type=agent_data["type"],
                        status="active",
                        skills=agent_data["skills"],
                        memory_enabled=True,
                        deepagent_config={}
                    )
                    db.add(agent)
                    print(f"  ✅ [{project.name}] Added AI agent: {agent.name}")

            # Add human members
            for human_data in human_members_template:
                if human_data["nickname"] not in existing_nicknames:
                    human = TeamMember(
                        id=str(uuid.uuid4()),
                        project_id=project.id,
                        name=human_data["name"],
                        nickname=human_data["nickname"],
                        email=human_data["email"],
                        role=human_data["role"],
                        type=human_data["type"],
                        status="active",
                        skills=[],
                        memory_enabled=False,
                        deepagent_config={}
                    )
                    db.add(human)
                    print(f"  ✅ [{project.name}] Added team member: {human.name}")

        db.commit()

        # ========================================
        # 4. Create Requirements
        # ========================================
        print()
        print("📝 Creating requirements...")

        requirements_data = [
            # Project 1 requirements
            {
                "project_slug": "ai-assistant-platform",
                "req_number": 1,
                "title": "User Authentication System",
                "description": "Implement secure user authentication with JWT tokens and refresh token mechanism",
                "status": "in_progress",
                "priority": "high"
            },
            {
                "project_slug": "ai-assistant-platform",
                "req_number": 2,
                "title": "Chat Interface",
                "description": "Build real-time chat interface with message history and typing indicators",
                "status": "todo",
                "priority": "high"
            },
            {
                "project_slug": "ai-assistant-platform",
                "req_number": 3,
                "title": "Agent Orchestration",
                "description": "Implement multi-agent orchestration system with task routing",
                "status": "backlog",
                "priority": "medium"
            },
            {
                "project_slug": "ai-assistant-platform",
                "req_number": 4,
                "title": "Analytics Dashboard",
                "description": "Create analytics dashboard for monitoring agent performance",
                "status": "ready_for_deployment",
                "priority": "low"
            },
            # Project 2 requirements
            {
                "project_slug": "ecommerce-website",
                "req_number": 1,
                "title": "Product Catalog",
                "description": "Implement product catalog with search, filtering, and categories",
                "status": "todo",
                "priority": "high"
            },
            {
                "project_slug": "ecommerce-website",
                "req_number": 2,
                "title": "Shopping Cart",
                "description": "Build shopping cart with persistent storage",
                "status": "in_progress",
                "priority": "high"
            },
            {
                "project_slug": "ecommerce-website",
                "req_number": 3,
                "title": "Payment Integration",
                "description": "Integrate payment gateway (Stripe/PayPal)",
                "status": "backlog",
                "priority": "high"
            },
            # Project 3 requirements
            {
                "project_slug": "mobile-banking-app",
                "req_number": 1,
                "title": "Biometric Authentication",
                "description": "Implement fingerprint and face recognition login",
                "status": "todo",
                "priority": "high"
            },
            {
                "project_slug": "mobile-banking-app",
                "req_number": 2,
                "title": "Transaction History",
                "description": "Display transaction history with filtering and export",
                "status": "in_progress",
                "priority": "medium"
            }
        ]

        created_requirements = []
        for req_data in requirements_data:
            project = db.query(Project).filter(Project.slug == req_data["project_slug"]).first()
            if not project:
                continue

            existing = db.query(Requirement).filter(
                Requirement.project_id == project.id,
                Requirement.req_number == req_data["req_number"]
            ).first()

            if not existing:
                requirement = Requirement(
                    id=str(uuid.uuid4()),
                    project_id=project.id,
                    req_number=req_data["req_number"],
                    title=req_data["title"],
                    description=req_data["description"],
                    status=req_data["status"],
                    priority=req_data["priority"],
                    source="manual",
                    created_by="system",
                    lark_editable=False,
                    return_count=0
                )
                db.add(requirement)
                db.flush()
                created_requirements.append(requirement)
                print(f"  ✅ [{project.name}] Created REQ-{requirement.req_number}: {requirement.title}")
            else:
                created_requirements.append(existing)
                print(f"  ℹ️  [{project.name}] REQ-{existing.req_number} already exists")

        db.commit()

        # ========================================
        # 5. Create Skills
        # ========================================
        print()
        print("🔧 Creating skills...")

        skills_data = [
            {
                "slug": "requirements-analysis",
                "name": "Requirements Analysis",
                "description": "Analyze and refine user requirements into clear specifications",
                "category": "analysis",
                "tags": ["requirements", "analysis", "specification"],
                "version": "1.0.0",
                "changelog": "Initial release"
            },
            {
                "slug": "system-design",
                "name": "System Design",
                "description": "Design system architecture and technical specifications",
                "category": "design",
                "tags": ["architecture", "design", "system"],
                "version": "1.0.0",
                "changelog": "Initial release"
            },
            {
                "slug": "code-development",
                "name": "Code Development",
                "description": "Write clean, maintainable code with best practices",
                "category": "development",
                "tags": ["coding", "development", "best-practices"],
                "version": "1.0.0",
                "changelog": "Initial release"
            },
            {
                "slug": "test-design",
                "name": "Test Design",
                "description": "Design comprehensive test cases and test plans",
                "category": "testing",
                "tags": ["testing", "qa", "test-cases"],
                "version": "1.0.0",
                "changelog": "Initial release"
            },
            {
                "slug": "code-review",
                "name": "Code Review",
                "description": "Review code for quality, security, and best practices",
                "category": "development",
                "tags": ["code-review", "quality", "security"],
                "version": "1.0.0",
                "changelog": "Initial release"
            },
            {
                "slug": "risk-identification",
                "name": "Risk Identification",
                "description": "Identify project risks and mitigation strategies",
                "category": "analysis",
                "tags": ["risk", "analysis", "mitigation"],
                "version": "1.0.0",
                "changelog": "Initial release"
            }
        ]

        # Get settings for storage path
        settings = Settings.get()
        base_dir = Path(settings.SKILL_STORAGE_DIR)

        # Clean up existing skills to start fresh
        print()
        print("🗑️  Cleaning up existing skills...")
        existing_files = db.query(SkillFile).all()
        for f in existing_files:
            db.delete(f)
        existing_versions = db.query(SkillVersion).all()
        for v in existing_versions:
            db.delete(v)
        existing_skills = db.query(Skill).all()
        for s in existing_skills:
            db.delete(s)
        db.commit()
        print(f"  🗑️  Deleted {len(existing_skills)} existing skills")

        for skill_data in skills_data:
            skill = Skill(
                id=str(uuid.uuid4()),
                slug=skill_data["slug"],
                name=skill_data["name"],
                description=skill_data["description"],
                category=skill_data["category"],
                tags=skill_data["tags"],
                is_published=True,
                is_archived=False,
                moderation_status="approved",
                stats={"downloads": 0, "views": 0}
            )
            db.add(skill)
            db.flush()

            # Create skill version
            version = SkillVersion(
                id=str(uuid.uuid4()),
                skill_id=skill.id,
                version=skill_data["version"],
                changelog=skill_data["changelog"],
                manifest={"name": skill.name, "version": skill_data["version"]},
                is_latest=True,
                is_deprecated=False
            )
            db.add(version)
            db.flush()

            # Update skill's latest_version_id
            skill.latest_version_id = version.id

            # Create SKILL.md content
            skill_md_content = f"""# {skill.name}

## Description
{skill.description}

## Version
{skill_data["version"]}

## Category
{skill.category}

## Tags
{', '.join(skill.tags)}
"""

            # Save file to local storage - using same format as storage_service
            # Note: storage_service uses "v{version}" directory
            version_dir = base_dir / skill.slug / f"v{skill_data['version']}"
            version_dir.mkdir(parents=True, exist_ok=True)
            skill_file_path = version_dir / "SKILL.md"
            skill_file_path.write_bytes(skill_md_content.encode('utf-8'))

            # Storage path should be relative to base_dir.parent (app/storage)
            storage_path = str(skill_file_path.relative_to(base_dir.parent))

            # Create SKILL.md file record in DB
            skill_file = SkillFile(
                id=str(uuid.uuid4()),
                version_id=version.id,
                path="SKILL.md",
                content_type="text/markdown",
                file_size=len(skill_md_content),
                storage_path=storage_path
            )
            db.add(skill_file)

            print(f"  ✅ Created skill: {skill.name} v{skill_data['version']} at {storage_path}")

        db.commit()

        # ========================================
        # 6. Create Tasks
        # ========================================
        print()
        print("📋 Creating tasks...")

        for req in created_requirements[:5]:  # Create tasks for first 5 requirements
            # Get existing max task number for this requirement
            max_task = db.query(Task).filter(Task.requirement_id == req.id).order_by(Task.task_number.desc()).first()
            next_task_num = max_task.task_number + 1 if max_task else 1

            task_templates = [
                {
                    "title": f"Research {req.title}",
                    "description": "Conduct initial research and gather requirements",
                    "status": "completed"
                },
                {
                    "title": f"Implement {req.title}",
                    "description": "Implement the core functionality",
                    "status": "in_progress"
                },
                {
                    "title": f"Test {req.title}",
                    "description": "Write and execute test cases",
                    "status": "pending"
                }
            ]

            for template in task_templates:
                existing = db.query(Task).filter(
                    Task.requirement_id == req.id,
                    Task.title == template["title"]
                ).first()

                if not existing:
                    task = Task(
                        id=str(uuid.uuid4()),
                        requirement_id=req.id,
                        task_number=next_task_num,
                        title=template["title"],
                        description=template["description"],
                        status=template["status"],
                        created_by="system"
                    )
                    db.add(task)
                    db.flush()
                    next_task_num += 1
                    print(f"  ✅ Created task #{task.task_number}: {task.title}")

        db.commit()

        # ========================================
        # Summary
        # ========================================
        print()
        print("========================================")
        print("✅ Mock Data Initialization Complete!")
        print("========================================")
        print()
        print("📊 Summary:")
        print(f"  👤 Users: {len(created_users)}")
        print(f"  📋 Projects: {len(created_projects)}")
        print(f"  📝 Requirements: {len(created_requirements)}")
        print(f"  🔧 Skills: {len(skills_data)}")
        print()
        print("🔑 Login Credentials:")
        for user_data in users_data:
            print(f"  - {user_data['email']} / {user_data['password']}")
        print()

    except Exception as e:
        print(f"❌ Error initializing mock data: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_mock_data()
