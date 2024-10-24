import os

import pkg_resources

DEFAULT_SETTINGS: dict[str, dict[str, str]] = {
    "TEXT": {"API": "GIGACHAT", "GENMODEL": "TWOSTEP"},
    "IMG": {"API": "KANDINSKY"},
    "PRESENTATION_SETTING": {
        "TEMPLATE_NAME": "minima",
    }
}

OPENING_PRESENTATION_THEME_TITLE = True

ENDING_PRESENTATION_STATUS = True

ENDING_PRESENTATION_TEXT = "Спасибо за внимание!"

DEFAULT_TEMPERATURE = 1.5

DEFAULT_NUMBER_OF_SLIDES = 10

MAX_COUNT_OF_GENERATION = 10

DEFAULT_REQUEST_NUMBER = 5

BASE_KANDINSKY_URL = "https://api-key.fusionbrain.ai/"

KANDINSKY_URLS: dict[str, str] = {
    "run": f"{BASE_KANDINSKY_URL}key/api/v1/text2image/run",
    "status": f"{BASE_KANDINSKY_URL}key/api/v1/text2image/status/$uuid",
    "styles": "https://cdn.fusionbrain.ai/static/styles/api",
    "models": f"{BASE_KANDINSKY_URL}key/api/v1/models",
}

DEFAULT_TEXT_SIZE = 16

DEFAULT_TEXT_FONT = "Arial"

DEFAULT_TEXT_FONT_SETTINGS: dict[str, bool] = {
    "BOLD": False,
    "ITALIC": False,
}

MAX_TIME_IMAGE_GENERATION = 180

MAX_SLIDE_TEXT_LENGTH = 650

MAX_NUMBER_OF_SLIDES_IN_TEMPLATES = 98

MAX_TEXT_LENGTH = MAX_NUMBER_OF_SLIDES_IN_TEMPLATES * MAX_SLIDE_TEXT_LENGTH


PROMPT_FOR_GENERATION_FROM_TEXT = '''
Ты ИИ для генерации презентаций. Тебе будет дан отрывок [TEXT] из презентации на тему \" THEME \",
выполни следующие действия:
1. Создай заголовок [TITLE] к [TEXT]. Заголовок должен отвечать содержанию, быть интригующим
и быть длинной от [MIN_CHAR] до [MAX_CHAR] символов.
2. Ты должен переписать [TEXT] грамотным литературным языком. Важно! Не добавляй новую информацию,
ничего не придумывай. В ответе выведи [NEW_TEXT]. Смысл [TEXT] и [NEW_TEXT]
должны быть одинаковыми.
3. Создай описание картинки [PICTURE_DESCRIPTION], которая подойдет к [TEXT].
4. Ответ выведи в формате:
    Заголовок:[TITLE]
    Текст:[NEW_TEXT]
    Картинка:[PICTURE_DESCRIPTION]


[TEXT]:
'''

PROMPT_FOR_THEME_GENERATION = '''
Ты ИИ для генерации презентаций. Тебе будет дан [TEXT]. Придумай название [THEME] к [TEXT].
[THEME] должно отвечать содержанию, быть интригующим и быть от MIN_CHAR до MAX_CHAR символов.


Ответ выведи в формате:
    Тема: [THEME]


[TEXT]:
'''


MAIN_PROMPT_FOR_TEXT_IN_TWO_STEPS = """
Ты ИИ для генерации презентаций. Твоя задача сгенерировать заголовки, краткие описания к слайдам
по их заголовкам, а также описания картинок для слайдов в презентации. Выполни следующие действия:

1. Создай заголовок [Заголовок] к слайду.
   Заголовок должен быть интригующим и быть от MIN_CHAR до MAX_CHAR символов.
2. Создай краткое описание к слайду [Описание].
3. Создай описание картинки [Картинка], которая подойдет к заголовоку слайда [Заголовок].

Для презентации на NUM_SL слайдов по теме \" THEME \" верни ответ в следующей форме:

Слайд {Номер слайда}
Заголовок:
Описание:
Картинка:
"""

SECOND_PROMPT_FOR_TEXT_IN_TWO_STEPS = """
Ты ИИ для генерации презентаций.
Напиши информационный текст с основной информацией. Важно - текст должен быть длиною
от [MIN_CHAR] до [MAX_CHAR] символов, который ты бы вставил
на слайд номер NUM_SLIDE по его описанию.

Верни ответ по форме:
Текст: {сгенерированный текст}.
\n
"""

SCALING_FACTOR = 0.1     # Меньше значение - более плавное уменьшение шрифта

TITLE_GENERATION_PROMPT = """
Ты ИИ для генерации презентаций. Твоя задача:
1. Сгенерировать NUM_SL заголовков для NUM_SL слайдов в презентации по теме \" THEME \".
Важно: не генерируй заголовки 'введение' и 'заключение'.
2. К каждому слайду придумать простое короткое описание для картинки людей,
зданий, предметов, которая будет изображена на слайде (картинка).
Важно: в описании к картинке не должно быть упоминание графиков или надписей.

Важно! Верни ответ в форме:

Слайд {Номер слайда}
Заголовок: {Заголовок}
Картинка: {Картинка}

"""

SUBTITLES_GENERATION_PROMPT = """
Ты ИИ для генерации презентаций. Тебе будут даны заголовки слайдов.
Твоя задача сгенерировать по 3 подзаголовка на каждый из заголовков
по теме \" THEME \".

TITLES

Важно! Верни ответ в форме:

Слайд {Номер слайда}
Заголовок слайда: {Заголовок слайда}
Подзаголовок 1: {Подзаголовок}
Подзаголовок 2: {Подзаголовок}
Подзаголовок 3: {Подзаголовок}

Ответы не выделяй звездочками!
"""

GENERAL_PROMPT_FOR_TEXT_IN_TWO_STEPS = """
Тема: THEME
Слайд NUM_SLIDE
Заголовок слайда: TITLE
Подзаголовок 1: Subtitle_1
Подзаголовок 2: Subtitle_2
Подзаголовок 3: Subtitle_3

Твоя задача на каждый из подзаголовков:
Написать очень краткий информационный текст в одно предложение с важными датами,
названиями и лицами (Описание)

Важно! Верни ответ в форме:

Слайд {Номер слайда}
Заголовок слайда: {Заголовок слайда}
Подзаголовок (номер подзаголовка): {Подзаголовок}
Описание: {Описание}

"""


def get_titles_generation_prompt(
    theme: str,
    count_sl: int = DEFAULT_NUMBER_OF_SLIDES
) -> str:
    res = TITLE_GENERATION_PROMPT.replace(
        "THEME", theme
    ).replace("NUM_SL", str(count_sl))
    return res


def get_subtitles_generation_prompt(
    theme: str,
    titles: str
) -> str:
    res = SUBTITLES_GENERATION_PROMPT.replace(
        "THEME", theme
    ).replace("TITLES", titles)
    return res


def get_general_prompt_for_each_slide(
    theme: str,
    num_slide: str,
    title: str,
    subtitle_1: str,
    subtitle_2: str,
    subtitle_3: str
) -> str:
    promt_for_slide = GENERAL_PROMPT_FOR_TEXT_IN_TWO_STEPS.replace(
        "NUM_SLIDE", num_slide
    ).replace("THEME", theme).replace(
        "TITLE", title
    ).replace("Subtitle_1", subtitle_1).replace(
        "Subtitle_2", subtitle_2
    ). replace("Subtitle_3", subtitle_3)
    return promt_for_slide


# Путь к проекту
path_to_project = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

# Путь к папке с презентацией, текстом, логом
path_to_file = os.path.join(os.path.dirname(path_to_project), "data", "presentation")


def load_template(template_name):
    # Получаем полный путь к шаблону
    template_path = pkg_resources.resource_filename(
        'make_presentation', f'templates/{template_name}'
    )
    return template_path


# Путь к картинкам переднего плана
path_to_foreground_image = load_template(template_name="foreground_images")

# Путь к шаблонам презентаций
path_to_template = load_template(template_name="templates")

path_to_fonts = load_template(template_name="fonts")
