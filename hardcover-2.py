import requests
from dotenv import load_dotenv
import os
load_dotenv()

# Directory containing JSON files
json_dir = 'api'
os.makedirs(json_dir, exist_ok=True)

# Directory to save individual book files
output_dir = 'data'
os.makedirs(output_dir, exist_ok=True)

url = "https://api.hardcover.app/v1/graphql"
# Set up the headers with the API key
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
OVERWRITE = False
for _ in range(1):
    res = requests.post(url, json={"query": query}, headers=headers).json()
    books = res["data"]["books"]
    for book in books:
        filename = f"{book['slug']}.md"  # use slug for filename, e.g., watchmen.json
        filepath = os.path.join(output_dir, filename)
        
        # Prepare content in the required format
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
        if book.get('tag'):
            content += f"tag: {book['tag']}\n"
        content = content.strip()

        # Check if the file already exists
        if os.path.exists(filepath) and not OVERWRITE:
            print(f"Skipped (already exists): {filepath}")
            continue
    
        # Write content to text file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
        print(f"Saved: {filepath}")
