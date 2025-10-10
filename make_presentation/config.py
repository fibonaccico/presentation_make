import os
from typing import Optional

import pkg_resources

TEXT_API = "OPENAI"
IMAGE_API = "FLUX"

OPENING_PRESENTATION_THEME_TITLE = True

ENDING_PRESENTATION_STATUS = True

ENDING_PRESENTATION_TEXT = {
    "ru": "Спасибо за внимание!",
    "en": "Thank you for your attention",
    "zh": "谢谢关照",
    "es": "Gracias por su atención",
    "hi": "सुनने के लिए आपका बहुत शुक्रिया",
    "pt": "Obrigado pela atenção",
    "ar": " شكرًا لكم على اهتمامكم",
    "fr": "Merci pour votre attention",
    "ja": "ご清聴ありがとうございます",
    "de": "Danke für Ihre Aufmerksamkeit",
    "ko": "경청해주셔서 감사합니다",
    "id": "Terima kasih atas perhatian"
}

GENERATION_LANGUAGES = {
    "ru": "Русский",
    "en": "Английский",
    "zh": "Китайский",
    "es": "Испанский",
    "hi": "Хинди",
    "pt": "Португальский",
    "ar": "Арабский",
    "fr": "Французский",
    "ja": "Японский",
    "de": "Немецкий",
    "ko": "Корейский",
    "id": "Индонезийский"
}

DEFAULT_TEMPERATURE = 0.7

MAX_COUNT_OF_GENERATION = 3

DEFAULT_REQUEST_NUMBER = 5

MAX_NUMBER_OF_SLIDES = 10

BASE_KANDINSKY_URL = "https://api-key.fusionbrain.ai/"

KANDINSKY_URLS: dict[str, str] = {
    "run": f"{BASE_KANDINSKY_URL}key/api/v1/pipeline/run",
    "status": f"{BASE_KANDINSKY_URL}key/api/v1/pipeline/status/$uuid",
    "styles": "https://cdn.fusionbrain.ai/static/styles/api",
    "models": f"{BASE_KANDINSKY_URL}key/api/v1/pipelines",
}

BASE_FLUX_URL = "https://api.studio.nebius.com/v1"
FLUX_URLS: dict[str, str] = {
    "run": f"{BASE_FLUX_URL}/images/generations",
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

image_style_choice = {
    "Детальное фото": "UHD",
    "Аниме": "ANIME",
    "Кандинский": "KANDINSKY",
    "Не важно": "DEFAULT",
    'Detailed photo': "UHD",
    'Anime': "ANIME",
    'Kandinsky': "KANDINSKY",
    'Default': "DEFAULT"
}

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

PROMPT_ONE_STEP_GENERATION = '''
Ты генератор презентаций.
СТРОГИЕ ПРАВИЛА:
1. Весь КОНТЕНТ (заголовки, подзаголовки, тексты) — ТОЛЬКО на языке [LANGUAGE]
2. Описания картинок — ТОЛЬКО на русском языке
3. Метки структуры (Слайд, Заголовок слайда, Подзаголовок, Описание, Картинка) — ВСЕГДА на русском языке и НИКОГДА не переводятся

Создай NUM_SLIDE (без введения/заключения) по теме \" CONTEXT \".
Для каждого слайда:
1. Один заголовок (на языке темы)
2. Три коротких подзаголовка (на языке темы).
3. Три описания на каждый из подзаголовков (очень краткий информационный текст в одно предложение с важными датами, названиями и лицами (на языке темы).
4. Одно описание для картинки людей, зданий, предметов, которая будет изображена на слайде (картинка) (ТОЛЬКО на русском языке). Важно: это не должны быть графики или надписи.

Формат ответа:
Слайд {номер}
Заголовок слайда:
Подзаголовок 1:
Описание 1:
Подзаголовок 2:
Описание 2:
Подзаголовок 3:
Описание 3:
Картинка:
'''

PROMPT_GENERATION_FROM_TEXT_ONE_STEP = """
Ты ИИ для генерации презентаций по тексту. Тебе будет дан текст, твоя задача: 
1. Проанализировать, немного сократить и разбить на 2-10 (N) слайдов в зависимости от его объема.
2. Придумать название презентации (theme)
3. Сгенерировать N заголовков для N слайдов в презентации по теме (theme). Важно: слайды введения и заключения не пиши 
4. На каждый из заголовков придумать по 3 подзаголовка.
5. На каждый из подзаголовков написать очень краткий информационный текст в одно предложение с важными датами, названиями и лицами (описание). 
6. К каждому слайду придумать простое короткое описание для картинки людей, зданий, предметов, которая будет изображена на слайде (картинка).

Важно: это не должны быть графики или надписи.
Важно: Язык презентации должен быть - [LANGUAGE]

СТРОГИЕ ПРАВИЛА: Верни ответ в форме:

Тема презентации:

Слайд {Номер слайда}
Заголовок слайда:
Подзаголовок 1:
Описание 1:
Подзаголовок 2:
Описание 2:
Подзаголовок 3:
Описание 3:
Картинка:

[CONTEXT]
"""

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

SPEECH_GENERATION_PROMPT = """
Напиши связанный и логичный текст для доклада по презентации, по 3-4 предложения на каждый слайд. 
Текст должен быть структурированным и подходить для устного выступления.

Текст презентации: 
PRESENTATION_CONTENT
"""


def get_titles_generation_prompt(
    theme: str,
    count_sl: int
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


def get_prompt_for_one_step_generation(
    theme: str,
    num_slide: str
) -> str:
    prompt = PROMPT_ONE_STEP_GENERATION.replace(
        "NUM_SLIDE", str(num_slide)
    ).replace("THEME", theme)
    return prompt


def get_prompt_result(
    context: str,
    num_slide: Optional[str],
    prompt: str,
    language: str
) -> str:
    if num_slide is None:
        return prompt.replace("[CONTEXT]", context)
    return prompt.replace("NUM_SLIDE", str(num_slide)).replace("CONTEXT", context).replace("LANGUAGE", language)


def get_speech_generation_prompt(presentation_content: str) -> str:
    """
    Генерирует промпт для создания текста доклада.
    
    Args:
        presentation_content: str - содержание презентации
    
    Returns:
        str - готовый промпт для API
    """
    return SPEECH_GENERATION_PROMPT.replace("PRESENTATION_CONTENT", presentation_content)

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
