
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

list_folders_files_source = os.listdir(source_folder_path)

# Destination directories for different file types

print("Choose Option 1. Move to Desired Folder, 2. Just Organize in Default Folder")
Location = input("Choose Option: ")

if Location == 1:
    dest_dir_images = str(input("Select Destination Directory for Images: "))
    dest_dir_videos = str(input("Select Destination Directory for Videos: "))
    dest_dir_audio = str(input("Select Destination Directory for Audio: "))
    dest_dir_documents = str(input("Select Destination Directory for Documents: "))
    
elif Location == 2:
    dest_dir_images = source_folder_path
    dest_dir_videos = source_folder_path
    dest_dir_audio = source_folder_path
    dest_dir_documents = source_folder_path

# Crating folders if they are not exist

def create_folders_with_categorization():
    
    if not os.path.exists(dest_dir_images):
        os.mkdir(dest_dir_images)
        
    if not os.path.exists(dest_dir_videos):
        os.makedirs(dest_dir_videos)
    
    if not os.path.exists(dest_dir_audio):
        os.makedirs(dest_dir_audio)
        
    if not os.path.exists(dest_dir_documents):
        os.makedirs(dest_dir_documents)


def move_file():
    
    for filename in list_folders_files_source:
        file_extension = os.path.splitext(filename)[1].lower()
        file_path = os.path.join(source_folder_path, filename)
        
        if os.path.isdir(file_path):
            continue

        
        if file_extension in image_extensions:
            shutil.move(filename, dest_dir_images)
            print(f"{filename} moved to {dest_dir_images}")
            
        if file_extension in video_extensions:
            shutil.move(filename, dest_dir_videos)
            print(f"{filename} moved to {dest_dir_videos}")
            
        if file_extension in audio_extensions:
            shutil.move(filename, dest_dir_audio)
            print(f"{filename} moved to {dest_dir_audio}")
            
        if file_extension in document_extensions:
            shutil.move(filename, dest_dir_documents)
            print(f"{filename} moved to {dest_dir_documents}")

    

if __name__ == "__main__":
    # Ensure destination directories exist
    create_folders_with_categorization()
    
    # Move files to appropriate directories
    move_file()