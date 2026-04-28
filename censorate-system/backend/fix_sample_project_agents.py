#!/usr/bin/env python3
"""Fix sample project AI agent members configuration"""

import sys
import uuid
sys.path.insert(0, '.')

from app.core.database import SessionLocal
from app.models.project import Project
from app.models.team_member import TeamMember

def main():
    db = SessionLocal()
    try:
        print("=" * 60)
        print("Fixing Sample Project AI Agents")
        print("=" * 60)

        # Find sample project
        project = db.query(Project).filter(
            Project.name == "示例项目"
        ).first()

        if not project:
            print("\n❌ Sample project not found!")
            return

        print(f"\n✅ Found project: {project.name}")

        # Get AI agents
        ai_agents = db.query(TeamMember).filter(
            TeamMember.project_id == project.id,
            TeamMember.type == "ai"
        ).all()

        print(f"\nFound {len(ai_agents)} AI agents to fix")

        # Define agent configurations
        agent_configs = {
            "需求分析助手": {
                "role": "analysis_agent",
                "skills": ["需求分析", "用户研究", "竞品分析", "PRD撰写"],
                "deepagent_config": {
                    "agent_type": "hermes",
                    "capabilities": ["analysis", "research", "documentation"]
                }
            },
            "方案设计助手": {
                "role": "design_agent",
                "skills": ["系统设计", "架构设计", "API设计", "数据库设计"],
                "deepagent_config": {
                    "agent_type": "hermes",
                    "capabilities": ["design", "architecture", "planning"]
                }
            },
            "代码开发助手": {
                "role": "development_agent",
                "skills": ["前端开发", "后端开发", "代码审查", "测试"],
                "deepagent_config": {
                    "agent_type": "openclaw",
                    "capabilities": ["coding", "review", "testing"]
                }
            },
            "测试助手": {
                "role": "testing_agent",
                "skills": ["单元测试", "集成测试", "性能测试", "BUG报告"],
                "deepagent_config": {
                    "agent_type": "hermes",
                    "capabilities": ["testing", "quality_assurance", "reporting"]
                }
            }
        }

        # Update each agent
        for agent in ai_agents:
            if agent.name in agent_configs:
                config = agent_configs[agent.name]
                print(f"\n🔧 Updating: {agent.name}")
                agent.role = config["role"]
                agent.skills = config["skills"]
                agent.deepagent_config = config["deepagent_config"]
                print(f"   - Role: {config['role']}")
                print(f"   - Skills: {len(config['skills'])} skills")
                print(f"   - Config added: YES")

        db.commit()
        print("\n" + "=" * 60)
        print("✅ All AI agents updated successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
