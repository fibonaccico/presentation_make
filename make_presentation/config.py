import os

DEFAULT_SETTINGS: dict[str, dict[str, str]] = {
    "TEXT": {"API": "GIGACHAT", "GENMODEL": "TWOSTEP"},
    "IMG": {"API": "KANDINSKY"},
    "PRESENTATION_SETTING": {
        "TEMPLATE_NAME": "1",
    }
}

OPENING_PRESENTATION_THEME_TITLE = True

ENDING_PRESENTATION_STATUS = True

ENDING_PRESENTATION_TEXT = "Спасибо за внимание!"

DEFAULT_TEMPERATURE = 1.5

DEFAULT_NUMBER_OF_SLIDES = 10

BASE_KANDINSKY_URL = "https://api-key.fusionbrain.ai/"

KANDINSKY_URLS = {
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

main_promt = """
Ты ИИ для генерации презентаций. Твоя задача сгенерировать заголовки, краткое описание слайдов,
а также описания картинок на слайдах.

Твоя задача вернуть мне заголовки слайдов , что должно быть описано в этих слайдах, а так же
какие картинки  должны быть использованы в данном слайде.

Верни ответ на тему презентации \" THEME \" на NUM_SL слайдов в форме:
Слайд {Номер слайда}
Заголовок:
Описание:
Картинка:
"""

new_end_promt = """
Напиши текст, который бы ты вставил на слайд номер NUM_SLIDE по его описанию.
Текст должен быть не более 350 символов.  \nВерни ответ по форме: \n"Текст:
{сгенерированный текст}".\n \nВот тебе пример рандомного текста, на структуру
которого можешь опираться при своем
ответе: "Заварной чай имеет свою богатую историю, начиная с Китая. Выращивание чайных листьев
осуществляется по специальным технологиям. Чай классифицируется по процессингу и существует
множество видов, включая черный, зеленый и белый чай."\n
"""


def get_main_promt(theme: str, count_sl: int = DEFAULT_NUMBER_OF_SLIDES) -> str:
    res = main_promt.replace("THEME", theme)
    promt = res.replace("NUM_SL", str(count_sl))
    return promt


def get_second_promt_beta(title_promt: str, num_slide: str) -> str:
    promt_for_slide = new_end_promt.replace("NUM_SLIDE", num_slide)
    return str(title_promt + "\n\n" + promt_for_slide)


# Путь к проекту
path_to_project = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

# Путь к папке с презентацией, текстом, логом
path_to_file = os.path.join(os.path.dirname(path_to_project), "data", "presentation")

# Путь к картинкам переднего плана
path_to_foreground_image = os.path.join(
    path_to_project,
    "make_presentation",
    "make_presentation",
    "templates",
    "foreground_images",
)

# Путь к шаблонам презентаций
path_to_template = os.path.join(
    path_to_project, "make_presentation", "make_presentation", "templates", "templates"
)
