# Video Caption Generator

A Flask-based web application that automatically generates and adds captions to videos. Supports multiple languages (English, Hindi) with transcription, translation, and customizable caption styles.

## Features

- 🎥 **Video Processing**: Upload videos in multiple formats (MP4, AVI, MOV, MKV, WEBM)
- 🎤 **Speech Recognition**: Automatic transcription using Google Speech Recognition
- 🌍 **Multi-language Support**: Support for English and Hindi with automatic translation
- 🎨 **Customizable Captions**: 
  - Multiple text colors (White, Yellow, Cyan, Green, Orange, Red, Pink, Black)
  - Background styles (Various colors and transparency levels)
  - Font sizes (Small, Medium, Large, Extra Large)
  - Style presets (Default, Bold, Outlined, Drop Shadow, Minimal)
- 📱 **Modern UI**: Beautiful, responsive interface with gradient backgrounds
- 💾 **Download**: Download your captioned videos instantly

## Requirements

- Python 3.8+
- FFmpeg (for audio/video processing)

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd caption-adder
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure FFmpeg is installed:
   - Windows: Download from [FFmpeg website](https://ffmpeg.org/download.html)
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt-get install ffmpeg`

## Usage

1. Run the Flask application:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. Upload a video file, select languages, customize caption styles, and generate captions!

## Project Structure

```
caption-adder/
├── app.py                 # Main Flask application
├── requirements.txt        # Python dependencies
├── templates/             # HTML templates
│   ├── home.html          # Landing page
│   ├── index.html         # Upload page
│   └── result.html        # Result display page
├── utils/                 # Utility modules
│   ├── audio_extractor.py    # Audio extraction from video
│   ├── caption_generator.py  # Caption rendering and video processing
│   ├── transcriber.py        # Speech-to-text transcription
│   └── translator.py         # Text translation
└── static/
    ├── fonts/             # Font files for captions
    ├── uploads/           # Uploaded videos
    ├── outputs/           # Generated captioned videos
    └── temp/              # Temporary files
```

## Configuration

- Maximum file size: 500MB (configurable in `app.py`)
- Default caption offset: -0.3 seconds (adjustable via `CAPTION_OFFSET_SECONDS` environment variable)

## Technologies Used

- **Flask**: Web framework
- **MoviePy**: Video processing
- **SpeechRecognition**: Speech-to-text
- **googletrans**: Translation
- **PIL/Pillow**: Image and text rendering
- **OpenCV**: Video processing utilities

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

