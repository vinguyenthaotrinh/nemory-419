from deepface import DeepFace
from sklearn.metrics.pairwise import cosine_similarity
import os
from numpy import array

# Tải đặc trưng của ảnh truy vấn
query_image = "query2.jpg"
query_vector = DeepFace.represent(
    img_path=query_image, 
    model_name="Facenet", 
    enforce_detection=False  # Thêm enforce_detection=False
)[0]["embedding"]

# Trích xuất đặc trưng cho tất cả ảnh trong thư mục
folder_path = "1"
image_vectors = []
filenames = []

for filename in os.listdir(folder_path):
    if filename.endswith((".jpg", ".png")):
        print(filename)
        image_path = os.path.join(folder_path, filename)
        try:
            vector = DeepFace.represent(
                img_path=image_path, 
                model_name="Facenet", 
                enforce_detection=False  # Thêm enforce_detection=False
            )[0]["embedding"]
            image_vectors.append(vector)
            filenames.append(filename)
        except Exception as e:
            print(f"Error processing {filename}: {e}")

# Tính toán độ tương đồng Cosine
similarities = cosine_similarity([query_vector], array(image_vectors))[0]

# Lấy top N ảnh tương đồng nhất
top_matches = sorted(zip(filenames, similarities), key=lambda x: x[1], reverse=True)[:10]
print("Matched images:", top_matches)
