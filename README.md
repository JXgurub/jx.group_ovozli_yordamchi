# Jarvis Voice Assistant
## JX.GROUP Ovozli Yordamchi

A voice-controlled desktop assistant application built with Python, Eel, and Machine Learning.

### Features

- **Voice Recognition**: Uzbek language speech recognition (uz-uz)
- **Hotword Detection**: Offline Uzbek Vosk model listens for "Liza"
- **Application Launcher**: Open applications and websites by voice command
- **YouTube Integration**: Play videos on YouTube
- **WhatsApp Integration**: Send messages, make calls via WhatsApp
- **Chat Bot**: AI-powered conversation with Hugging Face Inference Providers
- **Web Interface**: Modern web-based UI with real-time updates

### Requirements

- Python 3.11+
- Windows/Linux/macOS
- Microphone for voice input
- Speaker for voice output
- Internet connection

### Installation

#### 1. Clone or extract the project

```bash
cd jx.group_ovozli_yordamchi
```

#### 2. Run setup script

```bash
python setup.py
```

This will:
- Create necessary directories
- Install all Python dependencies
- Initialize the database
- Create sample data

#### 3. (Optional) Manual installation with pipenv

```bash
pip install pipenv
pipenv install
pipenv shell
```

### Usage

#### Run the complete application (with hotword detection):
```bash
python run.py
```

#### Run just the main assistant:
```bash
python main.py
```

#### Run setup script:
```bash
python setup.py
```

### Project Structure

```
jx.group_ovozli_yordamchi/
├── main.py              # Main entry point
├── run.py               # Multi-process runner (Jarvis + Hotword)
├── setup.py             # Setup and initialization script
├── Pipfile              # Python dependencies
├── engine/
│   ├── config.py        # Configuration settings
│   ├── command.py       # Voice command processing
│   ├── features.py      # Feature implementations
│   ├── helper.py        # Helper functions
│   ├── db.py            # Database utilities
│   ├── cookies.json     # HugChat cookies
│   └── jarvis.db        # SQLite database
├── www/                 # Web UI
│   ├── index.html       # Main page
│   ├── main.js          # Main JavaScript
│   ├── script.js        # Additional scripts
│   ├── style.css        # Styles
│   ├── controller.js    # Controller logic
│   └── assets/
│       ├── audio/       # Audio files
│       └── img/         # Images
└── README.md            # This file
```

### Configuration

Edit `engine/config.py` to customize:
- Assistant name (default: "liza")
- Language (default: "uz-uz")
- Voice rate (default: 174)
- Port and host settings

To enable chatbot responses, create a Hugging Face access token with Inference Providers permission at [Hugging Face token settings](https://huggingface.co/settings/tokens), then run `python refresh_cookies.py`. The token is entered without being displayed and saved in the local Hugging Face credential store.

`python setup.py` installs the 49 MB Uzbek Vosk model for offline Liza wake-word detection. Only wake-word detection is offline; command transcription, chatbot replies, and neural voice still use online services.

Voice replies use Microsoft's Uzbek `MadinaNeural` online voice at a slower rate. Reply text is sent to Microsoft's speech service; if it is unavailable, the assistant falls back to the installed local Windows voice.

### G-med Django and mobile PWA integration

The `www/` interface can be served by a Django project as an installable PWA. Copy `gmed_liza_api/` into the Django project, add `gmed_liza_api` to `INSTALLED_APPS`, and include its URLs under `/api/liza/`:

```python
# project/urls.py
from django.urls import include, path

urlpatterns = [
    # Keep the existing G-med URLs.
    path("api/liza/", include("gmed_liza_api.urls")),
]
```

Serve the files in `www/` from the same HTTPS origin as G-med, or copy them into its frontend/static build. In `index.html`, set `liza-api-url` and `liza-csrf-url` to the mounted endpoints. Same-origin hosting keeps the existing G-med session cookie and CSRF protection in effect. Microphone access and PWA installation require HTTPS (except localhost).

Connect the assistant to G-med's existing permission-checked application services; do not let it query arbitrary models or execute arbitrary code. Configure import paths to project-owned functions in Django settings:

```python
LIZA_COMMAND_HANDLER = "your_app.liza.handle_command"
LIZA_TRANSCRIBE_HANDLER = "your_app.liza.transcribe_audio"
```

`handle_command(*, user, message)` must enforce G-med permissions for every requested action and return a reply string (or `{"reply": "..."}`). `transcribe_audio(*, user, audio_file)` receives an uploaded audio file and must return recognized text; audio is limited to 10 MB and is not stored by this adapter. Until a speech-to-text backend has been approved/configured, the voice endpoint returns HTTP 503; typed commands can still be handled. Never send identifiable patient audio/text to an external speech or AI provider without G-med's privacy, security, and legal approval.

The PWA caches its app shell only; assistant API requests and patient data are never cached. Browser recording is user-initiated and stops after 20 seconds or when the microphone is tapped again. Background wake-word listening is not provided by a PWA.

### Database

The application uses SQLite database with these tables:

#### `sys_command`
```sql
CREATE TABLE sys_command(
    id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    path VARCHAR(1000)
);
```

#### `web_command`
```sql
CREATE TABLE web_command(
    id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    url VARCHAR(1000)
);
```

#### `contacts`
```sql
CREATE TABLE contacts(
    id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(100)
);
```

#### `command_history`
```sql
CREATE TABLE command_history(
    id INTEGER PRIMARY KEY,
    command TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Troubleshooting

#### Microphone not detected
- Check if microphone is properly connected
- Test with Windows Sound settings
- Reinstall PyAudio: `pip install pyaudio`

#### Speech recognition not working
- Check internet connection (Google Speech API requires it)
- Verify microphone permissions
- Try different language: change `LANGUAGE` in `config.py`

#### Web UI not opening
- Try opening manually: `http://localhost:8000`
- Check firewall settings
- Try different browser (Edge, Chrome)

#### Database errors
- Delete `jarvis.db` and run `setup.py` again
- Check file permissions in project directory

### Commands

#### Basic Commands
- "open notepad"
- "open instagram"
- "play [song name] on youtube"
- "send message to [contact name]"
- "phone call to [contact name]"

#### Query Examples
- "what is python?"
- "tell me a joke"
- "what's the weather?"

### Contributing

Feel free to submit issues and enhancement requests!

### License

This project is for educational purposes.

### Support

For issues and questions, please contact the development team.

---

**Developed by**: JX.GROUP
**Last Updated**: January 2026

