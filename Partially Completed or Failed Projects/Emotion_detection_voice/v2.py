import sounddevice as sd
from scipy.io.wavfile import write
import librosa
import torch
import numpy as np
import matplotlib.pyplot as plt
from transformers import Wav2Vec2FeatureExtractor, Wav2Vec2ForSequenceClassification
import IPython.display as ipd


# Step 1: Record audio
duration = 1 # seconds
sample_rate = 16000
print("🎙️ Recording for 10 seconds...")

audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
sd.wait()
print("✅ Recording complete!")

# Save as .wav
file_path = "E:\\Projects\\Master Projects (Core)\\Emotion_detection_voice\\videoplayback.wav"
write(file_path, sample_rate, audio_data)

# Step 2: Load model and extractor
labels = ['angry', 'calm', 'disgust', 'fearful', 'happy', 'neutral', 'sad', 'surprised']
feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained("superb/wav2vec2-base-superb-er")
model = Wav2Vec2ForSequenceClassification.from_pretrained("superb/wav2vec2-base-superb-er")
model.eval()

# Step 3: Load and display audio
audio, sr = librosa.load(file_path, sr=16000)
ipd.display(ipd.Audio(audio, rate=16000))

# Step 4: Process in chunks for time-based analysis
chunk_duration = 2  # seconds
chunk_size = chunk_duration * sample_rate
overlap = int(chunk_size * 0.5)
emotions = []
timestamps = []

for start in range(0, len(audio) - chunk_size + 1, chunk_size - overlap):
    chunk = audio[start:start + chunk_size]
    inputs = feature_extractor(chunk, sampling_rate=16000, return_tensors="pt", padding=True)
    with torch.no_grad():
        logits = model(**inputs).logits
        pred = torch.argmax(logits, dim=-1).item()
        emotions.append(labels[pred])
        timestamps.append(start / sample_rate)

# Step 5: Display final emotion
from collections import Counter
final_emotion = Counter(emotions).most_common(1)[0][0]
print(f"\n🧠 Final Predicted Emotion: **{final_emotion.upper()}**")

# Step 6: Plot emotion graph
plt.figure(figsize=(12, 4))
plt.plot(timestamps, emotions, marker='o')
plt.title("🧠 Emotion Timeline Over 10 Seconds")
plt.xlabel("Time (s)")
plt.ylabel("Predicted Emotion")
plt.grid(True)
plt.yticks(rotation=45)
plt.tight_layout()
plt.show()
