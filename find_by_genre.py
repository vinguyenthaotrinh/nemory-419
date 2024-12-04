import json

# Đường dẫn đến các file JSON
genres_file = "dataset/genres_inverted.json"
movies_file = "dataset/movies.json"

# Đọc file JSON
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

# Tính Weighted Rank (WR)
def weighted_rank(vote_average, vote_count, m, C):
    return ((vote_count / (vote_count + m)) * vote_average) + ((m / (vote_count + m)) * C)

# Tính danh sách phim theo thể loại và sắp xếp theo Weighted Rank (WR)
def find_sorted_movies_by_genre(genres_data, movies_data, genre, m, C):
    # Kiểm tra nếu thể loại tồn tại trong genres_inverted.json
    if genre in genres_data:
        movie_ids = genres_data[genre]  # Lấy danh sách ID phim
        movies = []
        for movie_id in movie_ids:
            # Lấy thông tin phim từ movies.json
            movie_details = movies_data.get(str(movie_id))
            if movie_details and "vote_average" in movie_details and "vote_count" in movie_details:
                vote_average = movie_details.get("vote_average", 0)
                vote_count = movie_details.get("vote_count", 0)
                
                # Tính điểm Weighted Rank cho phim
                wr_score = weighted_rank(vote_average, vote_count, m, C)
                
                # Thêm phim vào danh sách
                movies.append({
                    "id": movie_id,
                    "title": movie_details.get("title_y", "Unknown"),
                    "vote_average": vote_average,
                    "vote_count": vote_count,
                    "score": wr_score
                })
        
        # Sắp xếp giảm dần theo Weighted Rank (WR)
        sorted_movies = sorted(movies, key=lambda x: x["score"], reverse=True)
        return sorted_movies
    else:
        return []

# Sử dụng
genres_data = load_json(genres_file)
movies_data = load_json(movies_file)

if genres_data and movies_data:
    # Tính C (trung bình vote_average) và m (phân vị thứ 90 của vote_count)
    vote_averages = [movie["vote_average"] for movie in movies_data.values() if "vote_average" in movie]
    C = sum(vote_averages) / len(vote_averages)  # Trung bình vote_average
    print(f"The Mean value of the voting averages (C) = {C}")
    
    vote_counts = [movie["vote_count"] for movie in movies_data.values() if "vote_count" in movie]
    m = sorted(vote_counts)[int(len(vote_counts) * 0.96)]  # 90th percentile of vote_count
    print(f"The minimum vote count (m) = {m}")
    
    while True:
        # Nhập thể loại từ người dùng
        #for key in genres_data:
        #    print(key)
        genre = input("Nhập tên thể loại (hoặc nhập 'exit' để thoát): ").strip().lower()

        # Thoát nếu người dùng nhập 'exit'
        if genre == "exit":
            print("Thoát chương trình.")
            break

        # Lấy danh sách phim theo thể loại và sắp xếp theo Weighted Rank
        sorted_movies = find_sorted_movies_by_genre(genres_data, movies_data, genre, m, C)[:10]

        # In kết quả
        if sorted_movies:
            print(f"Các phim thuộc thể loại '{genre}':")
            for movie in sorted_movies:
                print(f"  - Title: {movie['title']}, Vote Average: {movie['vote_average']}, Vote Count: {movie['vote_count']}, Score (WR): {movie['score']}")
        else:
            print(f"Không tìm thấy thể loại '{genre}' trong dữ liệu.")
