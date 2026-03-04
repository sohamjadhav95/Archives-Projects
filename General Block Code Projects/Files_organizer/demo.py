import os
import shutil

# File Extensions list

image_extensions = [".jpg", ".jpeg", ".jpe", ".jif", ".jfif", ".jfi", ".png", ".gif", ".webp", ".tiff", ".tif", ".psd", ".raw", ".arw", ".cr2", ".nrw",
                    ".k25", ".bmp", ".dib", ".heif", ".heic", ".ind", ".indd", ".indt", ".jp2", ".j2k", ".jpf", ".jpf", ".jpx", ".jpm", ".mj2", ".svg", ".svgz", ".ai", ".eps", ".ico"]

video_extensions = [".webm", ".mpg", ".mp2", ".mpeg", ".mpe", ".mpv", ".ogg",
                    ".mp4", ".mp4v", ".m4v", ".avi", ".wmv", ".mov", ".qt", ".flv", ".swf", ".avchd"]

audio_extensions = [".m4a", ".flac", "mp3", ".wav", ".wma", ".aac"]

document_extensions = [".doc", ".docx", ".odt", ".pdf", ".xls", ".xlsx", ".ppt", ".pptx"]


# Source for operations

source_folder_path = str(input("Enter source folder path: "))

# Use os.walk to get all files in the directory and subdirectories
def categorize_files():
    for files in os.listdir(source_folder_path):
        for filename in files:
            file_extension = os.path.splitext(filename)[1].lower()
            if file_extension in image_extensions:
                print(f"Image file: {filename}")

# Call the function to categorize files
categorize_files()