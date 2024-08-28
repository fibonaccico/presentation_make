from __future__ import annotations

from typing import TYPE_CHECKING

from make_presentation.config import DEFAULT_NUMBER_OF_SLIDES, DEFAULT_SETTINGS
from make_presentation.errors import ContextDoesNotExistError
from make_presentation.factories import TextFactory

if TYPE_CHECKING:
    from make_presentation.DTO import TextDTO


class TextAdapter:
    def __init__(
        self,
        settings: dict[str, dict[str, str,]] = DEFAULT_SETTINGS
    ) -> None:
        self.settings = settings

    async def __call__(
        self,
        context: str | None,
        api_key: str,
        number_of_slides: int = DEFAULT_NUMBER_OF_SLIDES
    ) -> TextDTO:
        """
        To create text for each slide.
        """

        if not context:
            raise ContextDoesNotExistError("You should pass context into a generation text model.")

        text_factory = TextFactory(self.settings["TEXT"])

        text_api = text_factory.get_api(api_key=api_key)
        text_obj = text_factory.get_generation_model()

        text_dto = await text_obj.create_text(
            slides_count=number_of_slides,
            api=text_api,
            context=context,
            template=self.settings["PRESENTATION_SETTING"]["TEMPLATE_NAME"]
        )
        return text_dto
