

import sounddevice as sd
from scipy.io.wavfile import write
import librosa
import torch
from transformers import Wav2Vec2FeatureExtractor, Wav2Vec2ForSequenceClassification
import IPython.display as ipd

# Step 1: Record audio
duration = 10  # seconds
sample_rate = 16000
print("🎙️ Recording for 10 seconds...")

audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
sd.wait()
print("✅ Recording complete!")

# Save as .wav
file_path = "recorded_audio.wav"
write(file_path, sample_rate, audio_data)

# Step 2: Load model and extractor
labels = ['angry', 'calm', 'disgust', 'fearful', 'happy', 'neutral', 'sad', 'surprised']
feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained("superb/wav2vec2-base-superb-er")
model = Wav2Vec2ForSequenceClassification.from_pretrained("superb/wav2vec2-base-superb-er")
model.eval()

# Step 3: Load audio
audio, sr = librosa.load(file_path, sr=16000)
ipd.display(ipd.Audio(audio, rate=16000))  # Optional: play the recorded audio

# Step 4: Preprocess and predict
inputs = feature_extractor(audio, sampling_rate=16000, return_tensors="pt")

with torch.no_grad():
    logits = model(**inputs).logits
    predicted = torch.argmax(logits, dim=-1).item()

print(f"\n🧠 Predicted Emotion: **{labels[predicted].upper()}**")
