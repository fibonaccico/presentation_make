from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from make_presentation.DTO import ImageInfoDTO


@dataclass
class SlideDTO:
    number: int
    title: str
    text: str
    images: list[ImageInfoDTO] | None
