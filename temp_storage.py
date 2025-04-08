"""
temp_storage.py

Handles temporary storage of posts during a migration session
using a lightweight SQLite database (temp.db).
"""

import sqlite3
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class TempStorage:
    """
    A lightweight temporary storage system for scraped posts
    during a session run.
    """

    def __init__(self, db_name="temp.db"):
        """
        Initializes a new temporary database connection.
        Creates the posts table if it doesn't already exist.
        """
        self.conn = sqlite3.connect(db_name)
        self.c = self.conn.cursor()
        self.c.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                title TEXT,
                url TEXT UNIQUE,
                content_html TEXT
            )
        """)
        self.conn.commit()
        logging.info("Initialized temporary storage (temp.db)")

    def save_post(self, post):
        """
        Saves a post to the temp database.
        """
        try:
            self.c.execute(
                "INSERT INTO posts (title, url, content_html) VALUES (?, ?, ?)",
                (post["title"], post["url"], post["content_html"])
            )
            self.conn.commit()
            logging.info(f"📦 Saved post to temp storage: {post['title']}")
        except sqlite3.IntegrityError:
            logging.warning(f"⚠️ Post already exists in temp storage: {post['url']}")

    def close(self):
        """
        Closes the database connection.
        """
        self.conn.close()
        logging.info("Closed temporary storage connection")
