import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import json
import os

# Ensure nltk packages are downloaded
nltk_path = 'nltk_data'
if not os.path.exists(nltk_path):
    nltk.download('stopwords')
    nltk.download('wordnet')
    nltk.download('punkt')
    nltk.download('punkt_tab')

# Initialize the lemmatizer
lemmatizer = WordNetLemmatizer()

# Function to lemmatize text
def lemmatize_text(text):
    words = nltk.word_tokenize(text.lower())  # Tokenize and lowercase
    lemmatized_words = [lemmatizer.lemmatize(word) for word in words if word not in stop_words]
    return ' '.join(lemmatized_words)

# Load the CSV files
credits_df = pd.read_csv("dataset/tmdb_5000_credits.csv")
movies_df = pd.read_csv("dataset/tmdb_5000_movies.csv")

# Merge the DataFrames on movie ID
merged_df = pd.merge(movies_df, credits_df, left_on='id', right_on='movie_id', how='inner')

# Drop unnecessary columns
merged_df = merged_df.drop(columns=['original_title'])  # Remove less relevant columns

# Rename columns for consistency
merged_df = merged_df.rename(columns={'title_x': 'title'})  # Assuming 'title_x' is from movies_df

# Prepare the combined features
merged_df['combined_features'] = (
    merged_df['overview'].fillna('') + ' ' +
    merged_df['genres'].fillna('') + ' ' +
    merged_df['keywords'].fillna('') + ' ' +
    merged_df['cast'].fillna('') + ' ' +
    merged_df['crew'].fillna('') + ' ' +
    merged_df['production_companies'].fillna('') + ' ' +
    merged_df['production_countries'].fillna('') + ' ' +
    merged_df['release_date'].fillna('') + ' ' +
    merged_df['popularity'].fillna(0).astype(str) + ' ' +
    merged_df['vote_average'].fillna(0).astype(str) + ' ' +
    merged_df['vote_count'].fillna(0).astype(str) + ' ' +
    merged_df['runtime'].fillna(0).astype(str) + ' ' +
    merged_df['homepage'].fillna('').astype(str) + ' ' +
    merged_df['title'].fillna('')
)

# Apply lemmatization to the combined features
stop_words = list(stopwords.words('english'))  # Convert set to list
merged_df['combined_features'] = merged_df['combined_features'].apply(lemmatize_text)

# Text vectorization using TF-IDF
vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words=stop_words)  # Include bigrams for richer matches
tfidf_matrix = vectorizer.fit_transform(merged_df['combined_features'])

# Function to preprocess and lemmatize the query
def preprocess_query(query):
    return lemmatize_text(query)

# Search function
def search(user_query):
    processed_query = preprocess_query(user_query)
    user_vector = vectorizer.transform([processed_query])
    similarity_scores = cosine_similarity(user_vector, tfidf_matrix)
    
    # Add similarity scores to DataFrame
    merged_df['similarity'] = similarity_scores.flatten()

    # Filter and sort results
    filtered_results = merged_df[merged_df['similarity'] > 0].sort_values('similarity', ascending=False)

    # Display top 10 results
    top_movies = filtered_results.head(10)
    

    if not top_movies.empty:
        print(f"Found {len(top_movies)} result(s):")
        for _, row in top_movies.iterrows():
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
                cast_names = [cast['name'] for cast in cast_data[:5]]  # Limit to top 5 cast members
                print(f"Cast: {', '.join(cast_names) if cast_names else 'None'}")
            except json.JSONDecodeError:
                print("Cast: Invalid format")
            
            print("-" * 50)
    else:
        print("No results found that match your query.")

    return top_movies

# Run the search function
# if __name__ == '__main__':
#     user_query = input("Enter: ")
#     search(user_query)