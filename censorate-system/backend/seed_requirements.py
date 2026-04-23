"""
Seed mock requirements into the database
"""
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# Add the parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.project import Project
from app.models.requirement import Requirement


def get_or_create_project(db, name="示例项目"):
    """Get existing project or create a new one"""
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
            created_by="seed-script",
            settings={
                "swimlanes": ["待处理", "需求分析", "方案设计", "开发中", "测试中", "已完成"],
                "emoji": "🎯"
            }
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        print(f"Created new project: {project.name}")
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


def seed_requirements():
    """Seed mock requirements into the database"""
    db = SessionLocal()

    try:
        # Get or create a project
        project = get_or_create_project(db, "示例项目")
        next_req_num = get_next_req_number(db, project.id)

        # Mock requirements data
        mock_requirements = [
            {
                "title": "用户登录模块开发",
                "description": "开发用户登录功能，支持手机号和邮箱两种方式登录，需要包含验证码和记住密码功能。",
                "status": "开发中",
                "priority": "high",
                "return_count": 1,
                "created_by": "seed-script"
            },
            {
                "title": "用户资料页面设计",
                "description": "设计用户个人资料页面，包含头像、昵称、个人简介等字段的编辑功能。",
                "status": "需求分析",
                "priority": "medium",
                "created_by": "seed-script"
            },
            {
                "title": "订单支付功能实现",
                "description": "实现订单支付功能，支持微信支付和支付宝两种方式，需要处理支付回调和订单状态更新。",
                "status": "方案设计",
                "priority": "high",
                "return_count": 0,
                "created_by": "seed-script"
            },
            {
                "title": "搜索功能优化",
                "description": "优化现有搜索功能，增加历史搜索记录、热门搜索推荐等功能，提升搜索体验。",
                "status": "待处理",
                "priority": "medium",
                "created_by": "seed-script"
            },
            {
                "title": "首页轮播图管理",
                "description": "开发后台轮播图管理功能，支持上传、排序、上下架等操作。",
                "status": "已完成",
                "priority": "low",
                "return_count": 0,
                "created_by": "seed-script",
                "completed_at": datetime.utcnow() - timedelta(days=3)
            },
            {
                "title": "消息推送服务",
                "description": "开发消息推送服务，支持App推送、短信和邮件三种通知方式，可配置触发条件。",
                "status": "测试中",
                "priority": "high",
                "created_by": "seed-script"
            },
            {
                "title": "数据统计仪表盘",
                "description": "开发数据统计仪表盘，展示用户增长、订单量、交易额等核心指标的趋势图表。",
                "status": "需求分析",
                "priority": "medium",
                "created_by": "seed-script"
            },
            {
                "title": "用户权限管理",
                "description": "完善用户权限管理系统，支持角色定义和细粒度权限配置。",
                "status": "开发中",
                "priority": "high",
                "return_count": 2,
                "last_returned_at": datetime.utcnow() - timedelta(days=1),
                "created_by": "seed-script"
            },
            {
                "title": "移动端适配",
                "description": "对现有页面进行移动端适配优化，确保在手机和平板上有良好的展示效果。",
                "status": "待处理",
                "priority": "low",
                "created_by": "seed-script"
            },
            {
                "title": "API文档完善",
                "description": "完善API文档，添加详细的参数说明和调用示例，更新最新的接口变更。",
                "status": "已完成",
                "priority": "low",
                "created_by": "seed-script",
                "completed_at": datetime.utcnow() - timedelta(days=7)
            },
            {
                "title": "社交分享功能",
                "description": "开发社交分享功能，支持分享到微信、QQ、微博等主流社交平台。",
                "status": "方案设计",
                "priority": "medium",
                "created_by": "seed-script"
            },
            {
                "title": "评论与评价系统",
                "description": "开发评论和评价系统，支持用户发表评论、打分、点赞等操作。",
                "status": "需求分析",
                "priority": "medium",
                "created_by": "seed-script"
            }
        ]

        # Create requirements
        created_count = 0
        for req_data in mock_requirements:
            req = Requirement(
                id=uuid.uuid4(),
                project_id=project.id,
                req_number=next_req_num,
                **req_data
            )
            db.add(req)
            next_req_num += 1
            created_count += 1
            print(f"Created REQ-{req.req_number}: {req.title}")

        db.commit()
        print(f"\nSuccessfully created {created_count} mock requirements in project: {project.name}")
        print(f"Project ID: {project.id}")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Seeding mock requirements...")
    seed_requirements()
    print("Done!")
