from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PIL.Image import Image


@dataclass
class ImageDTO:
    image: Image | None
    path: str
    description: str


@dataclass
class ImageInfoDTO:
    path: str
    description: str
