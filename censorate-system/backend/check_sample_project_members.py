#!/usr/bin/env python3
"""Check sample project team members configuration"""

import sys
sys.path.insert(0, '.')

from app.core.database import SessionLocal
from app.models.project import Project
from app.models.team_member import TeamMember

def main():
    db = SessionLocal()
    try:
        print("=" * 60)
        print("Checking Sample Project Team Members")
        print("=" * 60)

        # Find sample project
        project = db.query(Project).filter(
            Project.name == "示例项目"
        ).first()

        if not project:
            print("\n❌ Sample project not found!")
            return

        print(f"\n✅ Found project: {project.name}")
        print(f"   Project ID: {project.id}")

        # Get all team members
        team_members = db.query(TeamMember).filter(
            TeamMember.project_id == project.id
        ).all()

        print(f"\nTotal team members: {len(team_members)}")

        # Separate human and AI members
        human_members = [m for m in team_members if m.type == "human"]
        ai_members = [m for m in team_members if m.type == "ai"]

        print(f"  - Human members: {len(human_members)}")
        print(f"  - AI agents: {len(ai_members)}")

        # Show human members
        if human_members:
            print("\n👥 Human Members:")
            for member in human_members:
                print(f"  • {member.name}")
                print(f"    - Nickname: {member.nickname}")
                print(f"    - Role: {member.role}")
                print(f"    - Email: {member.email}")
                print(f"    - Status: {member.status}")

        # Show AI agents with detailed check
        if ai_members:
            print("\n🤖 AI Agent Members:")
            for agent in ai_members:
                print(f"\n  • {agent.name}")
                print(f"    - Nickname: {agent.nickname}")
                print(f"    - Role: {agent.role}")
                print(f"    - Type: {agent.type}")
                print(f"    - Status: {agent.status}")
                print(f"    - Memory enabled: {agent.memory_enabled}")
                print(f"    - Skills: {agent.skills}")
                print(f"    - Has deepagent_config: {agent.deepagent_config is not None}")
                if agent.deepagent_config:
                    print(f"    - Config: {agent.deepagent_config}")

        # Check for common issues
        print("\n" + "=" * 60)
        print("Configuration Check:")
        print("=" * 60)

        issues_found = False

        # Check role formats for AI agents
        expected_roles = ["analysis_agent", "design_agent", "development_agent", "testing_agent"]
        for agent in ai_members:
            if agent.role not in expected_roles and "_agent" not in agent.role:
                print(f"⚠️  AI Agent '{agent.name}' has non-standard role: '{agent.role}'")
                print(f"    Expected roles like: {expected_roles}")
                issues_found = True

        # Check if AI agents have skills
        for agent in ai_members:
            if not agent.skills or len(agent.skills) == 0:
                print(f"⚠️  AI Agent '{agent.name}' has no skills configured")
                issues_found = True

        # Check if AI agents have deepagent_config
        for agent in ai_members:
            if not agent.deepagent_config:
                print(f"⚠️  AI Agent '{agent.name}' has no deepagent_config")
                issues_found = True

        if not issues_found:
            print("✅ No configuration issues found!")

        print("\n" + "=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
