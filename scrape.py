import json
import os


# Directory containing JSON files
json_dir = 'api'
os.makedirs(json_dir, exist_ok=True)

# Directory to save individual book files
output_dir = 'data'
os.makedirs(output_dir, exist_ok=True)

OVERWRITE = True

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
            filename = f"{book['slug']}.json"  # use slug for filename, e.g., watchmen.json
            filepath = os.path.join(output_dir, filename)
            
            # Prepare content in the required format
            content = f"title: {book['title']}\ndescription: {book['description']}\nrating: {book['rating']}\nrating_count: {book['ratings_count']}\npages: {book['pages']}\nrelease_date: {book['release_date']}".strip()

            # Check if the file already exists
            if os.path.exists(filepath) and not OVERWRITE:
                print(f"Skipped (already exists): {filepath}")
                continue
        
            # Write content to text file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        
            print(f"Saved: {filepath}")
