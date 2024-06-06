from typing import TypeAlias, TypeVar

from templates.template_config import templates_set

TITLE_TEXT = TypeVar("TITLE_TEXT", dict[str, str], dict[str, bool], dict[str, int])
PICTURE: TypeAlias = list[dict[str, str]]
FOREGROUND: TypeAlias = list[str]

INITIAL_END: TypeAlias = dict[str, TITLE_TEXT]
USUAL: TypeAlias = dict[str, TITLE_TEXT | PICTURE | FOREGROUND]


def get_slides_template_setting(
    template_name: str, num_slides: int
) -> list[INITIAL_END | USUAL]:
    """
    Return settings for each slide in the following format:
    {
        "TITLE": {"NAME": "Arial", "SIZE": 46, "BOLD": True, "ITALIC": False},
        "TEXT": {"NAME": "Arial", "SIZE": 16, "BOLD": False, "ITALIC": False},
        "PICTURE": [
            {"FIGURE": "ROUNDED RECTANGLE", "SIZE": "304 552"},
            {"FIGURE": "ROUNDED RECTANGLE", "SIZE": "304 552"}
        ]
    }
    """

    new_setting: list[INITIAL_END | USUAL] = []

    setting = templates_set[template_name]
    if setting:
        usual: USUAL = setting["USUAL"]
        num_slides -= 2
        initial = setting["INITIAL"]
        if initial is not None:
            new_setting.append(initial)
        if usual is not None:
            for i in range(num_slides):
                new_setting.append(usual[i % len(usual)])

        end = setting["END"]
        if end is not None:
            new_setting.append(end)

    return new_setting
