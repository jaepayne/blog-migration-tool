"""
scraper.py

This module handles scraping the homepage and individual blog post content
from the source blog using Selenium. It extracts titles, URLs, content HTML, and images.
"""

import logging
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

CHROMEDRIVER_PATH = "./chromedriver-mac-x64/chromedriver"
SOURCE_BLOG_URL = "https://whatisalexthinking.com/"


def scrape_homepage():
    """
    Scrapes the homepage of the source blog and returns a list of posts
    with title, URL, and featured image.
    """
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(SOURCE_BLOG_URL)
    time.sleep(5)  # Wait for JS to render post grid

    posts = []

    try:
        click_show_more_button(driver)
        time.sleep(2)

        container = driver.find_element(By.XPATH, '//*[@id="bs-2"]/span/div[1]/div')
        post_elements = container.find_elements(By.XPATH, './/*[@data-ux="GridCell"]')

        for post in post_elements:
            try:
                a_tag = post.find_element(By.TAG_NAME, "a")
                link = a_tag.get_attribute("href")

                title_tag = post.find_element(By.TAG_NAME, "h4")
                title = title_tag.text.strip()

                try:
                    img_tag = post.find_element(By.TAG_NAME, "img")
                    image = img_tag.get_attribute("src")
                except:
                    image = None

                if title and link:
                    posts.append({
                        "title": title,
                        "url": link if link.startswith("http") else SOURCE_BLOG_URL + link,
                        "featured_image": image
                    })
            except Exception as e:
                logging.warning(f"Error parsing a post: {e}")
                continue

    except Exception as e:
        logging.error(f"Could not locate main post container: {e}")

    driver.quit()
    return posts


def scrape_post_content(post_url):
    """
    Scrapes the full content of a blog post, including title, date,
    main content HTML, and any embedded images.
    """
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(post_url)
    time.sleep(5)

    try:
        title_tag = driver.find_element(By.XPATH, '//h3[contains(@data-ux, "BlogMainHeading")]')
        title = title_tag.text.strip()

        date_tag = driver.find_element(By.XPATH, '//span[contains(@data-aid, "RSS_POST_DATE")]')
        date = date_tag.text.strip()

        content_container = driver.find_element(By.XPATH, '//div[contains(@data-ux, "BlogContent")]')
        content_html = content_container.get_attribute("innerHTML")

        # Find all images (first <figure> block as fallback)
        image_elements = driver.find_elements(By.XPATH, '//*[@id="bs-2"]/span/section/div/div/div[1]/main/div[2]/p[1]/figure/div/img')
        images = [img.get_attribute("src") for img in image_elements if img.get_attribute("src")]

        driver.quit()

        return {
            "url": post_url,
            "title": title,
            "content_html": content_html,
            "date": date,
            "images": images
        }

    except Exception as e:
        logging.error(f"Error scraping post: {post_url} — {e}")
        driver.quit()
        return None


def click_show_more_button(driver):
    """
    Clicks the 'Show More' button on the homepage to load additional posts.
    """
    show_more_button = driver.find_element(By.XPATH, '//span[contains(@data-aid, "RSS_SHOW_MORE_BUTTON")]')
    show_more_button.click()
    return driver


if __name__ == "__main__":
    scrape_homepage()
    scrape_post_content("https://whatisalexthinking.com/f/movie-blog-novocaine")
