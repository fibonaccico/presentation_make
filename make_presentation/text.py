from __future__ import annotations

from typing import TYPE_CHECKING

from config import DEFAULT_NUMBER_OF_SLIDES, DEFAULT_SETTINGS
from factories import TextFactory

if TYPE_CHECKING:
    from DTO import TextDTO


class TextAdapter:
    def __init__(
        self, settings: dict[str, dict[str, str,]] = DEFAULT_SETTINGS
    ) -> None:
        self.settings = settings

    async def __call__(
        self, number_of_slides: int = DEFAULT_NUMBER_OF_SLIDES
    ) -> TextDTO:
        """
        To create text for each slide.
        """

        text_factory = TextFactory(self.settings["TEXT"])

        text_api = text_factory.get_api()
        text_obj = text_factory.get_generation_model()

        text_dto = await text_obj.create_text(
            theme=self.settings["PRESENTATION_SETTING"]["THEME"],
            slides_count=number_of_slides,
            api=text_api
        )
        return text_dto
