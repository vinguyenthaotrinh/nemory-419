import json  
from datetime import datetime

# Declare global variables
genres_data = None
movies_data = None
country_data = None
releases_data = None
m, C = None, None

def load_data(genres_file, movies_file, country_file, releases_file):
    """
    Load JSON data into global variables.
    Args:
        genres_file (str): Path to genres JSON file.
        movies_file (str): Path to movies JSON file.
        country_file (str): Path to country JSON file.
        releases_file (str): Path to releases JSON file.
    """
    global genres_data, movies_data, country_data, releases_data, m, C
    genres_data = load_json(genres_file)
    movies_data = load_json(movies_file)
    country_data = load_json(country_file)
    releases_data = load_json(releases_file)
    m, C = calculate_c_and_m()
    
# --- Hàm đọc JSON ---
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

# --- Hàm tính điểm có trọng số ---
def weighted_rank(vote_average, vote_count):
    if (vote_count == 0 or vote_average == 0):
        return 0
    return ((vote_count / (vote_count + m)) * vote_average) + ((m / (vote_count + m)) * C)

# --- Hàm tính giá trị trung bình và ngưỡng m ---
def calculate_c_and_m():
    vote_averages = [movie["vote_average"] for movie in movies_data.values() if "vote_average" in movie]
    C = sum(vote_averages) / len(vote_averages)  # Trung bình vote_average

    vote_counts = [movie["vote_count"] for movie in movies_data.values() if "vote_count" in movie]
    m = sorted(vote_counts)[int(len(vote_counts) * 0.96)]  # 96th percentile của vote_count

    return C, m

# --- Lấy danh sách ID phim theo thể loại ---
def find_movie_ids_by_genre(genre):
    """
    Tìm danh sách ID phim theo thể loại.
    Nếu genre rỗng, trả về tất cả các ID phim trong movies_data.
    """
    if not genre or genre == "Genre":  # Nếu genre rỗng, trả về tất cả các phim
        return list(movies_data.keys())
    
    genre = genre.lower()
    if genre in genres_data:
        return genres_data[genre]
    else:
        return []
    
def find_movie_ids_by_year(release_year):
    """
    Tìm danh sách ID phim theo năm phát hành.
    Nếu release_year rỗng, trả về tất cả các ID phim trong movies_data.
    """
    if not release_year or release_year == "Release Year":  # Nếu release_year rỗng, trả về tất cả các phim
        return list(movies_data.keys())
    
    return releases_data.get(release_year, [])

def find_movie_ids_by_country(country):
    """
    Tìm danh sách ID phim theo quốc gia.
    Nếu country rỗng, trả về tất cả các ID phim trong movies_data.
    """
    if not country or country=="Country":  # Nếu country rỗng, trả về tất cả các phim
        return list(movies_data.keys())
    
    return country_data.get(country.lower(), [])

# --- Lấy thông tin phim theo ID ---
def get_movie_information(movie_id):
    """
    Lấy thông tin chi tiết của một bộ phim từ movies_data dựa trên movie_id.
    """
    movie_details = movies_data.get(str(movie_id))
    if movie_details:
        return {
            "id": movie_id,
            "title": movie_details.get("title", "Unknown"),
            "vote_average": movie_details.get("vote_average", 0),
            "vote_count": movie_details.get("vote_count", 0),
            "popularity": movie_details.get("popularity", 0),
            "release_date": movie_details.get("release_date", "")
        }
    return None

# --- Lấy thông tin chi tiết của danh sách phim ---
def get_movies_information_from_ids(movie_ids):
    """
    Lấy thông tin chi tiết cho danh sách các ID phim.
    """
    movies_info = []
    for movie_id in movie_ids:
        movie_info = get_movie_information(movie_id)
        if movie_info:  # Chỉ thêm vào nếu thông tin không None
            movies_info.append(movie_info)
    return movies_info


# --- Sắp xếp phim theo điểm số ---
def sort_movies_by_score(movies, top_n=10):
    results = []
    for movie in movies:
        vote_average = movie["vote_average"]
        vote_count = movie["vote_count"]
        score = weighted_rank(vote_average, vote_count)
        movie["score"] = score
        results.append(movie)

    # Sắp xếp danh sách theo điểm số
    sorted_results = sorted(results, key=lambda x: x["score"], reverse=True)
    return sorted_results[:top_n]

# Function to sort by popularity (descending)
def sort_by_popularity(movies, top_n):
    return sorted(movies, key=lambda movie: -movie['popularity'])[:top_n]

# Function to sort by release date (ascending)
def sort_by_release_date(movies, top_n):
    return sorted(movies, key=lambda movie: datetime.strptime(movie['release_date'], '%Y-%m-%d'), reverse=True)[:top_n]

    
def find_movie_ids_by_filters(genre, release_year, country):
    """
    Tìm các ID phim dựa trên genre, release_year và country.
    Trả về danh sách các ID phim giao nhau từ các điều kiện.
    """
    # Lấy danh sách ID từ từng điều kiện
    genre_ids = set(find_movie_ids_by_genre(genre))
    # print(genre_ids)
    year_ids = set(find_movie_ids_by_year(release_year))
    # print(year_ids)
    country_ids = set(find_movie_ids_by_country(country))
    # print(country_ids)

    # Tìm giao nhau của các danh sách ID
    intersect_ids = genre_ids & year_ids & country_ids
    return list(intersect_ids)  # Chuyển kết quả thành danh sách


if __name__ == "__main__":
    genres_file = "dataset/genres_inverted.json"
    releases_file = "dataset/release_year_inverted.json"
    country_file = "dataset/production_countries_inverted.json"
    movies_file = "dataset/movies.json"
    
    load_data(genres_file, movies_file, country_file, releases_file)

    m, C = calculate_c_and_m()
    movies = find_movie_ids_by_filters("Genre", "Release Year", "Country")
    movies = get_movies_information_from_ids(movies)
    movies = sort_by_popularity(movies, 10)
    
    