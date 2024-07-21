from __future__ import annotations

import os
import re
import time

import aspose.slides as slides
from aspose.pdf import Document, HtmlFragment, HtmlLoadOptions
from spire.presentation import Presentation as PresentationPPTX
from spire.presentation import *  # noqa F403
from spire.presentation.common import *  # noqa F403

from make_presentation.config import (DEFAULT_SETTINGS,
                                      ENDING_PRESENTATION_STATUS,
                                      ENDING_PRESENTATION_TEXT,
                                      MAX_TEXT_LENGTH,
                                      OPENING_PRESENTATION_THEME_TITLE)
from make_presentation.DTO import ImageInfoDTO, PresentationDTO, SlideDTO
from make_presentation.errors import (MaxTextLengthError,
                                      TextDoesNotExistError,
                                      ThemeDoesNotExistError)
from make_presentation.factories.text.text_module_enum import TextGenModuleEnum
from make_presentation.generator_models.pptx import PresentationTemplate
from make_presentation.image import ImagesAdapter
from make_presentation.text import TextAdapter


class Presentation:
    def __init__(
        self,
        text_generation_model: str,
        config_data: dict[str, dict[str, str]] = DEFAULT_SETTINGS,
        template: str = "minima",
        opening_prentation_theme_title: bool = OPENING_PRESENTATION_THEME_TITLE,
        ending_presentation_status: bool = ENDING_PRESENTATION_STATUS
    ) -> None:
        self.settings = config_data
        self.settings["TEXT"]["GENMODEL"] = text_generation_model

        if template:
            self.settings["PRESENTATION_SETTING"]["TEMPLATE_NAME"] = template

        self.opening_prentation_theme_title = opening_prentation_theme_title
        self.ending_presentation_status = ending_presentation_status

    async def make_presentation(
        self,
        save_path_for_images: str,
        text_api_key: str,
        image_api_key: str,
        image_secret_key: str,
        image_style: str = "DEFAULT",
        theme: str = '',
        text: str = ''
    ) -> PresentationDTO:
        """
        Main function to create a presentation data transfer object.
        """

        context = None
        if self.settings["TEXT"]["GENMODEL"] == TextGenModuleEnum.TEXTINTWOSTEP.value:
            if not theme:
                raise ThemeDoesNotExistError("There is no theme. You should input a theme.")
            context = theme

        if self.settings["TEXT"]["GENMODEL"] == TextGenModuleEnum.FROMTEXT.value:
            if not text:
                raise TextDoesNotExistError(
                    "There is no text to create a presentation. \
                    You should input a text because of you are going to generate a \
                    presentation from text."
                )
            elif len(text) > MAX_TEXT_LENGTH:
                raise MaxTextLengthError(f"The text length can't be more than {MAX_TEXT_LENGTH}")
            context = text

        text_dto = await TextAdapter(settings=self.settings)(
            context=context,
            api_key=text_api_key
        )

        list_of_image_dto = await ImagesAdapter(settings=self.settings)(
            pictures_descriptions=text_dto.picture_discription_list,
            save_path=save_path_for_images,
            image_style=image_style,
            api_key=image_api_key,
            secret_key=image_secret_key
        )

        list_of_image_info_dto: list[list[ImageInfoDTO]] = []

        for images_in_slide in list_of_image_dto:
            img_info_dto_list_in_slide = []
            for image_dto in images_in_slide:
                image_info = ImageInfoDTO(
                    path=image_dto.path, description=image_dto.description
                )
                img_info_dto_list_in_slide.append(image_info)

            list_of_image_info_dto.append(img_info_dto_list_in_slide)

        slide_dto_list: list[SlideDTO] = []

        slides_count = len(text_dto.titles)

        finish_title = None

        if self.opening_prentation_theme_title:
            text_dto.titles = [text_dto.theme] + text_dto.titles
            text_dto.slides_text_list = [""] + text_dto.slides_text_list
            list_of_image_info_dto = [None] + list_of_image_info_dto   # type: ignore
            slides_count += 1

        if self.ending_presentation_status:
            text_dto.titles = text_dto.titles + [ENDING_PRESENTATION_TEXT]
            text_dto.slides_text_list = text_dto.slides_text_list + [""]
            list_of_image_info_dto = list_of_image_info_dto + [None]   # type: ignore
            slides_count += 1
            finish_title = ENDING_PRESENTATION_TEXT
        else:
            finish_title = None

        for slide in range(slides_count):
            slide_dto = SlideDTO(
                number=slide,
                title=text_dto.titles[slide],
                text=text_dto.slides_text_list[slide],
                images=list_of_image_info_dto[slide],
            )
            slide_dto_list.append(slide_dto)

        return PresentationDTO(
            template_name=self.settings["PRESENTATION_SETTING"]["TEMPLATE_NAME"],
            theme=text_dto.theme,
            finish_title=finish_title,
            slides=slide_dto_list,
        )

    @staticmethod
    def save_from_html_file(
        self,
        file_name: str,
        format: str,
        save_path: str,
    ) -> str:
        """
        To save a presentation from html string to pdf and pptx formats.
        file_name: str - path to the file we have to convert
        save_path: str - a path to the folder to save a presentation
        """
        # TODO use aspose libraries, we have to buy a certificate to escape aspose titiles

        output_path = os.path.join(save_path, ("prs_" + str(time.time())))

        # create a folder
        os.makedirs(output_path, exist_ok=True)

        output_path = self._get_pdf_from_file(
            file=file_name,
            output=output_path
        )

        if format == "pptx":
            with slides.Presentation() as pres:
                pres.slides.add_from_pdf(output_path)
                pres.save(output_path.replace("pdf", "pptx"), slides.export.SaveFormat.PPTX)
            return output_path.replace("pdf", "pptx")
        return output_path

    @staticmethod
    def save_from_html_string(
        self,
        data: str,
        format: str,
        save_path: str,
    ) -> str:
        """
        To save a presentation from html string to pdf and pptx formats.
        save_path: str - a path to the folder to save a presentation
        """
        # TODO use aspose libraries, we have to buy a certificate to escape aspose titiles

        output_path = os.path.join(save_path, ("prs_" + str(time.time())))

        # create a folder
        os.makedirs(output_path, exist_ok=True)

        doc = Document()
        page = doc.pages.add()
        html_fr = HtmlFragment(data)
        page.paragraphs.add(html_fr)
        output_file_name = os.path.join(output_path, str(time.time()))
        doc.save(output_file_name + ".pdf")

        if format == "pptx":
            with slides.Presentation() as pres:
                pres.slides.add_from_pdf(output_file_name + ".pdf")
                pres.save(output_file_name + ".pptx", slides.export.SaveFormat.PPTX)
            return output_file_name + ".pptx"
        return output_file_name + ".pdf"

    @staticmethod
    def save(
        self,
        data: PresentationDTO,
        format: str,
        save_path: str,
    ) -> str:
        """
        To save a presentation from PresentationDTO to pdf and pptx formats.
        Return a presentation path.

        save_path: str - a path to the folder to save a presentation
        """
        presentation = PresentationTemplate()
        presentation.create_presentation(data=data)

        output_path = os.path.join(save_path, ("prs_" + str(time.time())))

        # create a folder
        os.makedirs(output_path, exist_ok=True)

        presentation_save_path = self._get_presentationn_save_path(
            save_path=output_path,
            theme=data.theme
        )

        presentation.save_presentation(
            file_save_path=presentation_save_path
        )
        if format == "pdf":
            pdf_presentation_path = self._get_pdf_from_file(
                file=presentation_save_path,
                output=presentation_save_path.replace("pptx", "pdf")
            )
            return pdf_presentation_path
        return presentation_save_path

    def _get_pdf_from_file(self, file: str, output: str) -> str:
        if file.split(".")[1] == "html":
            output = os.path.join(output, f"{time.time()}.pdf")
            options = HtmlLoadOptions()
            document = Document(file, options)
            document.save(output)
        else:
            # Create an object of Presentation class
            presentation = PresentationPPTX()
            # Load a PPT or PPTX file
            presentation.LoadFromFile(file)
            # Convert the presentation file to PDF and save it
            presentation.SaveToFile(output, FileFormat.PDF)         # noqa F405
            presentation.Dispose()

        return output

    def _get_presentationn_save_path(self, save_path: str, theme: str) -> str:
        text = re.sub(r'[!/:*\\?"<>|+.]', "", theme)
        text = re.sub(r"\s", "_", text)

        save_name = ""
        if len(text) < 80:
            save_name = text + "_" + str(time.time()) + ".pptx"
        else:
            save_name = "prs" + str(time.time()) + ".pptx"

        presentation_save_path = os.path.join(save_path, save_name)
        return presentation_save_path
