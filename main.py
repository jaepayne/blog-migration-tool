"""
Main entry point for the Blog Migration Tool.

This script coordinates scraping blog post summaries from the source site,
extracting full post content, formatting it for WordPress, and uploading it
via the REST API. It also ensures no duplicate uploads by tracking migrated posts
in a local SQLite database.
"""

import os
import logging
from selenium.common.exceptions import WebDriverException

from db_handler import initialize_db, is_post_migrated, mark_post_as_migrated
from scraper import scrape_homepage, scrape_post_content
from formatter import format_post_content
from uploader import upload_post
from temp_storage import TempStorage
import update_chromedriver


# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def run_migration():
    """Coordinates the migration process step-by-step."""

    # Remove temporary database if it exists from a previous run
    if os.path.exists("temp.db"):
        os.remove("temp.db")

    # Ensure the main database for tracking migrations is initialized
    initialize_db()

    # Scrape the homepage for available blog posts
    posts = scrape_homepage()
    if not posts:
        logging.warning("No posts found on homepage.")
        return

    # Temporary storage during current run
    temp_db = TempStorage()

    for post in posts:
        if is_post_migrated(post["url"]):
            logging.info(f"Skipping (already migrated): {post['title']}")
            continue

        logging.info(f"Scraping: {post['title']}")
        full_post = scrape_post_content(post["url"])
        if not full_post:
            logging.error(f"Failed to scrape: {post['url']}")
            continue

        temp_db.save_post(full_post)

        # Format post into structure suitable for WordPress
        formatted = format_post_content(full_post)

        # Attempt to upload and mark as migrated if successful
        if upload_post(formatted):
            mark_post_as_migrated(post["url"])
            logging.info(f"Uploaded: {post['title']}")
        else:
            logging.error(f"Failed to upload: {post['title']}")

    # Clean up temporary storage
    temp_db.close()
    if os.path.exists("temp.db"):
        os.remove("temp.db")


if __name__ == "__main__":
    try:
        run_migration()
    except WebDriverException as e:
        logging.warning(f"Selenium error encountered: {e}")
        logging.info("Attempting to update ChromeDriver and retry migration...")
        update_chromedriver.run_update_chromedriver()
        run_migration()
