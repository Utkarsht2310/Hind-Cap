import os
import subprocess
import whisper
import noisereduce as nr
import librosa
import soundfile as sf

# ---------- SETTINGS ----------
VIDEO_PATH = "input_video.mp4"    # 🎥 your input video
AUDIO_PATH = "temp_audio.wav"
CLEAN_AUDIO = "clean_audio.wav"
SRT_PATH = "captions.srt"
MODEL_SIZE = "medium"  # or "large" for best accuracy
LANGUAGE = None        # None = auto-detect | "hi" = Hindi | "en" = English
# ------------------------------

def extract_audio(video_path, audio_path):
    """Extract mono 16kHz audio from video using ffmpeg"""
    print("🔹 Extracting audio from video...")
    command = ["ffmpeg", "-y", "-i", video_path, "-ac", "1", "-ar", "16000", audio_path]
    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    print("✅ Audio extracted successfully!")

def reduce_noise(input_audio, output_audio):
    """Optional: Denoise the audio"""
    print("🔹 Reducing background noise...")
    y, sr = librosa.load(input_audio, sr=None)
    reduced = nr.reduce_noise(y=y, sr=sr)
    sf.write(output_audio, reduced, sr)
    print("✅ Noise reduced successfully!")

def format_timestamp(seconds: float) -> str:
    """Format seconds to SRT timestamp"""
    h, m, s = int(seconds // 3600), int(seconds % 3600 // 60), seconds % 60
    return f"{h:02}:{m:02}:{s:06.3f}".replace(".", ",")

def transcribe_audio(audio_path, model_size="medium", language=None):
    """Run Whisper transcription"""
    print(f"🔹 Loading Whisper model ({model_size})...")
    model = whisper.load_model(model_size)
    print("🔹 Transcribing audio... (this may take a few minutes)")
    result = model.transcribe(audio_path, language=language)
    print("✅ Transcription complete!")
    return result

def save_srt(result, srt_path):
    """Save transcription result to .srt subtitle file"""
    print("🔹 Generating captions file...")
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, segment in enumerate(result["segments"], start=1):
            start = format_timestamp(segment["start"])
            end = format_timestamp(segment["end"])
            text = segment["text"].strip()
            f.write(f"{i}\n{start} --> {end}\n{text}\n\n")
    print(f"✅ Captions saved to {srt_path}")

if __name__ == "__main__":
    if not os.path.exists(VIDEO_PATH):
        raise FileNotFoundError(f"Video file not found: {VIDEO_PATH}")

    extract_audio(VIDEO_PATH, AUDIO_PATH)
    reduce_noise(AUDIO_PATH, CLEAN_AUDIO)
    result = transcribe_audio(CLEAN_AUDIO, MODEL_SIZE, LANGUAGE)
    save_srt(result, SRT_PATH)
    print("\n🎉 All done! You can now add captions.srt to your video.")
