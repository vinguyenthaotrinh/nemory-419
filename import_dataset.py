import kagglehub
import shutil
import os

# Download dataset
path = kagglehub.dataset_download("tmdb/tmdb-movie-metadata")

print("Path to dataset files:", path)

# Move files to the current directory
current_folder = os.getcwd() + '/dataset'
for file_name in os.listdir(path):
    shutil.move(os.path.join(path, file_name), current_folder)

print("Files moved to:", current_folder)
