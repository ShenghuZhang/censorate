#!/usr/bin/env python3
"""Test full upload flow"""
import sys
import os
import io

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.requirement import Requirement
from app.services.attachment_service import AttachmentService

print("Testing full upload flow...")

# Get a requirement ID first
db = SessionLocal()
try:
    req = db.query(Requirement).first()
    if not req:
        print("No requirements found!")
        sys.exit(1)
    requirement_id = str(req.id)
    print(f"Using requirement: {requirement_id}")

    # Create service
    service = AttachmentService()

    # Create a mock file
    class MockFile:
        def __init__(self):
            self.filename = "test.jpg"
            self.content_type = "image/jpeg"

        async def read(self):
            return b"test image data"

    # Test upload
    import asyncio

    async def test():
        try:
            attachment = await service.upload_attachment(
                db=db,
                requirement_id=requirement_id,
                file=MockFile(),
                uploaded_by="test",
                uploaded_by_name="Test User",
                description="Test upload"
            )
            print(f"✓ Upload successful!")
            print(f"  ID: {attachment.id}")
            print(f"  Filename: {attachment.filename}")

            # Test get_attachment_with_url
            result = service.get_attachment_with_url(db, attachment)
            print(f"✓ get_attachment_with_url successful")
            print(f"  URL: {result.get('url')}")
            return result

        except Exception as e:
            print(f"✗ Upload failed: {e}")
            import traceback
            traceback.print_exc()
            return None

    result = asyncio.run(test())

    if result:
        print("\n✓ All tests passed!")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
