from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from DTO import SlideDTO


@dataclass
class PresentationDTO:
    template_name: str
    theme: str
    finish_title: Optional[str]
    slides: list[SlideDTO]


@dataclass
class PresentationPPTXDTO:
    template_name: str
    theme: str
    finish_title: str
    slides: list[SlideDTO]
    path_to_file: str
