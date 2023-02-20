import pyttsx3
import speech_recognition as sr
from datetime import datetime, date
import locale

locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

name_json, task_json = 'datas.json', 'tasks.json'
flag = True

engine = pyttsx3.init()

engine.setProperty('rate', 150)
engine.setProperty('volume', 0.9)

ru_voice_id = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_RU-RU_IRINA_11.0"
voice = engine.setProperty('voice', ru_voice_id)

r = sr.Recognizer()
micro = sr.Microphone(device_index=1)


def speak(what_say: str) -> None:
    """Функция озвучивает переданный ей текст."""
    engine.say(what_say)
    engine.runAndWait()
    engine.stop()


string = [
    "19.2.2023 13:00",
    "19 февраля 2023 13:01",
    "19 февраль 2023 13:01",
]

mask = [
    '%d.%m.%Y %H:%M',
    '%d %B %Y %H:%M',
    '%x %H:%M'
]

mount = (
    ['январь', 'января'],
    ['февраль', 'февраля'],
    ['март', 'марта'],
    ['апрель', 'апреля'],
    ['май', 'мая'],
    ['июнь', 'июня'],
    ['июль', 'июля'],
    ['август', 'августа'],
    ['сентябрь', 'сентября'],
    ['октябрь', 'октября'],
    ['ноябрь', 'ноября'],
    ['декабрь', 'декабря']
)

date_task = date(int(2020), 10, int(22)).strftime("%x")
print(date_task)
print(type(date_task))

