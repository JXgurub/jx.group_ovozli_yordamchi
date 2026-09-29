import os

# Assistant name
ASSISTANT_NAME = "liza"

# Paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WWW_DIR = os.path.join(PROJECT_ROOT, "www")
DB_PATH = os.path.join(PROJECT_ROOT, "jarvis.db")
COOKIES_PATH = os.path.join(PROJECT_ROOT, "engine", "cookies.json")
WAKE_WORDS = ("liza", "lisa")
VOSK_MODEL_PATH = os.path.join(PROJECT_ROOT, "engine", "vosk-model-small-uz-0.22")
VOSK_SAMPLE_RATE = 16000

# Web server settings
WEB_HOST = "localhost"
WEB_PORT = 8000

# Audio settings
SPEECH_RATE = 174
VOICE_INDEX = 0

# Recognition settings
LANGUAGE = "uz-uz"
PAUSE_THRESHOLD = 1
LISTEN_TIMEOUT = 10
PHRASE_TIME_LIMIT = 6
