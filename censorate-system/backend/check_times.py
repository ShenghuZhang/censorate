#!/usr/bin/env python3
"""Check comment times in database."""
import sys
from pathlib import Path
from datetime import datetime, timezone

backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal, init_db
from app.models.comment import Comment


def check_comments():
    """Check comments and their times."""
    print("=== Checking database times ===\n")

    init_db()
    db = SessionLocal()

    try:
        comments = db.query(Comment).order_by(Comment.created_at.desc()).limit(5).all()

        print(f"Found {len(comments)} comments:\n")

        now_utc = datetime.now(timezone.utc)
        now_local = datetime.now()

        print(f"Current time (UTC): {now_utc.isoformat()}")
        print(f"Current time (local): {now_local.isoformat()}\n")

        for i, comment in enumerate(comments, 1):
            print(f"Comment {i}:")
            print(f"  ID: {comment.id}")
            print(f"  Author: {comment.author_name}")
            print(f"  Content: {comment.content[:50]}...")
            print(f"  Created at (DB): {comment.created_at}")
            print(f"  Created at (ISO): {comment.created_at.isoformat() if comment.created_at else 'None'}")

            if comment.created_at:
                comment_time = comment.created_at.replace(tzinfo=timezone.utc)
                diff = now_utc - comment_time
                print(f"  Age: {diff.total_seconds() / 60:.1f} minutes ago")

            print()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    check_comments()
