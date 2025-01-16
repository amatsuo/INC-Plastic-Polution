from pyannote.audio import Pipeline
import torch

hf_token = os.getenv("HF_AUTH_TOKEN")

pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token=hf_token
)
pipeline.to(torch.device("cuda"))

# !ffmpeg -i cut.m4a -ar 16000 -ac 1 cut.wav

# Path to the audio file
audio_path = "cut.wav"

# Apply the pipeline
diarization = pipeline(audio_path)

# Print the diarization result
for turn, _, speaker in diarization.itertracks(yield_label=True):
    print(f"Speaker {speaker} spoke from {turn.start:.1f}s to {turn.end:.1f}s")

with open("audio.rttm", "w") as rttm:
    diarization.write_rttm(rttm)

