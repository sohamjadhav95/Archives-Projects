# Desktop-Files-Automation
This is automation to manage file system in very efficient way

# 1st Code with one time Management

1. Importing Libraries


import os
import shutil
os: This module provides a way of interacting with the operating system, which includes handling file paths, directories, and general system commands like listing the contents of a directory.

shutil: This module offers high-level file operations like copying, moving, or removing files. In this case, we use it to move files from one folder to another.

2. Defining File Categories


file_types = {
    'Documents': ['.pdf', '.docx', '.txt'],
    'Images': ['.jpg', '.jpeg', '.png', '.gif'],
    'Videos': ['.mp4', '.mkv'],
    'Music': ['.mp3', '.wav'],
    'Archives': ['.zip', '.rar', '.tar'],
    # Add more categories as needed
}
file_types dictionary: This dictionary defines various file categories based on their extensions. Each key in the dictionary represents a category (e.g., 'Documents', 'Images'), and the corresponding value is a list of file extensions that belong to that category.

For example, files with extensions .pdf, .docx, and .txt are categorized as "Documents," while .jpg and .png are categorized as "Images."

This makes it easy to categorize any file by checking its extension and matching it with one of the predefined categories.

3. Path to the Download Folder


download_folder = os.path.expanduser("~/Downloads")
os.path.expanduser("~/Downloads"): This expands the tilde (~) to the path of the current user's home directory and appends the 'Downloads' folder. On a typical Linux or macOS system, this would resolve to something like /home/username/Downloads or /Users/username/Downloads. In Windows, this can be adjusted accordingly (e.g., "C:/Users/username/Downloads").

This sets the folder we want to organize. You can change the path to any folder you want to manage.

4. Function to Categorize Files


def categorize_files(file_name):
    for category, extensions in file_types.items():
        if any(file_name.endswith(ext) for ext in extensions):
            return category
    return 'Others'
categorize_files(file_name): This function takes a file's name as input and determines which category it belongs to by checking its extension.
The function iterates over each key-value pair in the file_types dictionary. For each category, it checks if the file ends with any of the extensions in the associated list.
If a match is found, the function returns the corresponding category (e.g., 'Documents', 'Images').

If the file does not match any of the predefined categories, the function returns 'Others'.
This helps organize files that don’t fit the common categories, preventing any files from being left uncategorized.

5. Function to Move Files

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
os.listdir(download_folder): This lists all the files (and subdirectories) present in the download_folder.

Loop through files: For each file in the download_folder:

file_path = os.path.join(download_folder, file_name): Construct the full path to the file by joining the folder path and the file name.
os.path.isfile(file_path): This checks whether the current item is a file (not a directory).
Categorize and Move:

categorize_files(file_name): The script calls the categorize_files function to determine which folder the file should go to.
os.path.join(download_folder, category): It then creates the path for the target folder (e.g., /Downloads/Documents/) based on the file's category.
os.makedirs(target_folder, exist_ok=True): This creates the target folder if it doesn't already exist (exist_ok=True ensures that no error is raised if the folder already exists).
shutil.move(file_path, os.path.join(target_folder, file_name)): This moves the file to the new folder (e.g., from /Downloads/file.pdf to /Downloads/Documents/file.pdf).
print(): The script prints a message indicating that the file has been successfully moved.

6. Main Program Execution


if __name__ == "__main__":
    move_files()
    print("File categorization complete.")

if __name__ == "__main__":: This is a common  idiom to ensure that certain parts of the code are only executed when the script is run directly, not when it is imported as a module.
move_files(): When the script is run, it calls the move_files() function to perform the categorization and moving process.
print("File categorization complete."): This indicates that the operation has completed.


Key Points & Potential Extensions:
Categorization: This approach is flexible because the file_types dictionary can easily be modified to add new categories or change the existing ones.

Folder Creation: The script automatically creates the destination folders if they don't already exist, ensuring it doesn’t run into issues with missing directories.
Handling of Other Files: Any files that don’t match a known extension will be placed in an "Others" folder, which you can examine later.

Potential Features to Add:
Handling Subdirectories: The current script only processes files in the top-level folder. You could add recursive processing to handle subdirectories.

Logging: You could log the movements of files to track the operations more formally.

Error Handling: Adding try-except blocks around file operations would make the script more robust in case of permission errors, locked files, etc.






# 2nd Code with automated Management

1. Importing Libraries
 
Copy code
from os import scandir, rename
from os.path import splitext, exists, join
from shutil import move
from time import sleep
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
os module: Used for interacting with the file system. In particular:

scandir lists all files and directories in a given folder.
rename is used to rename files in case of name conflicts.
splitext splits a file name from its extension.
exists checks if a file or directory already exists.
join joins folder and file names to create full paths.
shutil.move: Moves files from one directory to another.

sleep: Pauses execution for a specified amount of time (used to prevent the program from overloading the system with checks in a loop).

logging: Provides a way to log messages, so you can track the execution of the program and file movements.

watchdog.observers.Observer and watchdog.events.FileSystemEventHandler:

watchdog is an external library that allows real-time monitoring of directories. Observer watches for changes (e.g., file creation or modification) and FileSystemEventHandler responds to these changes by triggering events.


2. Global Variables for Directory Paths

Copy code
source_dir = ""
dest_dir_sfx = ""
dest_dir_music = ""
dest_dir_video = ""
dest_dir_image = ""
dest_dir_documents = ""
These variables are placeholders for folder paths where files will be moved based on their type. You need to fill in the actual directory paths.
source_dir: The directory you're monitoring (e.g., Downloads).
dest_dir_sfx, dest_dir_music, etc.: The directories where specific types of files will be moved (e.g., Music, Videos, Images, Documents).


3. File Type Extensions

Copy code
image_extensions = [".jpg", ".jpeg", ".png", ".gif", ...]
video_extensions = [".webm", ".mp4", ".avi", ...]
audio_extensions = [".m4a", ".mp3", ".wav", ...]
document_extensions = [".doc", ".pdf", ".xls", ...]
These lists define which file extensions belong to specific categories. This helps the program decide where to move a file based on its extension.
image_extensions: For image files.
video_extensions: For video files.
audio_extensions: For audio files.
document_extensions: For document files.


4. File Renaming Function

Copy code
def make_unique(dest, name):
    filename, extension = splitext(name)
    counter = 1
    while exists(f"{dest}/{name}"):
        name = f"{filename}({str(counter)}){extension}"
        counter += 1
    return name
make_unique: This function ensures that if a file with the same name already exists in the destination folder, the new file gets a unique name by appending a number (e.g., file(1).pdf).
splitext(name) separates the file name from its extension.
It checks if the file already exists using exists(). If the file exists, it adds a number in parentheses to the name (e.g., file(1).pdf, file(2).pdf).


5. File Moving Function

Copy code
def move_file(dest, entry, name):
    if exists(f"{dest}/{name}"):
        unique_name = make_unique(dest, name)
        oldName = join(dest, name)
        newName = join(dest, unique_name)
        rename(oldName, newName)
    move(entry, dest)
move_file: This function handles the actual movement of files.
First, it checks if a file with the same name exists in the destination folder using exists().
If the file exists, it renames the existing file in the destination folder to ensure uniqueness using the make_unique() function.
Then, it uses shutil.move() to move the file from the source to the destination folder.


6. The MoverHandler Class

Copy code
class MoverHandler(FileSystemEventHandler):
    def on_modified(self, event):
        with scandir(source_dir) as entries:
            for entry in entries:
                name = entry.name
                self.check_audio_files(entry, name)
                self.check_video_files(entry, name)
                self.check_image_files(entry, name)
                self.check_document_files(entry, name)
MoverHandler: This class inherits from FileSystemEventHandler and listens for file system changes in the source directory. When a change (e.g., a file being added or modified) is detected, it responds by categorizing and moving files.
on_modified(): This method is triggered whenever a modification is detected in the monitored folder (source_dir).
It calls scandir() to list all the files in the directory.
Then, for each file, it calls methods to check whether the file is an audio, video, image, or document file and moves it accordingly.
File Type Checking Methods

Copy code
def check_audio_files(self, entry, name):
    for audio_extension in audio_extensions:
        if name.endswith(audio_extension) or name.endswith(audio_extension.upper()):
            if entry.stat().st_size < 10_000_000 or "SFX" in name:
                dest = dest_dir_sfx
            else:
                dest = dest_dir_music
            move_file(dest, entry, name)
            logging.info(f"Moved audio file: {name}")

def check_video_files(self, entry, name):
    for video_extension in video_extensions:
        if name.endswith(video_extension) or name.endswith(video_extension.upper()):
            move_file(dest_dir_video, entry, name)
            logging.info(f"Moved video file: {name}")

def check_image_files(self, entry, name):
    for image_extension in image_extensions:
        if name.endswith(image_extension) or name.endswith(image_extension.upper()):
            move_file(dest_dir_image, entry, name)
            logging.info(f"Moved image file: {name}")

def check_document_files(self, entry, name):
    for documents_extension in document_extensions:
        if name.endswith(documents_extension) or name.endswith(documents_extension.upper()):
            move_file(dest_dir_documents, entry, name)
            logging.info(f"Moved document file: {name}")
These methods (check_audio_files, check_video_files, check_image_files, check_document_files) check the file extension and determine whether the file is of a certain type (audio, video, image, or document). If the file type matches, it is moved to the appropriate destination folder:
check_audio_files(): Handles audio files. It also checks if the file size is below 10MB or contains "SFX" in the name to differentiate between sound effects and music.
check_video_files(), check_image_files(), and check_document_files() do similar checks for their respective file types.
logging.info() logs the file movement for each file.


7. The Main Program

Copy code
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = source_dir
    event_handler = MoverHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            sleep(10)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
Logging Configuration: This sets up the logging system so that every log message includes the time and the message. This helps in tracking what the script is doing at any point in time.

event_handler = MoverHandler(): Creates an instance of the MoverHandler class to handle file system events.

Observer:

An Observer is created to watch the folder (source_dir).
observer.schedule(event_handler, path, recursive=True): This schedules the observer to monitor the source_dir for changes and applies the event handler.
recursive=True means it will also monitor subdirectories within the folder.
Starting and Running the Observer:

observer.start(): Starts the observer in the background, continuously watching for changes in the folder.
The while True loop keeps the program running, sleeping for 10 seconds between checks.
KeyboardInterrupt: If you press Ctrl+C, it will stop the observer and cleanly shut down the program.
Summary of Functionality:
The program continuously monitors a directory (source_dir) using the watchdog library.
When new files are added or modified in the directory, the program checks the file type (audio, video, image, document) based on the file extension.
The files are then moved to the appropriate destination folder (e.g., Music, Videos) based on their type.
File name conflicts are handled by appending numbers to the names, ensuring no files are overwritten.