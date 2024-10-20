from __future__ import annotations

from typing import TYPE_CHECKING

from make_presentation.api_models import GigaChatRequest, YandexRequest
from make_presentation.generator_models import (GenerationFromText,
                                                TextInTwoSteps)

from ..errors import InvalidFactoryNameError
from .text_module_enum import TextApiModuleEnum, TextGenModuleEnum

if TYPE_CHECKING:
    from make_presentation.api_models.interfaces import TextAPIProtocol

    from ...generator_models.interfaces import TextGeneratorProtocol


class TextFactory:
    def __init__(self, settings: dict[str, str]) -> None:
        self.settings = settings

    def get_api(self) -> TextAPIProtocol:
        text_api = self.settings["API"]
        if text_api == TextApiModuleEnum.GIGACHAT.value:
            text_request_model = GigaChatRequest()
        elif text_api == TextApiModuleEnum.YANDEXGPT.value:
            text_request_model = YandexRequest()
        else:
            raise InvalidFactoryNameError(
                f"Incorrect text api module in settings: {text_api}"
            )

        return text_request_model

    def get_generation_model(self) -> TextGeneratorProtocol:
        text_generation_model = self.settings["GENMODEL"]

        if text_generation_model == TextGenModuleEnum.TEXTINTWOSTEP.value:
            generation_model: TextGeneratorProtocol = TextInTwoSteps()
        elif text_generation_model == TextGenModuleEnum.FROMTEXT.value:
            generation_model = GenerationFromText()
        else:
            raise InvalidFactoryNameError(
                f"Incorrect text generation module in settings: {text_generation_model}"
            )

        return generation_model
