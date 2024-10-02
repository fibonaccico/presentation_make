from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from make_presentation.DTO import ImageInfoDTO


@dataclass
class SlideDTO:
    number: int
    title: str
    text: list[str]
    images: list[ImageInfoDTO] | None
    subtitle_1: str | None
    subtitle_2: str | None
    subtitle_3: str | None
