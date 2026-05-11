import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.core.config import Settings
from app.core.minio_client import minio_client

def migrate():
    settings = Settings.get()
    skills_root = Path(settings.SKILL_STORAGE_DIR)
    bucket = settings.MINIO_SKILLS_BUCKET_NAME
    
    if not skills_root.exists():
        print(f"Skills root {skills_root} does not exist. Nothing to migrate.")
        return

    print(f"Starting migration from {skills_root} to MinIO bucket '{bucket}'...")
    
    count = 0
    for skill_dir in skills_root.iterdir():
        if skill_dir.is_dir() and not skill_dir.name.startswith((".", "__")):
            print(f"Processing skill: {skill_dir.name}")
            
            # Walk through all files in the skill directory
            for root, dirs, files in os.walk(skill_dir):
                for file in files:
                    local_path = Path(root) / file
                    relative_path = local_path.relative_to(skills_root)
                    object_name = relative_path.as_posix()
                    
                    print(f"  Uploading {object_name}...")
                    
                    with open(local_path, "rb") as f:
                        content = f.read()
                        minio_client.put_object(
                            bucket_name=bucket,
                            object_name=object_name,
                            data=local_path.open("rb"),
                            length=len(content),
                            content_type=_get_content_type(object_name)
                        )
                    count += 1

    print(f"Migration complete! Uploaded {count} files.")

def _get_content_type(path: str) -> str:
    ext = Path(path).suffix.lower()
    content_types = {
        ".md": "text/markdown",
        ".json": "application/json",
        ".yaml": "application/x-yaml",
        ".yml": "application/x-yaml",
        ".txt": "text/plain",
        ".py": "text/x-python",
    }
    return content_types.get(ext, "application/octet-stream")

if __name__ == "__main__":
    migrate()
