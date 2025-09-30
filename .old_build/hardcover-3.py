import requests
from dotenv import load_dotenv
import os

DEBUG = False
load_dotenv()

output_dir = 'data'
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, "books.md")

url = "https://api.hardcover.app/v1/graphql"
headers = {
    "Authorization": os.getenv("HARDCOVER_KEY"),
    "Content-Type": "application/json"
}

query = """
query GetListById {
  books {
    title
    description
    rating
    ratings_count
    pages
    release_date
    slug
  }
}
"""

res = requests.post(url, json={"query": query}, headers=headers).json()
books = res["data"]["books"]

# Read existing file content (if exists)
if os.path.exists(output_file):
    with open(output_file, 'r', encoding='utf-8') as f:
        existing_content = f.read()
else:
    existing_content = ""

with open(output_file, 'a', encoding='utf-8') as f:
    for book in books:
        slug = book.get('slug')
        # Check if slug is in existing content to avoid duplicates
        if slug and slug in existing_content:
            if DEBUG:
                print(f"Skipped (already in file): {slug}")
            continue

        # Build content string for this book
        content = ""
        if book.get('title'):
            content += f"title: {book['title']}\n"
        if book.get('description'):
            content += f"description: {book['description']}\n"
        if book.get('rating'):
            content += f"rating: {book['rating']}\n"
        if book.get('ratings_count'):
            content += f"rating_count: {book['ratings_count']}\n"
        if book.get('pages'):
            content += f"pages: {book['pages']}\n"
        if book.get('release_date'):
            content += f"release_date: {book['release_date']}\n"
        if slug:
            content += f"slug: {slug}\n"

        content = content.strip()

        # Append to file with spacing
        f.write(content + "\n\n")
        if DEBUG:
            print(f"Appended: {slug}")
