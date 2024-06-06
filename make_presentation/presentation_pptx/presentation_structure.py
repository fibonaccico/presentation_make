from __future__ import annotations

import os.path
from typing import TYPE_CHECKING

from config import default_setting, path_to_template
from pptx import Presentation
from templates.get_settings import get_slides_template_setting

from .slide import Slide

if TYPE_CHECKING:
    from DTO import ImageDTO, SlideDTO
    from pptx.presentation import Presentation as PresentationClass


class PresentationTemplate:
    """
    Создаёт pptx файл из шаблона указанного в roots.path_to_template

    Также обрезает картинки во время их постановки в шаблон

    Необходимо:
    name - название призентации
    title - Заголовки призентаций
    text - Тексты призентаций
    img - list[list[ImageDTO]] Изображение
    """

    def __init__(
        self,
        name: str,
        title: list[str],
        text: list[str],
        images: list[list[ImageDTO]],
        settings: dict[str, dict[str, str | bool] | str],
    ) -> None:
        self.presentation_name = name
        self.slides_title = title
        self.slides_text = text
        self.slides_count = len(title)
        self.images = images

        if settings is not None:
            self.settings: dict[str, str | bool] = settings["PRESENTATION_SETTING"]
        else:
            self.settings: dict[str, str | bool] = default_setting[
                "PRESENTATION_SETTING"
            ]

        if self.settings["OPENING_PR_THEME_TITLE"]:
            self.slides_title = list([name] + self.slides_title)
            self.slides_text = list([""] + self.slides_text)
            self.images: list[list[ImageDTO] | str] = [""] + self.images
            self.slides_count += 1

        if self.settings["ENDING_PR_STATUS"]:
            finish_text: str = self.settings.get("ENDING_PR_TEXT")
            self.slides_title = list(self.slides_title + [finish_text])
            self.slides_count += 1

        self.slides_setting = get_slides_template_setting(
            template_name=self.settings.get("TEMPLATE_NAME"),
            num_slides=self.slides_count,
        )

    def __create_presentation_construction(self) -> PresentationClass:
        """
        To create presentation object from existing presentation template.
        """

        search_template = os.path.join(
            path_to_template,
            self.settings.get("TEMPLATE_NAME"),
            f"_{self.slides_count}.pptx",
        )

        self.presentation: PresentationClass = Presentation(search_template)

        return self.presentation

    def create_presentation(self) -> list[SlideDTO]:
        """
        To create presentation based on a particular template.
        """

        self.__create_presentation_construction()

        slides_info: list[SlideDTO] = []

        for slide_number in range(len(self.presentation.slides)):
            title = None
            if len(self.slides_title) > slide_number:
                title = self.slides_title[slide_number]

            text = None
            if len(self.slides_text) > slide_number:
                text = self.slides_text[slide_number]

            img = None
            if len(self.images) > slide_number:
                img = self.images[slide_number]

            slide = Slide(
                slide=self.presentation.slides[slide_number],
                title=title,
                text=text,
                img=img,
                settings=self.slides_setting[slide_number],
            )

            slide_dto = slide.make_slide()
            slides_info.append(slide_dto)

        return slides_info

    def save_presentation(self, file_save_path: str) -> None:
        self.presentation.save(file_save_path)
