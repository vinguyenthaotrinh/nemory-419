import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import os

# Load the pre-trained CLIP model
model_name = "openai/clip-vit-base-patch32"
model = CLIPModel.from_pretrained(model_name)
processor = CLIPProcessor.from_pretrained(model_name)

# Load a dataset of fashion images (ensure images are in a folder)
def load_images(image_folder):
    images = []
    for filename in os.listdir(image_folder):
        if filename.endswith((".jpg", ".png", ".jpeg")):
            images.append(os.path.join(image_folder, filename))
    return images

# Function to encode images into feature space
def encode_images(image_paths):
    encoded_images = []
    for image_path in image_paths:
        image = Image.open(image_path).convert("RGB")
        inputs = processor(images=image, return_tensors="pt")
        with torch.no_grad():
            image_features = model.get_image_features(**inputs)
        encoded_images.append(image_features)
    return torch.cat(encoded_images)

# Function to encode a text query
def encode_text(query):
    inputs = processor(text=query, return_tensors="pt")
    with torch.no_grad():
        text_features = model.get_text_features(**inputs)
    return text_features

# Find the best matches between text and image features
def retrieve_images(query, image_paths, encoded_images):
    text_features = encode_text(query)
    similarities = torch.nn.functional.cosine_similarity(
        text_features, encoded_images, dim=-1
    )
    ranked_indices = similarities.argsort(descending=True)
    return [image_paths[i] for i in ranked_indices], similarities[ranked_indices]

# Interactive search function
def interactive_search(image_folder):
    image_paths = load_images(image_folder)
    encoded_images = encode_images(image_paths)

    print("\n--- Interactive Fashion Search ---")
    print("Describe what you're looking for, e.g., 'Áo đỏ' hoặc 'T-shirt with graphic design.'")
    
    while True:
        query = input("\nNhập mô tả tìm kiếm (hoặc 'exit' để dừng): ")
        if query.lower() == 'exit':
            break
        
        results, scores = retrieve_images(query, image_paths, encoded_images)
        
        print(f"\nTop 3 kết quả cho '{query}':")
        for i, result in enumerate(results[:3]):
            print(f"{i+1}. {result} (Điểm: {scores[i].item():.4f})")

# Run interactive search on folder "0"
interactive_search("./0")
