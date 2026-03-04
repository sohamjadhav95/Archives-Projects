import os
import torch
from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq
import librosa

# Load model directly (instead of Groq client)
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
processor = AutoProcessor.from_pretrained("openai/whisper-small-v3")
model = AutoModelForSpeechSeq2Seq.from_pretrained("openai/whisper-small-v3").to(DEVICE)

filename = os.path.dirname(__file__) + "/audio.m4a"

# Read and process audio file
audio, sr = librosa.load(filename, sr=16000)
inputs = processor(audio, sampling_rate=sr, return_tensors="pt").to(DEVICE)

# Generate transcription
with torch.no_grad():
    predicted_ids = model.generate(**inputs)

transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
print(transcription)