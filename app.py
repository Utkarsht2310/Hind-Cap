from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import os
import json
from werkzeug.utils import secure_filename
from utils.audio_extractor import extract_audio
from utils.transcriber import transcribe_audio
from utils.caption_generator import add_captions_to_video
from utils.translator import translate_transcription, get_language_code_for_translation

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'mykey2310-change-in-production')

# Configuration
UPLOAD_FOLDER = 'static/uploads'
OUTPUT_FOLDER = 'static/outputs'
TEMP_FOLDER = 'static/temp'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['TEMP_FOLDER'] = TEMP_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

# Create necessary directories
for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER, TEMP_FOLDER]:
    os.makedirs(folder, exist_ok=True)


def allowed_file(filename):
    """Check if the uploaded file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def home():
    """Render the landing page"""
    return render_template('home.html')


@app.route('/add-captions')
def index():
    """Render the upload page"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_video():
    """Handle video upload and processing"""

    # Check if file is present in request
    if 'video' not in request.files:
        flash('No video file uploaded', 'error')
        return redirect(url_for('index'))

    file = request.files['video']
    transcription_language = request.form.get('transcription_language', 'en-US')  # Audio language for transcription
    caption_language = request.form.get('caption_language', 'en-US')  # Language for captions display
    
    # Caption style options
    text_color = request.form.get('text_color', 'white')
    box_color = request.form.get('box_color', 'black_semi')
    font_size = request.form.get('font_size', 'medium')
    caption_style = request.form.get('caption_style', 'default')

    # Check if file is selected
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))

    # Validate file type
    if not allowed_file(file.filename):
        flash('Invalid file type. Please upload a video file.', 'error')
        return redirect(url_for('index'))

    try:
        # Save uploaded video
        filename = secure_filename(file.filename)
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(video_path)

        # Extract audio from video
        print(f"Extracting audio from {filename}...")
        audio_path = os.path.join(app.config['TEMP_FOLDER'], f"{filename.rsplit('.', 1)[0]}.wav")
        extraction_ok = extract_audio(video_path, audio_path)
        if not extraction_ok or not os.path.exists(audio_path):
            flash('Failed to extract audio from the video.', 'error')
            return redirect(url_for('index'))

        # Transcribe audio to text
        print(f"Transcribing audio in {transcription_language}...")
        transcription = transcribe_audio(audio_path, transcription_language)

        if not transcription:
            flash('Could not transcribe audio. Please try with a clearer video.', 'error')
            return redirect(url_for('index'))

        # Check if translation is needed
        transcription_for_captions = transcription
        if transcription_language != caption_language:
            print(f"Translating captions from {transcription_language} to {caption_language}...")
            target_lang_code = get_language_code_for_translation(caption_language)
            transcription_for_captions = translate_transcription(transcription, target_lang_code)
            print(f"Translation complete: {len(transcription_for_captions)} segments translated")

        # Persist transcription for result view (save both original and translated)
        base_name = filename.rsplit('.', 1)[0]
        transcription_json_path = os.path.join(app.config['TEMP_FOLDER'], f"{base_name}.json")
        try:
            # Save translated version for display
            with open(transcription_json_path, 'w', encoding='utf-8') as f:
                json.dump(transcription_for_captions, f, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save transcription JSON: {str(e)}")

        # Generate captioned video (use translated text if translation was done)
        print("Adding captions to video...")
        output_filename = f"captioned_{filename}"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        # Create style options dict
        style_options = {
            'text_color': text_color,
            'box_color': box_color,
            'font_size': font_size,
            'caption_style': caption_style
        }
        
        captions_ok = add_captions_to_video(video_path, transcription_for_captions, output_path, style_options=style_options)
        if not captions_ok or not os.path.exists(output_path):
            flash('Failed to generate captioned video.', 'error')
            return redirect(url_for('index'))

        # Clean up temporary audio file
        if os.path.exists(audio_path):
            os.remove(audio_path)

        flash('Video processed successfully!', 'success')
        return redirect(url_for('result', filename=output_filename))

    except Exception as e:
        print(f"Error processing video: {str(e)}")
        flash(f'Error processing video: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/result')
def result():
    """Display the processed video with captions"""
    filename = request.args.get('filename')
    transcription = []

    # Try to load persisted transcription if available
    if filename:
        base_name = filename
        if base_name.startswith('captioned_'):
            base_name = base_name[len('captioned_'):]
        base_name = os.path.splitext(base_name)[0]
        transcription_json_path = os.path.join(app.config['TEMP_FOLDER'], f"{base_name}.json")
        try:
            if os.path.exists(transcription_json_path):
                with open(transcription_json_path, 'r', encoding='utf-8') as f:
                    transcription = json.load(f)
        except Exception as e:
            print(f"Failed to load transcription JSON: {str(e)}")

    if not filename:
        flash('No video to display', 'error')
        return redirect(url_for('index'))

    return render_template('result.html', filename=filename, transcription=transcription)


@app.route('/download/<filename>')
def download_video(filename):
    """Allow user to download the captioned video"""
    try:
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        flash(f'Error downloading file: {str(e)}', 'error')
        return redirect(url_for('index'))


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port)