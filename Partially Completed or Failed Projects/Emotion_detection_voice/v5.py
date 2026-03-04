import torch
import torchaudio
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from transformers import AutoFeatureExtractor, Wav2Vec2ForSequenceClassification
import subprocess
import yt_dlp
import uuid
import os
import warnings

warnings.filterwarnings("ignore")

# ---------- SETTINGS ----------
chunk_duration = 2  # seconds
sample_rate = 16000
input_source = input("Enter file path (.mp3/.mp4/.wav) or YouTube URL: ").strip()
temp_id = str(uuid.uuid4())[:8]
temp_wav = f"temp_{temp_id}.wav"

# ---------- LABELS ----------
model_name = "ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition"
model = Wav2Vec2ForSequenceClassification.from_pretrained(model_name)
feature_extractor = AutoFeatureExtractor.from_pretrained(model_name)
labels = model.config.id2label
model.eval()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# ---------- UTILS ----------
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

def load_audio(file_path):
    waveform, sr = torchaudio.load(file_path)
    return waveform.mean(dim=0), sr

# ---------- HANDLE INPUT ----------
if input_source.startswith("http"):
    download_youtube_audio(input_source, temp_wav)
elif input_source.endswith(".mp4") or input_source.endswith(".mp3"):
    convert_to_wav(input_source, temp_wav)
elif input_source.endswith(".wav"):
    temp_wav = input_source
else:
    raise ValueError("❌ Unsupported input format. Provide a .mp3, .mp4, .wav file or YouTube link.")

# ---------- LOAD AUDIO ----------
print("📥 Loading audio...")
waveform, sr = load_audio(temp_wav)

if waveform.numel() == 0 or torch.max(torch.abs(waveform)) < 1e-4:
    print("😶 Silent audio detected. Defaulting to 'neutral'")
    emotions = ['neutral']
    timestamps = [0]
else:
    chunk_size = int(chunk_duration * sample_rate)
    chunks = [waveform[i:i + chunk_size] for i in range(0, len(waveform), chunk_size)]

    print("🔍 Analyzing chunks...")
    emotions = []
    confidence_matrix = []

    for chunk in chunks:
        if chunk.shape[0] < chunk_size:
            chunk = torch.nn.functional.pad(chunk, (0, chunk_size - chunk.shape[0]))

        energy = torch.sum(chunk**2).item()
        if energy < 1e-4:
            emotions.append("silence")
            confidence_matrix.append([0.0] * len(labels))
            continue

        inputs = feature_extractor(chunk.numpy(), sampling_rate=sample_rate, return_tensors="pt", padding=True)
        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.no_grad():
            logits = model(**inputs).logits
            probs = torch.nn.functional.softmax(logits, dim=-1).cpu().numpy()[0]
            confidence_matrix.append(probs.tolist())
            predicted_label = labels[int(np.argmax(probs))]
            emotions.append(predicted_label)

    # ---------- PLOT ----------
# Map emotions to integers for plotting
unique_emotions = list(set(emotions))
emotion_to_int = {emotion: i for i, emotion in enumerate(sorted(unique_emotions))}
int_emotions = [emotion_to_int[e] for e in emotions]

plt.figure(figsize=(12, 4))
plt.plot(timestamps, int_emotions, marker='o', linestyle='-', color='b')
plt.yticks(list(emotion_to_int.values()), list(emotion_to_int.keys()))
plt.xlabel("Time (s)")
plt.ylabel("Predicted Emotion")
plt.title("🧠 Emotion Timeline")
plt.grid(True)
plt.tight_layout()
plt.show()


# ---------- CLEANUP ----------
if temp_wav.startswith("temp_") and os.path.exists(temp_wav):
    os.remove(temp_wav)
