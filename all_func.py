import json
import re
from datetime import datetime, timedelta, date
from random import randint, choice
from time import sleep

import pyttsx3
import requests
import speech_recognition as sr
import wikipedia
from bs4 import BeautifulSoup
from geopy import geocoders
from notifiers import get_notifier

name_json, task_json = 'datas.json', 'tasks.json'
flag = True
telegram = get_notifier('telegram')

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
name_assistant = data['name_assistant']

tuple_del_phrase = tuple(data['list_del_phrase'])
tuple_rename = tuple(data['rename'])
tuple_what_tasks_today = tuple(data['what_tasks_today'])
tuple_what_date_today = tuple(data['what_date_today'])
tuple_what_time = tuple(data['what_time'])
tuple_greeting = tuple(data['greeting'])
tuple_create_task = tuple(data['create_task'])
tuple_events = tuple(data['get_events'])
tuple_what_can_you_do = tuple(data['what_can_you_do'])
tuple_what_can_i_do = tuple(data['what_can_i_do'])
tuple_weather = tuple(data['what_is_the_weather'])
tuple_game_cube = tuple(data['game_cube'])
tuple_coin = tuple(data['coin'])
tuple_question_for_magic_ball = tuple(data['question_for_magic_ball'])

# tuple_music = tuple(data['play_music'])

list_days = data["list_days"]
list_mounts = data["list_mounts"]
yes_answer = data['yes_answer']
no_answer = data['no_answer']
stop_answer = data['stop_answer']
url_home_page = data['url_home_page']

dict_conditions_ru = data["data_weather"]["conditions_ru"]
dict_part_name_ru = data["data_weather"]["part_name_ru"]

mask_date = data['mask_date']
mask_params = data['mask_params']
mask_datetime = data['mask_datetime']
weather_api_key = data['weather_api_key']
city, city_en = data['city']


def write_json_file(dt: dict, name_file: str = name_json) -> None:
    """Функция перезаписи данных в файле формата json."""
    with open(name_file, 'w', encoding='utf8') as file:
        file.write(json.dumps(dt, indent=4, sort_keys=False, ensure_ascii=False))


# Блок для записи звука с микрофона и озвучивания результатов функции.
def speak(what_say: str) -> None:
    """Функция озвучивает переданный ей текст."""
    engine.say(what_say)
    engine.runAndWait()
    engine.stop()


def listen() -> str:
    """Функция записывает всё что услышит через микрофон."""
    try:
        with micro as source:
            r.adjust_for_ambient_noise(source=source, duration=0.5)  # настройка посторонних шумов
            audio = r.listen(source=source)

        result = r.recognize_google(audio, language='ru-RU').lower()

        return call_assistant(query=result)

    except sr.UnknownValueError:
        speak('Я Вас не понял, повторите!')
        listen()


# Блок с функциями для работы с задачами.
def what_tasks_today(*args, dt: dict = dict_tasks) -> None:
    """Функция проверяет словарь задач на наличие задач на сегодняшнюю дату
    и в зависимости от условия озвучивает задачу(и) или говорит что их нет."""
    date_today = datetime.today().strftime(mask_date)
    tasks = [f'В {key[-5:]} {var}' for key, var in dt.items() if date_today in key]
    if len(tasks) == 0:
        speak('На сегодня нет запланированных задач.')
    elif len(tasks) == 1:
        result = 'У Вас на сегодня запланирована одна задача.\n' + "\n".join(tasks)
        speak(result)
        telegram.notify(token=data["token_bot"], chat_id=data["user_id"], message=result)
    else:
        result = 'У Вас на сегодня запланировано несколько задач.\n' + "\n".join(tasks)
        speak(result)
        telegram.notify(token=data["token_bot"], chat_id=data["user_id"], message=result)


def have_tasks_today(dt: dict) -> None:
    """Функция проверяет словарь задач на наличие задач на сегодня в заданном интервале времени в
    и в зависимости от условия запускает определённую функцию."""
    global flag
    tasks = {key[-5:]: var for key, var in dt.items() if time_has_come(date_from_dict=key)}
    update_flag()
    if flag:
        if len(tasks.keys()) == 0:
            speak('В течении ближайшего часа нет задач.')
        elif len(tasks) == 1:
            begin = 'У Вас на сегодня запланирована одна задача.\n'
            result = begin + "\n".join([f'В {key[-5:]} {var}' for key, var in tasks.items()])
            telegram.notify(token=data["token_bot"], chat_id=data["user_id"], message=result)
            speak(result)
            update_flag()
            del_or_not_del()
        else:
            begin = 'У Вас на сегодня запланировано несколько задач.\n'
            result = begin + "\n".join([f'В {key[-5:]} {var}' for key, var in tasks.items()])
            telegram.notify(token=data["token_bot"], chat_id=data["user_id"], message=result)
            speak(result)
            update_flag()
            del_or_not_del()


def update_flag() -> None:
    """Функция возвращает bool значение если сейчас 00 минут. Необходимо, чтобы обновлять flag."""
    global flag
    flag = True if datetime.today().minute == 58 else False


def date_filter() -> tuple[str, str, str]:
    """Функция запрашивает данные для даты и преобразовывает в нужный формат."""
    speak('Какое число?')
    date_day = listen()

    for num, list_day in enumerate(list_days, start=1):
        if date_day in list_day or date_day == str(num):
            date_day = f'0{num}' if len(str(num)) == 1 else str(num)
            break
        else:
            continue

    speak('Какой месяц?')
    date_mount = listen()

    for num, list_mount in enumerate(list_mounts, start=1):
        if date_mount in list_mount or date_mount == str(num):
            date_mount = f'0{num}' if len(str(num)) == 1 else str(num)
            break
        else:
            continue

    speak('Какое год?')
    date_year = listen()

    for num, list_year in enumerate(list_days, start=1):
        if date_year in list_year or date_year == str(num):
            date_year = f'20{num}'
            break
        else:
            continue

    return date_year, date_mount, date_day


def create_task(*args) -> None:
    """Функция добавляет новую задачу и обновляет список файле."""

    date_fun = date_filter()

    speak('Укажите время.')
    time_task = listen()

    speak('Какая задача?')
    task = listen()

    try:
        date_task = date(int(date_fun[0]), int(date_fun[1]), int(date_fun[2])).strftime(mask_date)
        datetime_task = f'{date_task} {time_task}'
    except ValueError:
        speak('Я не так услышал дату, давайте повторим.')
        create_task()

    speak(f'Вы запланировали на {date_task} в {time_task} {task}. Всё верно?')

    flag_res = True
    while flag_res:
        query = listen()
        if question_in_or_no(tuple_words=yes_answer, word=query):
            dict_tasks[datetime_task] = dict_tasks.get(date_task, "") + task
            write_json_file(dt=dict_tasks, name_file=task_json)
            flag_res = False
            speak('Задача успешно добавлена')

        elif question_in_or_no(tuple_words=no_answer, word=query):
            speak('Значит я не правильно услышал. Давайте повторим.')
            flag_res = False
            create_task()

        else:
            speak('Я Вас не понял. Скажите да или нет.')


def del_or_not_del() -> None:
    """Функция уточняет удалять задачу или нет."""
    global dict_tasks

    speak('Удалить?')
    query = listen()

    if question_in_or_no(tuple_words=yes_answer, word=query):
        dict_tasks = delete_task(dt=dict_tasks)
        speak('Удалено.')
    elif question_in_or_no(tuple_words=no_answer, word=query):
        main()
    else:
        speak('Я Вас не понял. Давайте повторим.')
        del_or_not_del()


def delete_task(dt: dict) -> dict:
    # В будущем эта функция скорее всего станет функцией для удаления всех задач на сегодня
    # или превратится в функцию удаления всех задач на конкретную дату.
    """Функция создаёт, возвращает новый словарь, но без сегодняшних задача, на основе переданного (основного) словаря
    и перезаписывает данные по словарю в основном файле."""
    tasks = {key: var for key, var in dt.items() if not time_has_come(date_from_dict=key)}
    write_json_file(dt=tasks, name_file=task_json)
    return tasks


# Блок с функциями для работы с ассистентом.
def call_assistant(query: str) -> str:
    """Функция проверяет обратились к ассистенту или нет. Функция убирает из запроса имя ассистента."""
    if query == name_assistant:
        speak('Слушаю Вас.')
        record_volume()
    elif name_assistant in query:
        request = query.replace(name_assistant, '')
        result = stop_assistant(query=request)
        return result
    else:
        result = stop_assistant(query=query)
        return result


def stop_assistant(query: str) -> str:
    """Функция проверяет сказал ли пользователь Стоп или нет."""
    if question_in_or_no(tuple_words=stop_answer, word=query):
        main()
    else:
        return query


def rename_assistant(*args, old_dt: dict = data) -> None:
    """Функция переименовывает имя голосового помощника и
    запускает функцию перезаписи файла json, где его имя находится."""
    global name_assistant

    speak('Назовите моё новое имя')
    new_name = listen()
    speak(f'Вы сказали {new_name}. Всё верно?')

    flag_name = True
    while flag_name:
        query = listen()

        if question_in_or_no(tuple_words=yes_answer, word=query):
            old_dt['Name_assistant'] = new_name
            write_json_file(dt=old_dt, name_file=name_json)
            name_assistant = new_name
            flag_name = False
            speak(f'Теперь меня зовут {name_assistant}')

        elif question_in_or_no(tuple_words=no_answer, word=query):
            speak('Значит я не правильно услышал. Давайте повторим.')
            flag_name = False
            rename_assistant()

        else:
            speak('Я Вас не понял. Скажите да или нет.')


def what_can_you_do(*args) -> None:
    """Озвучиваются все возможности ассистента."""
    speak("Вот что я могу:\n")
    speak(" ".join(tuple_what_can_i_do))


# Блок с функциями для основных запросов к ассистенту.
def question_in_or_no(tuple_words: tuple, word: str) -> bool:
    """Функция для определения содержит ли запрос слова из заданного кортежа"""
    if isinstance(word, type(None)):
        # speak('Я вас не расслышал, повторите.')
        record_volume()
    else:
        return any([True for i in tuple_words if i.lower() in word.lower()])


def get_in_wiki(*args, tuple_del_phrase_wiki: tuple = tuple_del_phrase) -> None:  # Доделать !!!
    """Функция для парсинга Википедии на русском языке. Удалят слова совпадающие с кортежем list_del_phrase
    и возвращает первый абзац странички запроса."""
    wikipedia.set_lang("ru")
    mask_phrase = " |".join(tuple_del_phrase_wiki)

    string = args[0]

    phrase = re.sub(mask_phrase, r'', string)
    try:
        article = wikipedia.page(phrase).content
        result = article[:article.find('\n')]

        speak(f'Вот что удалось найти на Википедии. {result}')
    except wikipedia.exceptions.PageError:
        speak(f'Я не смог найти информацию по запросу {string}')


def greeting(*args, data_greeting: tuple = tuple_greeting) -> None:
    """Функция приветствует пользователя если с ним поздоровались."""
    time_hour_now = datetime.now().time().hour

    if 12 > time_hour_now >= 6:
        speak(data_greeting[1])
    elif 17 > time_hour_now >= 12:
        speak(data_greeting[2])
    elif 24 > time_hour_now >= 17:
        speak(data_greeting[3])
    else:
        speak(data_greeting[0])


def play_music(*args) -> None:
    """Функция для включения музыки. В разработке."""
    pass


def get_events(*args, city_requests=city_en) -> None:
    """Функция предоставляет информацию о мероприятиях в городе через сайт яндекс-афиша."""
    date_fun = date_filter()
    try:
        if datetime.today().date() > date(int(date_fun[0]), int(date_fun[1]), int(date_fun[2])):
            date_params = datetime.today().date().strftime(mask_params)
        else:
            date_params = "-".join(date_fun)
    except ValueError:
        speak('Я не так услышал дату, давайте повторим.')
        get_events()

    dict_result = {}
    url_page = f'https://afisha.yandex.ru/{city_requests}?source=menu-city'
    params = {'date': date_params, 'period': 1}

    resp = requests.get(url_page, params=params)
    soup = BeautifulSoup(resp.text, 'lxml')

    list_event = tuple(soup.find_all('div', class_='Root-fq4hbj-4 iFrhLC'))
    list_links = tuple(soup.find_all('a', class_='EventLink-sc-1x07jll-2 klGCIV'))

    for atr, part_link in zip(list_event, list_links):
        name_event = atr.find('h2', class_='Title-fq4hbj-3 hponhw').text
        date_event = f"{atr.find('li', class_='DetailsItem-fq4hbj-1 ZwxkD').text.capitalize()}:\n"
        link = f"{url_home_page}{part_link.get('href')}"
        dict_result[date_event] = dict_result.get(date_event, []) + [f"Мероприятие: {name_event}\nСсылка: {link}\n\n"]

    if len(dict_result.keys()) == 0:
        speak("""Запрос временно не возможен. 
        Я слишком часто направлял запрос Яндекс-Афише и мне временно ограничили доступ. 
        Попробуйте позже.""")
    else:
        begin = 'Вот мероприятия по Вашему запросу.\n'
        speak(begin)

        for date_event in dict_result.keys():
            num = 5 if len(dict_result[date_event]) >= 5 else len(dict_result[date_event])
            speak(date_event)

            for i in dict_result[date_event][:num]:
                speak(i[:i.rfind('Ссылка:')])

        speak("Направить весь список мероприятий в телеграмм?")

        flag_res = True
        while flag_res:
            query = listen()
            if question_in_or_no(tuple_words=yes_answer, word=query):
                flag_res = False
                result = f"""{begin}{''.join([f'{i}{"".join(dict_result[i])}' for i in dict_result.keys()])}"""
                telegram.notify(token=data["token_bot"], chat_id=data["user_id"], message=result)

            elif question_in_or_no(tuple_words=no_answer, word=query):
                flag_res = False
                record_volume()

            else:
                speak('Я Вас не понял. Скажите да или нет.')


def dice_roll(*args) -> None:
    """Функция для озвучки случайного числа от 1 до 6. Бросок кубика."""
    speak(f"Выпало {str(randint(1, 6))}")


def coin_toss(*args) -> None:
    """Функция для озвучки результата броска монетки."""
    speak("Подбрасываю.")
    sleep(1)
    speak("Решка" if randint(0, 1) else "Орёл")


def speak_random_words(*args, list_words: list[str] = data['answer_for_magic_ball']) -> None:
    """Функция для озвучивания случайной фразы из заданного списка."""
    speak(choice(list_words))


# Блок работы со временем и датами.
def time_has_come(date_from_dict: str, days: int = 0, hours: int = 1, minutes: int = 0, seconds: int = 0) -> bool:
    """Функция для отслеживания времени.
    Функция принимает дату и время в формате строки и необязательные аргументы времени для настройки интервала отбора.
    Если переданная дата и время приближена к текущей +- 1 час, то помощник напомнит что мы запланировали на это время.
    """
    datetime_now = datetime.today()
    delta = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

    return datetime_now + delta >= datetime.strptime(date_from_dict, mask_datetime) >= datetime_now - delta


def what_time_is_it(*args) -> None:
    """Функция возвращает предложение с обозначением текущего времени."""
    datetime_now = datetime.today()

    result = f'Точное время {datetime_now.hour}:{datetime_now.minute}:{datetime_now.second}'
    speak(result)


def what_date_today(*args) -> None:
    """Функция возвращает предложение с обозначением сегодняшней даты."""
    import locale
    datetime_now = datetime.today()
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

    speak(f'Сегодня {datetime_now.day}.{datetime_now.month}.{datetime_now.year}')


# Блок для работы с погодой
def get_geolocation(city_fun: str = city) -> tuple[float, float]:
    """Функция определяет ширину и долготу указанного города."""
    geolocator = geocoders.Nominatim(user_agent="app_assis")
    latitude = geolocator.geocode(city_fun).latitude
    longitude = geolocator.geocode(city_fun).longitude
    return latitude, longitude


def what_is_the_weather(*args) -> None:
    """Функция для запроса погоды на яндекс-погоде через API(не более 50 запросов в день) и озвучивания.
    Озвучивает температуру сейчас и как ощущается.
    Если пользователь согласится, то в телеграмм отправится более подробный прогноз погоды."""
    coordinates = get_geolocation()
    url_weather = 'https://api.weather.yandex.ru/v2/informers'

    headers = {'X-Yandex-API-Key': weather_api_key}
    weather_params = {
        'lat': coordinates[0],
        'lon': coordinates[1],
        'lang': 'ru_RU'
    }

    response = requests.get(url_weather, headers=headers, params=weather_params)
    data_weather = response.json()

    fact_weather_dict = data_weather['fact']

    result_speak = f"""Сейчас {dict_conditions_ru[fact_weather_dict['condition']]}. 
    Температура: {fact_weather_dict['temp']} ℃. 
    По ощущениям как {fact_weather_dict['feels_like']} ℃."""

    speak(result_speak)

    speak("Направить более подробный прогноз в телеграмм?")

    flag_res = True
    while flag_res:
        query = listen()
        if question_in_or_no(tuple_words=yes_answer, word=query):
            flag_res = False

            result = f"""Прогноз на {dict_part_name_ru['fact']}
    {dict_conditions_ru[fact_weather_dict['condition']].capitalize()}
        Температура: {fact_weather_dict['temp']} ℃
        По ощущениям как {fact_weather_dict['feels_like']} ℃
        Скорость ветра {fact_weather_dict['wind_speed']} м/с

"""

            for part in data_weather['forecast']['parts']:
                result += f"""Прогноз на {dict_part_name_ru[part['part_name']]}
    {dict_conditions_ru[part['condition']].capitalize()}
        Максимальная температура: {part['temp_max']} ℃
        Минимальная температура: {part['temp_min']} ℃
        По ощущениям как {part['feels_like']} ℃
        Скорость ветра {part['wind_speed']} м/с

"""

            link_weather = str(data_weather['info']['url'])

            result += f"Более подробнее тут:\n{link_weather}"
            telegram.notify(token=data["token_bot"], chat_id=data["user_id"], message=result)

        elif question_in_or_no(tuple_words=no_answer, word=query):
            flag_res = False
            record_volume()

        else:
            speak('Я Вас не понял. Скажите да или нет.')


# Блок main
dict_fun = {
    tuple_del_phrase: get_in_wiki,
    tuple_rename: rename_assistant,
    tuple_what_tasks_today: what_tasks_today,
    tuple_greeting: greeting,
    tuple_what_time: what_time_is_it,
    tuple_what_date_today: what_date_today,
    tuple_create_task: create_task,
    tuple_weather: what_is_the_weather,
    tuple_events: get_events,
    tuple_what_can_you_do: what_can_you_do,
    tuple_game_cube: dice_roll,
    tuple_coin: coin_toss,
    tuple_question_for_magic_ball: speak_random_words

}  # tuple_music: play_music,


def record_volume(flag_fun=True) -> None:
    """Функция запускает функцию listen и прогоняет её результат через словарь dict_fun
    и при совпадении выполняется функция, которая заложена в боте."""
    query = listen()
    for words_tuple, fun in dict_fun.items():
        if question_in_or_no(tuple_words=words_tuple, word=query):
            flag_fun = False
            fun(query)  # data, query
        else:
            continue
    if flag_fun:
        speak_random_words(list_words=data['i_do_not_know_how_to_do_that'])


def main() -> None:
    """Функция для запуска ассистента."""
    while True:
        have_tasks_today(dt=dict_tasks)

        record_volume()
