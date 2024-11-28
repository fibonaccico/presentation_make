from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, Optional

from make_presentation.config import get_prompt_result
from make_presentation.DTO import TextDTO
from make_presentation.errors import (InvalidTextNumberError,
                                      TittleOrSlideTextNotGeneratedError)

from ..interfaces import TextGeneratorProtocol

if TYPE_CHECKING:

    from make_presentation.api_models.interfaces import TextAPIProtocol


logger = logging.getLogger(__name__)


class TextInOneStep(TextGeneratorProtocol):
    """
    Класс для создания текста, создает макет который, выглядит как:

    Слайд {Номер слайда}
    Заголовок слайда:
    Подзаголовок 1:
    Описание 1:
    Подзаголовок 2:
    Описание 2:
    Подзаголовок 3:
    Описание 3:
    Картинка:
    """
    def __init__(self, prompt: str, theme: bool) -> None:
        self.prompt = prompt
        self.theme = theme

    async def create_text(
        self,
        slides_count: int,
        api: TextAPIProtocol,
        context: str,
        template: Optional[str] = None
    ) -> TextDTO:
        """
        To create Text data transfer object (TextTwoStepsDTO) with following parameters:
        titles, text of slide description, picture descriptions, full text
        """

        ai_answer = await self.__get_all_ai_answer(
            prompt=self.prompt,
            api=api,
            context=context,
            num_slide=slides_count
        )

        titles = self.__get_list_text(
            text=ai_answer,
            pattern=r"(?i)Заголовок слайда:(.+)",
            num_slides=slides_count
        )

        pictures = self.__get_list_text(
            text=ai_answer,
            pattern=r"(?i)Картинка:(.+)",
            num_slides=slides_count
        )

        subtitles_1 = self.__get_list_text(
            text=ai_answer,
            pattern=r"(?i)Подзаголовок 1:(.+)",
            num_slides=slides_count
        )

        subtitles_2 = self.__get_list_text(
            text=ai_answer,
            pattern=r"(?i)Подзаголовок 2:(.+)",
            num_slides=slides_count
        )

        subtitles_3 = self.__get_list_text(
            text=ai_answer,
            pattern=r"(?i)Подзаголовок 3:(.+)",
            num_slides=slides_count
        )

        slides_text_list = self.__get_slide_text(
            text=ai_answer,
            num_slides=slides_count
        )
        if not self.theme:
            presentation_theme = re.findall(
                r"(?i)Тема презентации:(.+)",
                ai_answer
            )[0]
        else:
            presentation_theme = context

        return TextDTO(
            titles=titles,
            slides_text_list=slides_text_list,
            picture_discription_list=pictures,
            subtitles_1=subtitles_1,
            subtitles_2=subtitles_2,
            subtitles_3=subtitles_3,
            fulltext=self.__get_full_text(
                titles=titles,
                subtitles_1=subtitles_1,
                subtitles_2=subtitles_2,
                subtitles_3=subtitles_3,
                slides_text_list=slides_text_list
                ),
            theme=presentation_theme
        )

    async def __get_all_ai_answer(
        self, prompt: str, api: TextAPIProtocol, context: str, num_slide: int
    ) -> str | list[str | dict]:

        res_prompt = get_prompt_result(
            context=context,
            num_slide=num_slide,
            prompt=prompt
        )
        ai_answer = await api.request(res_prompt)
        return ai_answer

    def __get_list_text(self, text: str,  pattern: str, num_slides: int) -> list[str]:
        text_list: list[str] = re.findall(pattern, text)
        new_text_list = []
        for item in text_list:
            new_text_list.append(self.__text_after_processing(item))

        if len(text_list) != num_slides:
            logging.error(f"Text items less than {num_slides}.")
            raise InvalidTextNumberError(f"Text items less than {num_slides}")
        return new_text_list

    def __get_slide_text(
        self,
        text: str,
        num_slides: int
    ) -> list[list[str]]:

        subtitle_text_1 = self.__get_list_text(
            text=text,
            pattern=r"(?i)Описание 1:(.+)",
            num_slides=num_slides
        )
        subtitle_text_2 = self.__get_list_text(
            text=text,
            pattern=r"(?i)Описание 2:(.+)",
            num_slides=num_slides
        )
        subtitle_text_3 = self.__get_list_text(
            text=text,
            pattern=r"(?i)Описание 3:(.+)",
            num_slides=num_slides
        )

        try:
            slides_text = []
            for slide in range(num_slides):
                slide_text = []
                slide_text.append(subtitle_text_1[slide])
                slide_text.append(subtitle_text_2[slide])
                slide_text.append(subtitle_text_3[slide])
                slides_text.append(slide_text)

        except IndexError:
            logging.error(f"Text items less than {num_slides}.")
            raise InvalidTextNumberError(f"Text items less than {num_slides}")

        return slides_text

    def __text_after_processing(self, text: str) -> str:
        text.strip(" ")
        text.strip('"')
        text.strip("'").strip('"').strip('«').strip('»')
        text.strip('*').strip('*').strip('*')
        return text

    def __get_full_text(
        self,
        titles: list[str],
        subtitles_1: list[str],
        subtitles_2: list[str],
        subtitles_3: list[str],
        slides_text_list: list[list[str]]
    ) -> str:
        """
        Return a string with following information for each slide:
        Slide {number of a slide}, title of a slide, generated text of slide.
        """

        if len(titles) == 0 or len(slides_text_list) == 0:
            logger.error(
                "There are no generated titles or slides descriptions."
            )
            raise TittleOrSlideTextNotGeneratedError(
                "There are no generated titles or slides descriptions."
            )

        fulltext = ""
        for i in range(len(titles)):
            fulltext += f"Слайд {i + 1}:"
            if len(titles) > i:
                fulltext += titles[i] + "\n"
            if len(subtitles_1) > i:
                fulltext += subtitles_1[i] + ""
                fulltext += slides_text_list[i][0] + "\n"
            if len(subtitles_2) > i:
                fulltext += subtitles_2[i] + ""
                fulltext += slides_text_list[i][1] + "\n"
            if len(subtitles_3) > i:
                fulltext += subtitles_3[i] + ""
                fulltext += slides_text_list[i][2] + "\n"
        return fulltext
