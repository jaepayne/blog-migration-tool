"""
formatter.py

Formats scraped post content into a payload suitable for WordPress REST API.
Handles Bootstrap styling, image processing, and date formatting.
"""

import random
import logging
from datetime import datetime
from bs4 import BeautifulSoup
from download import process_image_links
from uploader import upload_featured_image

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def format_post_content(post):
    """
    Takes a post dictionary and returns a formatted payload for uploading.

    Args:
        post (dict): Contains title, content_html, date, images.

    Returns:
        dict: A payload containing formatted post data.
    """
    date = format_post_date(str(post["date"]))
    soup = BeautifulSoup(post["content_html"], "html.parser")

    # Add Bootstrap styling to images and gather their src
    img_links = []
    for img in soup.find_all("img"):
        img["class"] = img.get("class", []) + ["img-fluid", "mb-3"]
        img_links.append(str(img["src"]))

    # Process and upload images (download, rename, optimize)
    image_path_dict = process_image_links(img_links, post["title"])

    # Upload the featured image and get its WordPress media ID
    featured_media_id = upload_featured_image(image_path_dict["featured_media"])

    # Convert updated HTML content to string
    content = str(soup)

    # Wrap with Bootstrap container and attribution notice
    wrapped_content = f"""
    <div class="container mt-4">
        {content}
    </div>

    <div class="bg-info-subtle text-left p-3 rounded">
        <strong><a href="https://whatisalexthinking.com/" target="_blank">Source</a></strong><br/>
        This blog post was re-posted here with the permission of the original author.
        Please take a look at his actual blog for more up-to-date content.
    </div>
    &nbsp;
    <hr />
    """

    # Final payload for WordPress REST API
    payload = {
        "date": date,
        "title": post["title"],
        "content": wrapped_content,
        "featured_media": featured_media_id
    }

    logging.info(f"Post payload ready: {payload['title']}")
    return payload


def format_post_date(date_str):
    """
    Converts a date like 'March 27, 2025' to ISO 8601 format with a randomized time.

    Args:
        date_str (str): The input date string.

    Returns:
        str: ISO 8601 formatted date with time.
    """
    try:
        date_obj = datetime.strptime(date_str, "%B %d, %Y")

        # Randomize publish time between 6 AM and 11 PM
        hour = random.randint(6, 23)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)

        full_datetime = date_obj.replace(hour=hour, minute=minute, second=second)

        formatted_date = full_datetime.strftime("%Y-%m-%dT%H:%M:%S")
        logging.info(f"Formatted publish date: {formatted_date}")
        return formatted_date

    except ValueError:
        raise ValueError("Date format must be like 'March 27, 2025'")


if __name__ == "__main__":
    # Test the date formatter
    format_post_date("March 27, 2025")
