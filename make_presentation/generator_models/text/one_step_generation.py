from __future__ import annotations

import json
from typing import TYPE_CHECKING, Optional

from config.logger import get_logger
from make_presentation.api_models.text.openai_api import ForbiddenContent
from make_presentation.config import (GENERATION_LANGUAGES,
                                      MAX_COUNT_OF_GENERATION,
                                      get_prompt_result)
from make_presentation.DTO import TextDTO
from make_presentation.errors import (InvalidTextNumberError,
                                      MaxCountGenerationError,
                                      MaxNumberOfSlidesExceededError,
                                      TittleOrSlideTextNotGeneratedError)

from ..interfaces import TextGeneratorProtocol

if TYPE_CHECKING:
    from make_presentation.api_models.interfaces import TextAPIProtocol


logger = get_logger()


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
    def __init__(self, prompt: str, theme: str | None) -> None:
        self.prompt = prompt
        self.theme = theme

    async def create_text(
        self,
        slides_count: Optional[int],
        api: TextAPIProtocol,
        context: str,
        language: str,
        template: Optional[str] = None
    ) -> TextDTO:
        """
        To create Text data transfer object (TextDTO) with following parameters:
        titles, text of slide description, picture descriptions, full text
        """
        flag = 1
        while flag <= MAX_COUNT_OF_GENERATION:
            logger.debug(f"{flag} attempt of generation.")
            try:
                ai_answer = await self.__get_all_ai_answer(
                    prompt=self.prompt,
                    api=api,
                    context=context,
                    num_slide=slides_count,
                    language=GENERATION_LANGUAGES.get(language, "Русский")
                )
                ai_text_dict = json.loads(ai_answer)

                titles = []
                pictures = []
                subtitles_1 = []
                subtitles_2 = []
                subtitles_3 = []
                slides_text_list = []
                for slide in ai_text_dict.get("slides"):
                    for slide_data in slide.values():
                        slide_discribtions = []
                        titles.append(slide_data.get("tittle", ""))
                        pictures.append(slide_data.get("picture", ""))
                        subtitles_1.append(slide_data.get("subtittle_1", ""))
                        subtitles_2.append(slide_data.get("subtittle_2", ""))
                        subtitles_3.append(slide_data.get("subtittle_3", ""))
                        slide_discribtions.append(slide_data.get("discribtion_1", ""))
                        slide_discribtions.append(slide_data.get("discribtion_2", ""))
                        slide_discribtions.append(slide_data.get("discribtion_3", ""))
                        slides_text_list.append(slide_discribtions)

                if titles is None:
                    logger.error(f"Titiles items: [{titles}] less than {slides_count}.")
                    raise InvalidTextNumberError(f"Text items less than {slides_count}")
                if slides_count and len(titles) > slides_count:
                    logger.error(f"Titles items: [{titles}] more than {slides_count}.")
                    raise MaxNumberOfSlidesExceededError(f"AI generated {len(titles)} items of titles. It is more than needed {slides_count}.")

                if pictures is None:
                    logger.error(f"Pictures items: [{pictures}] less than {slides_count}.")
                    raise InvalidTextNumberError(f"Pictures items less than {slides_count}")
                if slides_count and len(pictures) > slides_count:
                    logger.error(f"Pictures items: [{pictures}] more than {slides_count}.")
                    raise MaxNumberOfSlidesExceededError(f"AI generated {len(pictures)} items of Pictures. It is more than needed {slides_count}.")

                if subtitles_1 is None:
                    logger.error(f"subtitles_1 items: [{subtitles_1}] is empty.")
                    raise InvalidTextNumberError("subtitles_1 items is empty")
                if slides_count and len(subtitles_1) > slides_count:
                    logger.error(f"subtitles_1 items: [{subtitles_1}] more than {slides_count}.")
                    raise MaxNumberOfSlidesExceededError(f"AI generated {len(subtitles_1)} items of subtitles_1. It is more than needed {slides_count}.")

                if subtitles_2 is None:
                    logger.error(f"subtitles_2 items: [{subtitles_2}] is empty.")
                    raise InvalidTextNumberError("subtitles_2 items is empty}")
                if slides_count and len(subtitles_2) > slides_count:
                    logger.error(f"subtitles_2 items: [{subtitles_2}] more than {slides_count}.")
                    raise MaxNumberOfSlidesExceededError(f"AI generated {len(subtitles_2)} items of subtitles_2. It is more than needed {slides_count}.")

                if subtitles_3 is None:
                    logger.error(f"subtitles_3 items: [{subtitles_3}] is empty.")
                    raise InvalidTextNumberError("subtitles_3 items is empty.")
                if slides_count and len(subtitles_3) > slides_count:
                    logger.error(f"subtitles_3 items: [{subtitles_3}] more than {slides_count}.")
                    raise MaxNumberOfSlidesExceededError(f"AI generated {len(subtitles_3)} items of subtitles_3. It is more than needed {slides_count}.")

                if not self.theme:
                    presentation_theme = ai_text_dict.get("theme")

                else:
                    presentation_theme = context
                break
            except ForbiddenContent as err:
                logger.error(f"Generation fail. Reason: [{err}]")
                raise ForbiddenContent(f"{err}")
            except Exception as error:
                logger.error(f"Generation fail. Reason: [{error}]")
                flag += 1

        else:
            logger.error(f"The number of text generation exceeds the permissible value - {MAX_COUNT_OF_GENERATION}.")
            raise MaxCountGenerationError(
                "The number of text generation exceeds the permissible value."
            )

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
        self, prompt: str, api: TextAPIProtocol, context: str, num_slide: int | None,
        language: str
    ) -> str | list[str | dict]:

        res_prompt = get_prompt_result(
            context=context,
            num_slide=num_slide,
            prompt=prompt,
            language=language
        )
        ai_answer = await api.request(res_prompt)
        logger.debug(f"{ai_answer}")
        return ai_answer

    def __get_full_text(
        self,
        titles: list[str],
        subtitles_1: list[str] | None,
        subtitles_2: list[str] | None,
        subtitles_3: list[str] | None,
        slides_text_list: list[list[str]] | list[str]
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
            if subtitles_1 and len(subtitles_1) > i:
                fulltext += subtitles_1[i] + ""
                fulltext += slides_text_list[i][0] + "\n"
            if subtitles_2 and len(subtitles_2) > i:
                fulltext += subtitles_2[i] + ""
                fulltext += slides_text_list[i][1] + "\n"
            if subtitles_3 and len(subtitles_3) > i:
                fulltext += subtitles_3[i] + ""
                fulltext += slides_text_list[i][2] + "\n"
            else:
                fulltext += slides_text_list[i] + "\n"

        return fulltext
