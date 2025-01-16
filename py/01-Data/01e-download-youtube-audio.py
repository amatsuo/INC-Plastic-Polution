import os
import pandas as pd
from pytubefix import YouTube

# Path to save the audio files
output_folder = os.path.expanduser("~/Downloads/temp/inc-youtube-audio")
os.makedirs(output_folder, exist_ok=True)

# Load the CSV file into a pandas DataFrame
csv_file_path = '../../data/df_youtube_links_updated.csv'
df = pd.read_csv(csv_file_path)

# Filter DataFrame for rows with language == 'English' and day is not missing
filtered_df = df[(df['language'] == 'English') & (df['day'].notna())]
#filtered_df = df[(df['language'] == 'English') & (df['day'].notna()) & (df['day'] == 3) & (df['inc'] == 1)]

# Process each row to download audio
for _, row in filtered_df.iterrows():
    youtube_url = row['url']  # Replace 'url' with the actual column name for the YouTube URL
    newtitle = row['newtitle']  # Replace 'newtitle' with the actual column name for the title

    # Generate a safe file name
    safe_filename = "".join(c if c.isalnum() or c in "._-" else "_" for c in newtitle) + ".m4a"
    output_path = os.path.join(output_folder)
    #print(safe_filename)

    try:
        print(f"Processing: {youtube_url} -> {safe_filename}")
        
        # Download audio from YouTube
        yt = YouTube(youtube_url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        if audio_stream:
            audio_stream.download(output_path=output_path, filename = safe_filename)
            print(f"Audio saved to: {output_path}")
        else:
            print(f"No audio stream available for {youtube_url}")
    except Exception as e:
        print(f"Error processing {youtube_url}: {e}")
