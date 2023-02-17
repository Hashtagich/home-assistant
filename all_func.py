import json
import re
from datetime import datetime, timedelta

import pyttsx3
import speech_recognition as sr
import wikipedia

# from time import sleep

name_json, task_json = 'datas.json', 'tasks.json'
flag = True

engine = pyttsx3.init()

engine.setProperty('rate', 150)
engine.setProperty('volume', 0.9)

ru_voice_id = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_RU-RU_IRINA_11.0"
voice = engine.setProperty('voice', ru_voice_id)

r = sr.Recognizer()
micro = sr.Microphone(device_index=1)


# Блок с переменными и функция для работы с json файлами.
def open_json_file(name_file: str = name_json) -> dict:
    """Функция открывает файл формата json и возвращает словарь.
    Изначально основная задача функции открытие файла с основными переменными для программы."""
    with open(name_file, 'r', encoding='utf-8') as file:
        return json.load(file)


data = open_json_file()
dict_tasks = open_json_file(name_file=task_json)
name_assistant = data['Name_assistant']
tuple_del_phrase = tuple(data['list_del_phrase'])
tuple_rename = tuple(data['rename'])
tuple_music = tuple(data['play_music'])
dict_sec = data['dict_sec']
dict_min = data['dict_min']
dict_hours = data['dict_hours']
dict_number_calendar = data['dict_number_calendar']
mask = data['mask']
yes_answer = data['yes_answer']
no_answer = data['no_answer']


def write_json_file(dt: dict, name_file: str = name_json):
    """Функция перезаписи данных в файле формата json."""
    with open(name_file, 'w', encoding='utf8') as file:
        file.write(json.dumps(dt, indent=4, sort_keys=False, ensure_ascii=False))


# Блок для записи звука с микрофона и озвучивания результатов функции.
def speak(what_say: str) -> None:
    """Функция озвучивает переданный ей текст"""
    engine.say(what_say)
    engine.runAndWait()
    engine.stop()


def listen() -> str:
    """Функция записывает всё что услышит через микрофон."""
    with micro as source:
        r.adjust_for_ambient_noise(source, duration=0.5)  # настройка посторонних шумов
        audio = r.listen(source)
    try:

        result = r.recognize_google(audio, language='ru-RU').lower()
        return result

    except:  # raise UnknownValueError() speech_recognition.UnknownValueError
        speak('Я Вас не понял, повторите!')
        listen()


# Блок с функциями для работы с задачами.
def have_tasks_today(dt: dict) -> None:
    """Функция проверяет словарь задач на наличие задач на сегодня
    и в зависимости от условия запускает определённую функцию."""
    global flag
    tasks = {key[-5:]: var for key, var in dt.items() if time_has_come(date_from_dict=key)}
    update_flag()
    if flag:
        if len(tasks.keys()) == 0:
            flag = False
            speak('На сегодня нет запланированных задач.')

        elif len(tasks) == 1:
            begin = 'У Вас на сегодня запланирована одна задача. '
            result = begin + " ".join([f'В {key[-5:]} {var}' for key, var in tasks.items()])
            speak(result)
            flag = False
            update_flag()
            del_or_not_del()
        else:
            begin = 'У Вас на сегодня запланировано несколько задач. '
            result = begin + " ".join([f'В {key[-5:]} {var}' for key, var in tasks.items()])
            speak(result)
            flag = False
            update_flag()
            del_or_not_del()

    else:
        speak('Круг пройден')


def update_flag() -> None:
    """Функция возвращает bool значение если сейчас 00 минут. Необходимо, чтобы обновлять flag."""
    global flag
    if datetime.today().minute == 0:
        flag = True


def create_task() -> None:
    """Функция добавляет новую задачу и обновляет список файле."""
    speak('Укажите дату и время.')
    date_task = listen()
    speak('Какая задача?')
    task = listen()
    speak(f'Вы запланировали на {date_task} {task}. Всё верно?')
    query = listen()
    if query in yes_answer:
        dict_tasks[date_task] = dict_tasks.get(date_task, "") + task
        write_json_file(dt=dict_tasks, name_file=task_json)
        speak('Задача успешно добавлена')
    else:
        speak('Попробуем снова.')
        create_task()


def del_or_not_del():
    """Функция уточняет удалять задачу или нет."""
    global dict_tasks
    speak('Удалить?')

    query = listen()
    if query in yes_answer:
        delete_task(dt=dict_tasks)
        dict_tasks = open_json_file(name_file=task_json)
        speak('Удалено.')
    if query in no_answer:
        main()
    else:
        speak('Я Вас не понял. Давайте повторим.')
        del_or_not_del()


def delete_task(dt: dict) -> dict:
    """Функция создаёт, возвращает новый словарь, но без сегодняшних задача, на основе переданного (основного) словаря
    и перезаписывает данные по словарю в основном файле."""
    tasks = {key: var for key, var in dt.items() if not time_has_come(date_from_dict=key)}
    write_json_file(dt=tasks, name_file=task_json)
    return tasks


# Блок с функциями для работы с ассистентом.
def call_assistant(query) -> None:
    """Функция проверяет обратились к ассистенту или нет."""
    if name_assistant in query:
        query = query.replace(name_assistant, '')
        return query  # заглушка


def stop_assistant(query) -> None:
    """Функция проверяет сказал ли человек Стоп или нет"""
    if query in no_answer:
        main()


def rename_assistant(new_name_assistant: str, old_dt: dict):
    """Функция переименовывает имя голосового помощника и
    запускает функцию перезаписи файла json, где его имя находится."""
    old_dt['Name_assistant'] = new_name_assistant
    write_json_file(dt=old_dt, name_file=name_json)


# Блок с функциями для основных запросов к ассистенту.
def question_in_or_no(tuple_words: tuple, word: str) -> bool:
    """Функция для определения содержит ли запрос слова из заданного кортежа"""
    return any([True for i in tuple_words if i.lower() in word.lower()])


def get_in_wiki(string: str, tuple_del_phrase_wiki: tuple) -> str:
    """Функция для парсинга Википедии на русском языке. Удалят слова совпадающие с кортежем list_del_phrase
    и возвращает первый абзац странички запроса."""
    wikipedia.set_lang("ru")
    mask_phrase = " |".join(tuple_del_phrase_wiki)

    phrase = re.sub(mask_phrase, r'', string)

    article = wikipedia.page(phrase).content
    result = article[:article.find('\n')]
    return result


# Блок работы со временем и датами.
def what_name_time(dict_time: dict, number: int) -> str:
    """Функция для прогонки заданного словаря и возвращения ключа,
    который обозначает название времени, если номер времени находится в заданном списке."""
    for key, val in dict_time.items():
        if number in val:
            return key
        else:
            continue


def time_has_come(date_from_dict: str, days: int = 0, hours: int = 1, minutes: int = 0, seconds: int = 0) -> bool:
    """Функция для отслеживания времени.
    Функция принимает дату и время в формате строки и необязательные аргументы времени для настройки интервала отбора.
    Если переданная дата и время приближена к текущей +- 1 час, то помощник напомнит что мы запланировали на это время.
    """
    datetime_now = datetime.today()
    delta = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

    return datetime_now + delta >= datetime.strptime(date_from_dict, mask) >= datetime_now - delta


def what_time_is_it() -> str:
    """Функция возвращает предложение с обозначением текущего времени."""
    datetime_now = datetime.today()

    hour_str = what_name_time(dict_time=dict_hours, number=datetime_now.hour)
    minute_str = what_name_time(dict_time=dict_min, number=datetime_now.minute)
    second_str = what_name_time(dict_time=dict_sec, number=datetime_now.second)

    return f'Точное время ' \
           f'{datetime_now.hour} {hour_str} ' \
           f'{datetime_now.minute} {minute_str} ' \
           f'{datetime_now.second} {second_str}'


def what_date_today() -> str:
    """Функция возвращает предложение с обозначением сегодняшней даты."""
    from calendar import month_name
    import locale
    datetime_now = datetime.today()
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
    mount = f'{month_name[datetime_now.month][:-1]}а' \
        if datetime_now.month in [3, 8] else f'{month_name[datetime_now.month][:-1]}я'

    return f'Сегодня {dict_number_calendar[str(datetime_now.day)]} {mount.lower()} {datetime_now.year} года'


# Блок main
def record_volume():
    query = listen()


# запуск цикла и достаём по ключу функции созвучные со словами, что в списках (в мусоре есть пример связи)

def main():
    """Функция для запуска ассистента."""
    while True:
        have_tasks_today(dt=dict_tasks)

        record_volume()
# мусор
# commands_dict = {
#     'commands': {
#         'greeting': ['привет', 'приветствую'],
#         'create_task': ['добавить задачу', 'создать задачу', 'заметка'],
#         'play_music': ['включить музыку', 'дискотека']
#     }
# }
#
#
# def listen_command():
#     """The function will return the recognized command"""
#
#     try:
#         with speech_recognition.Microphone() as mic:
#             sr.adjust_for_ambient_noise(source=mic, duration=0.5)
#             audio = sr.listen(source=mic)
#             query = sr.recognize_google(audio_data=audio, language='ru-RU').lower()
#
#         return query
#     except speech_recognition.UnknownValueError:
#         return 'Damn... Не понял что ты сказал :/'
#
#
# def greeting():
#     """Greeting function"""
#
#     return 'Привет!'
#
#
# def create_task():
#     """Create a todo task"""
#
#     print('Что добавим в список дел?')
#
#     query = listen_command()
#
#     with open('todo-list.txt', 'a') as file:
#         file.write(f'❗️ {query}\n')
#
#     return f'Задача {query} добавлена в todo-list!'
#
#
# def play_music():
#     """Play a random mp3 file"""
#     return f'Танцуем 🔊🔊🔊'
#
#
