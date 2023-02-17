from all_func import *
import pyttsx3
from time import sleep
import speech_recognition as sr

engine = pyttsx3.init()

engine.setProperty('rate', 150)
engine.setProperty('volume', 0.9)

ru_voice_id = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_RU-RU_IRINA_11.0"
voice = engine.setProperty('voice', ru_voice_id)

r = sr.Recognizer()
micro = sr.Microphone(device_index=1)


def main():
    while True:
        have_tasks_today(dt=dict_tasks)

        record_volume()


if __name__ == '__main__':
    main()
