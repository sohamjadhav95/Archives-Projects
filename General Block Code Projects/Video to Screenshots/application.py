import sys
import cv2
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QPushButton, QLabel, QLineEdit, 
    QVBoxLayout, QWidget, QCheckBox, QProgressBar, QTextEdit, QSpinBox, QComboBox
)
from PyQt6.QtCore import Qt
from skimage.metrics import structural_similarity as ssim
import yt_dlp

# Helper functions
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

def get_stream_url(youtube_url):
    ydl_opts = {'format': 'best[ext=mp4]/best', 'quiet': True, 'no_warnings': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        return info['url']

class VideoToScreenshotsApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Video to Screenshots (YouTube or Local)")
        self.setGeometry(100, 100, 600, 500)

        layout = QVBoxLayout()

        # Input type selection: YouTube Link or Local Path
        self.input_type_label = QLabel("Select Input Type:")
        self.input_type_combo = QComboBox()
        self.input_type_combo.addItems(["YouTube Link", "Local Video Path"])
        self.input_type_combo.currentIndexChanged.connect(self.update_input_field)

        # Dynamic input field
        self.input_label = QLabel("Video Input:")
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Paste YouTube link or browse local video")
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_video)

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

        # Add watermark option
        self.watermark_checkbox = QCheckBox("Add Watermark")
        self.watermark_checkbox.setChecked(True)

        # Similarity threshold
        self.similarity_label = QLabel("Similarity Threshold (0.0 - 1.0):")
        self.similarity_input = QLineEdit("0.85")

        # Start button
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_capture)

        # Progress bar and log
        self.progress_bar = QProgressBar()
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)

        # Layout arrangement
        layout.addWidget(self.input_type_label)
        layout.addWidget(self.input_type_combo)
        layout.addWidget(self.input_label)
        layout.addWidget(self.input_field)
        layout.addWidget(self.browse_button)
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

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def update_input_field(self):
        if self.input_type_combo.currentText() == "YouTube Link":
            self.input_field.setPlaceholderText("Paste YouTube link here")
            self.browse_button.setEnabled(False)
        else:
            self.input_field.setPlaceholderText("Select local video file")
            self.browse_button.setEnabled(True)

    def browse_video(self):
        video_path, _ = QFileDialog.getOpenFileName(self, "Select Video File", "", "Video Files (*.mp4 *.avi *.mkv)")
        if video_path:
            self.input_field.setText(video_path)

    def select_output(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder_path:
            self.output_folder = folder_path
            self.output_label.setText(f"Output Folder: {folder_path}")

    def start_capture(self):
        try:
            input_type = self.input_type_combo.currentText()
            video_input = self.input_field.text()
            interval = self.interval_input.value()
            format_choice = self.format_combobox.currentText()
            add_watermark = self.watermark_checkbox.isChecked()
            similarity_threshold = float(self.similarity_input.text())

            if not video_input or not hasattr(self, 'output_folder'):
                self.log_output.append("Error: Provide a valid video input and output folder.")
                return

            if input_type == "YouTube Link":
                self.log_output.append("Fetching YouTube video stream...")
                stream_url = get_stream_url(video_input)
            else:
                stream_url = video_input

            self.log_output.append("Starting screenshot capture...")
            capture_screenshots(
                stream_url, self.output_folder, interval, format_choice,
                add_watermark, None, None, similarity_threshold,
                self.progress_bar, self.log_output
            )
        except Exception as e:
            self.log_output.append(f"Error: {str(e)}")

def capture_screenshots(stream_url, save_folder, interval, format_choice, add_watermark, width, height, similarity_threshold, progress_bar, log_output):
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    video = cv2.VideoCapture(stream_url)
    fps = video.get(cv2.CAP_PROP_FPS)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
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

        if last_saved_frame is not None and are_images_similar(frame, last_saved_frame, similarity_threshold):
            continue

        filename = os.path.join(save_folder, f"screenshot_{count:04d}.{format_choice}")
        cv2.imwrite(filename, frame)
        last_saved_frame = frame
        count += 1
        progress_bar.setValue(count)

    video.release()
    log_output.append("Screenshot capture completed.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoToScreenshotsApp()
    window.show()
    sys.exit(app.exec())
