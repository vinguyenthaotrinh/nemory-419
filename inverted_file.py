import json
from collections import defaultdict

# Assuming movies_dict is already loaded from movies_data.json
with open('dataset/movies.json', 'r', encoding='utf-8') as file:
    movies_dict = json.load(file)

# Initialize dictionaries to store inverted indices for each field
inverted_index = {
    "genres": defaultdict(list),
    "keywords": defaultdict(list),
    "production_companies": defaultdict(list),
    "production_countries": defaultdict(list),
    "spoken_languages": defaultdict(list),
    "cast": defaultdict(list),
    "crew": defaultdict(list)
}

# Populate the inverted index dictionaries
for movie_id, movie_data in movies_dict.items():
    # Convert string fields to lists if needed (e.g., JSON-like strings)
    for field in ["genres", "keywords", "production_companies", "production_countries", "spoken_languages", "cast", "crew"]:
        # Parse JSON strings to lists
        if movie_data[field]:
            items = json.loads(movie_data[field])
            for item in items:
                if isinstance(item, dict):
                    # If the item has an 'id' and 'name' key, use 'name' as key
                    key = item.get("name")
                    if key:
                        inverted_index[field][key].append(movie_id)
                else:
                    # If it's a simple value, use it directly
                    inverted_index[field][item].append(movie_id)

# Save each inverted index to a JSON file
for field, index in inverted_index.items():
    with open(f"{field}_inverted.json", 'w', encoding='utf-8') as file:
        json.dump(index, file, ensure_ascii=False, indent=4)

print("Inverted files have been created and saved.")
