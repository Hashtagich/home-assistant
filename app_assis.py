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

commands_dict = {
    '1': [get_in_wiki, ['1']]
}


def speak(what_say: str) -> None:
    engine.say(what_say)
    engine.runAndWait()
    engine.stop()


def record_volume():
    with micro as source:
        r.adjust_for_ambient_noise(source, duration=0.5)  # настройка посторонних шумов
        audio = r.listen(source)
    try:

        query = r.recognize_google(audio, language='ru-RU').lower()

        for key, val in commands_dict.items():
            if query in val[1]:
                val[0]

        # if name_assistant.lower() in query:
        #     speak(f'Вы сказали: {query}')
        #
        # if question_in_or_no(tuple_words=tuple_del_phrase, word=question):
        #     print('Запускаем функцию поиска в википедии')
        #
        # elif question_in_or_no(tuple_words=tuple_rename, word=question):
        #     print('Запускаем функцию переименовать')
        # elif question_in_or_no(tuple_words=tuple_music, word=question):
        #     print('Включаю музыку')
        # else:
        #     print('Идём по другому')
    except:
        speak('Я Вас не понял, повторите!')


def main():
    while True:
        # цикл нужно проверять чтобы он не циклинлся либо спросить удалить задачу или нет
        for key, var in dict_tasks.items():
            if time_has_come(date_from_dict=key):
                speak(f'У Вас на {key[-5:]} запланирована задача {var}')


        record_volume()


if __name__ == '__main__':
    main()
