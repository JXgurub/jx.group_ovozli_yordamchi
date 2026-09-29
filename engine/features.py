import os
import json
from urllib.parse import urlencode
import re
import sqlite3
import subprocess
import time
import webbrowser
import requests
from playsound import playsound
import eel
try:
    import pyaudio
except ImportError:
    pyaudio = None
import pyautogui
from engine.command import speak
from engine.config import ASSISTANT_NAME, DB_PATH, VOSK_MODEL_PATH, VOSK_SAMPLE_RATE, WAKE_WORDS, WWW_DIR
import pywhatkit as kit
from huggingface_hub import InferenceClient, get_token
from engine.helper import extract_yt_term, remove_words
try:
    from vosk import KaldiRecognizer, Model as VoskModel
except ImportError:
    KaldiRecognizer = None
    VoskModel = None

UZBEK_CHAT_SYSTEM_PROMPT = (
    "Siz o'zbek tilida javob beradigan ovozli yordamchisiz. "
    "Har doim ravon va tabiiy o'zbek tilida, ko'pi bilan 1-2 gapda javob bering. "
    "So'rov noaniq bo'lsa, faqat bitta qisqa aniqlashtiruvchi savol bering. "
    "Foydalanuvchi aytmagan tafsilotlarni taxmin qilmang yoki to'qib chiqarmang."
)
    
# Database ulanish
def get_db_connection():
    return sqlite3.connect(DB_PATH)


# Playing assistant sound function
@eel.expose
def playAssistantSound():
    try:
        music_path = os.path.join(WWW_DIR, "assets", "audio", "start_sound.mp3")
        if os.path.exists(music_path):
            playsound(music_path)
    except Exception as error:
        print(f"Audio playback error: {type(error).__name__}")


def openCommand(query):
    normalized_query = query.strip().lower()
    if normalized_query.startswith(ASSISTANT_NAME + " "):
        normalized_query = normalized_query[len(ASSISTANT_NAME):].strip()
    app_name = re.sub(r"^open\s+", "", normalized_query, count=1).strip()
    if not app_name:
        return

    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT path FROM sys_command WHERE LOWER(name) = ?", (app_name,))
        result = cursor.fetchone()
        if result:
            speak(f"Opening {app_name}")
            if hasattr(os, "startfile"):
                os.startfile(result[0])
            else:
                subprocess.Popen([result[0]])
            return

        cursor.execute("SELECT url FROM web_command WHERE LOWER(name) = ?", (app_name,))
        result = cursor.fetchone()
    except sqlite3.Error as error:
        print(f"Open command database error: {type(error).__name__}")
        speak("Ilovani ochishda xatolik yuz berdi")
    except Exception as error:
        print(f"Offline Liza wake-word error: {type(error).__name__}")
        return
    finally:
        connection.close()

    if result:
        speak(f"Opening {app_name}")

        webbrowser.open(result[0])
    else:
        speak("Ilova topilmadi")

       

def PlayYoutube(query):
    search_term = extract_yt_term(query)
    if not search_term:
        speak("YouTube'da qidirish uchun so'rov ayting")
        return
    speak("Playing "+search_term+" on YouTube")
    kit.playonyt(search_term)


def getWeather(query):
    weather_pattern = r'\b(?:ob[\s-]?havo|obxavo|pogoda|weather)\b'
    location_query = re.sub(weather_pattern, " ", query, flags=re.IGNORECASE)
    location_query = re.sub(
        r'\b(?:bugun|hozir|qanaqa|qanday|qa|today|now|in|at|da|uchun|shahrida|shaharida|shaharda|shahri|shahar)\b',
        " ",
        location_query,
        flags=re.IGNORECASE,
    )
    location = " ".join(location_query.split()).strip(" ,.?!")

    if not location:
        speak("Qaysi shahar uchun ob-havoni tekshiray?")
        return

    try:
        location_candidates = [location]
        if location.lower().endswith("da") and len(location) > 4:
            location_candidates.append(location[:-2])

        place = None
        fallback_place = None
        for candidate in location_candidates:
            geocoding = requests.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={"name": candidate, "count": 5, "language": "uz", "format": "json"},
                timeout=15,
            )
            geocoding.raise_for_status()
            places = geocoding.json().get("results", [])
            local_place = next(
                (item for item in places if item.get("country_code") == "UZ"),
                None,
            )
            if local_place:
                place = local_place
                break
            if places and fallback_place is None:
                fallback_place = places[0]
        place = place or fallback_place
        if place is None:
            speak(f"{location} nomli joy topilmadi. Boshqa shaharni ayting.")
            return

        weather = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": place["latitude"],
                "longitude": place["longitude"],
                "current": "temperature_2m,apparent_temperature,relative_humidity_2m,weather_code,wind_speed_10m",
                "timezone": "auto",
            },
            timeout=15,
        )
        weather.raise_for_status()
        current = weather.json()["current"]
        descriptions = {
            0: "ochiq", 1: "asosan ochiq", 2: "qisman bulutli", 3: "bulutli",
            45: "tumanli", 48: "tumanli", 51: "mayda yomg'irli", 53: "yomg'irli",
            55: "kuchli yomg'irli", 61: "yomg'irli", 63: "yomg'irli",
            65: "kuchli yomg'irli", 71: "qorli", 73: "qorli", 75: "kuchli qorli",
            80: "yomg'ir yog'ishi mumkin", 81: "yomg'ir yog'ishi mumkin",
            82: "kuchli yomg'ir yog'ishi mumkin", 95: "momaqaldiroqli",
            96: "do'l aralash momaqaldiroqli", 99: "do'l aralash momaqaldiroqli",
        }
        description = descriptions.get(current["weather_code"], "")
        answer = (
            f"{place['name']}da hozir {description}, "
            f"harorat {current['temperature_2m']} daraja. "
            f"Sezilishi {current['apparent_temperature']} daraja, "
            f"shamol {current['wind_speed_10m']} kilometr soatiga."
        )
        speak(answer)
        return answer
    except requests.RequestException as error:
        print(f"Weather lookup error: {type(error).__name__}")
        speak("Ob-havo ma'lumotini hozir olib bo'lmadi.")
        return


def is_liza_wake_word(transcript):
    words = set(re.findall(r"[a-z]+", transcript.casefold()))
    return bool(words.intersection(WAKE_WORDS))


def hotword():
    """Listen for Liza locally using the Uzbek Vosk model."""
    if pyaudio is None:
        print("PyAudio is not installed. Offline Liza detection is unavailable.")
        return
    if VoskModel is None or KaldiRecognizer is None:
        print("Vosk is not installed. Run setup.py to enable offline Liza detection.")
        return
    if not os.path.isdir(VOSK_MODEL_PATH):
        print(f"Uzbek Vosk model not found: {VOSK_MODEL_PATH}")
        return

    audio = None
    stream = None
    try:
        model = VoskModel(VOSK_MODEL_PATH)
        audio = pyaudio.PyAudio()
        stream = audio.open(
            rate=VOSK_SAMPLE_RATE,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=1600,
        )
        recognizer = KaldiRecognizer(model, VOSK_SAMPLE_RATE)
        recognizer.SetWords(False)
        print("Listening for Liza (offline Uzbek recognition)...")

        while True:
            frame = stream.read(1600, exception_on_overflow=False)
            if recognizer.AcceptWaveform(frame):
                transcript = json.loads(recognizer.Result()).get("text", "")
            else:
                transcript = json.loads(recognizer.PartialResult()).get("partial", "")

            if is_liza_wake_word(transcript):
                print("Liza wake word detected")
                stream.stop_stream()
                stream.close()
                stream = None
                audio.terminate()
                audio = None
                pyautogui.hotkey("win", "j")
                time.sleep(11)
                audio = pyaudio.PyAudio()
                stream = audio.open(
                    rate=VOSK_SAMPLE_RATE,
                    channels=1,
                    format=pyaudio.paInt16,
                    input=True,
                    frames_per_buffer=1600,
                )
                recognizer = KaldiRecognizer(model, VOSK_SAMPLE_RATE)
                recognizer.SetWords(False)
    except Exception as error:
        print(f"Offline Liza wake-word error: {type(error).__name__}")
    finally:
        if stream is not None:
            stream.close()
        if audio is not None:
            audio.terminate()


# find contacts
def findContact(query):
    words_to_remove = [ASSISTANT_NAME, "make", "a", "to", "phone", "call", "send", "message", "whatsapp", "video"]
    contact_name = remove_words(query, words_to_remove).strip().lower()
    if not contact_name:
        speak("Contact not found")
        return 0, 0

    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT phone FROM contacts WHERE LOWER(name) LIKE ?",
            ("%" + contact_name + "%",),
        )
        result = cursor.fetchone()
    except sqlite3.Error as error:
        print(f"Contact lookup error: {type(error).__name__}")
        speak("Contact not found")
        return 0, 0
    finally:
        connection.close()

    if not result or not result[0]:
        speak("Contact not found")
        return 0, 0

    phone = str(result[0]).strip()
    digits = re.sub(r"\D", "", phone)
    if not digits:
        speak("Contact phone number is invalid")
        return 0, 0
    if not phone.startswith("+"):
        phone = "+" + (digits if digits.startswith("998") else "998" + digits)
    return phone, contact_name
    
def whatsApp(mobile_no, message, flag, name):
    try:
        if flag == 'message':
            target_tab = 12
            jarvis_message = "message sent successfully to "+name

        elif flag == 'call':
            target_tab = 7
            message = ''
            jarvis_message = "calling to "+name

        else:
            target_tab = 6
            message = ''
            jarvis_message = "starting video call with "+name

        params = urlencode({"phone": mobile_no, "text": message})
        whatsapp_url = f"whatsapp://send?{params}"

        if hasattr(os, "startfile"):
            os.startfile(whatsapp_url)
        else:
            webbrowser.open(whatsapp_url)
        time.sleep(5)
        
        pyautogui.hotkey('ctrl', 'f')

        for i in range(1, target_tab):
            pyautogui.hotkey('tab')

        pyautogui.hotkey('enter')
        speak(jarvis_message)
    except Exception as error:
        print(f"WhatsApp error: {type(error).__name__}")
        speak("WhatsApp xabarini yuborishda xatolik yuz berdi")

# chat bot 
def chatBot(query):
    try:
        token = get_token()
        if not token:
            raise RuntimeError("Hugging Face tokeni sozlanmagan")

        client = InferenceClient(
            provider="featherless-ai",
            model="Qwen/Qwen3-32B",
            token=token,
            timeout=60,
        )
        response = client.chat_completion(
            messages=[
                {"role": "system", "content": UZBEK_CHAT_SYSTEM_PROMPT},
                {"role": "user", "content": str(query)},
            ],
            max_tokens=128,
            temperature=0.2,
            extra_body={"chat_template_kwargs": {"enable_thinking": False}},
        )
        answer = response.choices[0].message.content
        if not answer:
            raise RuntimeError("Model bo'sh javob qaytardi")
        answer = re.sub(r"\b(\w{2,})[!?.,]\1(\w*)", r"\1\2", answer, flags=re.IGNORECASE)
        answer = re.sub(r"([!?.,])\1+", r"\1", answer).strip()

        print(answer)
        speak(answer)
        return answer
    except Exception as error:
        status_code = getattr(getattr(error, "response", None), "status_code", None)
        if status_code:
            print(f"ChatBot error: {type(error).__name__} (HTTP {status_code})")
        else:
            print(f"ChatBot error: {type(error).__name__}")
        speak("Chatbot xizmatiga hozir ulanib bo'lmadi")
        return "Error"