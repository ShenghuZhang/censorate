#!/usr/bin/env python3
"""Simple test"""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Test 1: Import minio_client_simple
print("Testing import...")
try:
    from app.core.minio_client_simple import minio_client
    print("✓ Import successful")
    print(f"  Bucket: {minio_client.bucket_name}")
    print(f"  Upload dir: {minio_client.upload_dir}")
except Exception as e:
    print(f"✗ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Check attachments table
print("\nTesting database...")
try:
    from app.core.database import SessionLocal
    from app.models.attachment import Attachment
    db = SessionLocal()
    count = db.query(Attachment).count()
    print(f"✓ Database connected, attachments: {count}")
    db.close()
except Exception as e:
    print(f"✗ Database error: {e}")
    import traceback
    traceback.print_exc()
