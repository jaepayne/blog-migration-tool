"""
download.py

Handles downloading, resizing, and optimizing images found in blog posts.
Supports both featured and content images. Integrates with ImageOptim on macOS.
"""

import os
import re
import shutil
import logging
import subprocess
import requests
from PIL import Image
from io import BytesIO
from urllib.parse import urlparse

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def process_image_links(img_list, post_title):
    """
    Processes image links from a post: downloads and prepares the featured image.

    Args:
        img_list (list): List of image URLs.
        post_title (str): Title of the blog post for file naming.

    Returns:
        dict: Paths to processed featured and content images.
    """
    if not img_list:
        return {'featured_media': "", 'content_images': []}

    reset_directory('images')

    featured_media = img_list[0]
    featured_media_path = adjust_featured_media(featured_media, post_title)

    return {
        'featured_media': featured_media_path,
        'content_images': None  # Reserved for future content image processing
    }


def adjust_featured_media(featured_media_url, post_title):
    """
    Downloads and resizes a featured image with a max height of 300px.

    Args:
        featured_media_url (str): URL to the image.
        post_title (str): Blog post title for filename use.

    Returns:
        str: Path to the saved image file or None if failed.
    """
    try:
        featured_media_url = clean_and_validate_url(featured_media_url)
        response = requests.get(featured_media_url, timeout=10)

        if response.status_code != 200:
            logging.warning(f"Failed to download featured image: {featured_media_url}")
            return None

        title = f"{post_title}_featured_media".replace(" ", "_")
        image_path = f"images/{title}.jpg"

        img = Image.open(BytesIO(response.content))

        max_height = 300
        aspect_ratio = img.width / img.height
        new_width = int(aspect_ratio * max_height)

        resized_img = img.resize((new_width, max_height), Image.LANCZOS)
        os.makedirs("images", exist_ok=True)
        resized_img.save(image_path, "JPEG", quality=85)

        logging.info(f"✅ Saved and resized featured image: {image_path}")

        subprocess.run([
            "/Applications/ImageOptim.app/Contents/MacOS/ImageOptim",
            image_path
        ])
        logging.info("✨ Optimized image with ImageOptim")
        return image_path

    except Exception as e:
        logging.error(f"❌ Error processing featured image: {e}")
        return None


def adjust_content_images(img_list):
    """
    Processes and optionally resizes multiple content images.

    Args:
        img_list (list): List of image URLs.

    Returns:
        list: Paths to downloaded and optimized image files.
    """
    path_list = []
    os.makedirs("images", exist_ok=True)

    for img_url in img_list:
        try:
            clean_img_url = clean_and_validate_url(img_url)
            response = requests.get(clean_img_url, timeout=10)

            if response.status_code != 200:
                logging.warning(f"Failed to download image: {img_url}")
                continue

            parsed = urlparse(clean_img_url)
            file_name = os.path.basename(parsed.path)
            file_path = os.path.join("images", file_name)

            img = Image.open(BytesIO(response.content))
            if img.width > 1900:
                aspect_ratio = img.height / img.width
                new_size = (1900, int(1900 * aspect_ratio))
                img = img.resize(new_size, Image.LANCZOS)
                logging.info(f"Resized image: {file_name} to {new_size}")
            else:
                logging.info(f"Downloaded image (no resize): {file_name}")

            img.save(file_path, format=img.format or "JPEG", quality=85)
            path_list.append(file_path)

            subprocess.run([
                "/Applications/ImageOptim.app/Contents/MacOS/ImageOptim",
                file_path
            ])
            logging.info(f"✨ Optimized image: {file_name}")

        except Exception as e:
            logging.error(f"Error processing {img_url}: {e}")
            continue

    return path_list


def reset_directory(directory):
    """
    Deletes and recreates a clean version of the given directory.

    Args:
        directory (str): Directory path to reset.
    """
    if os.path.exists(directory):
        shutil.rmtree(directory)
        logging.info(f"Deleted '{directory}' directory.")
    os.makedirs(directory)
    logging.info(f"Created new '{directory}' directory.")


def delete_images_directory(directory="images"):
    """
    Deletes the images directory if it exists.

    Args:
        directory (str): Target directory path.
    """
    if os.path.exists(directory):
        shutil.rmtree(directory)
        logging.info(f"Deleted '{directory}' directory.")
    else:
        logging.info(f"'{directory}' directory does not exist. Nothing to delete.")


def clean_and_validate_url(url):
    """
    Cleans protocol-relative URLs and ensures valid format.

    Args:
        url (str): Original URL.

    Returns:
        str: Cleaned and validated URL.
    """
    if url.startswith("//"):
        url = "https:" + url
    if not is_valid_url(url):
        raise ValueError(f"Invalid URL format: {url}")
    return url


def is_valid_url(url):
    """
    Validates if the given string is a proper HTTP/HTTPS URL.

    Args:
        url (str): URL to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    return re.match(r'^https?://', url) is not None


if __name__ == "__main__":
    test_images = [
        'https://img1.wsimg.com/isteam/ip/adf7abff-81a7-40a1-8f98-b0b6c4e0afcd/16783734157120.jpg',
        'https://img1.wsimg.com/isteam/ip/adf7abff-81a7-40a1-8f98-b0b6c4e0afcd/GodzillaMinusOne_blog-1100x552.jpg',
        'https://img1.wsimg.com/isteam/ip/adf7abff-81a7-40a1-8f98-b0b6c4e0afcd/Ken-in-a-I-am-Kenough-shirt-from-Barbie-Movie.jpeg'
    ]
    result = process_image_links(test_images, "Test Post")
    logging.info(f"Image processing result: {result}")
