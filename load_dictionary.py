import pandas as pd
import json

# Load the CSV files
credits_df = pd.read_csv("dataset/tmdb_5000_credits.csv")
movies_df = pd.read_csv("dataset/tmdb_5000_movies.csv")

# Merge the DataFrames on movie ID
merged_df = pd.merge(movies_df, credits_df, left_on='id', right_on='movie_id', how='inner')

# Drop the 'original_title' column
merged_df = merged_df.drop(columns=['original_title'])
movies_dict = merged_df.set_index("id").to_dict(orient="index")

output_file = "dataset/movies.json"
with open(output_file, "w", encoding="utf-8") as json_file:
    json.dump(movies_dict, json_file, ensure_ascii=False, indent=4)

print(f"Data has been stored in a dictionary and saved to {output_file}.")