from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from make_presentation.config import DEFAULT_SETTINGS
from make_presentation.factories import ImgFactory
from make_presentation.utils import get_pictures_sizes

if TYPE_CHECKING:
    from make_presentation.DTO import ImageDTO


class ImagesAdapter:
    def __init__(
        self, settings: dict[str, dict[str, str]] = DEFAULT_SETTINGS
    ) -> None:
        self.settings = settings

    async def __call__(
        self,
        pictures_descriptions: list[str],
        save_path: str | None,
        negative_prompt: str = "",
        image_style: str = "DEFAULT",
    ) -> list[list[ImageDTO]]:
        """
        To create images for a presentation.
        """

        img_factory = ImgFactory(settings=self.settings["IMG"])
        image_api_obj = img_factory.get_img_api()

        template_name = self.settings["PRESENTATION_SETTING"]["TEMPLATE_NAME"]
        slides_count = len(pictures_descriptions)

        pictures_sizes = get_pictures_sizes(
            template_name=template_name, number_of_slides=slides_count
        )

        results = await asyncio.gather(
            *(
                image_api_obj.create_image(
                    save_path=save_path,
                    promt=pictures_descriptions[slide],
                    width_height=pictures_sizes[slide][picture_size],
                    negative_prompt=negative_prompt,
                    style=image_style,
                )
                for slide in range(len(pictures_descriptions))
                for picture_size in range(len(pictures_sizes[slide]))
            )
        )

        pictures_in_presentation: list[list[ImageDTO]] = []

        image_number = 0
        for slide in range(len(pictures_descriptions)):
            pictures_in_slide = []

            for _ in range(len(pictures_sizes[slide])):
                pictures_in_slide.append(results[image_number])
                image_number += 1

            pictures_in_presentation.append(pictures_in_slide)

        return pictures_in_presentation
