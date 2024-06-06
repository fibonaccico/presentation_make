from __future__ import annotations

from config import default_setting
from DTO import ImageInfoDTO, PresentationDTO, SlideDTO
from errors import ThemeDoesNotExistError
from image import ImagesAdapter
from text import TextAdapter


class Presentation:
    def __init__(
        self,
        theme: str,
        config_data: dict[str, dict[str, str | bool] | str] = default_setting,
        template: str = "1",
    ) -> None:
        self.settings = config_data

        self.settings["THEME"] = theme
        self.settings["PRESENTATION_SETTING"]["TEMPLATE_NAME"] = template

        if config_data.get("THEME") is None or config_data.get("THEME") == "":
            raise ThemeDoesNotExistError("There is no theme. You should input a theme.")

        # взяли первые 5 слов для названия
        self.name = " ".join((config_data.get("THEME")[:200].split(" ")[:5]))

    async def make_presentation(
        self, save_path_for_images, image_style: str = "DEFAULT"
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
            if images_in_slide:
                img_info_dto_list_in_slide = []
                for image_dto in images_in_slide:
                    image_info = ImageInfoDTO(
                        path=image_dto.path, description=image_dto.description
                    )
                    img_info_dto_list_in_slide.append(image_info)
                list_of_image_info_dto.append(img_info_dto_list_in_slide)
            else:
                list_of_image_info_dto.append(images_in_slide)

        slide_dto_list: list[SlideDTO] = []

        slides_count = len(text_dto.titles)

        if self.settings.get("PRESENTATION_SETTING").get("OPENING_PR_THEME_TITLE"):
            text_dto.titles = [self.name] + text_dto.titles
            text_dto.slides_text_list = [""] + text_dto.slides_text_list
            list_of_image_info_dto = [""] + list_of_image_info_dto
            slides_count += 1

        if self.settings.get("PRESENTATION_SETTING").get("ENDING_PR_STATUS"):
            text_dto.titles = text_dto.titles + [
                self.settings.get("PRESENTATION_SETTING").get("ENDING_PR_TEXT")
            ]
            text_dto.slides_text_list = text_dto.slides_text_list + [""]
            list_of_image_info_dto = list_of_image_info_dto + [""]
            slides_count += 1

        for slide in range(slides_count):
            slide_dto = SlideDTO(
                title=text_dto.titles[slide],
                text=text_dto.slides_text_list[slide],
                images=list_of_image_info_dto[slide],
            )
            slide_dto_list.append(slide_dto)

        finish_title: str = self.settings.get("PRESENTATION_SETTING").get(
            "ENDING_PR_TEXT"
        )

        return PresentationDTO(
            template_name=self.settings.get("PRESENTATION_SETTING").get(
                "TEMPLATE_NAME"
            ),
            theme=self.settings.get("THEME"),
            finish_title=finish_title,
            slides=slide_dto_list,
        )
