#!/usr/bin/env python3
"""Update sample project to have only one AI agent"""

import sys
sys.path.insert(0, '.')

from app.core.database import SessionLocal
from app.models.project import Project
from app.models.team_member import TeamMember

def main():
    db = SessionLocal()
    try:
        print("=" * 60)
        print("Updating Sample Project to Single AI Agent")
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

        print(f"\nFound {len(ai_agents)} AI agents")

        if len(ai_agents) <= 1:
            print("✅ Project already has 1 or fewer AI agents, no action needed")
            return

        # Keep only the first one (需求分析助手), delete others
        agents_to_keep = [a for a in ai_agents if a.name == "需求分析助手"]
        agents_to_delete = [a for a in ai_agents if a.name != "需求分析助手"]

        if not agents_to_keep:
            agents_to_keep = [ai_agents[0]]
            agents_to_delete = ai_agents[1:]

        print(f"\nKeeping: {agents_to_keep[0].name}")
        for agent in agents_to_delete:
            print(f"Deleting: {agent.name}")
            db.delete(agent)

        db.commit()
        print("\n" + "=" * 60)
        print("✅ Sample project now has only one AI agent!")
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
