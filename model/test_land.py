import clip
import torch
from PIL import Image
import os

# Tải model CLIP
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

# Hàm trích xuất đặc trưng hình ảnh
def extract_features(image_path):
    image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)
    with torch.no_grad():
        features = model.encode_image(image)
    return features / features.norm(dim=-1, keepdim=True)

# Đường dẫn folder và query image
folder_path = "0"
query_image = "query.jpg"

# Trích xuất đặc trưng của query image
query_features = extract_features(query_image)

# Tìm kiếm các hình ảnh khớp
matches = []
for filename in os.listdir(folder_path):
    if filename.endswith((".jpg", ".png")):
        image_path = os.path.join(folder_path, filename)
        candidate_features = extract_features(image_path)
        similarity = (query_features @ candidate_features.T).item()  # Cosine similarity
        matches.append((image_path, similarity))

# Sắp xếp kết quả
matches.sort(key=lambda x: x[1], reverse=True)
print("Matched images:", matches[:10])  # Top 10 hình tương tự
