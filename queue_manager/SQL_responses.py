import typing as t
from dataclasses import dataclass

from PIL.Image import Image


@dataclass
class PresentationSQL:
    slides: t.Sequence["SlideSQL"]
    template: str
    title: str


@dataclass
class SlideSQL:
    uuid: str
    number: int
    title: str
    text: list[str]
    images: list["ImageInfoSQL"] | None | list["ImageSQL"]
    subtitle1: str | None
    subtitle2: str | None
    subtitle3: str | None


@dataclass
class ImageSQL:
    image: Image | None
    path: str | None
    description: str


@dataclass
class ImageInfoSQL:
    path: str | None
    description: str
