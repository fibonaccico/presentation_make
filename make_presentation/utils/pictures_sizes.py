from typing import TypeAlias, TypeVar

from templates import templates_set

TITLE_TEXT = TypeVar("TITLE_TEXT", dict[str, str], dict[str, bool], dict[str, int])
PICTURE: TypeAlias = list[dict[str, str]]

INITIAL_END: TypeAlias = dict[str, TITLE_TEXT]
USUAL: TypeAlias = list[dict[str, TITLE_TEXT | PICTURE]]


def get_pictures_sizes(template_name: str, number_of_slides: int) -> list[list[str]]:
    """
    Return a list of pictures sizes list for each slide according to
    a template of presentation we use.
    """

    pictures: list[list[str]] = []

    setting = templates_set[template_name]
    usual: USUAL = setting["USUAL"]

    for i in range(number_of_slides):
        usual_set = usual[i % len(usual)]

        pictures_in_one_slide = []
        if usual_set.get("PICTURE"):
            for picture in usual_set["PICTURE"]:
                pictures_in_one_slide.append((picture["SIZE"]))

        pictures.append(pictures_in_one_slide)

    return pictures
