from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Protocol

from make_presentation.config import MAX_TIME_IMAGE_GENERATION

if TYPE_CHECKING:
    from langchain_core.messages import BaseMessage

    from make_presentation.DTO import ImageDTO


class TextAPIProtocol(Protocol):
    async def request(
        self,
        text: str
    ) -> BaseMessage:
        raise NotImplementedError


class ImageAPIProtocol(Protocol):
    async def create_image(
        self,
        save_path: Optional[str],
        promt: str,
        width_height: str,
        negative_prompt: str,
        images: int = 1,
        model: Optional[int] = None,
        style: str = "DEFAULT",
        art_gpt: bool = False,
        max_time: int = MAX_TIME_IMAGE_GENERATION,
    ) -> ImageDTO:
        raise NotImplementedError

    async def get_styles(self) -> list[dict[str, str]]:
        raise NotImplementedError

    async def get_model(self) -> int:
        raise NotImplementedError
