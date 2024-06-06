from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PIL import Image


@dataclass
class ImageDTO:
    image: Image
    path: str
    description: str


@dataclass
class ImageInfoDTO:
    path: str
    description: str
