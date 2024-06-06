from __future__ import annotations

import os
from io import BytesIO
from typing import TYPE_CHECKING, Any, Optional, TypeAlias, TypeVar

from config import DEFAULT_TEXT_SETTINGS, path_to_foreground_image
from DTO import ImageInfoDTO, SlideDTO
from pptx.dml.color import RGBColor

from .image_corrector import ImageCorrector

if TYPE_CHECKING:
    from DTO import ImageDTO
    from PIL.Image import Image
    from pptx.slide import Slide as PptxSlide


TITLE_TEXT = TypeVar("TITLE_TEXT", dict[str, str], dict[str, bool], dict[str, int])
PICTURE: TypeAlias = list[dict[str, str]]
FOREGROUND: TypeAlias = list[str]

INITIAL_END: TypeAlias = dict[str, TITLE_TEXT]
USUAL: TypeAlias = dict[str, TITLE_TEXT | PICTURE | FOREGROUND]


class Slide:
    def __init__(
        self,
        slide: PptxSlide,
        title: str | None,
        text: str,
        img: Optional[list[ImageDTO]],
        settings: INITIAL_END | USUAL,
    ) -> None:
        self.title = title
        self.text = text
        self.img = img
        self.slide = slide
        self.setting = settings

    def make_slide(self) -> SlideDTO:
        num_pic = 0

        for shape in self.slide.shapes:
            if shape.has_text_frame:
                if shape.text == "TITLE" and self.title is not None:
                    self.__add_text_to_placeholder(
                        text_placeholder=shape,
                        text=self.title,
                        settings=self.setting.get("TITLE"),
                    )
                elif shape.text == "TEXT" and self.text is not None:
                    self.__add_text_to_placeholder(
                        text_placeholder=shape,
                        text=self.text,
                        settings=self.setting.get("TEXT"),
                    )
                elif (
                    shape.text == "PIC"
                    and self.img is not None
                    and len(self.img) > num_pic
                ):
                    self.__add_picture(
                        shape=shape,
                        num_pic=num_pic,
                        settings=self.setting["PICTURE"][num_pic],
                    )
                    num_pic += 1

        if self.setting.get("FOREGROUND IMAGE") is not None:
            self.__add_foreground_images(names=self.setting.get("FOREGROUND IMAGE"))
        if self.img:
            images = []
            for image_dto in self.img:
                image_info = ImageInfoDTO(
                    path=image_dto.path, description=image_dto.description
                )
                images.append(image_info)
        else:
            images = self.img

        return SlideDTO(title=self.title, text=self.text, images=images)

    def __add_text_to_placeholder(
        self,
        text_placeholder: Any,
        text: str,
        settings: dict[str, dict[str, str | int | bool]] = DEFAULT_TEXT_SETTINGS,
    ) -> None:
        text_placeholder.text_frame.clear()

        paragraph = text_placeholder.text_frame.paragraphs[0]
        run = paragraph.add_run()
        run.text = text
        font = run.font
        try:
            text_placeholder.text_frame.fit_text(
                font_family=settings.get("NAME"),
                max_size=settings.get("SIZE"),
                bold=settings.get("BOLD"),
                italic=settings.get("ITALIC"),
                font_file=None,
            )

            if settings.get("COLOR"):
                color: Any = settings["COLOR"]
                font.color.rgb = RGBColor(color[0], color[1], color[2])

        except OSError:
            ...  # to escape OSError("unsupported operating system")

    def __add_picture(self, shape: Any, num_pic: int, settings: dict[str, str]) -> None:
        if len(self.img) < num_pic:
            return None
        if self.img:
            pic: Image = self.img[num_pic].image

        # Удаляет и восстанавливает объект картинки
        shape.element.getparent().remove(shape.element)
        left = shape.left
        top = shape.top
        width = shape.width
        height = shape.height

        # Кoрректирует форму картинки для вставки в презентацию
        img_corrector = ImageCorrector(pillow_img=pic, setting=settings)
        pic = img_corrector.correct()

        # Получите байтовые данные изображения
        image_data = BytesIO()
        pic.save(image_data, format="PNG")
        image_data.seek(0)

        # Вставляем в призентацию
        self.slide.shapes.add_picture(image_data, left, top, width, height)

    def __add_foreground_images(self, names: list[str]) -> None:
        for shape in self.slide.shapes:
            if shape.has_text_frame:
                if shape.text in names:
                    # Удаляет и восстанавливает объект картинки
                    shape.element.getparent().remove(shape.element)
                    left = shape.left
                    top = shape.top
                    width = shape.width
                    height = shape.height

                    # Вставляем в призентацию
                    self.slide.shapes.add_picture(
                        os.path.join(path_to_foreground_image, shape.text),
                        left,
                        top,
                        width,
                        height,
                    )
