"""
uploader.py

Handles communication with the WordPress REST API to upload posts and media.
Includes functionality for safe filename generation, image uploading, and post creation.
"""

import os
import re
import requests
import base64
import unicodedata
import logging
from datetime import datetime
from urllib.parse import urlparse
from config import WP_USER, WP_APP_PASS, WP_SITE

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

DB_PATH = "migrated_posts.db"
IMAGES_DIR = "images"
WP_MEDIA_URL = f"{WP_SITE}/wp-json/wp/v2/media"
WP_POST_URL = f"{WP_SITE}/wp-json/wp/v2/posts"


def upload_post(post_data):
    """
    Uploads a blog post to WordPress using the REST API.

    Args:
        post_data (dict): Contains post metadata and content.

    Returns:
        bool: True if upload was successful, False otherwise.
    """
    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{WP_USER}:{WP_APP_PASS}".encode()).decode("utf-8"),
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "WP-PostUploader/1.0"
    }

    post_payload = {
        "date": post_data["date"],
        "title": post_data["title"],
        "content": post_data["content"],
        "author": 2,
        "categories": [29],
        "status": "publish",
        "featured_media": post_data["featured_media"]
    }

    response = requests.post(WP_POST_URL, headers=headers, json=post_payload)

    if response.status_code == 201:
        logging.info(f"✅ Successfully uploaded post: {post_data['title']}")
        return True
    else:
        logging.error(f"❌ Failed to upload post: {post_data['title']} | {response.status_code} — {response.text}")
        return False


def get_image_headers():
    """
    Returns HTTP headers for uploading media to WordPress.
    """
    return {
        "Authorization": "Basic " + base64.b64encode(f"{WP_USER}:{WP_APP_PASS}".encode()).decode("utf-8"),
        "Content-Type": "application/octet-stream",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0"
    }


def get_current_wp_date_path():
    """
    Returns current year and month as strings for WordPress media folder path.
    """
    now = datetime.now()
    return now.strftime("%Y"), now.strftime("%m")


def upload_featured_image(image_path):
    """
    Uploads a featured image to WordPress media library.

    Args:
        image_path (str): Local path to the image file.

    Returns:
        int | None: Media ID of the uploaded image or None on failure.
    """
    try:
        with open(image_path, 'rb') as img_file:
            image_data = img_file.read()
    except FileNotFoundError:
        logging.warning("⚠️ No file found at image_path — skipping featured image upload.")
        return None

    filename = os.path.basename(image_path)
    filename = safe_filename(filename)
    headers = get_image_headers()
    headers.update({"Content-Disposition": f"attachment; filename={filename}"})

    response = requests.post(WP_MEDIA_URL, headers=headers, data=image_data)

    if response.status_code == 201:
        media_id = response.json().get("id")
        logging.info(f"✅ Uploaded featured image: {filename} | Media ID: {media_id}")
        return media_id
    else:
        logging.error(f"❌ Failed to upload featured image: {filename}
{response.text}")
        return None


def update_image_links_in_content(content, image_map):
    """
    Replaces original image URLs in post content with WordPress upload URLs.

    Args:
        content (str): Original post HTML.
        image_map (dict): Mapping of old image URLs to new file names.

    Returns:
        str: Updated HTML content.
    """
    year, month = get_current_wp_date_path()
    for original_url, local_filename in image_map.items():
        new_url = f"{WP_SITE}/wp-content/uploads/{year}/{month}/{local_filename}"
        content = content.replace(original_url, new_url)
    return content


def safe_filename(name):
    """
    Sanitizes and normalizes a string for safe file naming.

    Args:
        name (str): Original filename.

    Returns:
        str: ASCII-safe filename.
    """
    name = unicodedata.normalize("NFKD", name)
    return name.encode("ascii", "ignore").decode("ascii")


if __name__ == "__main__":
    # Example test post payload
    test_post = {
        "title": "Test Post - Hello World",
        "content": "<p>This is a simple test post using the WordPress REST API.</p>",
        "date": "2025-03-27T16:44:38",
        "featured_media": 885
    }

    success = upload_post(test_post)
    logging.info(f"Did it work? {success}")
