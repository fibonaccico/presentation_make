import enum


class TextGenModuleEnum(enum.Enum):
    TEXTINTWOSTEP = "TWOSTEP"
    TEXTINONESTEP = "ONESTEP"
    FROMTEXT = "FROMTEXT"


class TextApiModuleEnum(enum.Enum):
    GIGACHAT = "GIGACHAT"
    YANDEXGPT = "YANDEXGPT"
