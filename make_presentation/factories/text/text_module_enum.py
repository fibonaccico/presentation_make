import enum


class TextGenModuleEnum(enum.Enum):
    TEXTINTWOSTEP = "TWOSTEP"
    OLDTEXTINONESTEP = "TEXTINONESTEP"
    RECREATETEXT = "TEXTRECREATE"


class TextApiModuleEnum(enum.Enum):
    GIGACHAT = "GIGACHAT"
    CHATGPT = "CHATGPT"
