import kagglehub
import shutil
import os

# Download dataset
path = kagglehub.dataset_download("rounakbanik/the-movies-dataset")

# Move files to the current directory
current_folder = os.getcwd()
for file_name in os.listdir(path):
    shutil.move(os.path.join(path, file_name), current_folder)

print("Files moved to:", current_folder)
