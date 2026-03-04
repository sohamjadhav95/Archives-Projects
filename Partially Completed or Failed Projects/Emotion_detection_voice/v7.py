import torch
import torchaudio
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from scipy.ndimage import gaussian_filter1d
from transformers import AutoFeatureExtractor, Wav2Vec2ForSequenceClassification
import subprocess
import yt_dlp
import uuid
import os
import warnings
import argparse
from tqdm import tqdm
import time
import logging
from pydub import AudioSegment

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class VoiceEmotionDetector:
    def __init__(self, model_name="ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition", 
                 chunk_duration=1, sample_rate=16000, device=None):
        """
        Initialize the Voice Emotion Detector
        
        Args:
            model_name (str): HuggingFace model name for emotion detection
            chunk_duration (int): Duration of audio chunks in seconds
            sample_rate (int): Audio sample rate
            device (str): Device to run the model on ('cuda' or 'cpu')
        """
        self.chunk_duration = chunk_duration
        self.sample_rate = sample_rate
        
        # Set device
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
        
        logger.info(f"Using device: {self.device}")
        
        # Load model
        logger.info(f"Loading model: {model_name}")
        self.model = Wav2Vec2ForSequenceClassification.from_pretrained(model_name)
        self.feature_extractor = AutoFeatureExtractor.from_pretrained(model_name)
        self.labels = self.model.config.id2label
        self.model.eval()
        self.model.to(self.device)
        logger.info(f"Model loaded successfully with {len(self.labels)} emotion classes")
    
    def convert_to_wav(self, input_path, output_path):
        """Convert audio file to WAV format"""
        logger.info(f"Converting {input_path} to WAV...")
        try:
            command = [
                "ffmpeg", "-i", input_path, 
                "-ar", str(self.sample_rate), 
                "-ac", "1", output_path, 
                "-y", "-loglevel", "error"
            ]
            subprocess.run(command, check=True)
            logger.info("Conversion completed successfully")
            return True
        except subprocess.SubprocessError as e:
            logger.error(f"Error during conversion: {e}")
            return False
    
    def download_youtube_audio(self, url, output_path):
        """Download audio from YouTube URL"""
        logger.info(f"Downloading audio from YouTube: {url}")
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'yt_audio.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',
                    'preferredquality': '192',
                }],
                'quiet': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_title = info.get('title', 'Unknown')
            
            os.rename("yt_audio.wav", output_path)
            logger.info(f"YouTube download complete: '{video_title}'")
            return True
        except Exception as e:
            logger.error(f"Error downloading from YouTube: {e}")
            return False
    
    def load_audio(self, file_path):
        """Load audio file and return waveform"""
        logger.info(f"Loading audio file: {file_path}")
        try:
            waveform, sr = torchaudio.load(file_path)
            # Convert stereo to mono by averaging channels
            if waveform.shape[0] > 1:
                waveform = waveform.mean(dim=0)
            else:
                waveform = waveform.squeeze(0)
                
            # Normalize audio
            waveform = waveform / (torch.max(torch.abs(waveform)) + 1e-8)
            
            logger.info(f"Audio loaded: {waveform.shape[0]/sr:.2f} seconds, sample rate: {sr}Hz")
            return waveform, sr
        except Exception as e:
            logger.error(f"Error loading audio: {e}")
            return None, None
    
    def process_audio(self, input_source):
        """Process audio from file or URL and prepare for analysis"""
        temp_id = str(uuid.uuid4())[:8]
        temp_wav = f"temp_{temp_id}.wav"
        
        try:
            if input_source.startswith(("http://", "https://", "www.")):
                if not self.download_youtube_audio(input_source, temp_wav):
                    return None, None
            elif input_source.endswith((".mp4", ".mp3", ".m4a", ".aac", ".flac")):
                if not self.convert_to_wav(input_source, temp_wav):
                    return None, None
            elif input_source.endswith(".wav"):
                temp_wav = input_source
            else:
                logger.error("Unsupported input format. Provide a valid audio file or YouTube link.")
                return None, None
            
            # Load the prepared WAV file
            waveform, sr = self.load_audio(temp_wav)
            
            # Clean up temporary file if it was created
            if temp_wav != input_source and temp_wav.startswith("temp_") and os.path.exists(temp_wav):
                os.remove(temp_wav)
                
            return waveform, sr
            
        except Exception as e:
            logger.error(f"Error processing audio input: {e}")
            if temp_wav != input_source and temp_wav.startswith("temp_") and os.path.exists(temp_wav):
                os.remove(temp_wav)
            return None, None
    
    def analyze_emotion(self, waveform, sr=None):
        """
        Analyze emotion in audio waveform
        
        Args:
            waveform (Tensor): Audio waveform
            sr (int): Sample rate (optional, uses self.sample_rate if None)
            
        Returns:
            tuple: (emotions, confidence_matrix, timestamps)
        """
        if sr is None:
            sr = self.sample_rate
            
        # Check if the audio is silent
        if waveform is None or waveform.numel() == 0 or torch.max(torch.abs(waveform)) < 1e-4:
            logger.warning("Silent audio detected. Defaulting to 'neutral'")
            return ['neutral'], [[1.0] * len(self.labels)], [0]
        
        # Resample if needed
        if sr != self.sample_rate:
            logger.info(f"Resampling from {sr}Hz to {self.sample_rate}Hz")
            waveform = torchaudio.functional.resample(waveform, sr, self.sample_rate)
        
        # Calculate chunk size and split audio into chunks
        chunk_size = int(self.chunk_duration * self.sample_rate)
        chunks = [waveform[i:i + chunk_size] for i in range(0, len(waveform), chunk_size)]
        
        logger.info(f"Analyzing {len(chunks)} audio chunks...")
        
        emotions = []
        confidence_matrix = []
        
        # Process each chunk
        for i, chunk in enumerate(tqdm(chunks, desc="Processing chunks")):
            # Pad short chunks
            if chunk.shape[0] < chunk_size:
                chunk = torch.nn.functional.pad(chunk, (0, chunk_size - chunk.shape[0]))
            
            # Check if chunk is silent
            energy = torch.sum(chunk**2).item()
            if energy < 1e-4:
                emotions.append("silence")
                confidence_matrix.append([0.0] * len(self.labels))
                continue
            
            # Run through model
            try:
                inputs = self.feature_extractor(
                    chunk.numpy(), 
                    sampling_rate=self.sample_rate, 
                    return_tensors="pt", 
                    padding=True
                )
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                with torch.no_grad():
                    logits = self.model(**inputs).logits
                    probs = torch.nn.functional.softmax(logits, dim=-1).cpu().numpy()[0]
                    confidence_matrix.append(probs.tolist())
                    predicted_label = self.labels[int(np.argmax(probs))]
                    emotions.append(predicted_label)
            except Exception as e:
                logger.error(f"Error processing chunk {i}: {e}")
                emotions.append("error")
                confidence_matrix.append([0.0] * len(self.labels))
        
        # Calculate timestamps
        timestamps = [i * self.chunk_duration for i in range(len(emotions))]
        
        return emotions, confidence_matrix, timestamps
    
    def smooth_emotions(self, emotions, confidence_matrix, window_size=3):
        """Apply smoothing to emotion predictions to reduce noise"""
        if len(emotions) <= window_size:
            return emotions  # Not enough data for smoothing
            
        # Convert emotions to numerical indices
        unique_emotions = sorted(set(e for e in emotions if e != "silence" and e != "error"))
        emotion_to_idx = {emotion: i for i, emotion in enumerate(unique_emotions)}
        idx_to_emotion = {i: emotion for emotion, i in emotion_to_idx.items()}
        
        # Process confidence values into a smoothed prediction
        smoothed_emotions = []
        
        for i in range(len(emotions)):
            if emotions[i] in ["silence", "error"]:
                smoothed_emotions.append(emotions[i])
                continue
                
            # Create a window around current position
            start = max(0, i - window_size // 2)
            end = min(len(emotions), i + window_size // 2 + 1)
            window = [emotions[j] for j in range(start, end) 
                     if emotions[j] not in ["silence", "error"]]
            
            # If window is empty, use original emotion
            if not window:
                smoothed_emotions.append(emotions[i])
                continue
                
            # Get most frequent emotion in window
            emotion_counts = {}
            for emotion in window:
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            
            most_common = max(emotion_counts.items(), key=lambda x: x[1])[0]
            smoothed_emotions.append(most_common)
            
        return smoothed_emotions
    
    def visualize_emotions(self, emotions, confidence_matrix, timestamps, 
                          output_path=None, smoothed_emotions=None, title=None):
        """
        Visualize emotion detection results with multiple views
        
        Args:
            emotions (list): List of detected emotions
            confidence_matrix (list): Matrix of confidence values for each emotion
            timestamps (list): List of timestamps for each emotion
            output_path (str): Path to save the visualization (None for display)
            smoothed_emotions (list): List of smoothed emotions (optional)
            title (str): Plot title (optional)
        """
        if not emotions:
            logger.error("No emotions to visualize")
            return
            
        # Create figure with subplots
        fig = plt.figure(figsize=(14, 10))
        gs = fig.add_gridspec(3, 2, height_ratios=[1, 1, 2])
        
        # 1. Emotion Timeline (Top Left)
        ax1 = fig.add_subplot(gs[0, 0])
        
        # Map emotions to integers for plotting
        unique_emotions = sorted(set(e for e in emotions if e != "silence" and e != "error"))
        emotion_to_int = {emotion: i for i, emotion in enumerate(unique_emotions)}
        
        # Handle silence and error separately
        emotion_to_int["silence"] = -1
        emotion_to_int["error"] = -2
        
        int_emotions = [emotion_to_int.get(e, -2) for e in emotions]
        
        # Plot the emotion timeline
        ax1.plot(timestamps, int_emotions, marker='o', linestyle='-', color='blue', alpha=0.7)
        
        # If smoothed emotions are provided, plot them too
        if smoothed_emotions:
            int_smoothed = [emotion_to_int.get(e, -2) for e in smoothed_emotions]
            ax1.plot(timestamps, int_smoothed, linestyle='-', color='red', 
                    linewidth=2, label='Smoothed')
            ax1.legend()
            
        # Set y-ticks with emotion labels
        ytick_positions = sorted(list(set(int_emotions)))
        ytick_labels = [k for k, v in emotion_to_int.items() if v in ytick_positions]
        ax1.set_yticks(ytick_positions)
        ax1.set_yticklabels(ytick_labels)
        
        ax1.set_xlabel("Time (s)")
        ax1.set_ylabel("Emotion")
        ax1.set_title("Emotion Timeline")
        ax1.grid(True, alpha=0.3)
        
        # 2. Emotion Distribution (Top Right)
        ax2 = fig.add_subplot(gs[0, 1])
        emotion_counts = {}
        for e in emotions:
            if e not in ["silence", "error"]:
                emotion_counts[e] = emotion_counts.get(e, 0) + 1
                
        # Sort by count
        emotions_sorted = sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)
        emotions_labels = [e[0] for e in emotions_sorted]
        emotions_values = [e[1] for e in emotions_sorted]
        
        ax2.bar(emotions_labels, emotions_values, color='skyblue')
        ax2.set_xlabel("Emotion")
        ax2.set_ylabel("Count")
        ax2.set_title("Emotion Distribution")
        plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
        
        # 3. Confidence Heatmap (Middle)
        ax3 = fig.add_subplot(gs[1, :])
        
        # Prepare data for heatmap
        confidence_df = pd.DataFrame(confidence_matrix, columns=self.labels.values())
        
        # Filter out silence and error frames
        valid_indices = [i for i, e in enumerate(emotions) if e not in ["silence", "error"]]
        if valid_indices:
            confidence_df = confidence_df.iloc[valid_indices]
            
            # Create the heatmap
            sns.heatmap(
                confidence_df.T, 
                cmap="viridis", 
                ax=ax3,
                cbar_kws={"label": "Confidence"}
            )
            ax3.set_xlabel("Time Chunk")
            ax3.set_title("Emotion Confidence Over Time")
        else:
            ax3.text(0.5, 0.5, "No valid emotion data for heatmap", 
                    ha='center', va='center', fontsize=12)
            ax3.axis('off')
        
        # 4. Confidence Line Plot (Bottom)
        ax4 = fig.add_subplot(gs[2, :])
        
        # Plot confidence for each emotion over time
        filtered_timestamps = [timestamps[i] for i in valid_indices]
        for emotion in unique_emotions:
            emotion_idx = list(self.labels.values()).index(emotion)
            confidence_values = [confidence_matrix[i][emotion_idx] for i in valid_indices]
            
            if confidence_values:
                ax4.plot(filtered_timestamps, confidence_values, 
                        label=emotion, linewidth=2, alpha=0.7)
        
        ax4.set_xlabel("Time (s)")
        ax4.set_ylabel("Confidence")
        ax4.set_title("Emotion Confidence Timeline")
        ax4.legend(loc="upper right")
        ax4.grid(True, alpha=0.3)
        
        # Set overall title if provided
        if title:
            fig.suptitle(title, fontsize=16, y=0.98)
            
        plt.tight_layout()
        
        # Save or display
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            logger.info(f"Visualization saved to {output_path}")
        else:
            plt.show()
            
    def analyze_file(self, input_source, output_dir=None, apply_smoothing=True, window_size=3):
        """
        Complete analysis pipeline for a file or URL
        
        Args:
            input_source (str): Path to audio file or YouTube URL
            output_dir (str): Directory to save outputs (None for no saving)
            apply_smoothing (bool): Whether to apply emotion smoothing
            window_size (int): Smoothing window size
            
        Returns:
            dict: Analysis results
        """
        # Create output directory if needed
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Process audio
        start_time = time.time()
        waveform, sr = self.process_audio(input_source)
        
        if waveform is None:
            logger.error("Failed to process audio input")
            return None
            
        # Analyze emotions
        emotions, confidence_matrix, timestamps = self.analyze_emotion(waveform, sr)
        
        # Apply smoothing if requested
        smoothed_emotions = None
        if apply_smoothing:
            smoothed_emotions = self.smooth_emotions(emotions, confidence_matrix, window_size)
        
        # Generate filename from input
        if output_dir:
            base_filename = os.path.splitext(os.path.basename(input_source))[0]
            if input_source.startswith(("http://", "https://", "www.")):
                base_filename = "youtube_" + str(uuid.uuid4())[:8]
                
            # Create visualization
            viz_path = os.path.join(output_dir, f"{base_filename}_emotions.png")
            self.visualize_emotions(
                emotions, 
                confidence_matrix, 
                timestamps, 
                output_path=viz_path,
                smoothed_emotions=smoothed_emotions,
                title=f"Emotion Analysis: {base_filename}"
            )
            
            # Save analysis results as CSV
            results_df = pd.DataFrame({
                'timestamp': timestamps,
                'emotion': emotions
            })
            if smoothed_emotions:
                results_df['smoothed_emotion'] = smoothed_emotions
                
            csv_path = os.path.join(output_dir, f"{base_filename}_results.csv")
            results_df.to_csv(csv_path, index=False)
            logger.info(f"Results saved to {csv_path}")
            
            # Save confidence matrix
            conf_df = pd.DataFrame(confidence_matrix, columns=self.labels.values())
            conf_df['timestamp'] = timestamps
            conf_csv_path = os.path.join(output_dir, f"{base_filename}_confidence.csv")
            conf_df.to_csv(conf_csv_path, index=False)
            logger.info(f"Confidence data saved to {conf_csv_path}")
        else:
            # Just display the visualization
            self.visualize_emotions(
                emotions, 
                confidence_matrix, 
                timestamps,
                smoothed_emotions=smoothed_emotions,
                title="Emotion Analysis"
            )
            
        processing_time = time.time() - start_time
        logger.info(f"Analysis completed in {processing_time:.2f} seconds")
        
        # Count emotions
        emotion_counts = {}
        for e in emotions:
            if e not in ["silence", "error"]:
                emotion_counts[e] = emotion_counts.get(e, 0) + 1
                
        # Determine dominant emotion
        if emotion_counts:
            dominant_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0]
        else:
            dominant_emotion = "unknown"
            
        # Calculate emotion percentages
        total_frames = len([e for e in emotions if e not in ["silence", "error"]])
        emotion_percentages = {
            e: count / total_frames * 100 if total_frames > 0 else 0
            for e, count in emotion_counts.items()
        }
        
        # Return results
        return {
            'emotions': emotions,
            'smoothed_emotions': smoothed_emotions,
            'timestamps': timestamps,
            'dominant_emotion': dominant_emotion,
            'emotion_counts': emotion_counts,
            'emotion_percentages': emotion_percentages,
            'duration': len(emotions) * self.chunk_duration,
            'processing_time': processing_time
        }


def main():
    """Main function for command-line interface"""
    parser = argparse.ArgumentParser(description='Voice Emotion Detection System')
    parser.add_argument('input', nargs='?', help='Audio file path or YouTube URL')
    parser.add_argument('--output-dir', '-o', help='Output directory for results')
    parser.add_argument('--chunk-duration', '-c', type=float, default=1.0, 
                        help='Duration of each audio chunk in seconds')
    parser.add_argument('--sample-rate', '-sr', type=int, default=16000, 
                        help='Sample rate for audio processing')
    parser.add_argument('--device', '-d', choices=['cuda', 'cpu'], 
                        help='Device to run the model on (cuda or cpu)')
    parser.add_argument('--no-smoothing', action='store_true', 
                        help='Disable emotion smoothing')
    parser.add_argument('--window-size', '-w', type=int, default=3, 
                        help='Window size for emotion smoothing')
    parser.add_argument('--batch-mode', '-b', action='store_true', 
                        help='Run in batch mode (no interactive prompts)')
    
    args = parser.parse_args()
    
    # Interactive mode if no input is provided
    input_source = args.input
    if not input_source and not args.batch_mode:
        input_source = input("Enter file path (.mp3/.mp4/.wav) or YouTube URL: ").strip()
    
    if not input_source:
        logger.error("No input source provided.")
        return
    
    # Initialize the detector
    detector = VoiceEmotionDetector(
        chunk_duration=args.chunk_duration,
        sample_rate=args.sample_rate,
        device=args.device
    )
    
    # Run analysis
    results = detector.analyze_file(
        input_source, 
        output_dir=args.output_dir,
        apply_smoothing=not args.no_smoothing,
        window_size=args.window_size
    )
    
    if results:
        # Print summary
        print("\n===== EMOTION ANALYSIS SUMMARY =====")
        print(f"Duration: {results['duration']:.2f} seconds")
        print(f"Dominant emotion: {results['dominant_emotion']}")
        print("\nEmotion distribution:")
        for emotion, percentage in sorted(
            results['emotion_percentages'].items(), 
            key=lambda x: x[1], 
            reverse=True
        ):
            print(f"  - {emotion}: {percentage:.1f}%")
        print("\nAnalysis complete!")


if __name__ == "__main__":
    main()