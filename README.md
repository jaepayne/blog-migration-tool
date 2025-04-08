# 🛠️ Blog Migration Tool (v2)

A professional tool for automating the migration of blog posts from [What Is Alex Thinking](https://whatisalexthinking.com) to [Payne Enterprises](http://payne-enterprises.com) using the WordPress REST API.

## 🚀 Features

- 🔎 Scrapes the homepage for featured blog posts
- 🧠 Uses a local SQLite database to track migrated posts and avoid duplicates
- 📝 Extracts and formats full post content using **Bootstrap 5.3**
- 📤 Authenticates and uploads each post to WordPress via API

## 📂 Directory Structure

```
blog_migration_v2/
├── main.py
├── scraper.py
├── formatter.py
├── uploader.py
├── config.py
├── db_handler.py
├── temp_storage.py
├── download.py
├── update_chromedriver.py
├── migrated_posts.db
├── images/
└── README.md
```

## ⚙️ Requirements

- Python 3.7.3
- Requests, BeautifulSoup4, and optionally Selenium (if enabled later)
- WordPress site with REST API and Application Password plugin enabled

## 🧪 Usage

Run the tool:

```bash
python main.py
```

To update the Chromedriver (if Selenium is integrated):

```bash
python update_chromedriver.py
```

## 🧼 Notes

- Be sure to add your API credentials in `config.py`
- Posts are checked against `migrated_posts.db` before uploading
- Includes graceful handling of post content formatting and media files
