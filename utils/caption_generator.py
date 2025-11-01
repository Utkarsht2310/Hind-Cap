# from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip
# from moviepy.video.tools.subtitles import SubtitlesClip
# from PIL import Image, ImageDraw, ImageFont
# import numpy as np
# import textwrap
# import os
#
#
# def _detect_script(text):
#     """
#     Detect basic script to pick a font. Returns 'devanagari' if chars in that block.
#     """
#     for ch in text:
#         code = ord(ch)
#         if 0x0900 <= code <= 0x097F:
#             return 'devanagari'
#     return 'latin'
#
#
# def _find_font_for_text(text, requested_path=None, fallback_size=40):
#     """
#     Determine a suitable font path for the provided text. Honors CAPTION_FONT_PATH then requested_path.
#     """
#     # 1) Environment override
#     env_font = os.environ.get('CAPTION_FONT_PATH')
#     if env_font and os.path.exists(env_font):
#         try:
#             print(f"Using CAPTION_FONT_PATH: {env_font}")
#             return ImageFont.truetype(env_font, fallback_size)
#         except Exception:
#             pass
#
#     # 2) Requested explicit path
#     if requested_path and os.path.exists(requested_path):
#         try:
#             print(f"Using requested font: {requested_path}")
#             return ImageFont.truetype(requested_path, fallback_size)
#         except Exception:
#             pass
#
#     # 3) Pick based on script
#     script = _detect_script(text)
#     windows_fonts_dir = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts')
#
#     candidate_files = []
#     if script == 'devanagari':
#         candidate_files = [
#             'Nirmala.ttf', 'NirmalaUI.ttf', 'Mangal.ttf', 'Kokila.ttf', 'Aparajita.ttf', 'NotoSansDevanagari-Regular.ttf', 'NotoSerifDevanagari-Regular.ttf'
#         ]
#     else:
#         candidate_files = [
#             'arial.ttf', 'SegoeUI.ttf', 'Calibri.ttf', 'NotoSans-Regular.ttf'
#         ]
#
#     for fname in candidate_files:
#         fpath = os.path.join(windows_fonts_dir, fname)
#         if os.path.exists(fpath):
#             try:
#                 print(f"Using detected font: {fpath}")
#                 return ImageFont.truetype(fpath, fallback_size)
#             except Exception:
#                 continue
#
#     # 4) Last resort
#     print("Falling back to default PIL font; may not support all scripts")
#     return ImageFont.load_default()
#
#
# def _create_pil_caption_image(text, max_width_px, font_path=None, font_size=40, padding=20, line_spacing=6, text_color=(255, 255, 255), box_color=(0, 0, 0, 180)):
#     """
#     Render a multiline caption image using PIL to avoid ImageMagick dependency.
#
#     Returns a PIL.Image with transparent background and a rounded rectangle box.
#     """
#     # Load font with fallback
#     font = _find_font_for_text(text, requested_path=font_path, fallback_size=font_size)
#
#     # Wrap text to fit max width
#     draw_dummy = ImageDraw.Draw(Image.new('RGB', (10, 10)))
#     words = text.split()
#     lines = []
#     current = []
#     for word in words:
#         test_line = (" ".join(current + [word])).strip()
#         bbox = draw_dummy.textbbox((0, 0), test_line, font=font)
#         line_width = bbox[2] - bbox[0]
#         if line_width <= max_width_px or not current:
#             current.append(word)
#         else:
#             lines.append(" ".join(current))
#             current = [word]
#     if current:
#         lines.append(" ".join(current))
#
#     # Calculate text block size
#     line_heights = []
#     line_widths = []
#     for line in lines:
#         bbox = draw_dummy.textbbox((0, 0), line, font=font)
#         line_widths.append(bbox[2] - bbox[0])
#         line_heights.append(bbox[3] - bbox[1])
#     text_width = min(max(line_widths) if line_widths else 0, max_width_px)
#     text_height = sum(line_heights) + max(0, (len(lines) - 1) * line_spacing)
#
#     box_width = text_width + padding * 2
#     box_height = text_height + padding * 2
#
#     # Create transparent image and draw rounded rectangle
#     img = Image.new('RGBA', (box_width, box_height), (0, 0, 0, 0))
#     draw = ImageDraw.Draw(img)
#
#     # Rounded rectangle background
#     radius = 12
#     rect = (0, 0, box_width, box_height)
#     try:
#         draw.rounded_rectangle(rect, radius=radius, fill=box_color)
#     except Exception:
#         draw.rectangle(rect, fill=box_color)
#
#     # Draw text centered
#     y = padding
#     for idx, line in enumerate(lines):
#         bbox = draw.textbbox((0, 0), line, font=font)
#         lw = bbox[2] - bbox[0]
#         lh = bbox[3] - bbox[1]
#         x = (box_width - lw) // 2
#         # Optional subtle shadow for contrast
#         shadow_offset = 1
#         draw.text((x + shadow_offset, y + shadow_offset), line, font=font, fill=(0, 0, 0, 200))
#         draw.text((x, y), line, font=font, fill=text_color)
#         y += lh + line_spacing
#
#     return img
#
#
# def create_subtitle_clips(transcription_segments, video_size):
#     """
#     Create subtitle clips from transcription segments
#
#     Args:
#         transcription_segments (list): List of dicts with 'text', 'start', 'end'
#         video_size (tuple): Width and height of the video
#
#     Returns:
#         list: List of TextClip objects
#     """
#     subtitle_clips = []
#
#     for segment in transcription_segments:
#         # Render caption image using PIL
#         max_text_width = max(200, video_size[0] - 140)
#         pil_img = _create_pil_caption_image(
#             segment['text'],
#             max_width_px=max_text_width,
#             font_size=40,
#         )
#
#         # Convert PIL image to numpy array and create ImageClip with alpha mask
#         pil_img = pil_img.convert('RGBA')
#         img_arr = np.array(pil_img)
#         rgb_arr = img_arr[:, :, :3]
#         alpha_arr = img_arr[:, :, 3]
#
#         img_clip = ImageClip(rgb_arr).set_start(segment['start']).set_duration(max(0.01, segment['end'] - segment['start']))
#         # Attach mask for transparency
#         mask_clip = ImageClip(alpha_arr / 255.0, ismask=True).set_start(segment['start']).set_duration(max(0.01, segment['end'] - segment['start']))
#         img_clip = img_clip.set_mask(mask_clip)
#
#         # Position at bottom center with some margin from bottom
#         img_clip = img_clip.set_position(("center", video_size[1] - 150))
#
#         subtitle_clips.append(img_clip)
#
#     return subtitle_clips
#
#
# def add_captions_to_video(video_path, transcription_segments, output_path):
#     """
#     Add captions to video based on transcription segments
#
#     Args:
#         video_path (str): Path to input video
#         transcription_segments (list): Transcription data
#         output_path (str): Path for output video
#
#     Returns:
#         bool: True if successful, False otherwise
#     """
#     try:
#         # Load the video
#         video = VideoFileClip(video_path)
#         video_size = video.size
#
#         print(f"Video loaded: {video_size[0]}x{video_size[1]}, duration: {video.duration}s")
#
#         if not transcription_segments:
#             print("No transcription segments to add")
#             video.write_videofile(output_path, codec='libx264', audio_codec='aac')
#             video.close()
#             return True
#
#         # Create subtitle clips
#         subtitle_clips = create_subtitle_clips(transcription_segments, video_size)
#
#         # Composite video with subtitles
#         final_video = CompositeVideoClip([video] + subtitle_clips)
#
#         # Write output video
#         print(f"Writing output video to {output_path}...")
#         fps = video.fps or 24
#         final_video.write_videofile(
#             output_path,
#             codec='libx264',
#             audio_codec='aac',
#             temp_audiofile='temp-audio.m4a',
#             remove_temp=True,
#             fps=fps,
#             logger=None
#         )
#
#         # Close video files
#         video.close()
#         final_video.close()
#
#         print("Video with captions created successfully!")
#         return True
#
#     except Exception as e:
#         print(f"Error adding captions: {str(e)}")
#         return False
#
#
# def generate_srt_file(transcription_segments, output_path):
#     """
#     Generate SRT subtitle file from transcription
#
#     Args:
#         transcription_segments (list): Transcription data
#         output_path (str): Path for SRT file
#     """
#     try:
#         with open(output_path, 'w', encoding='utf-8') as f:
#             for i, segment in enumerate(transcription_segments, 1):
#                 # Write subtitle number
#                 f.write(f"{i}\n")
#
#                 # Write timestamp (format: HH:MM:SS,mmm --> HH:MM:SS,mmm)
#                 start_time = format_time(segment['start'])
#                 end_time = format_time(segment['end'])
#                 f.write(f"{start_time} --> {end_time}\n")
#
#                 # Write text
#                 f.write(f"{segment['text']}\n\n")
#
#         print(f"SRT file created: {output_path}")
#         return True
#
#     except Exception as e:
#         print(f"Error creating SRT file: {str(e)}")
#         return False
#
#
# def format_time(seconds):
#     """
#     Convert seconds to SRT timestamp format (HH:MM:SS,mmm)
#
#     Args:
#         seconds (float): Time in seconds
#
#     Returns:
#         str: Formatted timestamp
#     """
#     hours = int(seconds // 3600)
#     minutes = int((seconds % 3600) // 60)
#     secs = int(seconds % 60)
#     millis = int((seconds % 1) * 1000)
#
#     return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"






























from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import textwrap
import os


def _get_text_color(color_name):
    """Convert color name to RGB tuple"""
    colors = {
        'white': (255, 255, 255),
        'yellow': (255, 255, 0),
        'cyan': (0, 255, 255),
        'green': (0, 255, 0),
        'orange': (255, 165, 0),
        'red': (255, 0, 0),
        'pink': (255, 192, 203),
        'black': (0, 0, 0)
    }
    return colors.get(color_name, (255, 255, 255))


def _get_box_color(box_color_name):
    """Convert box color name to RGBA tuple"""
    colors = {
        'black_semi': (0, 0, 0, 180),
        'black_solid': (0, 0, 0, 255),
        'dark_blue': (20, 30, 80, 200),
        'dark_purple': (60, 30, 80, 200),
        'dark_green': (20, 80, 40, 200),
        'dark_red': (80, 20, 20, 200),
        'white_semi': (255, 255, 255, 180),
        'none': (0, 0, 0, 0)
    }
    return colors.get(box_color_name, (0, 0, 0, 180))


def _get_font_size(size_name):
    """Convert font size name to pixel value"""
    sizes = {
        'small': 28,
        'medium': 36,
        'large': 44,
        'xlarge': 52
    }
    return sizes.get(size_name, 36)


def _detect_script(text):
    """
    Detect script: 'devanagari' for Hindi, else 'latin'.
    """
    for ch in text:
        code = ord(ch)
        if 0x0900 <= code <= 0x097F:
            return 'devanagari'
    return 'latin'


def _find_font_for_text(text, font_size=40):
    """
    Select a Unicode font that supports the text (Hindi/English).
    Tries project fonts first, then common Windows fonts as fallback.
    """
    # Project fonts
    devanagari_font = os.path.join("static", "fonts", "NotoSansDevanagari-Regular.ttf")
    latin_font = os.path.join("static", "fonts", "NotoSans-Regular.ttf")

    script = _detect_script(text)

    # 1) Try bundled fonts
    try:
        if script == "devanagari" and os.path.exists(devanagari_font):
            print(f"Using Devanagari font: {devanagari_font}")
            return ImageFont.truetype(devanagari_font, font_size)
        if os.path.exists(latin_font):
            print(f"Using Latin font: {latin_font}")
            return ImageFont.truetype(latin_font, font_size)
    except Exception as e:
        print("Error loading bundled font:", e)

    # 2) Try common Windows fonts
    try:
        windows_fonts_dir = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts")
        if script == "devanagari":
            candidates = [
                "Nirmala.ttf", "NirmalaUI.ttf", "Mangal.ttf", "Kokila.ttf", "Aparajita.ttf"
            ]
        else:
            candidates = [
                "arial.ttf", "seguiemj.ttf", "segoeui.ttf", "calibri.ttf"
            ]
        for fname in candidates:
            fpath = os.path.join(windows_fonts_dir, fname)
            if os.path.exists(fpath):
                try:
                    print(f"Using system font: {fpath}")
                    return ImageFont.truetype(fpath, font_size)
                except Exception:
                    continue
    except Exception as e:
        print("Error searching Windows fonts:", e)

    # 3) Last resort
    print("⚠️ Falling back to default font; may not support all scripts.")
    return ImageFont.load_default()


def _create_pil_caption_image(
    text,
    max_width_px,
    font_size=36,
    padding=20,
    line_spacing=6,
    text_color=(255, 255, 255),
    box_color=(0, 0, 0, 180),
    caption_style='default'
):
    """
    Render multiline caption image using PIL (Unicode safe).
    Supports different caption styles: default, bold, outline, shadow, minimal
    """
    font = _find_font_for_text(text, font_size=font_size)
    draw_dummy = ImageDraw.Draw(Image.new("RGB", (10, 10)))

    # Word wrapping
    words = text.split()
    lines = []
    current = []
    for word in words:
        test_line = (" ".join(current + [word])).strip()
        bbox = draw_dummy.textbbox((0, 0), test_line, font=font)
        line_width = bbox[2] - bbox[0]
        if line_width <= max_width_px or not current:
            current.append(word)
        else:
            lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))

    # Calculate text box dimensions
    line_heights, line_widths = [], []
    for line in lines:
        bbox = draw_dummy.textbbox((0, 0), line, font=font)
        line_widths.append(bbox[2] - bbox[0])
        line_heights.append(bbox[3] - bbox[1])
    text_width = min(max(line_widths) if line_widths else 0, max_width_px)
    text_height = sum(line_heights) + max(0, (len(lines) - 1) * line_spacing)

    box_width = text_width + padding * 2
    box_height = text_height + padding * 2

    # Create transparent background image
    img = Image.new("RGBA", (box_width, box_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Background rectangle (semi-transparent)
    try:
        draw.rounded_rectangle((0, 0, box_width, box_height), radius=12, fill=box_color)
    except Exception:
        draw.rectangle((0, 0, box_width, box_height), fill=box_color)

    # Draw text centered with style
    y = padding
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        lw = bbox[2] - bbox[0]
        lh = bbox[3] - bbox[1]
        x = (box_width - lw) // 2
        
        # Apply different caption styles
        if caption_style == 'outline':
            # Draw outline effect (multiple offset strokes)
            # Use white outline for dark text, black outline for light text
            outline_color = (255, 255, 255, 255) if sum(text_color) < 300 else (0, 0, 0, 255)
            outline_width = 2
            for adj_x in range(-outline_width, outline_width + 1):
                for adj_y in range(-outline_width, outline_width + 1):
                    if adj_x != 0 or adj_y != 0:
                        draw.text((x + adj_x, y + adj_y), line, font=font, fill=outline_color)
            draw.text((x, y), line, font=font, fill=text_color)
        elif caption_style == 'shadow':
            # Draw drop shadow
            shadow_offset = 3
            draw.text((x + shadow_offset, y + shadow_offset), line, font=font, fill=(0, 0, 0, 200))
            draw.text((x, y), line, font=font, fill=text_color)
        elif caption_style == 'bold':
            # Draw multiple times with slight offsets to create bold effect
            for adj_x in range(-1, 2):
                for adj_y in range(-1, 2):
                    if adj_x == 0 and adj_y == 0:
                        continue
                    draw.text((x + adj_x, y + adj_y), line, font=font, fill=text_color)
            draw.text((x, y), line, font=font, fill=text_color)
        elif caption_style == 'minimal':
            # Just the text, no shadow
            draw.text((x, y), line, font=font, fill=text_color)
        else:  # default
            # Default shadow for contrast
            draw.text((x + 1, y + 1), line, font=font, fill=(0, 0, 0, 200))
            draw.text((x, y), line, font=font, fill=text_color)
        
        y += lh + line_spacing

    return img


def _split_text_into_chunks(text, max_words_per_chunk=8):
    """
    Split text into small chunks (approximately subtitle-sized) by word count.
    """
    words = text.split()
    if not words:
        return []
    chunks = []
    for i in range(0, len(words), max_words_per_chunk):
        chunk_words = words[i:i + max_words_per_chunk]
        chunks.append(" ".join(chunk_words))
    return chunks


def create_subtitle_clips(transcription_segments, video_size, video_duration, global_offset_seconds=0.0, style_options=None):
    """
    Create subtitle clips from transcription segments.
    
    Args:
        transcription_segments: List of transcription dicts
        video_size: Tuple of (width, height)
        video_duration: Duration in seconds
        global_offset_seconds: Time offset for caption timing
        style_options: Dict with 'text_color', 'box_color', 'font_size', 'caption_style'
    """
    # Default style options
    if style_options is None:
        style_options = {
            'text_color': 'white',
            'box_color': 'black_semi',
            'font_size': 'medium',
            'caption_style': 'default'
        }
    
    # Convert style options to actual values
    text_color_rgb = _get_text_color(style_options.get('text_color', 'white'))
    box_color_rgba = _get_box_color(style_options.get('box_color', 'black_semi'))
    font_size_px = _get_font_size(style_options.get('font_size', 'medium'))
    caption_style = style_options.get('caption_style', 'default')
    
    subtitle_clips = []
    for segment in transcription_segments:
        text = segment.get("text", "").strip()
        if not text:
            continue

        start_t = float(segment["start"]) + float(global_offset_seconds)
        end_t = float(segment["end"]) + float(global_offset_seconds)
        # Clamp to video bounds
        start_t = max(0.0, min(start_t, max(0.0, video_duration)))
        end_t = max(0.0, min(end_t, max(0.0, video_duration)))
        total_duration = max(0.1, end_t - start_t)

        # Split long text into smaller chunks
        chunks = _split_text_into_chunks(text, max_words_per_chunk=8)
        if not chunks:
            continue

        total_words = max(1, len(text.split()))
        per_word = total_duration / total_words

        current_start = start_t
        for chunk in chunks:
            chunk_words = max(1, len(chunk.split()))
            chunk_duration = max(0.6, chunk_words * per_word)  # ensure readable min duration
            current_end = min(end_t, current_start + chunk_duration)

            max_text_width = max(200, int(video_size[0] * 0.8))
            pil_img = _create_pil_caption_image(
                chunk, 
                max_width_px=max_text_width, 
                font_size=font_size_px,
                text_color=text_color_rgb,
                box_color=box_color_rgba,
                caption_style=caption_style
            )
            pil_img = pil_img.convert("RGBA")
            img_arr = np.array(pil_img)
            rgb_arr = img_arr[:, :, :3]
            alpha_arr = img_arr[:, :, 3]

            img_clip = ImageClip(rgb_arr).set_start(current_start).set_end(current_end)
            mask_clip = ImageClip(alpha_arr / 255.0, ismask=True).set_start(current_start).set_end(current_end)
            img_clip = img_clip.set_mask(mask_clip)

            margin_bottom = max(40, int(video_size[1] * 0.08))
            y_pos = max(0, video_size[1] - int(img_clip.h) - margin_bottom)
            img_clip = img_clip.set_position(("center", y_pos))

            subtitle_clips.append(img_clip)

            current_start = current_end
            if current_start >= end_t:
                break
    return subtitle_clips


def add_captions_to_video(video_path, transcription_segments, output_path, style_options=None):
    """
    Add captions to the video using transcription segments.
    
    Args:
        video_path: Path to input video
        transcription_segments: List of transcription dicts
        output_path: Path for output video
        style_options: Dict with caption style options (optional)
    """
    try:
        video = VideoFileClip(video_path)
        video_size = video.size
        print(f"Video loaded: {video_size}, duration: {video.duration}s")

        if not transcription_segments:
            print("No transcription found; saving original video.")
            video.write_videofile(output_path, codec="libx264", audio_codec="aac")
            video.close()
            return True

        # Global caption offset to compensate for muxing latency; negative pulls captions earlier
        global_offset = float(os.environ.get("CAPTION_OFFSET_SECONDS", "-0.3"))
        subtitle_clips = create_subtitle_clips(
            transcription_segments, 
            video_size, 
            video.duration, 
            global_offset_seconds=global_offset,
            style_options=style_options
        )
        # Ensure composite respects the background video timing and retains original audio
        final_video = CompositeVideoClip([video] + subtitle_clips, size=video.size, use_bgclip=True)
        if video.audio is not None:
            final_video = final_video.set_audio(video.audio)

        fps = video.fps or 24
        print(f"Writing output video to {output_path}...")
        final_video.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile="temp-audio.m4a",
            remove_temp=True,
            fps=fps,
            logger=None,
        )

        video.close()
        final_video.close()
        print("✅ Video with captions created successfully!")
        return True

    except Exception as e:
        print(f"❌ Error adding captions: {str(e)}")
        return False


def generate_srt_file(transcription_segments, output_path):
    """
    Generate SRT subtitle file.
    """
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(transcription_segments, 1):
                f.write(f"{i}\n")
                start = format_time(segment["start"])
                end = format_time(segment["end"])
                f.write(f"{start} --> {end}\n")
                f.write(f"{segment['text']}\n\n")
        print(f"SRT saved: {output_path}")
        return True
    except Exception as e:
        print(f"Error creating SRT: {e}")
        return False


def format_time(seconds):
    """
    Format seconds to SRT timestamp.
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
