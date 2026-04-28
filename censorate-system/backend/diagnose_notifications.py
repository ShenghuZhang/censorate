#!/usr/bin/env python3
"""Diagnostic script to check notification system."""

import sys
from uuid import UUID
from datetime import datetime

# Add the app directory to the path
sys.path.insert(0, '.')

from app.core.database import SessionLocal
from app.core.security import get_current_user
from app.models.user import User
from app.models.notification import Notification
from app.models.team_member import TeamMember
from app.services.notification_service import get_notification_service

def main():
    db = SessionLocal()
    notification_service = get_notification_service()

    try:
        print("=" * 60)
        print("NOTIFICATION SYSTEM DIAGNOSTIC")
        print("=" * 60)

        # Check all users
        print("\n1. ALL USERS:")
        users = db.query(User).all()
        for user in users:
            print(f"   - User ID: {user.id}, Name: {user.name}, Email: {user.email}")

        # Check all team members
        print("\n2. ALL TEAM MEMBERS:")
        team_members = db.query(TeamMember).all()
        for tm in team_members:
            print(f"   - TeamMember ID: {tm.id}, Name: {tm.name}, Email: {tm.email}, Project ID: {tm.project_id}")

        # Check all notifications
        print("\n3. ALL NOTIFICATIONS:")
        notifications = db.query(Notification).order_by(Notification.created_at.desc()).all()
        if not notifications:
            print("   (No notifications found)")
        else:
            for notif in notifications:
                print(f"   - ID: {notif.id}")
                print(f"     User ID: {notif.user_id}")
                print(f"     Type: {notif.type}")
                print(f"     Title: {notif.title}")
                print(f"     Read: {notif.read}")
                print(f"     Created: {notif.created_at}")

        # Get testuser specifically
        print("\n4. TESTUSER DETAILS:")
        testuser = db.query(User).filter(User.email == "testuser@example.com").first()
        if testuser:
            print(f"   - User ID: {testuser.id}")
            print(f"   - Name: {testuser.name}")
            print(f"   - Email: {testuser.email}")

            # Get notifications for testuser
            print("\n5. TESTUSER'S NOTIFICATIONS:")
            testuser_notifs = db.query(Notification).filter(
                Notification.user_id == testuser.id
            ).order_by(Notification.created_at.desc()).all()

            if testuser_notifs:
                for notif in testuser_notifs:
                    print(f"   - {notif.type}: {notif.title} (read: {notif.read})")

                # Get unread count
                unread_count = len([n for n in testuser_notifs if not n.read])
                print(f"\n   Unread count: {unread_count}")
            else:
                print("   (No notifications for testuser)")

            # Test notification service
            print("\n6. TEST NOTIFICATION SERVICE:")
            service_notifs = notification_service.get_user_notifications(db, testuser.id, limit=50, offset=0, unread_only=False)
            print(f"   Service returned {len(service_notifs)} notifications")

            service_unread = notification_service.get_unread_count(db, testuser.id)
            print(f"   Service unread count: {service_unread}")

        else:
            print("   (testuser@example.com not found!)")

        print("\n" + "=" * 60)
        print("DIAGNOSTIC COMPLETE")
        print("=" * 60)

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
