# When you need a quick, one-time organization of files from a directory like Downloads.


import os
import shutil                   # This module provides a number of high-level operations on files and collections of files.

# Define file categories and their respective folders
file_types = {
    'Documents': [".doc", ".docx", ".odt",
                       ".pdf", ".xls", ".xlsx", ".ppt", ".pptx"],
    'Images': [".jpg", ".jpeg", ".jpe", ".jif", ".jfif", ".jfi", ".png", ".gif", ".webp", ".tiff", ".tif", ".psd", ".raw", ".arw", ".cr2", ".nrw",
                    ".k25", ".bmp", ".dib", ".heif", ".heic", ".ind", ".indd", ".indt", ".jp2", ".j2k", ".jpf", ".jpf", ".jpx", ".jpm", ".mj2", ".svg", ".svgz", ".ai", ".eps", ".ico"],
    'Videos': [".webm", ".mpg", ".mp2", ".mpeg", ".mpe", ".mpv", ".ogg",
                    ".mp4", ".mp4v", ".m4v", ".avi", ".wmv", ".mov", ".qt", ".flv", ".swf", ".avchd"],
    'Music': [".m4a", ".flac", "mp3", ".wav", ".wma", ".aac"],
    'Archives': ['.zip', '.rar', '.tar'],
    # Add more categories as needed
}

# Path to your Downloads folder
download_folder = os.path.expanduser("~/Downloads")

# Function to categorize files
def categorize_files(file_name):
    for category, extensions in file_types.items():
        if any(file_name.endswith(ext) for ext in extensions):
            return category
    return 'Others'

# Function to move files
def move_files():
    for file_name in os.listdir(download_folder):
        file_path = os.path.join(download_folder, file_name)
        
        if os.path.isfile(file_path):
            category = categorize_files(file_name)
            target_folder = os.path.join(download_folder, category)
            
            # Create the folder if it doesn't exist
            os.makedirs(target_folder, exist_ok=True)
            
            # Move the file
            shutil.move(file_path, os.path.join(target_folder, file_name))
            print(f'Moved: {file_name} to {target_folder}')

if __name__ == "__main__":
    move_files()
    print("File categorization complete.")