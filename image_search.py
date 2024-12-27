import builtins
from DeepImageSearch import Load_Data, Search_Setup

import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

# Override the input function to automatically respond 'no' without causing an error
builtins.input = lambda prompt="": "no"  # Automatically answers 'no' when input is called

def preprocess_image():
    image_list = Load_Data().from_folder(['poster'])
    st = Search_Setup(image_list=image_list, model_name='resnet50', pretrained=True, image_count=5000)
    st.run_index()  # This will now run without asking for user input
    return st

st = preprocess_image()

def search_movie_by_image(image_path, num_of_images=10):
    similar_images = st.get_similar_images(image_path=image_path, number_of_images=num_of_images)
    movie_ids = [path.split('/')[-1].split('.')[0] for _, path in similar_images.items()]
    return movie_ids

if __name__ == "__main__":
    st = preprocess_image()
    # print(search_movie_by_image(st, 'test_image/4.jpg'))
