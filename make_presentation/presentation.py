from __future__ import annotations

from config import (DEFAULT_SETTINGS, ENDING_PRESENTATION_STATUS,
                    ENDING_PRESENTATION_TEXT, OPENING_PRESENTATION_THEME_TITLE)
from DTO import ImageInfoDTO, PresentationDTO, SlideDTO
from errors import ThemeDoesNotExistError
from image import ImagesAdapter
from text import TextAdapter


class Presentation:
    def __init__(
        self,
        theme: str,
        config_data: dict[str, dict[str, str]] = DEFAULT_SETTINGS,
        template: str = "1",
    ) -> None:
        self.settings = config_data

        self.settings["PRESENTATION_SETTING"]["THEME"] = theme
        if template:
            self.settings["PRESENTATION_SETTING"]["TEMPLATE_NAME"] = template

        if (
            self.settings["PRESENTATION_SETTING"]["THEME"] is None
            or self.settings["PRESENTATION_SETTING"]["THEME"] == ""
        ):
            raise ThemeDoesNotExistError("There is no theme. You should input a theme.")

        # взяли первые 5 слов для названия
        self.name = " ".join(
            (self.settings["PRESENTATION_SETTING"]["THEME"][:200].split(" ")[:5])
        )

    async def make_presentation(
        self,
        save_path_for_images,
        image_style: str = "DEFAULT",
        opening_prentation_theme_title: bool = OPENING_PRESENTATION_THEME_TITLE,
        ending_presentation_status: bool = ENDING_PRESENTATION_STATUS
    ) -> PresentationDTO:
        """
        Main function to create a presentation data transfer object.
        """

        text_dto = await TextAdapter(settings=self.settings)()

        list_of_image_dto = await ImagesAdapter(settings=self.settings)(
            pictures_descriptions=text_dto.picture_discription_list,
            save_path=save_path_for_images,
            image_style=image_style,
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

        if opening_prentation_theme_title:
            text_dto.titles = [self.name] + text_dto.titles
            text_dto.slides_text_list = [""] + text_dto.slides_text_list
            list_of_image_info_dto = [
                [ImageInfoDTO(path="", description="")]
            ] + list_of_image_info_dto
            slides_count += 1

        if ending_presentation_status:
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
            theme=self.settings["PRESENTATION_SETTING"]["THEME"],
            finish_title=finish_title,
            slides=slide_dto_list,
        )
