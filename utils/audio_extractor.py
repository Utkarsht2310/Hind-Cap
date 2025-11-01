from moviepy.editor import VideoFileClip
import os


def extract_audio(video_path, audio_output_path):
    """
    Extract audio from video file and save as WAV

    Args:
        video_path (str): Path to the input video file
        audio_output_path (str): Path where audio will be saved

    Returns:
        bool: True if extraction successful, False otherwise
    """
    try:
        # Load the video file
        video = VideoFileClip(video_path)

        # Extract audio
        audio = video.audio

        if audio is None:
            print("No audio track found in video")
            return False

        # Save audio as WAV file (better for speech recognition)
        audio.write_audiofile(
            audio_output_path,
            codec='pcm_s16le',  # 16-bit PCM format
            fps=16000,  # 16kHz sample rate (good for speech recognition)
            nbytes=2,
            buffersize=2000,
            logger=None  # Suppress moviepy logs
        )

        # Close the video file
        video.close()

        print(f"Audio extracted successfully: {audio_output_path}")
        return True

    except Exception as e:
        print(f"Error extracting audio: {str(e)}")
        return False