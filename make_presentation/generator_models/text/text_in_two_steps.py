from __future__ import annotations

import re
from typing import TYPE_CHECKING

from make_presentation.config import get_main_promt, get_second_promt_beta
from make_presentation.DTO import TextDTO
from make_presentation.errors import TittleOrSlideTextNotGeneratedError
from make_presentation.templates.template_config import MAX_CHARS

from ..interfaces import TextGeneratorProtocol

if TYPE_CHECKING:
    from langchain.schema import AIMessage

    from make_presentation.api_models.interfaces import TextAPIProtocol


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
        template: str
    ) -> TextDTO:
        """
        To create Text data transfer object with following parameters:
        titles, text of slide description, picture descriptions, full text
        """

        title_and_prompt = await self.__main_request(
            api=api, theme=context, slides_count=slides_count, template=template
        )
        title_list, picture_discription_list = self.__split_text(
            title_and_prompt.content
        )
        slides_text_list = await self.__get_list_of_slides_text(
            api=api, titles=title_list, title_and_prompt=title_and_prompt.content,
            template=template
        )
        return TextDTO(
            titles=title_list,
            slides_text_list=slides_text_list,
            picture_discription_list=picture_discription_list,
            fulltext=self.__get_full_text(title_list, slides_text_list),
            theme=context
        )

    async def __main_request(
        self, api: TextAPIProtocol, theme: str, slides_count: int, template: str
    ) -> AIMessage:
        """
        Return 'AIMessage' object with following content for each slide:
        title, slide description, picture description.
        """

        main_promt = get_main_promt(
            theme=theme,
            count_sl=slides_count,
            title_min_char=MAX_CHARS[template]["min"]["USUAL"]["TITLE"],
            title_max_char=MAX_CHARS[template]["max"]["USUAL"]["TITLE"],
        )

        title_and_prompt = await api.request(main_promt)
        return title_and_prompt

    def __split_text(self, text: str) -> tuple[list[str], list[str]]:
        """
        Return a tuple of lists of titles, slide descriptions and picture descriptions.
        """

        title_list: list[str] = re.findall(r"(?i)Заголовок:\s(.+)", text)
        new_title_list: list[str] = []
        for title in title_list:
            new_title_list.append(title.strip('"').strip('«').strip('»'))
        picture_discription_list: list[str] = re.findall(r"(?i)Картинка:\s(.+)", text)

        return new_title_list, picture_discription_list

    async def __get_list_of_slides_text(
        self, api: TextAPIProtocol, titles: list[str], title_and_prompt: str, template: str
    ) -> list[str]:
        """
        Generate a text for each slide and return a list of slides text.
        """

        list_of_slides_text = []

        for i in range(len(titles)):
            list_of_slides_text.append(
                await self.__get_slide_text(
                    api=api,
                    title_prompt=title_and_prompt,
                    num_slide=str(i + 1),
                    template=template
                )
            )

        return list_of_slides_text

    async def __get_slide_text(
        self, api: TextAPIProtocol, title_prompt: str, num_slide: str, template: str
    ) -> str:
        """
        Generate text for a particular slide.
        num_slide: str - a serial number of slide.
        """

        promt_for_slide = get_second_promt_beta(
            title_promt=title_prompt,
            num_slide=num_slide,
            text_min_char=MAX_CHARS[template]["min"]["USUAL"]["TEXT"],
            text_max_char=MAX_CHARS[template]["max"]["USUAL"]["TEXT"]
        )
        generated_text_for_slide = await api.request(
            text=promt_for_slide)
        return self.__text_after_processing(generated_text_for_slide.content)

    def __text_after_processing(self, text: str) -> str:
        text = text.strip('"')
        if text.startswith("Текст: "):
            text = text[7:].strip('"')
        elif "Текст: " in text:
            text = text.split("Текст: ")[1].strip('"')
        return text

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
        for i in range(max(len(titles), len(slides_text_list))):
            fulltext += f"Слайд {i + 1}:"
            if len(titles) > i:
                fulltext += titles[i] + "\n"
            if len(slides_text_list) > i:
                fulltext += slides_text_list[i] + "\n\n"

        return fulltext
