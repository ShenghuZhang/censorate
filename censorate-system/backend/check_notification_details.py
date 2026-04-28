#!/usr/bin/env python3
"""Check detailed notification data."""

import sys
sys.path.insert(0, '.')

from app.core.database import SessionLocal
from app.models.notification import Notification

def main():
    db = SessionLocal()
    try:
        print("=" * 60)
        print("NOTIFICATION DETAILS")
        print("=" * 60)

        notifications = db.query(Notification).all()
        for notif in notifications:
            print(f"\nNOTIFICATION: {notif.id}")
            print(f"  user_id: {notif.user_id}")
            print(f"  type: {notif.type}")
            print(f"  title: {notif.title}")
            print(f"  message: {notif.message}")
            print(f"  read: {notif.read}")
            print(f"  requirement_id: {notif.requirement_id}")
            print(f"  created_at: {notif.created_at}")

    finally:
        db.close()

if __name__ == "__main__":
    main()
