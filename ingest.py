import os
from dotenv import load_dotenv
import whisper
from config import VIDEO_FOLDER, TRANSCRIPT_FOLDER

load_dotenv()

model = whisper.load_model("base")

def transcribe_video(video_path):
    print(f"Transcribing {video_path}")
    result = model.transcribe(video_path)
    transcript_text = result["text"]
    return transcript_text

def save_transcript(video_filename, transcript_text):
    os.makedirs(TRANSCRIPT_FOLDER, exist_ok=True)
    out_file = os.path.join(TRANSCRIPT_FOLDER, video_filename + ".txt")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(transcript_text)
    print(f"Saved transcript to {out_file}")

if __name__ == "__main__":
    os.makedirs(VIDEO_FOLDER, exist_ok=True)
    for file in os.listdir(VIDEO_FOLDER):
        if file.endswith(".mp4"):
            video_path = os.path.join(VIDEO_FOLDER, file)
            transcript = transcribe_video(video_path)
            save_transcript(os.path.splitext(file)[0], transcript)
