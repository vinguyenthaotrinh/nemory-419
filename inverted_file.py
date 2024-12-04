import json
from collections import defaultdict

# Load the movies dictionary from the JSON file
with open('dataset/movies.json', 'r', encoding='utf-8') as file:
    movies_dict = json.load(file)

# Initialize the inverted index dictionaries
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
    # Process 'genres', 'keywords', 'production_companies', 'production_countries', and 'spoken_languages' fields
    for field in ["genres", "keywords", "production_companies", "production_countries", "spoken_languages"]:
        if movie_data[field]:
            items = json.loads(movie_data[field])
            for item in items:
                if isinstance(item, dict):
                    key = item.get("name").lower()
                    if key:
                        inverted_index[field][key].append(movie_id)
                else:
                    inverted_index[field][item].append(movie_id)

    # Process 'cast' field
    if movie_data["cast"]:
        cast_list = json.loads(movie_data["cast"])
        for cast_entry in cast_list:
            cast_id = cast_entry.get("id")
            name = cast_entry.get("name")
            character = cast_entry.get("character")
            if cast_id is not None and name and character:
                # Create the composite key for cast
                cast_key = name.lower()
                # Check if an entry for the same composite key and movie_id exists; if not, add it
                if not any(
                    entry['movie_id'] == movie_id and entry['character'] == character
                    for entry in inverted_index["cast"][cast_key]
                ):
                    inverted_index["cast"][cast_key].append({
                        "movie_id": movie_id,
                        "character": character
                    })

    # Process 'crew' field
    if movie_data["crew"]:
        crew_list = json.loads(movie_data["crew"])
        for crew_member in crew_list:
            name = crew_member.get("name")
            crew_id = crew_member.get("id")
            gender = crew_member.get("gender")
            department = crew_member.get("department")
            job = crew_member.get("job")
            if name and crew_id is not None and gender is not None:
                # Create the composite key for crew
                crew_key = name.lower()
                inverted_index["crew"][crew_key].append({
                    "gender": gender,
                    "movie_id": movie_id,
                    "department": department,
                    "job": job
                })

# Save each inverted index to a JSON file
for field, index in inverted_index.items():
    with open(f"dataset/{field}_inverted.json", 'w', encoding='utf-8') as file:
        json.dump(index, file, ensure_ascii=False, indent=4)

print("Inverted files have been created and saved.")