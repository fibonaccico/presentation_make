from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Protocol

if TYPE_CHECKING:
    from make_presentation.api_models.interfaces import TextAPIProtocol
    from make_presentation.DTO import TextDTO


class TextGeneratorProtocol(Protocol):
    async def create_text(
        self,
        slides_count: Optional[int],
        api: TextAPIProtocol,
        context: str,
        template: Optional[str]
    ) -> TextDTO:
        raise NotImplementedError
