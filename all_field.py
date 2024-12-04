import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Ensure nltk packages are downloaded
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('punkt')  # Required for tokenization

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
merged_df = merged_df.drop(columns=['original_title', 'homepage'])  # Remove less relevant columns

# Rename columns for consistency
merged_df = merged_df.rename(columns={'title_x': 'title'})  # Assuming 'title_x' is from movies_df

# Prepare the combined features
merged_df['combined_features'] = (
    merged_df['overview'].fillna('') + ' ' +
    merged_df['genres'].fillna('') + ' ' +
    merged_df['keywords'].fillna('') + ' ' +
    merged_df['cast'].fillna('') + ' ' +
    merged_df['crew'].fillna('') + ' ' +
    merged_df['production_companies'].fillna('')
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
def search():
    user_query = input("Enter your search query: ")
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
            print(f"Keywords: {row['keywords']}")
            print(f"Genres: {row['genres']}")
            print(f"Cast: {row['cast']}")
            print("-" * 50)
    else:
        print("No results found that match your query.")

# Run the search function
if __name__ == '__main__':
    search()
