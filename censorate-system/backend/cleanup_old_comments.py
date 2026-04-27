#!/usr/bin/env python3
"""
Script to update old comments in the database.
This will help with testing the comment display fix.
"""
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal, init_db
from app.models.comment import Comment
from app.models.user import User


def cleanup_old_comments():
    """Update or remove old test comments."""
    print("Initializing database...")
    init_db()

    db = SessionLocal()
    try:
        print("\n=== Checking comments ===")
        comments = db.query(Comment).all()
        print(f"Found {len(comments)} comments")

        for comment in comments:
            print(f"\nComment ID: {comment.id}")
            print(f"  Author: {comment.author_name} (ID: {comment.author_id})")
            print(f"  Content: {comment.content[:50]}...")
            print(f"  Created: {comment.created_at}")

            # Option: update "你" to something else for testing
            if comment.author_name == "你":
                print("  → Updating author name to 'TestUser'")
                comment.author_name = "TestUser"

        db.commit()
        print("\n=== Comments updated ===")

        print("\n=== Checking users ===")
        users = db.query(User).all()
        print(f"Found {len(users)} users:")
        for user in users:
            print(f"  - {user.name} ({user.email})")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def delete_all_comments():
    """Delete all comments (for clean testing)."""
    print("Initializing database...")
    init_db()

    db = SessionLocal()
    try:
        print("\n=== Deleting all comments ===")
        comments = db.query(Comment).all()
        print(f"Deleting {len(comments)} comments...")

        for comment in comments:
            db.delete(comment)

        db.commit()
        print("All comments deleted!")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Cleanup old test comments")
    parser.add_argument(
        "--delete-all",
        action="store_true",
        help="Delete all comments instead of updating"
    )

    args = parser.parse_args()

    if args.delete_all:
        delete_all_comments()
    else:
        cleanup_old_comments()
