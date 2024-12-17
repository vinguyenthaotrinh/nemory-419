import json
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import GPT2LMHeadModel, GPT2Tokenizer, GPTNeoForCausalLM

# Load Movie Dataset from JSON
def load_dataset(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    movies = []
    for movie_id, movie_data in data.items():
        movies.append({
            'movie_id': movie_id,
            'title': movie_data.get('title', ''),
            'overview': movie_data.get('overview', ''),
            })
    return pd.DataFrame(movies)

# Initialize Search Engine
def initialize_search_engine(movies):
    print("Preparing the search engine...")
    # Combine relevant fields for searching
    movies['combined'] = (
        movies['title'].fillna('') + ' ' + 
        movies['overview'].fillna('')
    )
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(movies['combined'])
    return vectorizer, tfidf_matrix

# Search Movies
def search_movies(query, vectorizer, tfidf_matrix, movies):
    query_vec = vectorizer.transform([query])
    scores = cosine_similarity(query_vec, tfidf_matrix).flatten()
    ranked_indices = scores.argsort()[::-1][:10]  # Top 10 results
    return movies.iloc[ranked_indices][['title', 'overview']]

def initialize_llm_model():
    print("Initializing the Local LLM model...")
    model_name = "EleutherAI/gpt-neo-2.7B"  # Use a suitable model like GPT-Neo or GPT-2
    
    # Load the tokenizer
    try:
        tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        print("Tokenizer loaded successfully.")
    except Exception as e:
        print(f"Error loading tokenizer: {e}")
        return None, None
    
    # Load the model
    try:
        model = GPTNeoForCausalLM.from_pretrained(model_name)
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Error loading model: {e}")
        return None, None
    
    # Add pad_token if not present
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token  # Set pad_token to eos_token if it's not defined
    
    return tokenizer, model

# Function to refine the query using the model without tokenizing
def generate_refined_query(query, refinement, tokenizer, model):
  #  return query + " " + refinement
    prompt = f"Original query: '{query}'\nRefinement: '{refinement}'\nGenerate a more precise and relevant search query based on this refinement:"
    
    # Directly pass the prompt text to the model without tokenization
    inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True)
    print("INPUT", inputs)
    
    # Ensure pad_token_id is set correctly
    pad_token_id = tokenizer.pad_token_id if tokenizer.pad_token_id else tokenizer.eos_token_id
    
    try:
        # Generate the refined query based on the original input
        outputs = model.generate(
            **inputs, 
            max_length=100, 
            num_return_sequences=1, 
            do_sample=False,  # No sampling for deterministic output
            temperature=0.7,  # Set temperature for creativity, if do_sample is True
            pad_token_id=pad_token_id
        )
        # print("OUTPUT")
        # print(outputs)

        # Decode the output back into text without skipping special tokens
        refined_query = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # print("FINE QUERY", refined_query)
        # Clean up the result to only return the refined query
        refined_query = refined_query.strip().replace(prompt, '').strip()
        
        return refined_query
    except Exception as e:
        print(f"Error generating refined query: {e}")
        return query  # Return the original query in case of error

tokenized_cache = {}

def interactive_search():
    print("\nWelcome to the Movie Search Chatbot!")
    movies = load_dataset("dataset/movies.json")
    vectorizer, tfidf_matrix = initialize_search_engine(movies)
    
    # Initialize LLM Model
    tokenizer, model = initialize_llm_model()
    print(model)

    query = ""  # Initialize an empty query variable outside the loop
    print("\nYou can ask for movie recommendations based on a brief description or genre.")
    while True:
        print("query: ", query)
        if not query:  # Only ask for the query if it hasn't been set yet
            query = input("\nWhat movie are you looking for? (type 'exit' to quit): ")
            if query.lower() == 'exit':
                print("Goodbye!")
                break

        # Search the movies based on the current query
        results = search_movies(query, vectorizer, tfidf_matrix, movies)
        if results.empty:
            print("No movies found. Try refining your query.")
        else:
            print("\nTop results:")
            for i, row in results.iterrows():
                print(f"{i + 1}. {row['title']}\n")

            feedback = input("\nAre these results relevant? (yes/no): ")
            if feedback.lower() == 'no':
                refinement = input("What would you like to refine? Add more details (e.g., 'action movies after 2010'): ")
                # Generate a refined query using the local LLM
                query = generate_refined_query(query, refinement, tokenizer, model)
                print(f"Searching again with the refined query: {query}")
            else:
                query = ""  # Reset query after a successful search if feedback is yes

if __name__ == "__main__":
    interactive_search()
