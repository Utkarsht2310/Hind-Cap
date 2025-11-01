import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
import os


def _normalize_language(language: str) -> str:
    """Map various English/Hindi locale tags to Google's expected forms."""
    if not language:
        return 'en-US'
    lang = language.strip()
    # Common aliases
    aliases = {
        'en': 'en-US',
        'en_IN': 'en-IN',
        'en-IND': 'en-IN',
        'en_UK': 'en-GB',
        'en-UK': 'en-GB',
        'hi': 'hi-IN',
        'hi_IN': 'hi-IN',
    }
    return aliases.get(lang, lang)


def _fixed_window_chunks(audio: AudioSegment, window_ms: int = 6000) -> list:
    """Fallback: split audio into fixed windows when silence split fails."""
    chunks = []
    total_ms = len(audio)
    for start in range(0, total_ms, window_ms):
        end = min(total_ms, start + window_ms)
        if end - start < 300:
            break
        chunks.append(audio[start:end])
    return chunks


def transcribe_audio(audio_path, language='en-US'):
    """
    Transcribe audio file to text using Google Speech Recognition

    Args:
        audio_path (str): Path to the audio file
        language (str): Language code ('en-US' for English, 'hi-IN' for Hindi)

    Returns:
        list: List of tuples containing (text, start_time, end_time) for each segment
    """
    recognizer = sr.Recognizer()

    # Load audio file
    audio = AudioSegment.from_wav(audio_path)

    # Normalize language
    language = _normalize_language(language)

    # Split audio on silence (multi-pass for robustness)
    # Pass 1: current settings
    chunks = split_on_silence(
        audio,
        min_silence_len=500,
        silence_thresh=audio.dBFS - 14,
        keep_silence=300,
    )
    # Pass 2: more sensitive for quieter English audio
    if len(chunks) <= 1:
        chunks = split_on_silence(
            audio,
            min_silence_len=300,
            silence_thresh=audio.dBFS - 20,
            keep_silence=200,
        )
    # Pass 3: most permissive, then fallback to fixed windows
    if len(chunks) == 0:
        chunks = split_on_silence(
            audio,
            min_silence_len=200,
            silence_thresh=audio.dBFS - 24,
            keep_silence=150,
        )
    if len(chunks) == 0:
        chunks = _fixed_window_chunks(audio, window_ms=6000)

    print(f"Audio split into {len(chunks)} chunks")

    transcription_segments = []
    current_time = 0

    # Create a temporary directory for chunks
    temp_dir = os.path.join(os.path.dirname(audio_path), 'chunks')
    os.makedirs(temp_dir, exist_ok=True)

    # Process each chunk
    for i, chunk in enumerate(chunks):
        # Skip very short chunks (less than 0.5 seconds)
        if len(chunk) < 500:
            current_time += len(chunk) / 1000.0
            continue

        # Export chunk to temporary file
        chunk_path = os.path.join(temp_dir, f"chunk{i}.wav")
        chunk.export(chunk_path, format="wav")

        # Transcribe the chunk
        try:
            with sr.AudioFile(chunk_path) as source:
                audio_data = recognizer.record(source)

                try:
                    # Recognize speech using Google Speech Recognition
                    text = recognizer.recognize_google(audio_data, language=language)

                    # Calculate timing for this segment
                    start_time = current_time
                    end_time = current_time + (len(chunk) / 1000.0)

                    transcription_segments.append({
                        'text': text,
                        'start': start_time,
                        'end': end_time
                    })

                    print(f"Chunk {i}: {text[:50]}...")

                except sr.UnknownValueError:
                    print(f"Chunk {i}: Could not understand audio")
                except sr.RequestError as e:
                    print(f"Chunk {i}: API error - {e}")

        except Exception as e:
            print(f"Error processing chunk {i}: {str(e)}")

        finally:
            # Clean up chunk file
            if os.path.exists(chunk_path):
                os.remove(chunk_path)

            # Update current time
            current_time += len(chunk) / 1000.0

    # Clean up temporary directory
    try:
        os.rmdir(temp_dir)
    except:
        pass

    print(f"Transcription complete: {len(transcription_segments)} segments")
    return transcription_segments


def transcribe_audio_simple(audio_path, language='en-US'):
    """
    Simple transcription for shorter audio files (fallback method)

    Args:
        audio_path (str): Path to the audio file
        language (str): Language code

    Returns:
        str: Transcribed text
    """
    recognizer = sr.Recognizer()

    try:
        with sr.AudioFile(audio_path) as source:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=1)

            # Record the audio
            audio_data = recognizer.record(source)

            # Recognize speech
            text = recognizer.recognize_google(audio_data, language=language)

            return [{'text': text, 'start': 0, 'end': 0}]

    except sr.UnknownValueError:
        print("Could not understand audio")
        return []
    except sr.RequestError as e:
        print(f"API error: {e}")
        return []
    except Exception as e:
        print(f"Error: {str(e)}")
        return []