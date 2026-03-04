import cv2
import os
from PIL import Image, ImageDraw, ImageFont
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import imageio

# Validate if the video format is supported
def validate_video_format(video_path):
    supported_formats = ['.mp4', '.avi', '.mov', '.mkv']
    return os.path.splitext(video_path)[1].lower() in supported_formats

# Add timestamp watermark to a frame
def add_timestamp(frame, timestamp):
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    color = (255, 255, 255)  # White color for text
    thickness = 2
    position = (10, 30)  # Position of the timestamp
    return cv2.putText(frame, timestamp, position, font, font_scale, color, thickness, cv2.LINE_AA)

# Resize the frame to the desired width and height
def resize_frame(frame, width, height):
    return cv2.resize(frame, (width, height))

# Capture a single frame and save it as an image
def capture_frame(video_path, save_folder, frame_num, count, format_choice, add_watermark, width, height):
    video = cv2.VideoCapture(video_path)
    video.set(cv2.CAP_PROP_POS_FRAMES, frame_num)  # Move to the target frame
    success, frame = video.read()
    if success:
        if add_watermark:
            timestamp = f"{frame_num / video.get(cv2.CAP_PROP_FPS):.2f}s"  # Calculate timestamp
            frame = add_timestamp(frame, timestamp)
        if width and height:
            frame = resize_frame(frame, width, height)  # Resize if needed
        filename = os.path.join(save_folder, f"screenshot_{count:04d}.{format_choice}")
        cv2.imwrite(filename, frame)  # Save the frame as an image
    video.release()

# Generate a GIF from captured images
def generate_gif(image_folder, output_path):
    images = []
    for file_name in sorted(os.listdir(image_folder)):
        if file_name.endswith(('.png', '.jpg', '.bmp')):
            images.append(imageio.imread(os.path.join(image_folder, file_name)))
    imageio.mimsave(output_path, images, fps=2)  # Save images as GIF

# Capture screenshots from the video at specific intervals
def capture_screenshots(video_path, save_folder, interval, format_choice='png', add_watermark=True, width=None, height=None, start_time=0, end_time=None, generate_gif_option=False):
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)  # Create folder if it doesn't exist
    if not validate_video_format(video_path):
        raise ValueError("Unsupported video format.")

    video = cv2.VideoCapture(video_path)
    fps = video.get(cv2.CAP_PROP_FPS)  # Frames per second
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))  # Total frames in video
    duration = total_frames / fps  # Total duration in seconds
    end_time = duration if end_time is None else end_time  # Default end time if not specified

    start_frame = int(fps * start_time)  # Convert start time to frame
    end_frame = int(fps * end_time)  # Convert end time to frame
    frame_interval = int(fps * interval)  # Interval between frames

    # Use ThreadPoolExecutor for parallel processing and tqdm for progress bar
    with ThreadPoolExecutor() as executor, tqdm(total=(end_frame - start_frame) // frame_interval) as pbar:
        futures = []
        for count, frame_num in enumerate(range(start_frame, end_frame, frame_interval)):
            futures.append(executor.submit(capture_frame, video_path, save_folder, frame_num, count, format_choice, add_watermark, width, height))
            pbar.update(1)
        for future in futures:
            future.result()  # Ensure all tasks are completed
    video.release()

    # Generate GIF if the option is enabled
    if generate_gif_option:
        gif_path = os.path.join(save_folder, "timelapse.gif")
        generate_gif(save_folder, gif_path)
        print(f"GIF saved at {gif_path}")

# Example usage:
capture_screenshots(
    video_path=r"E:\Projects\General Projects\Video to Screenshots\Activation Functions ｜ Deep Learning Tutorial 8 (Tensorflow Tutorial, Keras & Python).mp4",  # Path to video file
    save_folder=r"E:\Projects\General Projects\Video to Screenshots\Screenshots",  # Folder to save screenshots
    interval=10,  # Interval in seconds
    format_choice='jpg',  # Image format (png, jpg, bmp)
    add_watermark=True,  # Add timestamp watermark
    width=1920,  # Resize width
    height=1080,  # Resize height
    start_time=0,  # Start time in seconds
    end_time=60,  # End time in seconds
    generate_gif_option=True  # Generate GIF from screenshots
)
