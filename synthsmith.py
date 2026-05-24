import base64
import configparser
import logging
import uuid
import os
from flask import Flask, render_template, request, send_file, redirect, url_for, flash, session
from io import BytesIO
from openai import OpenAI

# Temporary storage for generated audio files
audio_storage = {}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load config.ini
config = configparser.ConfigParser()
config.read("config.ini")

OPENROUTER_API_KEY = config.get("openrouter", "api_key", fallback=None)
MODEL_NAME = config.get("openrouter", "model", fallback="google/lyria-3-pro-preview")

app = Flask(__name__)
app.secret_key = "change-this-in-production"

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if not OPENROUTER_API_KEY:
            flash("Missing API key in config.ini", "error")
            return redirect(url_for("index"))

        prompt = request.form.get("prompt", "").strip()
        if not prompt:
            flash("Please enter a prompt.", "error")
            return redirect(url_for("index"))

        try:
            stream = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                modalities=["text", "audio"],
                audio={"format": "mp3"},
                stream=True,
            )

            # Collect streaming response
            collected_content = []
            audio_data = None
            
            for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta and delta.content:
                        collected_content.append(delta.content)
                    # Check for audio in the chunk
                    if hasattr(delta, 'audio') and delta.audio:
                        logger.info(f"Found audio in chunk: {type(delta.audio)}")
                        audio_data = delta.audio
            
            # Combine all content
            full_content = "".join(collected_content)
            logger.info(f"Collected content length: {len(full_content)}")
            logger.info(f"Audio data found: {audio_data is not None}")

            audio_bytes = None
            text_blocks = []
            content = full_content

            # Process audio data from streaming chunks
            if audio_data:
                if isinstance(audio_data, dict) and 'data' in audio_data:
                    audio_bytes = base64.b64decode(audio_data['data'])
                elif hasattr(audio_data, 'data'):
                    audio_bytes = base64.b64decode(audio_data.data)
                logger.info(f"Audio bytes decoded: {len(audio_bytes) if audio_bytes else 0}")

            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "audio":
                        audio_bytes = base64.b64decode(block["data"])
                    elif isinstance(block, dict) and block.get("type") == "text":
                        text_blocks.append(block.get("text", ""))
            else:
                text_blocks.append(str(content))

            lyrics = "\n\n".join(text_blocks).strip()

            if not audio_bytes:
                # Check if response contains any indication of audio (URL, markdown, etc.)
                full_response = str(content)
                if "http" in full_response and (".mp3" in full_response or ".wav" in full_response or ".ogg" in full_response):
                    flash("Model returned an audio URL instead of audio data. Check the lyrics below for the link.", "error")
                else:
                    flash(f"Model returned no audio. Response type: {type(content).__name__}. Check the server logs for details on what was returned.", "error")
                return render_template("index.html", lyrics=lyrics)

            # Store audio temporarily and show download link with lyrics
            track_id = str(uuid.uuid4())
            audio_storage[track_id] = audio_bytes
            
            # Clean up old entries (keep only last 10)
            if len(audio_storage) > 10:
                oldest_key = next(iter(audio_storage))
                del audio_storage[oldest_key]
            
            flash("Track generated successfully! Click below to download.", "success")
            return render_template("index.html", lyrics=lyrics, track_id=track_id)

        except Exception as e:
            # Log full error server-side for debugging
            logger.error(f"Error generating track: {e}", exc_info=True)
            # Show generic error to user
            flash("An error occurred while generating the track. Please try again.", "error")
            return redirect(url_for("index"))

    return render_template("index.html")


@app.route("/download/<track_id>")
def download_track(track_id):
    """Serve the generated audio file for download."""
    if track_id not in audio_storage:
        flash("Track not found or expired. Please generate again.", "error")
        return redirect(url_for("index"))
    
    audio_bytes = audio_storage[track_id]
    audio_io = BytesIO(audio_bytes)
    audio_io.seek(0)
    
    return send_file(
        audio_io,
        mimetype="audio/mpeg",
        as_attachment=True,
        download_name="synthsmith_track.mp3",
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
