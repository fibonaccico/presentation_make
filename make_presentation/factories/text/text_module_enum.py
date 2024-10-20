import enum


class TextGenModuleEnum(enum.Enum):
    TEXTINTWOSTEP = "TWOSTEP"
    FROMTEXT = "FROMTEXT"


class TextApiModuleEnum(enum.Enum):
    GIGACHAT = "GIGACHAT"
    YANDEXGPT = "YANDEXGPT"
