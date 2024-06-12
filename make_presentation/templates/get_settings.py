from errors import NoPicturesInTemplateConfig

from .template_config import FOREGROUND_IMAGE_SETTINGS, USUAL_PICTURES


def get_slides_pictures_setting(
    template_name: str,
    num_slides: int
) -> list[list[dict[str, str]]]:

    pictures_setting_for_each_slide = []

    usual = USUAL_PICTURES[template_name]
    num_slides -= 2
    if usual is not None:
        for i in range(num_slides):
            pictures_setting_for_each_slide.append(usual[i % len(usual)])
    else:
        raise NoPicturesInTemplateConfig("There are no picture in the template config.")

    return pictures_setting_for_each_slide


def get_slides_foreground_pictures_setting(
    template_name: str,
    num_slides: int
) -> list[list[str]]:

    foreground_pictures_setting_for_each_slide = []

    usual = FOREGROUND_IMAGE_SETTINGS[template_name]
    num_slides -= 2
    if usual is not None:
        for i in range(num_slides):
            foreground_pictures_setting_for_each_slide.append(usual[i % len(usual)])

    return foreground_pictures_setting_for_each_slide
