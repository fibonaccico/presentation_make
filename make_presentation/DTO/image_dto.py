from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PIL.Image import Image


@dataclass
class ImageInfoDTO:
    path: str | None
    description: str
    style: str


@dataclass
class ImageDTO(ImageInfoDTO):
    image: Image | None
