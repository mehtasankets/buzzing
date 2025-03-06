"""Script to apply database migrations."""
import sqlite3
import sys
import os
import logging
import time
from typing import List, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def ensure_migration_table(conn: sqlite3.Connection) -> None:
    """Ensure the migration tracking table exists.
    
    Args:
        conn: SQLite database connection
    """
    conn.execute("""
    CREATE TABLE IF NOT EXISTS applied_migrations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        script_name TEXT UNIQUE,
        script_path TEXT,
        applied_at TEXT,
        checksum TEXT
    )
    """)
    conn.commit()

def get_file_checksum(file_path: str) -> str:
    """Get a simple checksum of file contents.
    
    Args:
        file_path: Path to the file
        
    Returns:
        A simple checksum string
    """
    with open(file_path, 'r') as f:
        content = f.read()
    # Very simple checksum - in production you'd use a real hash
    return str(len(content))

def is_migration_applied(conn: sqlite3.Connection, script_path: str) -> bool:
    """Check if a migration has already been applied.
    
    Args:
        conn: SQLite database connection
        script_path: Path to the migration script
        
    Returns:
        True if the migration has been applied, False otherwise
    """
    script_name = os.path.basename(script_path)
    cursor = conn.execute(
        "SELECT checksum FROM applied_migrations WHERE script_name = ?", 
        (script_name,)
    )
    row = cursor.fetchone()
    
    if row is None:
        return False
    
    stored_checksum = row[0]
    current_checksum = get_file_checksum(script_path)
    
    if stored_checksum != current_checksum:
        logger.warning(f"Migration {script_name} was previously applied but has changed!")
    
    return True

def record_migration(conn: sqlite3.Connection, script_path: str) -> None:
    """Record that a migration has been applied.
    
    Args:
        conn: SQLite database connection
        script_path: Path to the migration script
    """
    script_name = os.path.basename(script_path)
    checksum = get_file_checksum(script_path)
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    
    conn.execute(
        """
        INSERT INTO applied_migrations (script_name, script_path, applied_at, checksum)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(script_name) DO UPDATE SET
            applied_at = excluded.applied_at,
            checksum = excluded.checksum
        """,
        (script_name, script_path, timestamp, checksum)
    )
    conn.commit()

def apply_migration(db_path: str, migration_script_path: str) -> None:
    """Apply a SQL migration script to the database.
    
    Args:
        db_path: Path to the SQLite database file
        migration_script_path: Path to the SQL migration script
    """
    if not os.path.exists(db_path):
        logger.error(f"Database file not found: {db_path}")
        sys.exit(1)
        
    if not os.path.exists(migration_script_path):
        logger.error(f"Migration script not found: {migration_script_path}")
        sys.exit(1)
    
    # Read the migration script
    with open(migration_script_path, 'r') as f:
        migration_sql = f.read()
    
    # Apply the migration
    try:
        conn = sqlite3.connect(db_path)
        
        # Ensure migration tracking table exists
        ensure_migration_table(conn)
        
        # Check if this migration has already been applied
        if is_migration_applied(conn, migration_script_path):
            logger.info(f"Migration already applied: {migration_script_path}")
            return
        
        # Apply the migration
        conn.executescript(migration_sql)
        
        # Record the migration
        record_migration(conn, migration_script_path)
        
        logger.info(f"Successfully applied migration: {migration_script_path}")
    except sqlite3.Error as e:
        logger.error(f"Error applying migration: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()

def main():
    """Main function to run the migration."""
    if len(sys.argv) != 3:
        print(f"Usage: python -m buzzing.scripts.apply_migration <db_path> <migration_script_path>")
        sys.exit(1)
    
    db_path = sys.argv[1]
    migration_script_path = sys.argv[2]
    
    apply_migration(db_path, migration_script_path)
    
if __name__ == "__main__":
    main()
