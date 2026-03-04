import cv2
import os

def capture_screenshots(video_path, save_folder, interval):
    # Create save folder if it doesn't exist
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    # Load video
    video = cv2.VideoCapture(video_path)

    if not video.isOpened():
        print("Error: Cannot open video file.")
        return

    fps = video.get(cv2.CAP_PROP_FPS)  # Frames per second
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps  # Total video duration in seconds

    frame_interval = int(fps * interval)  # Convert time interval to frame interval
    count = 0
    frame_num = 0

    while frame_num < total_frames:
        video.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        success, frame = video.read()

        if not success:
            break

        # Save the frame as an image
        screenshot_path = os.path.join(save_folder, f"screenshot_{count:04d}.png")
        cv2.imwrite(screenshot_path, frame)

        print(f"Saved screenshot: {screenshot_path}")

        count += 1
        frame_num += frame_interval

    video.release()
    print("Screenshot capturing completed.")

# Example usage
video_path = r"E:\Projects\General Projects\Video to Screenshots\Activation Functions ｜ Deep Learning Tutorial 8 (Tensorflow Tutorial, Keras & Python).mp4"
save_folder = r"E:\Projects\General Projects\Video to Screenshots"
interval = 10  # Interval in seconds

capture_screenshots(video_path, save_folder, interval)
