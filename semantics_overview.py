from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import json
import pickle

# Load the pre-trained model
model = SentenceTransformer('all-MiniLM-L6-v2') 
# model = SentenceTransformer('paraphrase-MiniLM-L3-v2')  # mô hình nhẹ hơn 

# Load the datasets
credits_df = pd.read_csv("dataset/tmdb_5000_credits.csv")
movies_df = pd.read_csv("dataset/tmdb_5000_movies.csv")

# Merge the DataFrames on movie ID
merged_df = pd.merge(movies_df, credits_df, left_on='id', right_on='movie_id', how='inner')

# Drop unnecessary columns
merged_df = merged_df.drop(columns=['original_title'])

# Rename columns for consistency
merged_df = merged_df.rename(columns={'title_x': 'title'})

# Prepare the combined features
merged_df['combined_features'] = (
    merged_df['overview'].fillna('') + ' ' +
    merged_df['title'].fillna('')
)

# Function to save embeddings
def save_embeddings():
    print("Encoding movie features...")
    merged_df['embedding'] = list(model.encode(merged_df['combined_features'].tolist(), show_progress_bar=True))
    # Save embeddings and DataFrame to a file
    with open("movie_embeddings.pkl", "wb") as f:
        pickle.dump(merged_df[['title', 'id', 'vote_average', 'overview', 'release_date', 'keywords', 'genres', 'cast', 'embedding']], f)
    print("Embeddings saved!")

# Function to load embeddings
def load_embeddings():
    global merged_df
    with open("movie_embeddings.pkl", "rb") as f:
        merged_df = pickle.load(f)
    print("Embeddings loaded!")

# Check if embeddings file exists, otherwise create it
try:
    load_embeddings()
except FileNotFoundError:
    save_embeddings()

# Search function using Sentence Transformers
def search(user_query):
    query_embedding = model.encode(user_query)
    
    # Compute similarity scores
    merged_df['similarity'] = merged_df['embedding'].apply(
        lambda emb: cosine_similarity([query_embedding], [emb])[0][0]
    )
    
    # Filter and sort results
    filtered_results = merged_df[merged_df['similarity'] > 0].sort_values('similarity', ascending=False)
    top_movies = filtered_results.head(40)

    # Display top results
    if not top_movies.empty:
        print(f"Found {len(top_movies)} result(s):")
        for _, row in top_movies.iterrows():
            #print(row)
            print(f"Title: {row['title']}")
            print(f"Overview: {row['overview']}")
            print(f"Release Date: {row['release_date']}")
            
            # Extract and print keyword names
            try:
                keywords_data = json.loads(row['keywords']) if row['keywords'] else []
                keyword_names = [keyword['name'] for keyword in keywords_data]
                print(f"Keywords: {', '.join(keyword_names) if keyword_names else 'None'}")
            except json.JSONDecodeError:
                print("Keywords: Invalid format")
            
            # Extract and print genre names
            try:
                genres_data = json.loads(row['genres']) if row['genres'] else []
                genre_names = [genre['name'] for genre in genres_data]
                print(f"Genres: {', '.join(genre_names) if genre_names else 'None'}")
            except json.JSONDecodeError:
                print("Genres: Invalid format")
            
            # Extract and print cast names
            try:
                cast_data = json.loads(row['cast']) if row['cast'] else []
                cast_names = [cast['name'] for cast in cast_data[:5]]
                print(f"Cast: {', '.join(cast_names) if cast_names else 'None'}")
            except json.JSONDecodeError:
                print("Cast: Invalid format")
            
            print("-" * 50)
    else:
        print("No results found that match your query.")
        
    return top_movies

def get_merged_df():
    return merged_df
    
# Run the search function
if __name__ == '__main__':
    # user_query = input("Enter your search query: ")
    search("spider")
