from __future__ import annotations

import logging
import os
import re
import time

from make_presentation.config import (DEFAULT_SETTINGS,
                                      ENDING_PRESENTATION_STATUS,
                                      ENDING_PRESENTATION_TEXT,
                                      OPENING_PRESENTATION_THEME_TITLE,
                                      path_to_file)
from make_presentation.DTO import PresentationPPTXDTO
from make_presentation.errors import (TextDoesNotExistError,
                                      ThemeDoesNotExistError)
from make_presentation.factories.text.text_module_enum import TextGenModuleEnum
from make_presentation.image import ImagesAdapter
from make_presentation.text import TextAdapter

from .presentation_structure import PresentationTemplate

logger = logging.getLogger(__name__)


class PresentationPPTX:
    """
    Класс для создания презентации.
    Создаёт в три основных этапа
    1. Создание текста и промптов для картинок
    2. Создание картинок и их сохранение
    3. Создание pptx файла и его сохранение
    """

    def __init__(
        self,
        text_generation_model: str,
        config_data: dict[str, dict[str, str]] = DEFAULT_SETTINGS,
        template: str = "1",
        path: str = path_to_file,
        opening_prentation_theme_title: bool = OPENING_PRESENTATION_THEME_TITLE,
        ending_presentation_status: bool = ENDING_PRESENTATION_STATUS
    ) -> None:

        self.settings = config_data
        self.settings["TEXT"]["GENMODEL"] = text_generation_model

        if template:
            self.settings["PRESENTATION_SETTING"]["TEMPLATE_NAME"] = template

        # создали название папки для сохранения презентации
        self.file_save_path = os.path.join(path, ("prs_" + str(time.time())))

        # создали папку
        os.makedirs(self.file_save_path, exist_ok=True)

        self.opening_prentation_theme_title = opening_prentation_theme_title
        self.ending_presentation_status = ending_presentation_status

    async def make_presentation(
        self,
        save_path_for_images: str,
        text_api_key: str,
        image_api_key: str,
        image_secret_key: str,
        image_style: str = "DEFAULT",
        theme: str = "",
        text: str = ''
    ) -> PresentationPPTXDTO:
        """
        Main function to create a presentation.
        """

        if self.settings["TEXT"]["GENMODEL"] == TextGenModuleEnum.TEXTINTWOSTEP.value:
            if not theme:
                logger.error("There is no theme. You should input a theme.")
                raise ThemeDoesNotExistError("There is no theme. You should input a theme.")
            context = theme

        if self.settings["TEXT"]["GENMODEL"] == TextGenModuleEnum.FROMTEXT.value:
            if not text:
                logger.error("There is no text to create a presentation such way.")
                raise TextDoesNotExistError(
                    "There is no text to create a presentation. \
                    You should input a text because of you are going to generate a \
                    presentation from text."
                )
            context = text

        text_dto = await TextAdapter(settings=self.settings)(
            context=context,
            api_key=text_api_key
        )

        list_of_image_dto = await ImagesAdapter(
            settings=self.settings
        )(
            pictures_descriptions=text_dto.picture_discription_list,
            save_path=save_path_for_images,
            image_style=image_style,
            api_key=image_api_key,
            secret_key=image_secret_key
        )

        presentation = PresentationTemplate(
            name=text_dto.theme,
            text=text_dto.slides_text_list,
            title=text_dto.titles,
            images=list_of_image_dto,
            settings=self.settings,
            opening_prentation_theme_title=self.opening_prentation_theme_title,
            ending_presentation_status=self.ending_presentation_status
        )

        slides = presentation.create_presentation()

        self.save_presentation(
            presentation=presentation,
            path_to_save=self.file_save_path,
            theme=text_dto.theme
        )

        return PresentationPPTXDTO(
            template_name=self.settings["PRESENTATION_SETTING"]["TEMPLATE_NAME"],
            theme=text_dto.theme,
            finish_title=ENDING_PRESENTATION_TEXT if self.ending_presentation_status else "",
            slides=slides,
            path_to_file=self.presentation_save_path,
        )

    def save_presentation(
        self, presentation: PresentationTemplate, path_to_save: str, theme: str
    ) -> None:
        """
        Save .pptx file of presentation into file {path_to_save + save_name}.pptx
        """

        text = re.sub(r'[!/:*\\?"<>|+.]', "", theme)
        text = re.sub(r"\s", "_", text)

        save_name = ""
        if len(text) < 80:
            save_name = text + "_" + str(time.time()) + ".pptx"
        else:
            save_name = "prs" + str(time.time()) + ".pptx"

        self.presentation_save_path = os.path.join(path_to_save, save_name)

        presentation.save_presentation(file_save_path=self.presentation_save_path)
