import os
import whisper
import subprocess
import csv
from pyannote.audio import Pipeline, Audio
from pyannote.core import Segment
import torch


hf_token = os.getenv("HF_AUTH_TOKEN")

# Step 2: Initialize Pyannote pipeline
pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token=hf_token
)
pipeline.to(torch.device("cuda"))

# Step 3: Load Whisper model
model = whisper.load_model("medium")

def convert_audio(input_file, output_file, format="wav"):
    if format == "wav":
        command = [
            "ffmpeg", "-i", input_file, "-ar", "16000", "-ac", "1", output_file
        ]
    else:
        raise ValueError("Unsupported format. Only WAV is supported.")
    subprocess.run(command, check=True)
    print(f"Converted {input_file} to {output_file}")


def diarize_and_transcribe(input_file, output_dir):
    """
    Diarize and transcribe an audio file, saving the transcript as a CSV.

    Args:
        input_file (str): Path to the input audio file.
        output_dir (str): Directory to save the transcript CSV.

    Returns:
        str: Path to the saved transcript CSV.
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Extract input filename without extension
    input_filename = os.path.basename(input_file)
    input_basename, _ = os.path.splitext(input_filename)
    
    # Set output WAV file and transcript paths
    audio_wave_path = os.path.join(output_dir, f"{input_basename}.wav")
    output_csv = os.path.join(output_dir, f"transcript-{input_basename}.csv")

    # Step 1: Convert input file to WAV format
    convert_audio(input_file, audio_wave_path)

    # Step 2: Apply diarization
    print("Applying diarization...")
    diarization = pipeline(audio_wave_path)
    audio = Audio(sample_rate=16000, mono=True)

    # Step 3: Merge consecutive speaker segments
    merged_segments = []
    current_speaker = None
    current_start = None
    current_end = None

    for segment, _, speaker in diarization.itertracks(yield_label=True):
        if speaker == current_speaker and (segment.start - current_end) <= 60: # merge if the speakers are the same and small gap
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

    # Step 4: Generate transcript and save to CSV
    print("Generating transcript...")
    with open(output_csv, mode="w", newline="", encoding="utf-8") as csvfile:
        csv_writer = csv.writer(csvfile)
        # Write the header
        csv_writer.writerow(["start", "end", "speaker", "text"])
    
        # Process merged segments and write rows to CSV
        for start, end, speaker in merged_segments:
            print(f"Processing segment: {start:.1f}s - {end:.1f}s, Speaker: {speaker}")
    
            try:
                # Crop audio for the segment
                waveform, sample_rate = audio.crop(audio_wave_path, segment=Segment(start, end))
    
                # Transcribe the segment
                text = model.transcribe(waveform.squeeze().numpy(), fp16=False, language="en")
    
                # Write the segment details to the CSV
                csv_writer.writerow([start, end, speaker, text['text']])
            except ValueError as e:
                # Log the error and skip the problematic segment
                print(f"Skipping segment [{start:.1f}s - {end:.1f}s] due to error: {e}")
    print(f"Transcript saved to {output_csv}")

    # Step 5: Remove the intermediate WAV file
    if os.path.exists(audio_wave_path):
        os.remove(audio_wave_path)
        print(f"Deleted intermediate WAV file: {audio_wave_path}")

    return output_csv
  
# Example usage
# input_file = "cut.m4a"
# output_dir = "output"
# transcript_path = diarize_and_transcribe(input_file, output_dir)
# print(f"Transcript file saved at: {transcript_path}")


# Define input and output directories
input_dir = "/home/akitaka/python_projects/inc/gen_trans/audio_data"  
output_dir = "/home/akitaka/python_projects/inc/gen_trans/transcripts"  

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# List all MP4 files in the input directory
#audio_files = [f for f in os.listdir(input_dir) if f.endswith((".mp4", ".m4a"))]
audio_files = []
for root, _, files in os.walk(input_dir):
    for file in files:
        if file.endswith((".mp4", ".m4a")):
            audio_files.append(os.path.join(root, file))

print(audio_files)

# Process each file
for audio_file in audio_files:
    print(f"Processing: {audio_file}")
    diarize_and_transcribe(audio_file, output_dir)
    
