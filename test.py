import locale

import pyttsx3
import speech_recognition as sr
from notifiers import get_notifier

locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 0.9)
ru_voice_id = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_RU-RU_IRINA_11.0"
voice = engine.setProperty('voice', ru_voice_id)
r = sr.Recognizer()
micro = sr.Microphone(device_index=1)

telegram = get_notifier('telegram')


def speak(what_say: str) -> None:
    """Функция озвучивает переданный ей текст."""
    engine.say(what_say)
    engine.runAndWait()
    engine.stop()
