from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, Optional

from make_presentation.config import (get_general_prompt_for_each_slide,
                                      get_subtitles_generation_prompt,
                                      get_titles_generation_prompt)
from make_presentation.DTO import TextDTO
from make_presentation.errors import (InvalidSubtitlesNumberError,
                                      InvalidTitlesNumberError,
                                      NoSlideTextError, NoSubtitlesError,
                                      TittleOrSlideTextNotGeneratedError)

from ..interfaces import TextGeneratorProtocol

if TYPE_CHECKING:
    from langchain_core.messages import BaseMessage

    from make_presentation.api_models.interfaces import TextAPIProtocol


logger = logging.getLogger(__name__)


class TextInTwoSteps(TextGeneratorProtocol):
    """
    Класс для создания текста, сперва создает макет который, выглядит как:

    Заголовок: {Текст заголовка}
    Описание: {Текст содержания слайда}
    Картинка: {Описание картинки}

    Затем для каждого слайда генерируется текст согласно сгенерированному ранее описанию.
    """

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

        titles_and_picture_descriptions = await self.__get_titles_and_picture_descriptions(
            api=api,
            theme=context,
            slides_count=slides_count
        )
        title_list, picture_discription_list = self.__split_text_into_titles_pictures(
            text=titles_and_picture_descriptions,
            slides_count=slides_count
        )

        subtitles_1, subtitles_2, subtitles_3 = await self.__get_subtitles(
            api=api,
            theme=context,
            titles=titles_and_picture_descriptions
        )

        if len(subtitles_1) < slides_count or (
            len(subtitles_1) < slides_count
        ) or len(subtitles_1) < slides_count:
            logger.error("Invalid number of generated subtitles.")
            raise InvalidSubtitlesNumberError("Invalid number of generated subtitles.")

        slides_text_list = await self.__get_list_of_slides_text(
            api=api,
            theme=context,
            titles=title_list,
            subtitles_1=subtitles_1,
            subtitles_2=subtitles_2,
            subtitles_3=subtitles_3
        )
        return TextDTO(
            titles=title_list,
            slides_text_list=slides_text_list,
            picture_discription_list=picture_discription_list,
            subtitles_1=subtitles_1,
            subtitles_2=subtitles_2,
            subtitles_3=subtitles_3,
            fulltext=self.__get_full_text(
                titles=title_list,
                subtitles_1=subtitles_1,
                subtitles_2=subtitles_2,
                subtitles_3=subtitles_3,
                slides_text_list=slides_text_list
                ),
            theme=context
        )

    async def __get_titles_and_picture_descriptions(
        self, api: TextAPIProtocol, theme: str, slides_count: int
    ) -> BaseMessage:
        """
        Return 'AIMessage' object with following content for each slide:
        title, picture description.
        """

        promt = get_titles_generation_prompt(
            theme=theme,
            count_sl=slides_count
        )

        titles_and_picture_descriptions = await api.request(promt)

        return titles_and_picture_descriptions

    async def __get_subtitles(
        self, api: TextAPIProtocol, theme: str, titles: str
    ) -> tuple[list[str], list[str], list[str]]:
        """
        Return lists of subtitles
        """

        promt = get_subtitles_generation_prompt(
            theme=theme,
            titles=titles
        )
        ai_answer = await api.request(text=promt)
        subtitles_1, subtitles_2, subtitles_3 = self.__split_text_into_subtitles_lists(
            text=ai_answer
        )
        return subtitles_1, subtitles_2, subtitles_3

    def __split_text_into_titles_pictures(
        self, text: str,  slides_count: int
    ) -> tuple[list[str], list[str]]:
        """
        Return a tuple of title lists and picture descriptions.
        """

        title_list: list[str] = re.findall(r"(?i)Заголовок:(.+)", text)
        new_title_list: list[str] = []
        for title in title_list:
            new_title_list.append(self.__text_after_processing(text=title))
        picture_discription_list: list[str] = re.findall(r"(?i)Картинка:(.+)", text)

        if len(title_list) != slides_count:
            logger.error(f"Titles number less than {slides_count}.")
            raise InvalidTitlesNumberError(f"Titles number less than {slides_count}")

        return new_title_list, picture_discription_list

    def __split_text_into_subtitles_lists(
        self,
        text: str
    ) -> tuple[list[str], list[str], list[str]]:
        """
        Return a tuple of subtitles lists.
        """

        subtitles_1: list[str] = re.findall(r"(?i)Подзаголовок 1:(.+)", text)
        new_subtitles_1 = []
        for item in subtitles_1:
            new_subtitles_1.append(self.__text_after_processing(item))
        subtitles_2: list[str] = re.findall(r"(?i)Подзаголовок 2:(.+)", text)
        new_subtitles_2 = []
        for item in subtitles_2:
            new_subtitles_2.append(self.__text_after_processing(item))
        subtitles_3: list[str] = re.findall(r"(?i)Подзаголовок 3:(.+)", text)
        new_subtitles_3 = []
        for item in subtitles_3:
            new_subtitles_3.append(self.__text_after_processing(item))

        if not any([new_subtitles_1, new_subtitles_2, new_subtitles_3]):
            logger.error("Subtitles have not been generated.")
            raise NoSubtitlesError("Subtitles have not been generated.")
        elif len(new_subtitles_1) < 3 or len(new_subtitles_2) < 3 or len(new_subtitles_3) < 3:
            logger.error("Number of subtitles is invalid.")
            raise InvalidSubtitlesNumberError("Number of subtitles is invalid.")

        return new_subtitles_1, new_subtitles_2, new_subtitles_3

    async def __get_list_of_slides_text(
        self,
        api: TextAPIProtocol,
        theme: str,
        titles: list[str],
        subtitles_1: list[str],
        subtitles_2: list[str],
        subtitles_3: list[str]
    ) -> list[list[str]]:
        """
        Generate a text for each slide and return a list of slides text.
        """
        list_of_slides_text = []
        for i in range(len(titles)):
            resp = await self.__get_slide_text(
                api=api,
                theme=theme,
                title=titles[i],
                num_slide=str(i + 1),
                subtitle_1=subtitles_1[i],
                subtitle_2=subtitles_2[i],
                subtitle_3=subtitles_3[i]
            )
            list_of_slides_text.append(resp)

        return list_of_slides_text

    async def __get_slide_text(
        self,
        api: TextAPIProtocol,
        theme: str,
        title: str,
        num_slide: str,
        subtitle_1: str,
        subtitle_2: str,
        subtitle_3: str
    ) -> list[str]:
        """
        Generate text for a particular slide.
        num_slide: str - a serial number of slide.
        """

        promt_for_slide = get_general_prompt_for_each_slide(
            theme=theme,
            num_slide=num_slide,
            title=title,
            subtitle_1=subtitle_1,
            subtitle_2=subtitle_2,
            subtitle_3=subtitle_3
        )

        generated_text_for_slide = await api.request(
            text=promt_for_slide)

        text = re.findall(r"(?i)Описание:(.+)", generated_text_for_slide)
        new_text = []
        for description in text:
            new_text.append(self.__text_after_processing(description))

        if new_text and len(new_text) == 3:
            return new_text
        else:
            logger.error(
                "A slide text has not been generated. There is no 'Описание:' in AI answer."
            )
            raise NoSlideTextError(
                "A slide text has not been generated. There is no 'Описание:' in AI answer."
            )

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
