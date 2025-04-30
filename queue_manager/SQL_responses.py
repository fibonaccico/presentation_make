import typing as t
from uuid import UUID
from dataclasses import dataclass


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
class ImageInfoSQL:
    local_file_path: str | None
    description: str


@dataclass
class ImageSQL(ImageInfoSQL):
    uuid: UUID
    slide_uuid: UUID
    number: int
    style: str
    regenerate_status: str
    regenerate_attempts: int
