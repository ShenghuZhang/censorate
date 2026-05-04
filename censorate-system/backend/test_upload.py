#!/usr/bin/env python3
"""Test upload directly"""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.core.minio_client_simple import minio_client
import io

print("Testing SimpleMinioClient...")

# Test 1: Check upload directory exists
print(f"Upload directory: {minio_client.upload_dir}")
print(f"Directory exists: {os.path.exists(minio_client.upload_dir)}")

# Test 2: Try to generate object name
try:
    obj_name = minio_client._generate_object_name("test-id", "test.jpg")
    print(f"Generated object name: {obj_name}")
except Exception as e:
    print(f"Error generating object name: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Try to upload a test file
try:
    test_data = b"test image data"
    file_obj = io.BytesIO(test_data)
    obj_name, url = minio_client.upload_file(
        "test-id",
        "test.jpg",
        file_obj,
        "image/jpeg",
        len(test_data)
    )
    print(f"Upload successful!")
    print(f"  Object name: {obj_name}")
    print(f"  URL: {url}")

    # Check if file exists
    file_path = os.path.join(minio_client.upload_dir, obj_name.replace('/', os.sep))
    print(f"  File path: {file_path}")
    print(f"  File exists: {os.path.exists(file_path)}")

except Exception as e:
    print(f"Error uploading: {e}")
    import traceback
    traceback.print_exc()
