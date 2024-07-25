from __future__ import annotations

import logging
import os.path
from typing import TYPE_CHECKING

from pptx import Presentation

from make_presentation.config import path_to_template
from make_presentation.DTO import PresentationDTO
from make_presentation.templates.get_settings import (
    get_slides_foreground_pictures_setting, get_slides_pictures_setting)
from make_presentation.templates.template_config import (TEXT_COLOR, TEXT_FONT,
                                                         TEXT_FONT_SETTINGS,
                                                         TEXT_FONT_SIZE)

from .slide import Slide

if TYPE_CHECKING:
    from pptx.presentation import Presentation as PresentationClass


logger = logging.getLogger(__name__)


class PresentationTemplate:
    """
    Создаёт pptx файл из шаблона
    """

    def _get_presentation_template(
        self,
        template_name: str,
        slides_count: int
    ) -> PresentationClass:
        """
        To create presentation object from existing presentation template.
        """

        search_template = os.path.join(
            path_to_template,
            template_name,
            f"_{slides_count}.pptx",
        )

        presentation: PresentationClass = Presentation(search_template)
        logger.info(f"A presentation template has been created. {search_template}")

        return presentation

    def create_presentation(self, data: PresentationDTO) -> None:
        """
        To create presentation based on a particular template.
        """
        number_of_slides = len(data.slides)
        self.presentation = self._get_presentation_template(
            template_name=data.template_name,
            slides_count=number_of_slides
        )

        for slide in data.slides:
            if slide.number == 0:
                slide_type = "INITIAL"
            elif slide.number == number_of_slides - 1:
                slide_type = "END"
            else:
                slide_type = "USUAL"

            pictures_setting = get_slides_pictures_setting(
                template_name=data.template_name,
                num_slides=number_of_slides,
            )

            foreground_pictures_setting = get_slides_foreground_pictures_setting(
                template_name=data.template_name,
                num_slides=number_of_slides,
            )

            slide_in_pres = Slide(
                slide=self.presentation.slides[slide.number],
                title=slide.title,
                text=slide.text,
                img=slide.images,
                slide_number=slide.number,
                slide_type=slide_type,
                text_font=TEXT_FONT.get(data.template_name),
                text_font_settings=TEXT_FONT_SETTINGS.get(data.template_name),
                text_font_size=TEXT_FONT_SIZE.get(data.template_name),
                text_color=TEXT_COLOR.get(data.template_name),
                pictures_setting=(
                    pictures_setting[slide.number - 1]
                    if slide_type == "USUAL" else None
                ),
                foreground_pictures_setting=(
                    foreground_pictures_setting[slide.number - 1]
                    if foreground_pictures_setting and slide_type == "USUAL" else None
                )
            )

            slide_in_pres.make_slide()

    def save_presentation(self, file_save_path: str) -> None:
        self.presentation.save(file_save_path)
        logger.info(f"A presentation has been saved into {file_save_path}.")
