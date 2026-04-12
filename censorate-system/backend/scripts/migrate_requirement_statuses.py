#!/usr/bin/env python
"""Migrate requirement statuses from old 6-state system to new 4-state system."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.requirement import Requirement
from app.state_machine.requirement_state_machine import RequirementStateMachine


def migrate_statuses():
    """Migrate all requirement statuses to the new 4-state system."""
    print("Starting requirement status migration...")

    db = SessionLocal()

    try:
        # Get all requirements
        requirements = db.query(Requirement).all()
        print(f"Found {len(requirements)} requirements to migrate")

        migrated_count = 0
        skipped_count = 0

        for req in requirements:
            old_status = req.status

            # Check if already using new status
            if old_status in RequirementStateMachine.SIMPLIFIED_TRANSITIONS:
                print(f"  REQ-{req.req_number}: Already using new status '{old_status}' - skipping")
                skipped_count += 1
                continue

            # Map old status to new status
            new_status = RequirementStateMachine.get_new_state(old_status)

            if new_status == old_status:
                print(f"  REQ-{req.req_number}: No mapping found for status '{old_status}' - skipping")
                skipped_count += 1
                continue

            # Update the status
            req.status = new_status
            print(f"  REQ-{req.req_number}: {old_status} → {new_status}")
            migrated_count += 1

        db.commit()
        print(f"\n✅ Migration complete!")
        print(f"   Migrated: {migrated_count}")
        print(f"   Skipped: {skipped_count}")
        print(f"   Total: {len(requirements)}")

    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()


def rollback_migration():
    """Rollback migration - restore old statuses (NOT IMPLEMENTED)."""
    print("Rollback is not implemented. Please restore from database backup.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--rollback":
        rollback_migration()
    else:
        migrate_statuses()
