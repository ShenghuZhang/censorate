#!/usr/bin/env python3
"""
Simple server runner - run from this directory to avoid import issues.
"""
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run
from backend.main import app
import uvicorn

if __name__ == "__main__":
    print("Starting Censorate Management System...")
    print("API: http://localhost:8010")
    print("Docs: http://localhost:8010/docs")
    print("")
    uvicorn.run(app, host="0.0.0.0", port=8010, reload=True)
