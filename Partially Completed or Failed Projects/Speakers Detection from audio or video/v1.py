import whisper
from pyannote.audio import Pipeline
from moviepy.editor import VideoFileClip
import matplotlib.pyplot as plt

# STEP 1: Load and extract audio from video
def extract_audio(video_path, audio_path="temp_audio.wav"):
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path)
    return audio_path

# STEP 2: Speaker Diarization
def diarize(audio_path):
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization", use_auth_token="your_hf_token")
    diarization = pipeline(audio_path)
    speakers = {}
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        duration = turn.end - turn.start
        if speaker not in speakers:
            speakers[speaker] = 0
        speakers[speaker] += duration
    return diarization, speakers

# STEP 3: Transcription
def transcribe(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result["text"]

# STEP 4: Visualization
def plot_speaker_distribution(speakers):
    names = list(speakers.keys())
    times = list(speakers.values())
    plt.figure(figsize=(8, 5))
    plt.bar(names, times, color='skyblue')
    plt.title("Speaker Talk Time Distribution")
    plt.xlabel("Speaker")
    plt.ylabel("Time (seconds)")
    plt.show()

# MAIN FUNCTION
def process_video(video_path):
    print("Extracting audio...")
    audio_path = extract_audio(video_path)

    print("Performing speaker diarization...")
    diarization, speakers = diarize(audio_path)

    print("Transcribing audio...")
    transcript = transcribe(audio_path)

    print("Plotting results...")
    plot_speaker_distribution(speakers)

    print("\n--- Transcription ---\n")
    print(transcript)

# Example usage:
# process_video("meeting.mp4")
