import requests
from bs4 import BeautifulSoup
from PIL import Image
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
    url = f"https://www.themoviedb.org/movie/{id}"
    response = requests.get(url)
    
    # Kiểm tra nếu truy cập trang thành công
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Tìm thẻ img trong class 'poster w-full'
        poster = soup.find('img', class_='poster w-full')
        
        if poster:
            # Lấy giá trị của thuộc tính 'src'
            return poster['src']
        else:
            print("Không tìm thấy poster.")
    else:
        print(f"Truy cập trang thất bại với mã lỗi {response.status_code}.")

# Hàm nhập ID từ người dùng
def input_movie_id():
    try:
        movie_id = int(input("Nhập ID của bộ phim: "))
        return movie_id
    except ValueError:
        print("ID phải là một số nguyên hợp lệ.")
        return None

# Sử dụng hàm nhập ID và lấy URL poster
movie_id = input_movie_id()

if movie_id:
    poster_url = get_poster_image(movie_id)
    if poster_url:
        print("Poster Image URL:", poster_url)
        
        # Tải hình ảnh và hiển thị
        response = requests.get(poster_url)
        img = Image.open(BytesIO(response.content))
        img.show()  # Hiển thị hình ảnh
