"""
Add history records to existing requirements
"""
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.requirement import Requirement
from app.models.requirement_status_history import RequirementStatusHistory


def add_history():
    """Add history records to existing requirements"""
    db = SessionLocal()

    try:
        # Get all requirements
        requirements = db.query(Requirement).filter(
            Requirement.archived_at.is_(None)
        ).all()

        for req in requirements:
            # Check if they already have history
            existing_history = db.query(RequirementStatusHistory).filter(
                RequirementStatusHistory.requirement_id == req.id
            ).count()

            if existing_history > 0:
                print(f"REQ-{req.req_number} already has history, skipping")
                continue

            print(f"Adding history to REQ-{req.req_number}")

            # Add creation history
            creation_history = RequirementStatusHistory(
                id=uuid.uuid4(),
                requirement_id=req.id,
                from_status=None,
                to_status="backlog",
                changed_by=req.created_by,
                changed_by_name="Alex Kim",
                note="Requirement created",
                is_backward=False,
                changed_at=req.created_at
            )
            db.add(creation_history)

            # Check if we need more history based on current status
            current_status = req.status
            if current_status != "backlog":
                # Add transition history
                statuses = ["backlog", "todo", "in_progress", "review", "done"]
                try:
                    current_idx = statuses.index(current_status)
                    for idx in range(1, current_idx + 1):
                        from_s = statuses[idx-1]
                        to_s = statuses[idx]
                        history = RequirementStatusHistory(
                            id=uuid.uuid4(),
                            requirement_id=req.id,
                            from_status=from_s,
                            to_status=to_s,
                            changed_by="System",
                            changed_by_name="System",
                            changed_at=req.created_at + timedelta(hours=idx*2)
                        )
                        db.add(history)
                except ValueError:
                    pass

        db.commit()
        print("Done!")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Adding history to existing requirements...")
    add_history()
