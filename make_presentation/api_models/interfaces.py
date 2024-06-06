from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Protocol

if TYPE_CHECKING:
    from DTO import ImageDTO
    from langchain_core.messages import BaseMessage


class TextAPIProtocol(Protocol):
    async def request(
        self,
        text: str,
        assistant: Optional[str] = None,
    ) -> BaseMessage:
        raise NotImplementedError


class ImageAPIProtocol(Protocol):
    async def create_image(
        self,
        save_path: str,
        promt: str,
        width_height: str,
        negative_prompt: str,
        images: int,
        model: Optional[int],
        style: str,
        art_gpt: bool,
        max_time: int,
    ) -> ImageDTO:
        raise NotImplementedError

    async def get_styles(self) -> list[dict[str, str]]:
        raise NotImplementedError

    async def get_model(self) -> int:
        raise NotImplementedError
