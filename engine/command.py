import asyncio
import os
import pyttsx3
import speech_recognition as sr
import eel
import time
import tempfile
import edge_tts
from playsound import playsound
from datetime import date
from engine.config import WAKE_WORDS

def _speak_with_edge(text):
    temporary_audio = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as audio_file:
            temporary_audio = audio_file.name
        communicator = edge_tts.Communicate(
            text,
            voice="uz-UZ-MadinaNeural",
            rate="-15%",
            volume="+0%",
        )
        asyncio.run(communicator.save(temporary_audio))
        playsound(temporary_audio)
    finally:
        if temporary_audio and os.path.exists(temporary_audio):
            os.remove(temporary_audio)


def _speak_local(text):
    engine = pyttsx3.init("sapi5")
    voices = engine.getProperty("voices")
    preferred_voice = next(
        (voice for voice in voices if "zira" in voice.name.lower()),
        voices[0] if voices else None,
    )
    if preferred_voice is not None:
        engine.setProperty("voice", preferred_voice.id)
    engine.setProperty("rate", 145)
    engine.setProperty("volume", 1.0)
    engine.say(text)
    engine.runAndWait()


def speak(text):
    """Speak Uzbek with neural TTS, falling back to the local SAPI voice."""
    text = str(text)
    try:
        eel.DisplayMessage(text)
    except Exception:
        pass
    try:
        eel.receiverText(text)
    except Exception:
        pass

    try:
        _speak_with_edge(text)
    except Exception as error:
        print(f"Neural TTS unavailable ({type(error).__name__}); using local voice")
        try:
            _speak_local(text)
        except Exception as fallback_error:
            print(f"Speak error: {type(fallback_error).__name__}")


def takecommand():
    """Mikrofondan ovoz yozib olish"""
    try:
        r = sr.Recognizer()

        with sr.Microphone() as source:
            print('listening....')
            try:
                eel.DisplayMessage('listening....')
            except:
                pass
                
            r.pause_threshold = 1
            r.adjust_for_ambient_noise(source)
            
            audio = r.listen(source, timeout=10, phrase_time_limit=6)

        try:
            print('recognizing')
            try:
                eel.DisplayMessage('recognizing....')
            except:
                pass
                
            query = r.recognize_google(audio, language='uz-uz')
            print(f"user said: {query}")
            try:
                eel.DisplayMessage(query)
            except:
                pass
                
            time.sleep(2)
           
        except Exception as e:
            print(f"Recognition error: {e}")
            return ""
        
        return query.lower()
    except Exception as e:
        print(f"Microphone error: {e}")
        return ""

@eel.expose
def allCommands(message=1):
    """Barcha commandlarni boshqarish"""
    try:
        if message == 1:
            query = takecommand()
            print(query)
            try:
                eel.senderText(query)
            except:
                pass
        else:
            query = message
            try:
                eel.senderText(query)
            except:
                pass
        
        query = str(query).strip()
        if not query:
            return
        normalized_query = query.lower()
            
        try:
            if normalized_query in WAKE_WORDS:
                speak("Ha, eshitaman. Buyruqni ayting.")

            elif any(
                phrase in normalized_query
                for phrase in (
                    "bugungi sana", "bugun sana", "sana qanaqa", "sana qanday",
                    "bugun nechi", "bugun nechanchi", "hozirgi sana", "today's date",
                )
            ):
                months = (
                    "yanvar", "fevral", "mart", "aprel", "may", "iyun",
                    "iyul", "avgust", "sentabr", "oktabr", "noyabr", "dekabr",
                )
                today = date.today()
                answer = f"Bugun {today.day}-{months[today.month - 1]}, {today.year}-yil."
                print(answer)
                speak(answer)

            elif any(term in normalized_query for term in ("ob-havo", "ob havo", "obxavo", "pogoda", "weather")):
                from engine.features import getWeather
                getWeather(query)

            elif (
                normalized_query.startswith("open ")
                and len(normalized_query.split()) > 2
                and any(
                    word in normalized_query.split()
                    for word in ("youtube", "youtub", "yutub", "yutib", "yutuq")
                )
            ):
                from engine.features import PlayYoutube
                PlayYoutube(query[5:])

            elif normalized_query.startswith("open "):
                from engine.features import openCommand
                openCommand(query)
                
            elif any(
                word in normalized_query.split()
                for word in (
                    "youtube", "youtub", "yutub", "yutib", "yutuq",
                    "play", "music", "muzik", "muzika", "musiqa",
                )
            ) or "you tube" in normalized_query:
                from engine.features import PlayYoutube
                PlayYoutube(query)
            
            elif any(phrase in normalized_query for phrase in ("send message", "phone call", "video call")):
                from engine.features import findContact, whatsApp
                flag = ""
                contact_no, name = findContact(query)
                if(contact_no != 0):

                    if "send message" in normalized_query:
                        flag = 'message'
                        speak("what message to send")
                        query = takecommand()
                        
                    elif "phone call" in normalized_query:
                        flag = 'call'
                    else:
                        flag = 'video call'
                        
                    whatsApp(contact_no, query, flag, name)
            else:
                from engine.features import chatBot
                chatBot(query)
        except Exception as e:
            print(f"Command processing error: {e}")
        
        try:
            eel.ShowHood()
        except:
            pass
            
    except Exception as e:
        print(f"allCommands error: {e}")
