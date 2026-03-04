import sys
import cv2
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QPushButton, QLabel, QLineEdit, 
    QVBoxLayout, QWidget, QCheckBox, QProgressBar, QTextEdit, QSpinBox, QComboBox
)
from PyQt6.QtCore import Qt
from skimage.metrics import structural_similarity as ssim

# Helper functions for video processing
def add_timestamp(frame, timestamp):
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    color = (255, 255, 255)
    thickness = 2
    position = (10, 30)
    return cv2.putText(frame, timestamp, position, font, font_scale, color, thickness, cv2.LINE_AA)

def resize_frame(frame, width, height):
    return cv2.resize(frame, (width, height))

def are_images_similar(frame1, frame2, threshold):
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    if gray1.shape != gray2.shape:
        gray2 = cv2.resize(gray2, (gray1.shape[1], gray1.shape[0]))
    score, _ = ssim(gray1, gray2, full=True)
    return score >= threshold

class VideoToScreenshotsApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Video to Screenshots")
        self.setGeometry(100, 100, 600, 400)

        # Layout
        layout = QVBoxLayout()

        # Video selection
        self.video_label = QLabel("Video Path: None selected")
        self.select_video_button = QPushButton("Select Video")
        self.select_video_button.clicked.connect(self.select_video)

        # Output folder selection
        self.output_label = QLabel("Output Folder: None selected")
        self.select_output_button = QPushButton("Select Output Folder")
        self.select_output_button.clicked.connect(self.select_output)

        # Interval input
        self.interval_label = QLabel("Interval (seconds):")
        self.interval_input = QSpinBox()
        self.interval_input.setRange(1, 3600)
        self.interval_input.setValue(5)

        # Format selection
        self.format_label = QLabel("Image Format:")
        self.format_combobox = QComboBox()
        self.format_combobox.addItems(["png", "jpg", "bmp"])

        # Add watermark checkbox
        self.watermark_checkbox = QCheckBox("Add Watermark")
        self.watermark_checkbox.setChecked(True)

        # Similarity threshold
        self.similarity_label = QLabel("Similarity Threshold (0.0 - 1.0):")
        self.similarity_input = QLineEdit("0.85")

        # Start button
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_capture)

        # Progress and log
        self.progress_bar = QProgressBar()
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)

        # Add widgets to layout
        layout.addWidget(self.video_label)
        layout.addWidget(self.select_video_button)
        layout.addWidget(self.output_label)
        layout.addWidget(self.select_output_button)
        layout.addWidget(self.interval_label)
        layout.addWidget(self.interval_input)
        layout.addWidget(self.format_label)
        layout.addWidget(self.format_combobox)
        layout.addWidget(self.watermark_checkbox)
        layout.addWidget(self.similarity_label)
        layout.addWidget(self.similarity_input)
        layout.addWidget(self.start_button)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.log_output)

        # Set central widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def select_video(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Video File", "", "Video Files (*.mp4 *.avi *.mov *.mkv)")
        if file_path:
            self.video_path = file_path
            self.video_label.setText(f"Video Path: {file_path}")
    
    def select_output(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder_path:
            self.output_folder = folder_path
            self.output_label.setText(f"Output Folder: {folder_path}")
    
    def start_capture(self):
        try:
            interval = self.interval_input.value()
            format_choice = self.format_combobox.currentText()
            add_watermark = self.watermark_checkbox.isChecked()
            similarity_threshold = float(self.similarity_input.text())
            
            # Validate inputs
            if not hasattr(self, 'video_path') or not hasattr(self, 'output_folder'):
                self.log_output.append("Error: Please select both video and output folder.")
                return

            self.log_output.append("Starting screenshot capture...")
            capture_screenshots(
                self.video_path, self.output_folder, interval, format_choice, 
                add_watermark, None, None, similarity_threshold, self.progress_bar, self.log_output
            )
        except Exception as e:
            self.log_output.append(f"Error: {str(e)}")

def capture_screenshots(video_path, save_folder, interval, format_choice, add_watermark, width, height, similarity_threshold, progress_bar, log_output):

    width = 1920
    height = 1080
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    video = cv2.VideoCapture(video_path)
    fps = video.get(cv2.CAP_PROP_FPS)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps

    frame_interval = int(fps * interval)
    count = 0
    last_saved_frame = None

    progress_bar.setMaximum(total_frames // frame_interval)

    for frame_num in range(0, total_frames, frame_interval):
        video.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        success, frame = video.read()
        if not success:
            break

        if add_watermark:
            timestamp = f"{frame_num / fps:.2f}s"
            frame = add_timestamp(frame, timestamp)

        if width and height:
            frame = resize_frame(frame, width, height)

        if last_saved_frame is not None:
            if are_images_similar(frame, last_saved_frame, similarity_threshold):
                log_output.append(f"[Skipped] Frame {frame_num} is similar to the last one.")
                continue

        filename = os.path.join(save_folder, f"screenshot_{count:04d}.{format_choice}")
        cv2.imwrite(filename, frame)
        log_output.append(f"[Saved] Frame {frame_num} as {filename}")

        last_saved_frame = frame
        count += 1
        progress_bar.setValue(count)

    video.release()
    log_output.append("Screenshot capture completed.")

# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoToScreenshotsApp()
    window.show()
    sys.exit(app.exec())
