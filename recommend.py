from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import json
import numpy as np
import pickle
import semantics_overview as so

class MovieRecommender:
    def __init__(self):
        self.movies_df = so.get_merged_df()
            
    def find_similar_movies(self, movie_ids, n_recommendations=10):
        """Find similar movies based on a list of movie IDs"""
        if self.movies_df is None:
            raise ValueError("Please load embeddings first using load_embeddings()")
            
        movie_ids = [int(ids) for ids in movie_ids]
        # Find the movies in our dataset
        input_movies = self.movies_df[self.movies_df['id'].isin(movie_ids)]
        if input_movies.empty:
            print(f"None of the provided movie IDs were found in the database.")
            return None
            
        if len(input_movies) < len(movie_ids):
            print(f"Warning: Only {len(input_movies)} out of {len(movie_ids)} movies were found.")
            
        # Get the average embedding of all input movies
        input_embeddings = np.array(input_movies['embedding'].tolist())
        average_embedding = np.mean(input_embeddings, axis=0)
        
        # Calculate similarity scores with the average embedding
        similarities = self.movies_df['embedding'].apply(
            lambda x: cosine_similarity([average_embedding], [x])[0][0]
        )
        
        # Add similarities to the dataframe
        self.movies_df['similarity'] = similarities
        
        # Get similar movies (excluding the input movies)
        similar_movies = (
            self.movies_df[~self.movies_df['id'].isin(movie_ids)]
            .sort_values('similarity', ascending=False)
            .head(n_recommendations)
        )
        
        return self._format_recommendations(similar_movies)
    
    def _format_recommendations(self, similar_movies):
        """Format the recommendation results"""
        recommendations = []
        
        for _, movie in similar_movies.iterrows():
            try:
                # Parse JSON strings
                genres = json.loads(movie['genres'])
                keywords = json.loads(movie['keywords'])
                cast = json.loads(movie['cast'])
                
                recommendation = {
                    'id': movie['id'],
                    'title': movie['title'],
                    'similarity_score': round(movie['similarity'] * 100, 2),
                    'overview': movie['overview'],
                    'release_date': movie['release_date'],
                    'genres': [genre['name'] for genre in genres],
                    'keywords': [keyword['name'] for keyword in keywords],
                    'cast': [actor['name'] for actor in cast[:5]],
                    'vote_average': movie['vote_average']
                }
                recommendations.append(recommendation)
                
            except json.JSONDecodeError:
                continue
                
        return recommendations

def print_movie_info(movies_df, movie_id):
    """Helper function to print movie information"""
    movie = movies_df[movies_df['id'] == movie_id].iloc[0]
    print(f"Title: {movie['title']}")
    print(f"Overview: {movie['overview'][:150]}...")
    print()

# Example usage
if __name__ == "__main__":
    # Initialize recommender
    recommender = MovieRecommender()

    # Example list of movie IDs
    movie_ids = [24428, 99861, 271110]  # Example IDs
    
    print("Input Movies:")
    for movie_id in movie_ids:
        print_movie_info(recommender.movies_df, movie_id)
    
    # Get recommendations
    recommendations = recommender.find_similar_movies(movie_ids, n_recommendations=5)
    
    if recommendations:
        print("\nTop 5 Similar Movies:\n")
        for i, movie in enumerate(recommendations, 1):
            print(f"{i}. {movie['title']} (ID: {movie['id']}, Similarity: {movie['similarity_score']}%)")
            print(f"   Genres: {', '.join(movie['genres'])}")
            print(f"   Cast: {', '.join(movie['cast'][:3])}")
            print(f"   Rating: {movie['vote_average']}/10")
            print(f"   Overview: {movie['overview'][:150]}...")
            print()