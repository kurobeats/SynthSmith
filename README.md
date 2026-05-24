# SynthSmith 🎵

An AI-powered music generator web application that uses OpenRouter's API to create custom tracks from text prompts.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)
![License](https://img.shields.io/badge/License-GPL3-yellow.svg)

## Features

- 🎹 Generate AI music from text descriptions
- 🎤 Supports audio generation models (e.g., Google Lyria 3)
- 📝 Displays generated lyrics on the page
- ⬇ Download generated tracks via on-page button
- 🎨 Clean, dark-themed web interface with loading spinner
- ⚡ Streaming audio generation for compatible models
- 🔒 Sanitized error messages (full errors logged server-side)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/kurobeats/SynthSmith
cd SynthSmith
python -m venv venv
source venv/bin/active
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your API key:
```bash
cp config.ini.example config.ini
# Edit config.ini and add your OpenRouter API key
```

## Configuration

Edit `config.ini` with your settings:

```ini
[openrouter]
api_key = YOUR_OPENROUTER_API_KEY_HERE
model = google/lyria-3-pro-preview
```

Get your API key from [OpenRouter](https://openrouter.ai/).

## Usage

1. Start the Flask development server:
```bash
python synthsmith.py
```

2. Open your browser and navigate to:
```
http://127.0.0.1:5000
```

3. Enter a prompt describing the track you want to create, for example:
> "A dark cyberpunk track with female vocals, slow build, heavy synth drop at 1:20"

4. Click **"Generate Track"** and wait for the AI to create your song.

5. Once complete, the page will display:
   - A **green download button** to save your MP3
   - The **lyrics** generated for the track

6. Click the download button to save your track!

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Missing API key" error | Check that `config.ini` exists and contains a valid `api_key` |
| "Model returned no audio" | The selected model may not support audio output. Try a different model in `config.ini` |
| "Audio output requires stream: true" | This is handled automatically—ensure you're using the latest code |
| Connection errors | Verify your internet connection and OpenRouter API status |
| Page stays loading | Check browser console and Flask terminal for error messages |

## How It Works

1. **Streaming Generation**: Audio models like Lyria 3 require streaming mode (`stream: true`) to return audio data
2. **Temporary Storage**: Generated tracks are stored temporarily in memory (last 10 tracks kept)
3. **Download Flow**: After generation, a download button appears—click it to save your MP3
4. **Lyrics Display**: Song lyrics are parsed from the model response and shown on the page

## Project Structure

```
SynthSmith/
├── synthsmith.py          # Main Flask application
├── config.ini.example     # Configuration template
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html         # Web interface
└── README.md              # This file
```

## License

This project is licensed under the GPL3 License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Powered by [OpenRouter](https://openrouter.ai/) for AI model access
- Built with [Flask](https://flask.palletsprojects.com/)

