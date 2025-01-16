import os
import whisper
from tqdm import tqdm  # For the progress bar

# Load the Whisper model
model = whisper.load_model("turbo")

# Define input and output directories
input_dir = "/content"  # Replace with the directory containing MP4 files
#output_folder = os.path.expanduser("~/Downloads/temp/inc-youtube-audio")
output_dir = "/content/transcript"  # Replace with the directory to save transcripts

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# List all MP4 files in the input directory
mp4_files = [f for f in os.listdir(input_dir) if f.endswith(".mp4")]

print(mp4_files)

# Process each MP4 file
for mp4_file in mp4_files:
    input_path = os.path.join(input_dir, mp4_file)
    output_path = os.path.join(output_dir, os.path.splitext(mp4_file)[0] + ".txt")

    print(f"Processing: {input_path}")

    # Transcribe the audio from the MP4 file
    result = model.transcribe(input_path)

    # Save the transcript to the output file
    with open(output_path, 'w', encoding='utf-8') as file:
        for item in result['segments']:
            file.write(item['text'] + '\n')

    print(f"Transcript saved to: {output_path}")
