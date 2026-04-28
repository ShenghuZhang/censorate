"""
Seed complete mock data including users, projects, requirements, comments and history
"""
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# Add the parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.project import Project
from app.models.team_member import TeamMember
from app.models.requirement import Requirement
from app.models.comment import Comment
from app.models.requirement_status_history import RequirementStatusHistory


def get_or_create_users(db):
    """Create mock users"""
    users_data = [
        {
            "email": "alex.kim@example.com",
            "name": "Alex Kim",
            "is_superuser": True
        },
        {
            "email": "julian.rossi@example.com",
            "name": "Julian Rossi",
            "is_superuser": False
        },
        {
            "email": "sarah.chen@example.com",
            "name": "Sarah Chen",
            "is_superuser": False
        }
    ]

    users = []
    for user_data in users_data:
        user = db.query(User).filter(User.email == user_data["email"]).first()
        if not user:
            user = User(
                id=uuid.uuid4(),
                **user_data
            )
            db.add(user)
            db.flush()
            print(f"Created user: {user.name}")
        else:
            print(f"Found existing user: {user.name}")
        users.append(user)

    db.commit()
    return users


def get_or_create_project(db, users, name="示例项目"):
    """Get existing project or create a new one with members"""
    project = db.query(Project).filter(
        Project.name == name,
        Project.archived_at.is_(None)
    ).first()

    if not project:
        project = Project(
            id=uuid.uuid4(),
            name=name,
            slug=name.lower().replace(" ", "-"),
            description="这是一个用于演示的示例项目，包含各种类型的需求",
            project_type="non_technical",
            created_by=str(users[0].id),
            settings={
                "swimlanes": ["Backlog", "Todo", "In Progress", "Review", "Done"],
                "emoji": "🎯"
            }
        )
        db.add(project)
        db.flush()
        print(f"Created new project: {project.name}")

        # Add all users as team members
        for user in users:
            member = TeamMember(
                id=uuid.uuid4(),
                project_id=project.id,
                name=user.name,
                nickname=user.name,
                email=user.email,
                role="developer",
                type="human"
            )
            db.add(member)
            print(f"Added team member: {user.name}")

        # Add AI agent team members - only one per project
        ai_config = {
            "name": "AI助手",
            "role": "analysis_agent",
            "skills": ["需求分析", "方案设计", "代码开发", "测试"],
            "deepagent_config": {
                "agent_type": "hermes",
                "capabilities": ["analysis", "design", "coding", "testing"]
            }
        }

        member = TeamMember(
            id=uuid.uuid4(),
            project_id=project.id,
            name=ai_config["name"],
            nickname=ai_config["name"],
            role=ai_config["role"],
            type="ai",
            skills=ai_config["skills"],
            deepagent_config=ai_config["deepagent_config"],
            memory_enabled=True
        )
        db.add(member)
        print(f"Added AI agent: {ai_config['name']}")

        db.commit()
        db.refresh(project)
    else:
        print(f"Found existing project: {project.name}")

    return project


def get_next_req_number(db, project_id):
    """Get next requirement number for a project"""
    max_req = db.query(Requirement).filter(
        Requirement.project_id == project_id,
        Requirement.archived_at.is_(None)
    ).order_by(Requirement.req_number.desc()).first()

    return (max_req.req_number + 1) if max_req else 1


def seed_complete_data():
    """Seed complete mock data"""
    db = SessionLocal()

    try:
        print("=" * 60)
        print("Seeding complete mock data...")
        print("=" * 60)

        # Create users
        print("\n[1/4] Creating users...")
        users = get_or_create_users(db)

        # Create project and team members
        print("\n[2/4] Creating project and team members...")
        project = get_or_create_project(db, users)
        next_req_num = get_next_req_number(db, project.id)

        # Create requirements with history
        print("\n[3/4] Creating requirements with history...")

        # Check if we already have requirements
        existing_reqs = db.query(Requirement).filter(
            Requirement.project_id == project.id
        ).count()

        if existing_reqs >= 3:
            print("Requirements already exist, skipping creation")
        else:
            # Requirement 1: New requirement
            req1 = Requirement(
                id=uuid.uuid4(),
                project_id=project.id,
                req_number=next_req_num,
                title="用户登录模块开发",
                description="开发用户登录功能，支持手机号和邮箱两种方式登录，需要包含验证码和记住密码功能。",
                status="todo",
                priority="high",
                created_by=str(users[0].id),
                assigned_to=str(users[1].id),
                assigned_to_name=users[1].name,
                return_count=0
            )
            db.add(req1)
            db.flush()

            # Create history
            history1 = RequirementStatusHistory(
                id=uuid.uuid4(),
                requirement_id=req1.id,
                from_status=None,
                to_status="backlog",
                changed_by=str(users[0].id),
                changed_by_name=users[0].name,
                note="Requirement created",
                is_backward=False,
                changed_at=datetime.utcnow() - timedelta(days=3)
            )
            db.add(history1)

            history2 = RequirementStatusHistory(
                id=uuid.uuid4(),
                requirement_id=req1.id,
                from_status="backlog",
                to_status="todo",
                assigned_to=str(users[1].id),
                assigned_to_name=users[1].name,
                changed_by=str(users[0].id),
                changed_by_name=users[0].name,
                note="Ready to start",
                is_backward=False,
                changed_at=datetime.utcnow() - timedelta(days=2)
            )
            db.add(history2)

            print(f"Created REQ-{req1.req_number}: {req1.title}")
            next_req_num += 1

            # Requirement 2: In progress with comments
            req2 = Requirement(
                id=uuid.uuid4(),
                project_id=project.id,
                req_number=next_req_num,
                title="评论与评价系统",
                description="开发评论和评价系统，支持用户发表评论、打分、点赞等操作。",
                status="in_progress",
                priority="medium",
                created_by=str(users[1].id),
                assigned_to="AI-代码开发助手",
                assigned_to_name="代码开发助手",
                return_count=1,
                last_returned_at=datetime.utcnow() - timedelta(days=1)
            )
            db.add(req2)
            db.flush()

            # Create history
            history1 = RequirementStatusHistory(
                id=uuid.uuid4(),
                requirement_id=req2.id,
                from_status=None,
                to_status="backlog",
                changed_by=str(users[1].id),
                changed_by_name=users[1].name,
                note="Requirement created",
                is_backward=False,
                changed_at=datetime.utcnow() - timedelta(days=4)
            )
            db.add(history1)

            history2 = RequirementStatusHistory(
                id=uuid.uuid4(),
                requirement_id=req2.id,
                from_status="backlog",
                to_status="todo",
                changed_by=str(users[0].id),
                changed_by_name=users[0].name,
                note="Let's do this",
                is_backward=False,
                changed_at=datetime.utcnow() - timedelta(days=3)
            )
            db.add(history2)

            history3 = RequirementStatusHistory(
                id=uuid.uuid4(),
                requirement_id=req2.id,
                from_status="todo",
                to_status="in_progress",
                assigned_to="AI-代码开发助手",
                assigned_to_name="代码开发助手",
                changed_by=str(users[0].id),
                changed_by_name=users[0].name,
                note="Assign to AI",
                is_backward=False,
                changed_at=datetime.utcnow() - timedelta(days=2)
            )
            db.add(history3)

            # Create comments
            comment1 = Comment(
                id=uuid.uuid4(),
                requirement_id=req2.id,
                content="这个需求看起来不错。让我们明天安排一次评审。",
                author_name=users[1].name,
                created_at=datetime.utcnow() - timedelta(hours=2)
            )
            db.add(comment1)

            comment2 = Comment(
                id=uuid.uuid4(),
                requirement_id=req2.id,
                content="我已经附上了设计规范供参考。",
                author_name=users[2].name,
                created_at=datetime.utcnow() - timedelta(hours=1)
            )
            db.add(comment2)

            comment3 = Comment(
                id=uuid.uuid4(),
                requirement_id=req2.id,
                content="实施",
                author_name=users[0].name,
                created_at=datetime.utcnow() - timedelta(minutes=30)
            )
            db.add(comment3)

            print(f"Created REQ-{req2.req_number}: {req2.title}")
            next_req_num += 1

            # Requirement 3: Done
            req3 = Requirement(
                id=uuid.uuid4(),
                project_id=project.id,
                req_number=next_req_num,
                title="首页轮播图管理",
                description="开发后台轮播图管理功能，支持上传、排序、上下架等操作。",
                status="done",
                priority="low",
                created_by=str(users[2].id),
                assigned_to=str(users[1].id),
                assigned_to_name=users[1].name,
                return_count=0,
                completed_at=datetime.utcnow() - timedelta(days=5)
            )
            db.add(req3)
            db.flush()

            # Create history
            history1 = RequirementStatusHistory(
                id=uuid.uuid4(),
                requirement_id=req3.id,
                from_status=None,
                to_status="backlog",
                changed_by=str(users[2].id),
                changed_by_name=users[2].name,
                note="Requirement created",
                is_backward=False,
                changed_at=datetime.utcnow() - timedelta(days=10)
            )
            db.add(history1)

            history2 = RequirementStatusHistory(
                id=uuid.uuid4(),
                requirement_id=req3.id,
                from_status="backlog",
                to_status="todo",
                changed_by=str(users[0].id),
                changed_by_name=users[0].name,
                is_backward=False,
                changed_at=datetime.utcnow() - timedelta(days=8)
            )
            db.add(history2)

            history3 = RequirementStatusHistory(
                id=uuid.uuid4(),
                requirement_id=req3.id,
                from_status="todo",
                to_status="in_progress",
                assigned_to=str(users[1].id),
                assigned_to_name=users[1].name,
                changed_by=str(users[0].id),
                changed_by_name=users[0].name,
                is_backward=False,
                changed_at=datetime.utcnow() - timedelta(days=7)
            )
            db.add(history3)

            history4 = RequirementStatusHistory(
                id=uuid.uuid4(),
                requirement_id=req3.id,
                from_status="in_progress",
                to_status="review",
                changed_by=str(users[1].id),
                changed_by_name=users[1].name,
                note="Ready for review",
                is_backward=False,
                changed_at=datetime.utcnow() - timedelta(days=6)
            )
            db.add(history4)

            history5 = RequirementStatusHistory(
                id=uuid.uuid4(),
                requirement_id=req3.id,
                from_status="review",
                to_status="done",
                changed_by=str(users[0].id),
                changed_by_name=users[0].name,
                note="Looks good!",
                is_backward=False,
                changed_at=datetime.utcnow() - timedelta(days=5)
            )
            db.add(history5)

            print(f"Created REQ-{req3.req_number}: {req3.title}")

            db.commit()

        print("\n[4/4] Done!")
        print("=" * 60)
        print(f"Successfully seeded complete mock data!")
        print(f"Project ID: {project.id}")
        print(f"Users created/used: {[u.name for u in users]}")
        print("=" * 60)

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_complete_data()
