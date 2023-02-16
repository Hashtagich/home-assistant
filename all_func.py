import json

import wikipedia
import re
from datetime import datetime, timedelta

name_json, task_json = 'datas.json', 'tasks.json'


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


def write_json_file(dt: dict, name_file: str = name_json):
    """Функция перезаписи данных в файле формата json."""
    with open(name_file, 'w', encoding='utf8') as file:
        file.write(json.dumps(dt, indent=4, sort_keys=False, ensure_ascii=False))


def rename_assistant(new_name_assistant: str, old_dt: dict):
    """Функция переименовывает имя голосового помощника и
    запускает функцию перезаписи файла json, где его имя находится."""
    old_dt['Name_assistant'] = new_name_assistant
    write_json_file(dt=old_dt, name_file=name_json)


def get_in_wiki(string: str, tuple_del_phrase: tuple) -> str:
    """Функция для парсинга Википедии на русском языке. Удалят слова совпадающие с кортежем list_del_phrase
    и возвращает первый абзац странички запроса."""
    wikipedia.set_lang("ru")
    mask_phrase = " |".join(tuple_del_phrase)

    phrase = re.sub(mask_phrase, r'', string)

    article = wikipedia.page(phrase).content
    result = article[:article.find('\n')]
    return result


def question_in_or_no(tuple_words: tuple, word: str) -> bool:
    """Функция для определения содержит ли запрос слова из заданного кортежа"""
    return any([True for i in tuple_words if i.lower() in word.lower()])


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
        # return True


def what_time_is_it() -> str:
    """Функция возвращает предложение с обозначением текущего времени."""
    datetime_now = datetime.today()

    hour_str = what_name_time(dict_time=dict_hours, number=datetime_now.hour)
    minute_str = what_name_time(dict_time=dict_min, number=datetime_now.minute)
    second_str = what_name_time(dict_time=dict_sec, number=datetime_now.second)

    return f'Точное время {datetime_now.hour} {hour_str} {datetime_now.minute} {minute_str} {datetime_now.second} {second_str}'


def what_today() -> str:
    """Функция возвращает предложение с обозначением сегодняшней даты."""
    from calendar import month_name
    import locale
    datetime_now = datetime.today()
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
    mount = f'{month_name[datetime_now.month][:-1]}а' \
        if datetime_now.month in [3, 8] else f'{month_name[datetime_now.month][:-1]}я'

    return f'Сегодня {dict_number_calendar[str(datetime_now.day)]} {mount.lower()} {datetime_now.year} года'

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
