import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import font

# Define file categories and their respective extensions
file_types = {
    'Documents': [".doc", ".docx", ".odt", ".pdf", ".xls", ".xlsx", ".ppt", ".pptx"],
    'Images': [".jpg", ".jpeg", ".jpe", ".jif", ".jfif", ".jfi", ".png", ".gif", ".webp", ".tiff", ".tif", ".psd", ".raw", ".arw", ".cr2", ".nrw",
               ".k25", ".bmp", ".dib", ".heif", ".heic", ".ind", ".indd", ".indt", ".jp2", ".j2k", ".jpf", ".jpf", ".jpx", ".jpm", ".mj2", ".svg", ".svgz", ".ai", ".eps", ".ico"],
    'Videos': [".webm", ".mpg", ".mp2", ".mpeg", ".mpe", ".mpv", ".ogg", ".mp4", ".mp4v", ".m4v", ".avi", ".wmv", ".mov", ".qt", ".flv", ".swf", ".avchd"],
    'Music': [".m4a", ".flac", ".mp3", ".wav", ".wma", ".aac"],
    'Archives': ['.zip', '.rar', '.tar'],
    # Add more categories as needed
}

# Function to categorize files
def categorize_files(file_name):
    for category, extensions in file_types.items():
        if any(file_name.endswith(ext) for ext in extensions):
            return category
    return 'Others'

# Function to move files
def move_files(folder_path):
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        
        if os.path.isfile(file_path):
            category = categorize_files(file_name)
            target_folder = os.path.join(folder_path, category)
            
            # Create the folder if it doesn't exist
            os.makedirs(target_folder, exist_ok=True)
            
            # Move the file
            shutil.move(file_path, os.path.join(target_folder, file_name))

    messagebox.showinfo("Success", "File categorization complete!")

# Function to open file dialog and organize files
def organize_files():
    folder_path = filedialog.askdirectory()
    if folder_path:
        move_files(folder_path)

# Setting up the GUI
root = tk.Tk()
root.title("File Organizer")
root.geometry("400x250")
root.config(bg="#f2f2f2")

# Custom font and style
header_font = font.Font(family="Helvetica", size=16, weight="bold")
button_font = font.Font(family="Arial", size=12, weight="bold")

# Adding header label
header_label = tk.Label(root, text="Organize Files by Category", font=header_font, bg="#f2f2f2", fg="#4a4a4a")
header_label.pack(pady=20)

# Adding button with styles
organize_button = tk.Button(
    root, 
    text="Select Folder and Organize", 
    command=organize_files,
    font=button_font,
    bg="#4a90e2", 
    fg="white", 
    activebackground="#357ABD", 
    activeforeground="white",
    relief="raised", 
    bd=4,
    padx=20, 
    pady=10
)
organize_button.pack(pady=30)

# Run the main loop
root.mainloop()
