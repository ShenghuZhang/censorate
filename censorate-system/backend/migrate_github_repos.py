#!/usr/bin/env python3
"""
Migration script to add url and description columns to github_repos table.
This preserves existing data.
"""

import sqlite3
import os

# Get the database path
db_path = os.path.join(os.path.dirname(__file__), 'database.db')

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

print(f"Connecting to database at {db_path}")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check if columns already exist
    cursor.execute("PRAGMA table_info(github_repos)")
    columns = [col[1] for col in cursor.fetchall()]

    print(f"Current columns in github_repos: {columns}")

    # Add url column if not exists
    if 'url' not in columns:
        print("Adding 'url' column...")
        cursor.execute("ALTER TABLE github_repos ADD COLUMN url VARCHAR(1024)")
        print("✓ 'url' column added")
    else:
        print("'url' column already exists, skipping")

    # Add description column if not exists
    if 'description' not in columns:
        print("Adding 'description' column...")
        cursor.execute("ALTER TABLE github_repos ADD COLUMN description TEXT")
        print("✓ 'description' column added")
    else:
        print("'description' column already exists, skipping")

    # Make url and description nullable (they already are by default in SQLite)
    # Make owner and repo nullable (they were NOT NULL before)

    # SQLite doesn't support ALTER COLUMN, so we need to recreate the table
    print("\nChecking if owner and repo need to be nullable...")

    # Get the current schema
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='github_repos'")
    create_sql = cursor.fetchone()[0]

    print(f"\nOriginal create SQL:\n{create_sql}")

    # If owner or repo are NOT NULL, we need to recreate the table
    if 'NOT NULL' in create_sql and ('owner' in create_sql or 'repo' in create_sql):
        print("\nRecreating table to make owner and repo nullable...")

        # 1. Create new table with nullable owner and repo
        new_create_sql = """
        CREATE TABLE github_repos_new (
            id VARCHAR NOT NULL,
            created_at DATETIME NOT NULL,
            updated_at DATETIME,
            archived_at DATETIME,
            project_id VARCHAR NOT NULL,
            url VARCHAR(1024),
            description TEXT,
            owner VARCHAR(255),
            repo VARCHAR(255),
            installation_id INTEGER,
            webhook_id INTEGER,
            last_synced_at DATETIME,
            PRIMARY KEY (id),
            FOREIGN KEY(project_id) REFERENCES projects (id)
        )
        """

        cursor.execute(new_create_sql)
        print("✓ New table created")

        # 2. Copy data from old table to new table
        cursor.execute("""
            INSERT INTO github_repos_new
            (id, created_at, updated_at, archived_at, project_id, owner, repo, installation_id, webhook_id, last_synced_at)
            SELECT id, created_at, updated_at, archived_at, project_id, owner, repo, installation_id, webhook_id, last_synced_at
            FROM github_repos
        """)
        print("✓ Data copied")

        # 3. Drop old table
        cursor.execute("DROP TABLE github_repos")
        print("✓ Old table dropped")

        # 4. Rename new table
        cursor.execute("ALTER TABLE github_repos_new RENAME TO github_repos")
        print("✓ Table renamed")

        print("\n✓ Table recreation complete!")
    else:
        print("\nowner and repo are already nullable, skipping table recreation")

    # Commit changes
    conn.commit()
    print("\n✓ Migration completed successfully!")

    # Verify the final schema
    print("\nFinal schema:")
    cursor.execute("PRAGMA table_info(github_repos)")
    for col in cursor.fetchall():
        print(f"  {col[1]}: {col[2]} {'NOT NULL' if col[3] else 'NULL'}")

except Exception as e:
    print(f"\n✗ Error during migration: {e}")
    conn.rollback()
    print("Changes rolled back")
    raise
finally:
    conn.close()
