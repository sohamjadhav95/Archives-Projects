import os
from speechbrain.pretrained import SpeakerDiarization
import whisper
from pydub import AudioSegment

def parse_rttm(rttm_str):
    """
    Parses an RTTM string to extract segments with start time, end time, and speaker label.
    
    RTTM lines have the format:
    SPEAKER <file_id> 1 <start_time> <duration> <NA> <NA> <speaker_label> <NA> <NA>
    
    Returns:
        segments (list of dict): Each dict contains 'start', 'end', and 'speaker' keys.
    """
    segments = []
    for line in rttm_str.splitlines():
        parts = line.strip().split()
        if len(parts) < 8:
            continue
        start = float(parts[3])
        duration = float(parts[4])
        speaker = parts[7]
        end = start + duration
        segments.append({'start': start, 'end': end, 'speaker': speaker})
    return segments

def diarize_and_transcribe(audio_path):
    """
    Diarizes the audio using SpeechBrain and transcribes each segment using Whisper.
    
    Parameters:
        audio_path (str): Path to the input audio file.
        
    Returns:
        transcript (str): A transcript with speaker labels.
    """
    # 1. Load the SpeechBrain diarization model.
    print("Loading Speaker Diarization model from SpeechBrain...")
    diarization = SpeakerDiarization.from_hparams(
        source="speechbrain/spkrec-diarization",
        savedir="pretrained_models/spkrec-diarization"
    )
    
    # 2. Perform diarization; this returns an RTTM-formatted string.
    print("Performing speaker diarization...")
    rttm = diarization.diarize_file(audio_path)
    
    # 3. Parse the RTTM output to get segments.
    segments = parse_rttm(rttm)
    
    # 4. Load the full audio file using pydub.
    audio = AudioSegment.from_file(audio_path)
    
    # 5. Load the Whisper ASR model (choose a model size: tiny, base, small, etc.).
    print("Loading Whisper model...")
    model = whisper.load_model("base")
    
    transcript = ""
    print("Processing segments and transcribing...")
    
    # 6. For each segment, extract the audio, transcribe, and label with the speaker.
    for segment in segments:
        start_sec = segment['start']
        end_sec = segment['end']
        speaker = segment['speaker']
        
        # pydub works in milliseconds
        start_ms = int(start_sec * 1000)
        end_ms = int(end_sec * 1000)
        
        # Extract the segment from the full audio
        segment_audio = audio[start_ms:end_ms]
        
        # Export the segment to a temporary WAV file (Whisper works well with WAV)
        temp_filename = "temp_segment.wav"
        segment_audio.export(temp_filename, format="wav")
        
        # Transcribe the segment using Whisper
        result = model.transcribe(temp_filename)
        segment_text = result.get("text", "").strip()
        
        # Append the speaker label and transcription to the full transcript
        transcript += f"[{speaker}] {segment_text}\n"
        
        # Remove the temporary file
        os.remove(temp_filename)
    
    return transcript

if __name__ == "__main__":
    # Path to your input audio file (e.g., WAV, MP3, etc.)
    audio_file = "C:/Users/soham/Downloads/horimiya_ep1.mp3" 
    
    full_transcript = diarize_and_transcribe(audio_file)
    
    print("\nFinal Transcript:")
    print("-----------------")
    print(full_transcript)
