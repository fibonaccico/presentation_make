from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from api_models.interfaces import TextAPIProtocol
    from DTO import TextDTO


class TextGeneratorProtocol(Protocol):
    async def create_text(
        self, theme: str, slides_count: int, api: TextAPIProtocol
    ) -> TextDTO:
        raise NotImplementedError
