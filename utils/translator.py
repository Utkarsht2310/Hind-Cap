"""
Translation utility for converting transcriptions between languages.
Uses Google Translate API via googletrans library.
"""
try:
    from googletrans import Translator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    try:
        # Alternative import path for some versions
        from googletrans import google_translator as Translator
        TRANSLATOR_AVAILABLE = True
    except ImportError:
        TRANSLATOR_AVAILABLE = False
        print("Warning: googletrans not available. Install with: pip install googletrans==4.0.0rc1")


def translate_text(text, target_language='en'):
    """
    Translate text to target language using Google Translate.
    
    Args:
        text (str): Text to translate
        target_language (str): Target language code (e.g., 'en', 'hi')
    
    Returns:
        str: Translated text, or original text if translation fails
    """
    if not TRANSLATOR_AVAILABLE:
        print("Translation not available - googletrans not installed")
        return text
    
    if not text or not text.strip():
        return text
    
    try:
        translator = Translator()
        # Add timeout and retry logic for network issues
        result = translator.translate(text, dest=target_language)
        if result and hasattr(result, 'text') and result.text:
            return result.text
        return text
    except Exception as e:
        print(f"Translation error for text '{text[:50]}...': {str(e)}")
        # Return original text if translation fails
        return text


def translate_transcription(transcription_segments, target_language='en'):
    """
    Translate all transcription segments to target language.
    
    Args:
        transcription_segments (list): List of dicts with 'text', 'start', 'end'
        target_language (str): Target language code
    
    Returns:
        list: Translated transcription segments with same timing
    """
    if not transcription_segments:
        return []
    
    translated_segments = []
    
    for segment in transcription_segments:
        original_text = segment.get('text', '')
        if original_text:
            translated_text = translate_text(original_text, target_language)
            translated_segments.append({
                'text': translated_text,
                'start': segment.get('start', 0),
                'end': segment.get('end', 0),
                'original_text': original_text  # Keep original for reference
            })
        else:
            translated_segments.append(segment)
    
    return translated_segments


def get_language_code_for_translation(language):
    """
    Map language selection to Google Translate language codes.
    
    Args:
        language (str): Language code from form (e.g., 'en-US', 'hi-IN')
    
    Returns:
        str: Google Translate language code (e.g., 'en', 'hi')
    """
    mapping = {
        'en-US': 'en',
        'en-GB': 'en',
        'en-IN': 'en',
        'hi-IN': 'hi',
    }
    return mapping.get(language, 'en')

