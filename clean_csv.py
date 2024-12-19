import pandas as pd
import json
import re

# Load the original CSV file
df = pd.read_csv("dataset/data.csv")

# --- Data Cleaning and Formatting ---

def extract_names(json_str):
    """Extracts names from JSON string."""
    try:
        items = json.loads(json_str)
        return ', '.join([item['name'] for item in items])
    except (json.JSONDecodeError, TypeError):
        return ''

def extract_cast_names(json_str, limit=5):
    """Extracts the names of the first 'limit' actors from the cast JSON string."""
    try:
        cast = json.loads(json_str)
        return ', '.join([actor['name'] for actor in cast[:limit]])
    except (json.JSONDecodeError, TypeError):
        return ''

def clean_text(text):
    """Cleans the text by removing special characters and extra spaces."""
    text = re.sub(r'[^\w\s]', '', text)  # Remove special characters
    text = re.sub(r'\s+', ' ', text)  # Remove extra spaces
    return text.lower().strip()

# --- Applying transformations ---

# Convert 'release_date' to datetime and format as YYYY-MM-DD
df['release_date'] = pd.to_datetime(df['release_date']).dt.strftime('%Y-%m-%d')

# Extract names from JSON strings in 'genres' and 'cast' columns
df['genres'] = df['genres'].apply(extract_names)
df['cast'] = df['cast'].apply(extract_cast_names)

# Clean 'overview' and 'title' columns
df['overview'] = df['overview'].apply(lambda x: clean_text(str(x)) if pd.notnull(x) else '')
df['title'] = df['title'].apply(lambda x: clean_text(str(x)) if pd.notnull(x) else '')

# Remove unnecessary columns
df_new = df.drop(columns=['homepage', 'id', 'production_companies', 'production_countries', 'cast'])

# --- Create new CSV ---
df_new.to_csv("model_gpt/movie_data.csv", index=False)

print("Data cleaning and formatting complete. 'movie_data.csv' created.")