import cv2
import os
from skimage.metrics import structural_similarity as ssim

# Add timestamp watermark
def add_timestamp(frame, timestamp):
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    color = (255, 255, 255)
    thickness = 2
    position = (10, 30)
    return cv2.putText(frame, timestamp, position, font, font_scale, color, thickness, cv2.LINE_AA)

# Resize frame
def resize_frame(frame, width, height):
    return cv2.resize(frame, (width, height))

# Compute SSIM between two images
def are_images_similar(frame1, frame2, threshold):
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    
    # Resize if needed
    if gray1.shape != gray2.shape:
        gray2 = cv2.resize(gray2, (gray1.shape[1], gray1.shape[0]))
    
    score, _ = ssim(gray1, gray2, full=True)
    return score >= threshold

# Main function to capture screenshots
def capture_screenshots(video_path, save_folder, interval, format_choice='png', add_watermark=True, width=None, height=None, similarity_threshold=0.9):
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    video = cv2.VideoCapture(video_path)
    fps = video.get(cv2.CAP_PROP_FPS)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps

    frame_interval = int(fps * interval)
    count = 0
    last_saved_frame = None

    for frame_num in range(0, total_frames, frame_interval):
        video.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        success, frame = video.read()
        if not success:
            break

        # Add timestamp if needed
        if add_watermark:
            timestamp = f"{frame_num / fps:.2f}s"
            frame = add_timestamp(frame, timestamp)

        # Resize if needed
        if width and height:
            frame = resize_frame(frame, width, height)

        # Compare with last saved frame
        if last_saved_frame is not None:
            if are_images_similar(frame, last_saved_frame, similarity_threshold):
                print(f"[Skipped] Frame {frame_num} is similar to the last one.")
                continue  # Skip saving if similar

        # Save unique frame
        filename = os.path.join(save_folder, f"screenshot_{count:04d}.{format_choice}")
        cv2.imwrite(filename, frame)
        print(f"[Saved] Frame {frame_num} as {filename}")

        last_saved_frame = frame
        count += 1

    video.release()
    print("Screenshot capture completed.")

# Example usage
video_path = "E:\Projects\General Projects\Video to Screenshots\Activation Functions ｜ Deep Learning Tutorial 8 (Tensorflow Tutorial, Keras & Python).mp4"
save_folder = "E:\Projects\General Projects\Video to Screenshots\Screenshots"
interval = 5  # Capture every 5 seconds
format_choice = 'png'
add_watermark = True
width, height = None, None
similarity_threshold = 0.85  # Lowered to allow more images

capture_screenshots(video_path, save_folder, interval, format_choice, add_watermark, width, height, similarity_threshold)
