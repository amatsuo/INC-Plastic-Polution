import whisper
import os

from pyannote.audio import Pipeline
from pyannote.audio import Audio
from pyannote.core import Segment
import torch
import subprocess
import csv

def convert_audio(input_file, output_file, format="wav"):
    if format == "wav":
        command = [
            "ffmpeg", "-i", input_file, "-ar", "16000", "-ac", "1", output_file
        ]
    elif format == "mp3":
        command = [
            "ffmpeg", "-i", input_file, "-vn", "-ar", "44100", "-ac", "2", "-b:a", "192k", output_file
        ]
    else:
        raise ValueError("Unsupported format. Use 'wav' or 'mp3'.")

    subprocess.run(command, check=True)
    print(f"Converted {input_file} to {output_file}")


# Path to the audio file
audio_path = "cut.m4a"
audio_wave_path = "cut.wav"

# Create wav file
convert_audio(audio_path, audio_wave_path, format="wav")

hf_token = os.getenv("HF_AUTH_TOKEN")

pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token=hf_token
)
pipeline.to(torch.device("cuda"))

# Load the Whisper model
model = whisper.load_model("turbo")

# Apply the pipeline
diarization = pipeline(audio_wave_path)
audio = Audio(sample_rate=16000, mono=True)

# Merge consecutive segments by the same speaker
merged_segments = []
current_speaker = None
current_start = None
current_end = None

for segment, _, speaker in diarization.itertracks(yield_label=True):
    if speaker == current_speaker:
        # Extend the current segment
        current_end = segment.end
    else:
        # Save the previous segment if it exists
        if current_speaker is not None:
            merged_segments.append((current_start, current_end, current_speaker))
        # Start a new segment
        current_speaker = speaker
        current_start = segment.start
        current_end = segment.end

# Add the last segment
if current_speaker is not None:
    merged_segments.append((current_start, current_end, current_speaker))

# Generate the transcript and save to CSV
output_csv = "transcript.csv"
 
# Open the CSV file for writing
with open(output_csv, mode="w", newline="", encoding="utf-8") as csvfile:
    csv_writer = csv.writer(csvfile)
    # Write the header
    csv_writer.writerow(["start", "end", "speaker", "text"])
    
    # Process merged segments and write rows to CSV
    for start, end, speaker in merged_segments:
        print(f"Processing segment: {start:.1f}s - {end:.1f}s, Speaker: {speaker}")
        
        # Crop audio for the segment
        waveform, sample_rate = audio.crop(audio_wave_path, segment=Segment(start, end))
        
        # Transcribe the segment
        text = model.transcribe(waveform.squeeze().numpy(), fp16=False, language="en")
        
        # Write the segment details to the CSV
        csv_writer.writerow([start, end, speaker, text['text']])

print(f"Transcript saved to {output_csv}")
