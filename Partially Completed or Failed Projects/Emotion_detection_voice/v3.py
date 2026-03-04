import os
import subprocess
import torch
import numpy as np
import librosa
from transformers import Wav2Vec2FeatureExtractor, Wav2Vec2ForSequenceClassification
import matplotlib.pyplot as plt
from collections import Counter
import yt_dlp
from pydub import AudioSegment
import uuid

# ---------- SETTINGS ----------
labels = ['angry', 'calm', 'disgust', 'fearful', 'happy', 'neutral', 'sad', 'surprised']
sample_rate = 16000
chunk_duration = 2  # seconds
input_source = input("Enter file path (.mp3/.mp4/.wav) or YouTube URL: ").strip()
temp_id = str(uuid.uuid4())[:8]
temp_wav = f"temp_{temp_id}.wav"

# ---------- CONVERSION ----------
def convert_to_wav(input_path, output_path):
    print(f"🎧 Converting {input_path} to WAV...")
    command = ["ffmpeg", "-i", input_path, "-ar", str(sample_rate), "-ac", "1", output_path, "-y", "-loglevel", "error"]
    subprocess.run(command, check=True)
    print("✅ Conversion done!")

def download_youtube_audio(url, output_path):
    print(f"⬇️ Downloading audio from YouTube...")
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
        ydl.download([url])
    os.rename("yt_audio.wav", output_path)
    print("✅ YouTube download and conversion complete!")

# ---------- HANDLE INPUT ----------
if input_source.startswith("http"):
    download_youtube_audio(input_source, temp_wav)
elif input_source.endswith(".mp4") or input_source.endswith(".mp3"):
    convert_to_wav(input_source, temp_wav)
elif input_source.endswith(".wav"):
    temp_wav = input_source
else:
    raise ValueError("Unsupported input format. Provide a valid file or YouTube link.")

# ---------- LOAD AUDIO ----------
print("📥 Loading audio...")
audio, sr = librosa.load(temp_wav, sr=sample_rate)

# Handle empty or silent audio
if np.max(np.abs(audio)) < 1e-4 or len(audio) == 0:
    print("😶 Silent audio detected. Defaulting to 'neutral'")
    emotions = ['neutral']
    timestamps = [0]
else:
    # ---------- LOAD MODEL ----------
    print("🧠 Loading model...")
    extractor = Wav2Vec2FeatureExtractor.from_pretrained("superb/wav2vec2-base-superb-er")
    model = Wav2Vec2ForSequenceClassification.from_pretrained("superb/wav2vec2-base-superb-er")
    model.eval()

    # ---------- CHUNK ANALYSIS ----------
    chunk_size = chunk_duration * sample_rate
    overlap = int(chunk_size * 0.5)
    emotions = []
    timestamps = []

    print("🔍 Analyzing chunks...")
    for start in range(0, len(audio) - chunk_size + 1, chunk_size - overlap):
        chunk = audio[start:start + chunk_size]
        inputs = extractor(chunk, sampling_rate=sample_rate, return_tensors="pt", padding=True)
        with torch.no_grad():
            logits = model(**inputs).logits
            pred = torch.argmax(logits, dim=-1).item()
            emotions.append(labels[pred])
            timestamps.append(start / sample_rate)

# ---------- FINAL EMOTION ----------
final_emotion = Counter(emotions).most_common(1)[0][0]
print(f"\n🎯 Final Predicted Emotion: **{final_emotion.upper()}**")

# ---------- PLOT ----------
plt.figure(figsize=(12, 4))
plt.plot(timestamps, emotions if len(emotions) > 1 else [emotions[0]], marker='o')
plt.title("🧠 Emotion Timeline")
plt.xlabel("Time (s)")
plt.ylabel("Predicted Emotion")
plt.grid(True)
plt.tight_layout()
plt.show()

# Cleanup
if os.path.exists(temp_wav) and temp_wav.startswith("temp_"):
    os.remove(temp_wav)
