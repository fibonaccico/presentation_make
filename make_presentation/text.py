from __future__ import annotations

from typing import TYPE_CHECKING

from make_presentation.errors import ContextDoesNotExistError
from make_presentation.factories import TextFactory

if TYPE_CHECKING:
    from make_presentation.DTO import TextDTO


class TextAdapter:
    async def __call__(
        self,
        context: str | None,
        number_of_slides: int,
        template: str,
        text_generation_model: str
    ) -> TextDTO:
        """
        To create text for each slide.
        """

        if not context:
            raise ContextDoesNotExistError("You should pass context into a generation text model.")

        text_factory = TextFactory()

        text_api = text_factory.get_api()
        text_obj = text_factory.get_generation_model(
            text_generation_model=text_generation_model)

        text_dto = await text_obj.create_text(
            slides_count=number_of_slides,
            api=text_api,
            context=context,
            template=template
        )
        return text_dto
