from __future__ import annotations

import re
from typing import TYPE_CHECKING

from make_presentation.config import (MAX_COUNT_OF_GENERATION,
                                      PROMPT_FOR_GENERATION_FROM_TEXT,
                                      PROMPT_FOR_THEME_GENERATION)
from make_presentation.DTO import TextDTO
from make_presentation.errors import (MaxCountGenerationError,
                                      TittleOrSlideTextNotGeneratedError)
from make_presentation.logger import logger
from make_presentation.templates.template_config import MAX_CHARS

from ..interfaces import TextGeneratorProtocol

if TYPE_CHECKING:
    from langchain.schema import AIMessage

    from ...api_models.interfaces import TextAPIProtocol


class GenerationFromText(TextGeneratorProtocol):
    """
    Класс для создания текстов для слайдов из переданного пользователем текста.
    """
    def __init__(self, prompt: str, theme: bool) -> None:
        self.prompt = prompt
        self.theme = theme

    async def create_text(
        self,
        slides_count: int,
        api: TextAPIProtocol,
        context: str,
        template: str
    ) -> TextDTO:
        """
        To create Text data transfer object with following parameters:
        titles, text of slide description, picture descriptions, full text
        """

        generated_theme = await self.__get_presentation_theme(text=context, text_api=api)
        if "Тема:" in generated_theme:
            presentation_theme = generated_theme.split("Тема:")[1].strip()
        else:
            presentation_theme = generated_theme

        list_of_excerpts = self.__split_text(text=context, template=template)

        titles_list: list[str] = []
        slides_text_list: list[str] = []
        pictures_description_list: list[str] = []

        for excerpts in list_of_excerpts:
            flag = 0
            while flag < MAX_COUNT_OF_GENERATION:
                logger.info(
                        f"{flag} text generation."
                    )

                slide_text = await self.__get_slide_text(
                    text_api=api, text=excerpts,
                    theme=presentation_theme,
                    template=template
                )

                title, text_list, picture_description = self.__get_slide_info(
                    text=slide_text
                )

                if not picture_description or not title or not text_list:
                    logger.info(
                        f"{api.__str__} could not create required text structure. Will try again."
                    )
                    flag += 1
                    continue
                else:
                    logger.info(
                        f"{api.__str__} has generated required text structure."
                    )
                    break
            else:
                raise MaxCountGenerationError(
                    "The number of text generation exceeds the permissible value."
                )

            titles_list.extend(title)
            slides_text_list.extend(text_list)
            pictures_description_list.extend(picture_description)

        all_text = self.__get_full_text(titles=titles_list, slides_text_list=slides_text_list)

        return TextDTO(
            titles=titles_list,
            slides_text_list=slides_text_list,
            picture_discription_list=pictures_description_list,
            fulltext=all_text,
            theme=presentation_theme
        )

    async def __get_slide_text(
        self, text_api: TextAPIProtocol, text: str, theme: str, template: str
    ) -> AIMessage:
        title_min_char = MAX_CHARS[template]["min"]["USUAL"]["TITLE"]
        title_max_char = MAX_CHARS[template]["max"]["USUAL"]["TITLE"]
        prompt = PROMPT_FOR_GENERATION_FROM_TEXT.replace("THEME", theme)
        prompt = PROMPT_FOR_GENERATION_FROM_TEXT.replace("MIN_CHAR", str(title_min_char))
        prompt = PROMPT_FOR_GENERATION_FROM_TEXT.replace("MAX_CHAR", str(title_max_char))
        return await text_api.request(text=(prompt + text))

    async def __get_presentation_theme(self, text_api: TextAPIProtocol, text: str) -> AIMessage:
        return await text_api.request(text=(PROMPT_FOR_THEME_GENERATION + text))

    def __split_text(self, text: str, template: str) -> list[str]:
        """
        Divide text into sentenses then create a list of excerpts
        of text with length <= max_length.
        """

        sentences = text.replace("\n", " ").split(". ")
        excerpts = []
        current_excerpt = ""

        max_length = MAX_CHARS[template]["max"]["USUAL"]["TEXT"]

        for sentence in sentences:
            if len(current_excerpt) + len(sentence) <= max_length:
                current_excerpt += sentence.strip() + " "
            else:
                excerpts.append(current_excerpt.strip())
                current_excerpt = sentence.strip() + " "

        if current_excerpt:
            excerpts.append(current_excerpt.strip())
        return excerpts

    def __get_slide_info(self, text: str) -> tuple[list[str], list[str], list[str]]:
        """
        Return a tuple of title, slide text and picture description.
        """

        title: list[str] = re.findall(r"(?i)Заголовок:(.+)", text)
        text_list: list[str] = re.findall(r"(?i)Текст:(.+)", text)
        pictures_list: list[str] = re.findall(r"(?i)Картинка:(.+)", text)

        if not pictures_list:
            picture_discription: list[str] = re.findall(r"(?i)Описание картинки:\s(.+)", text)
        else:
            picture_discription = pictures_list

        title = self.__clean_text(title)
        text_list = self.__clean_text(text_list)
        picture_discription = self.__clean_text(picture_discription)

        return title, text_list, picture_discription

    def __clean_text(self, text: list[str]) -> list[str]:
        result = []
        for item in text:
            text_item = item.strip().strip("*").strip("*").strip("*")
            text_item = item.strip('«').strip('»')
            result.append(text_item)
        return result

    def __get_full_text(self, titles: list[str], slides_text_list: list[str]) -> str:
        """
        Return a string with following information for each slide:
        Slide {number of a slide}, title of a slide, generated text of slide.
        """

        if len(titles) == 0 or len(slides_text_list) == 0:
            raise TittleOrSlideTextNotGeneratedError(
                "There are no generated titles or slides descriptions."
            )

        fulltext = ""
        for i in range(len(titles)):
            fulltext += f"Слайд {i + 1}:"
            if len(titles) > i:
                fulltext += titles[i] + "\n"
            if len(slides_text_list) > i:
                fulltext += slides_text_list[i] + "\n\n"

        return fulltext
