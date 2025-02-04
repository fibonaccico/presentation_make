from __future__ import annotations

import math
import os
from io import BytesIO
from typing import TYPE_CHECKING, Any

from PIL import Image
from pptx.dml.color import RGBColor

from make_presentation.config import (DEFAULT_TEXT_FONT,
                                      DEFAULT_TEXT_FONT_SETTINGS,
                                      DEFAULT_TEXT_SIZE, SCALING_FACTOR,
                                      path_to_fonts, path_to_foreground_image)
from make_presentation.DTO import ImageDTO, ImageInfoDTO
from make_presentation.errors import FontDoesNotExistError, PicturesNumberError
from make_presentation.logger import logger

from .image_corrector import ImageCorrector

if TYPE_CHECKING:
    from pptx.slide import Slide as PptxSlide


class Slide:
    def __init__(
        self,
        slide: PptxSlide,
        title: str,
        text: list[str],
        subtitle_1: str | None,
        subtitle_2: str | None,
        subtitle_3: str | None,
        img: list[ImageInfoDTO] | None | list[ImageDTO],
        slide_type: str,
        slide_number: int,
        text_font: dict[str, dict[str, str]] | None,
        text_font_settings: dict[str, dict[str, dict[str, bool]]] | None,
        text_font_size: dict[str, dict[str, int]] | None,
        text_color: dict[str, dict[str, list[int]]] | None,
        pictures_setting: list[dict[str, str]] | None,
        foreground_pictures_setting: list[str] | None,
        max_chars: dict[str, dict[str, int]]
    ) -> None:
        self.title = title
        self.text = text
        self.subtitle_1 = subtitle_1
        self.subtitle_2 = subtitle_2
        self.subtitle_3 = subtitle_3
        self.img = img
        self.slide = slide
        self.slide_type = slide_type
        self.slide_number = slide_number
        self.text_font = text_font
        self.text_font_settings = text_font_settings
        self.text_font_size = text_font_size
        self.text_color = text_color
        self.pictures_setting = pictures_setting
        self.foreground_pictures_setting = foreground_pictures_setting
        self.max_chars = max_chars

    def make_slide(self) -> None:
        num_pic = 0

        for shape in self.slide.shapes:
            if shape.has_text_frame:
                if shape.text == "TITLE" and self.title is not None:
                    text_color_slide_type = (
                        self.text_color.get(self.slide_type)
                        if self.text_color else None
                    )
                    self.__add_text_to_placeholder(
                        text_placeholder=shape,
                        text=self.title,
                        text_font=(
                            self.text_font[self.slide_type]["TITLE"]
                            if self.text_font else DEFAULT_TEXT_FONT
                        ),
                        text_font_settings=(
                            self.text_font_settings[self.slide_type]["TITLE"]
                            if self.text_font_settings else DEFAULT_TEXT_FONT_SETTINGS
                        ),
                        text_font_size=(
                            self.text_font_size[self.slide_type]["TITLE"]
                            if self.text_font_size else DEFAULT_TEXT_SIZE
                        ),
                        text_color=(
                            self.text_color[self.slide_type]["TITLE"]
                            if self.text_color and text_color_slide_type else None
                        ),
                        max_chars=self.max_chars[self.slide_type]["TITLE"]
                    )
                elif "TEXT" in shape.text and self.text is not None:
                    text_color_slide_type = (
                        self.text_color.get(self.slide_type)
                        if self.text_color else None
                    )
                    shape_text = shape.text
                    if self.subtitle_1 or self.subtitle_2 or self.subtitle_3:
                        text_number = int(shape_text[-1])
                        text_for_slide = self.text[text_number - 1]
                    else:
                        text_for_slide = self.text

                    self.__add_text_to_placeholder(
                        text_placeholder=shape,
                        text=text_for_slide,
                        text_font=(
                            self.text_font[self.slide_type]["TEXT"]
                            if self.text_font else DEFAULT_TEXT_FONT
                        ),
                        text_font_settings=(
                            self.text_font_settings[self.slide_type]["TEXT"]
                            if self.text_font_settings else DEFAULT_TEXT_FONT_SETTINGS
                        ),
                        text_font_size=(
                            self.text_font_size[self.slide_type]["TEXT"]
                            if self.text_font_size else DEFAULT_TEXT_SIZE
                        ),
                        text_color=(
                            self.text_color[self.slide_type]["TEXT"]
                            if self.text_color and text_color_slide_type else None
                        ),
                        max_chars=self.max_chars[self.slide_type]["TEXT"]
                    )

                elif "SUBTITLE" in shape.text and self.text is not None:
                    text_color_slide_type = (
                        self.text_color.get(self.slide_type)
                        if self.text_color else None
                    )
                    shape_text = shape.text
                    subtitle_number = int(shape_text[-1])
                    if subtitle_number == 1:
                        subtitle = self.subtitle_1
                    elif subtitle_number == 2:
                        subtitle = self.subtitle_2
                    else:
                        subtitle = self.subtitle_3
                    self.__add_text_to_placeholder(
                        text_placeholder=shape,
                        text=subtitle,
                        text_font=(
                            self.text_font[self.slide_type]["SUBTITLE"]
                            if self.text_font else DEFAULT_TEXT_FONT
                        ),
                        text_font_settings=(
                            self.text_font_settings[self.slide_type]["SUBTITLE"]
                            if self.text_font_settings else DEFAULT_TEXT_FONT_SETTINGS
                        ),
                        text_font_size=(
                            self.text_font_size[self.slide_type]["SUBTITLE"]
                            if self.text_font_size else DEFAULT_TEXT_SIZE
                        ),
                        text_color=(
                            self.text_color[self.slide_type]["SUBTITLE"]
                            if self.text_color and text_color_slide_type else None
                        ),
                        max_chars=self.max_chars[self.slide_type]["SUBTITLE"]
                    )

                elif (
                    shape.text == "PIC"
                    and self.img is not None
                    and len(self.img) > num_pic
                    and self.pictures_setting is not None
                ):
                    self.__add_picture(
                        shape=shape,
                        num_pic=num_pic,
                        settings=self.pictures_setting[num_pic],
                    )
                    num_pic += 1

        if self.foreground_pictures_setting is not None:
            self.__add_foreground_images(names=self.foreground_pictures_setting)

    def __calculate_font_size(
        self,
        text: str,
        max_chars: int,
        base_font_size: int,
        scaling_factor: float = SCALING_FACTOR
    ) -> int:
        font_size = base_font_size
        if len(text) > max_chars:
            # Вычисляем новый размер шрифта с использованием логарифмической функции
            font_size = base_font_size * (1 - scaling_factor * math.log(len(text) / max_chars))
        return math.floor(font_size)

    def __add_text_to_placeholder(
        self,
        text_placeholder: Any,
        text: str,
        text_font: str,
        text_font_settings: dict[str, bool],
        text_font_size: int,
        text_color: list[int] | None,
        max_chars: int
    ) -> None:
        """
        Add text into a shape with font settings.

        :param text_placeholder: text box.
        :param text: text for adding.
        :param text_font: a font name.
        :param text_font_settings: font settings (bold, italic).
        :param text_font_size: font size.
        :param text_color: text color in RGB format.
        :param max_chars: max number of characters
        """

        text_placeholder.text_frame.clear()

        paragraph = text_placeholder.text_frame.paragraphs[0]
        run = paragraph.add_run()
        run.text = text
        font = run.font

        font_size = self.__calculate_font_size(
            text=text,
            max_chars=max_chars,
            base_font_size=text_font_size
        )

        try:
            if text_color:
                font.color.rgb = RGBColor(*text_color)

            text_placeholder.text_frame.fit_text(
                font_family=text_font,
                max_size=font_size,
                bold=text_font_settings.get("BOLD", False),
                italic=text_font_settings.get("ITALIC", False),
                font_file=os.path.join(path_to_fonts, f"{text_font}.ttf")
            )
        except OSError:
            logger.error("Could not set text fonts because of unsuppored OS.")
            raise FontDoesNotExistError("There is no font file.")
        except TypeError:
            logger.error("Could not fit text because of litle text frame.")

    def __add_picture(self, shape: Any, num_pic: int, settings: dict[str, str]) -> None:
        if self.img:
            if len(self.img) < num_pic:
                logger.error("Wrong picteres number.")
                raise PicturesNumberError("Wrong picteres number.")
            if self.img[num_pic].path:
                pic = Image.open(self.img[num_pic].path)
            else:
                pic = self.img[num_pic].image

        # Удаляет и восстанавливает объект картинки
        shape.element.getparent().remove(shape.element)
        left = shape.left
        top = shape.top
        width = shape.width
        height = shape.height

        if pic:
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
