import requests
from bs4 import BeautifulSoup
from PIL import Image
import requests
import os
from io import BytesIO
import json

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

movies_data = load_json("dataset/movies.json")

def get_poster_image(id):
    # Đường dẫn file poster
    poster_path = f"poster/{id}.jpg"
    default_path = "poster/default.jpg"
    
    # Kiểm tra nếu poster đã tồn tại
    if os.path.exists(poster_path):
        return poster_path

    # Nếu chưa tồn tại, tiến hành crawl poster
    url = f"https://www.themoviedb.org/movie/{id}"
    response = requests.get(url)
    
    # Kiểm tra nếu truy cập trang thành công
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Tìm thẻ img trong class 'poster w-full'
        poster = soup.find('img', class_='poster w-full')
        
        if poster:
            # Lấy giá trị của thuộc tính 'src'
            poster_url = poster['src']
            
            # Tải ảnh về
            img_response = requests.get(poster_url)
            
            if img_response.status_code == 200:
                # Tạo thư mục 'poster' nếu chưa tồn tại
                os.makedirs('poster', exist_ok=True)
                
                # Lưu ảnh vào file poster/{id}.jpg
                with open(poster_path, 'wb') as f:
                    f.write(img_response.content)
                
                # Kiểm tra lại nếu file ảnh thực sự tồn tại
                if os.path.exists(poster_path):
                    return poster_path
                else:
                    print("Lỗi khi lưu poster.")
            else:
                print("Không tải được ảnh từ URL.")
        else:
            print("Không tìm thấy poster.")
    else:
        print(f"Truy cập trang thất bại với mã lỗi {response.status_code}.")
    
    # Trả về ảnh mặc định nếu không có poster
    return default_path

# Hàm nhập ID từ người dùng
def input_movie_id():
    try:
        movie_id = int(input("Nhập ID của bộ phim: "))
        return movie_id
    except ValueError:
        print("ID phải là một số nguyên hợp lệ.")
        return None

# # Sử dụng hàm nhập ID và lấy URL poster
# movie_id = input_movie_id()

# if movie_id:
#     poster_url = get_poster_image(movie_id)
#     if poster_url:
#         print("Poster Image URL:", poster_url)
        
#         # Tải hình ảnh và hiển thị
#         response = requests.get(poster_url)
#         img = Image.open(BytesIO(response.content))
#         img.show()  # Hiển thị hình ảnh

def crawl_poster():
    with open('dataset/movies.json', 'r', encoding='utf-8') as file:
        movies_data = json.load(file)   

    for movie_id, movie in movies_data.items():  # Iterate over key-value pairs
        try:
            poster_url = get_poster_image(movie_id)  # Use the key as the movie ID
            print(f"Poster URL for {movie['title']}: {poster_url}")
        except Exception as e:
            print(f"Lỗi khi tải poster cho phim {movie.get('title', 'Unknown')}: {e}")

if __name__ == "__main__":
    crawl_poster()
