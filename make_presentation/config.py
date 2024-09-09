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

SCALING_FACTOR = 0.3     # Меньше значение - более плавное уменьшение шрифта


def get_main_promt(
    theme: str,
    title_min_char: int,
    title_max_char: int,
    count_sl: int = DEFAULT_NUMBER_OF_SLIDES
) -> str:
    res = MAIN_PROMPT_FOR_TEXT_IN_TWO_STEPS.replace(
        "THEME", theme
    ).replace("MIN_CHAR", str(title_min_char)).replace("MAX_CHAR", str(title_max_char))
    promt = res.replace("NUM_SL", str(count_sl))
    return promt


def get_second_promt_beta(
    title_promt: str,
    num_slide: str,
    text_min_char: int,
    text_max_char: int
) -> str:
    promt_for_slide = SECOND_PROMPT_FOR_TEXT_IN_TWO_STEPS.replace(
        "NUM_SLIDE", num_slide
    ).replace("MIN_CHAR", str(text_min_char)).replace("MAX_CHAR", str(text_max_char))
    return str(title_promt + "\n\n" + promt_for_slide)


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
