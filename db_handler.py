"""
db_handler.py

Manages SQLite database interactions for migrated blog posts.
Includes utilities for initialization, migration tracking, table viewing,
schema updates, and bulk resets.
"""

import sqlite3
import logging
from tabulate import tabulate

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

DB_FILE = "migrated_posts.db"


def initialize_db():
    """
    Initializes the database and creates the 'posts' table if it doesn't exist.
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            featured_image BOOL,
            wp_post_id INTEGER
        )
    """)
    conn.commit()
    conn.close()


def is_post_migrated(url):
    """
    Checks if a given post URL already exists in the migration table.
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT 1 FROM posts WHERE url = ?", (url,))
    result = c.fetchone()
    conn.close()
    return result is not None


def mark_post_as_migrated(url):
    """
    Inserts a URL into the posts table to track migration.
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO posts (url) VALUES (?)", (url,))
    conn.commit()
    conn.close()


def mark_featured_image_as_migrated(url):
    """
    Stub function for future support. Currently unused.
    """
    logging.warning("mark_featured_image_as_migrated is defined but not used.")


def view_migrated_posts(db_path="migrated_posts.db", table_name="posts"):
    """
    Displays all records from the posts table in a formatted table.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        if not rows:
            logging.info(f"No records found in '{table_name}'.")
            return

        column_names = [description[0] for description in cursor.description]
        print("\nMigrated Posts:\n")
        print(tabulate(rows, headers=column_names, tablefmt="fancy_grid"))

    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
    finally:
        if conn:
            conn.close()


def add_field_to_table(db_filename, table_name, new_field_name, field_type="TEXT"):
    """
    Adds a new column to the specified table if it doesn't already exist.
    """
    try:
        conn = sqlite3.connect(db_filename)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        if new_field_name in columns:
            logging.warning(f"⚠️ Field '{new_field_name}' already exists in '{table_name}'.")
            return

        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {new_field_name} {field_type}")
        conn.commit()
        logging.info(f"✅ Added column '{new_field_name}' ({field_type}) to table '{table_name}'.")

    except sqlite3.Error as e:
        logging.error(f"❌ SQLite error: {e}")
    finally:
        if conn:
            conn.close()


def set_default_value_for_field(db_filename, table_name, field_name, default_value):
    """
    Sets a default value for a specific field across all rows in a table.
    """
    try:
        conn = sqlite3.connect(db_filename)
        cursor = conn.cursor()
        cursor.execute(f"UPDATE {table_name} SET {field_name} = ?", (default_value,))
        conn.commit()
        logging.info(f"✅ Default value '{default_value}' set for field '{field_name}' in '{table_name}'.")

    except sqlite3.Error as e:
        logging.error(f"❌ SQLite error: {e}")
    finally:
        if conn:
            conn.close()


def delete_migrated_posts():
    """
    Deletes all entries from the posts table and resets the ID counter.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM posts")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='posts'")
    conn.commit()
    conn.close()
    logging.info("🧹 All posts deleted and sequence reset.")


if __name__ == "__main__":
    # Sample call to display posts table
    view_migrated_posts()
