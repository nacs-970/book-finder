import json
import os

# Directory containing JSON files
json_dir = 'api'
os.makedirs(json_dir, exist_ok=True)

# Directory to save individual book files
output_dir = 'data'
os.makedirs(output_dir, exist_ok=True)

OVERWRITE = True

# Helper to extract tag names by category
def extract_tags_by_category(taggings, category):
    seen = set()
    tags = []
    print(taggings)
    for tagging in taggings:
        tag_info = tagging.get("tag", {})
        category_info = tag_info.get("tag_category", {})
        tag_category = category_info.get("category", "").strip().lower()
        tag_value = tag_info.get("tag", "").strip()

        if tag_category == category.lower() and tag_value not in seen:
            seen.add(tag_value)
            tags.append(tag_value)
    return tags

# Iterate over all files in the directory
for filename in os.listdir(json_dir):
    if filename.endswith('.json'):
        file_path = os.path.join(json_dir, filename)

        # Load JSON data from file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Extract books list
        books_list = data['data']['lists_by_pk']['list_books']

        
        # Save each book as a separate JSON file
        for book_info in books_list:
            book = book_info['book']
            filename = f"{book['slug']}.md"  # use slug for filename, e.g., watchmen.json
            filepath = os.path.join(output_dir, filename)

            # Check if the file already exists
            if os.path.exists(filepath) and not OVERWRITE:
                print(f"Skipped (already exists): {filepath}")
                continue

            # Extract tags
            taggings = []

            if book.get('taggings'):
                taggings = book.get("taggings")

            genres = extract_tags_by_category(taggings, "Genre")
            moods = extract_tags_by_category(taggings, "Mood")
            paces = extract_tags_by_category(taggings, "Pace")
            
            # Prepare content in the required format
            lines = []
            if book.get('title'):
                lines.append(f"title: {book['title']}\n")
            if book.get('rating'):
                lines.append(f"rating: {book['rating']:.2f}\n")
            if book.get('ratings_count'):
                lines.append(f"rating_count: {book['ratings_count']}\n")
            if book.get('pages'):
                lines.append(f"pages: {book['pages']}\n")
            if book.get('release_date'):
                lines.append(f"release_date: {book['release_date']}\n")

            if genres:
                lines.append(f"genres: {', '.join(genres)}\n")
            if moods:
                lines.append(f"moods: {', '.join(moods)}\n")
            if paces:
                lines.append(f"paces: {', '.join(paces)}\n")
                
            if book.get('description'):
                lines.append(f"description: {book['description']}")
            content = "\n".join(lines)

            # Write content to text file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Saved: {filepath}")
