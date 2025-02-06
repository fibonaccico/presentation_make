from __future__ import annotations

import os
from typing import TypeVar

import fitz
from pptx import Presentation as PresentationPPTX

from config.logger import get_logger
from make_presentation.config import path_to_template
from make_presentation.converters import (convert_pdf_to_pptx,
                                          convert_pptx_to_pdf)
from make_presentation.DTO import PresentationDTO
from make_presentation.errors import TemplateConfigDoesNotExistError
from make_presentation.templates.get_settings import (
    get_slides_foreground_pictures_setting, get_slides_pictures_setting)
from make_presentation.templates.template_config import (MAX_CHARS, TEXT_COLOR,
                                                         TEXT_FONT,
                                                         TEXT_FONT_SETTINGS,
                                                         TEXT_FONT_SIZE,
                                                         USUAL_PICTURES)

from .slide import Slide

logger = get_logger()

T = TypeVar('T')


class PresentationTemplate:
    """
    Создаёт pptx файл из шаблона
    """

    def _get_presentation_template(
        self,
        template_name: str,
        slides_count: int,
        save_path: str
    ) -> T:
        """
        To create presentation object from existing presentation template.
        """

        search_template = os.path.join(
            path_to_template,
            template_name,
            f"_{slides_count}.pptx",
        )
        presentation: T = PresentationPPTX(search_template)
        logger.info(f"A presentation template has been created. {search_template}")

        return presentation

    def _create_presentation_template(
        self,
        template_name: str,
        slides_count: int,
        save_path: str
    ) -> str:
        '''
        Not implemented now!!!!!
        '''

        slides_list = []

        path_to_temp = os.path.join(path_to_template, template_name)

        slides_list.append(convert_pptx_to_pdf(
            file=os.path.join(path_to_temp, "start.pptx"),
            output=os.path.join(path_to_temp, "start.pdf")
        ))

        types_of_slides = USUAL_PICTURES.get(template_name)
        usual_slides_count = slides_count - 2
        if types_of_slides is not None:
            for i in range(usual_slides_count):
                slides_list.append(convert_pptx_to_pdf(
                    file=os.path.join(path_to_temp, f"{i % len(types_of_slides)}.pptx"),
                    output=os.path.join(path_to_temp, f"{i % len(types_of_slides)}.pdf")
                ))
        else:
            raise TemplateConfigDoesNotExistError(
                f"There are no configs for the template {template_name}."
            )

        slides_list.append(convert_pptx_to_pdf(
            file=os.path.join(path_to_temp, "end.pptx"),
            output=os.path.join(path_to_temp, "end.pdf")
        ))

        template_pdf = self._merge_pdf_files(
            files=slides_list,
            output_file_path=os.path.join(save_path, f"_{slides_count}_template.pdf")
        )

        result_template = convert_pdf_to_pptx(
            file=template_pdf,
            save_path=os.path.join(save_path, f"_{slides_count}_template.pptx")
        )

        return result_template

    def _merge_pdf_files(self, files: list[str], output_file_path: str) -> str:
        '''
        Not implemented now!!!!!
        '''

        result = fitz.open()
        for pdf in files:
            with fitz.open(pdf) as current_file:
                result.insert_pdf(current_file)
        result.save(output_file_path)
        return output_file_path

    def create_presentation(self, data: PresentationDTO, save_path: str) -> None:
        """
        To create presentation based on a particular template.
        """
        number_of_slides = len(data.slides)
        self.presentation = self._get_presentation_template(
            template_name=data.template_name,
            slides_count=number_of_slides,
            save_path=save_path
        )
        for slide in data.slides:
            if slide.number == 0:
                slide_type = "INITIAL"
            elif slide.number == number_of_slides - 1:
                slide_type = "END"
            else:
                slide_type = "USUAL"
            pictures_setting = get_slides_pictures_setting(
                template_name=data.template_name,
                num_slides=number_of_slides,
            )

            foreground_pictures_setting = get_slides_foreground_pictures_setting(
                template_name=data.template_name,
                num_slides=number_of_slides,
            )

            slide_in_pres = Slide(
                slide=self.presentation.slides[slide.number],
                title=slide.title,
                text=slide.text,
                subtitle_1=slide.subtitle_1,
                subtitle_2=slide.subtitle_2,
                subtitle_3=slide.subtitle_3,
                img=slide.images,
                slide_number=slide.number,
                slide_type=slide_type,
                text_font=TEXT_FONT.get(data.template_name),
                text_font_settings=TEXT_FONT_SETTINGS.get(data.template_name),
                text_font_size=TEXT_FONT_SIZE.get(data.template_name),
                text_color=TEXT_COLOR.get(data.template_name),
                pictures_setting=(
                    pictures_setting[slide.number - 1]
                    if slide_type == "USUAL" else None
                ),
                foreground_pictures_setting=(
                    foreground_pictures_setting[slide.number - 1]
                    if foreground_pictures_setting and slide_type == "USUAL" else None
                ),
                max_chars=MAX_CHARS[data.template_name]["max"]
            )

            slide_in_pres.make_slide()

        logger.info(f"A presentation {data.theme} has been created.")

    def save_presentation(self, file_save_path: str) -> None:
        self.presentation.save(file_save_path)
        logger.info(f"A presentation has been saved into {file_save_path}.")
