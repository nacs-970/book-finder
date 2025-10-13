import requests
import os
import json

# API endpoint and headers
url = "https://api.hardcover.app/v1/graphql"
headers = {
    "Content-Type": "application/json",
    "Authorization": "apikey"
}

# GraphQL query
query = """
query GetListById {
  lists_by_pk(id: 3) {
    list_books {
      book {
        title
        description
        rating
        ratings_count
        pages
        release_date
        slug
        taggings {
          tag {
            tag_category {
              category
            }
            tag
          }
        }
      }
    }
  }
}
"""

# Request payload
payload = {
    "query": query
}

# Send the request
response = requests.post(url, json=payload, headers=headers)

# Make sure the 'api' directory exists
os.makedirs("api", exist_ok=True)

# Save the response JSON
if response.status_code == 200:
    data = response.json()
    with open("api/response.json", "w", encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("done")

else:
    print(f"failed with status code {response.status_code}")
    print(response.text)

