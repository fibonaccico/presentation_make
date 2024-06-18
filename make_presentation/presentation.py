from __future__ import annotations

from make_presentation.config import (DEFAULT_SETTINGS,
                                      ENDING_PRESENTATION_STATUS,
                                      ENDING_PRESENTATION_TEXT,
                                      OPENING_PRESENTATION_THEME_TITLE)
from make_presentation.DTO import ImageInfoDTO, PresentationDTO, SlideDTO
from make_presentation.errors import (TextDoesNotExistError,
                                      ThemeDoesNotExistError)
from make_presentation.factories.text.text_module_enum import TextGenModuleEnum
from make_presentation.image import ImagesAdapter
from make_presentation.text import TextAdapter


class Presentation:
    def __init__(
        self,
        text_generation_model: str,
        theme: str,
        config_data: dict[str, dict[str, str]] = DEFAULT_SETTINGS,
        template: str = "1",
        opening_prentation_theme_title: bool = OPENING_PRESENTATION_THEME_TITLE,
        ending_presentation_status: bool = ENDING_PRESENTATION_STATUS
    ) -> None:
        self.settings = config_data
        self.settings["TEXT"]["GENMODEL"] = text_generation_model

        if text_generation_model == TextGenModuleEnum.TEXTINTWOSTEP.value:
            if not theme:
                raise ThemeDoesNotExistError("There is no theme. You should input a theme.")

        self.settings["PRESENTATION_SETTING"]["THEME"] = theme

        if template:
            self.settings["PRESENTATION_SETTING"]["TEMPLATE_NAME"] = template

        self.opening_prentation_theme_title = opening_prentation_theme_title
        self.ending_presentation_status = ending_presentation_status

    async def make_presentation(
        self,
        save_path_for_images: str,
        text_api_key: str,
        image_api_key: str,
        image_secret_key: str,
        image_style: str = "DEFAULT",
        text: str = ''
    ) -> PresentationDTO:
        """
        Main function to create a presentation data transfer object.
        """

        if self.settings["TEXT"]["GENMODEL"] == TextGenModuleEnum.FROMTEXT.value:
            if not text:
                raise TextDoesNotExistError(
                    "There is no text to create a presentation. \
                    You should input a text because of you are going to generate a \
                    presentation from text."
                )

        text_dto = await TextAdapter(settings=self.settings)(
            text=text,
            api_key=text_api_key
        )

        list_of_image_dto = await ImagesAdapter(settings=self.settings)(
            pictures_descriptions=text_dto.picture_discription_list,
            save_path=save_path_for_images,
            image_style=image_style,
            api_key=image_api_key,
            secret_key=image_secret_key
        )

        list_of_image_info_dto = []

        for images_in_slide in list_of_image_dto:
            img_info_dto_list_in_slide = []
            for image_dto in images_in_slide:
                image_info = ImageInfoDTO(
                    path=image_dto.path, description=image_dto.description
                )
                img_info_dto_list_in_slide.append(image_info)
            list_of_image_info_dto.append(img_info_dto_list_in_slide)

        slide_dto_list: list[SlideDTO] = []

        slides_count = len(text_dto.titles)

        if self.opening_prentation_theme_title:
            text_dto.titles = [self.settings["PRESENTATION_SETTING"]["THEME"]] + text_dto.titles
            text_dto.slides_text_list = [""] + text_dto.slides_text_list
            list_of_image_info_dto = [
                [ImageInfoDTO(path="", description="")]
            ] + list_of_image_info_dto
            slides_count += 1

        if self.ending_presentation_status:
            text_dto.titles = text_dto.titles + [ENDING_PRESENTATION_TEXT]
            text_dto.slides_text_list = text_dto.slides_text_list + [""]
            list_of_image_info_dto = list_of_image_info_dto + [
                [ImageInfoDTO(path="", description="")]
            ]
            slides_count += 1
            finish_title = ENDING_PRESENTATION_TEXT
        else:
            finish_title = None

        for slide in range(slides_count):
            slide_dto = SlideDTO(
                title=text_dto.titles[slide],
                text=text_dto.slides_text_list[slide],
                images=list_of_image_info_dto[slide],
            )
            slide_dto_list.append(slide_dto)

        return PresentationDTO(
            template_name=self.settings["PRESENTATION_SETTING"]["TEMPLATE_NAME"],
            theme=text_dto.theme,
            finish_title=finish_title,
            slides=slide_dto_list,
        )
