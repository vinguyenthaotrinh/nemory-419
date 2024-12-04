import json
import dearpygui.dearpygui as dpg

# --- Hàm đọc JSON và xử lý phim ---
def load_json(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Không tìm thấy file: {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Lỗi khi đọc file JSON: {file_path}")
        return None

def weighted_rank(vote_average, vote_count, m, C):
    return ((vote_count / (vote_count + m)) * vote_average) + ((m / (vote_count + m)) * C)

def calculate_c_and_m(movies_data):
    vote_averages = [movie["vote_average"] for movie in movies_data.values() if "vote_average" in movie]
    C = sum(vote_averages) / len(vote_averages)  # Trung bình vote_average

    vote_counts = [movie["vote_count"] for movie in movies_data.values() if "vote_count" in movie]
    m = sorted(vote_counts)[int(len(vote_counts) * 0.96)]  # 96th percentile của vote_count

    return C, m

def get_movies_by_genre(genre, genres_data, movies_data, m, C):
    if genre in genres_data:
        movie_ids = genres_data[genre]
        movies = []
        for movie_id in movie_ids:
            movie_details = movies_data.get(str(movie_id))
            if movie_details and "vote_average" in movie_details and "vote_count" in movie_details:
                vote_average = movie_details.get("vote_average", 0)
                vote_count = movie_details.get("vote_count", 0)
                wr_score = weighted_rank(vote_average, vote_count, m, C)
                movies.append({
                    "title": movie_details.get("title", "Unknown"),
                    "vote_average": vote_average,
                    "vote_count": vote_count,
                    "score": wr_score
                })
        sorted_movies = sorted(movies, key=lambda x: x["score"], reverse=True)
        return sorted_movies[:10]
    else:
        return []

def find_top_movies_by_genre(genre):
    genres_file = "dataset/genres_inverted.json"
    movies_file = "dataset/movies.json"
    genres_data = load_json(genres_file)
    movies_data = load_json(movies_file)

    if genres_data and movies_data:
        C, m = calculate_c_and_m(movies_data)
        return get_movies_by_genre(genre, genres_data, movies_data, m, C)
    else:
        return []
