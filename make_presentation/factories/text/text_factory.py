from __future__ import annotations

from typing import TYPE_CHECKING

from make_presentation.api_models import (GigaChatRequest, OpenAIRequest,
                                          YandexRequest)
from make_presentation.config import (PROMPT_GENERATION_FROM_TEXT_ONE_STEP,
                                      PROMPT_ONE_STEP_GENERATION, TEXT_API)
from make_presentation.generator_models import TextInOneStep, TextInTwoSteps

from ..errors import InvalidFactoryNameError
from .text_module_enum import TextApiModuleEnum, TextGenModuleEnum

if TYPE_CHECKING:
    from make_presentation.api_models.interfaces import TextAPIProtocol

    from ...generator_models.interfaces import TextGeneratorProtocol


class TextFactory:
    def __init__(self) -> None:
        self.text_api = TEXT_API

    def get_api(self) -> TextAPIProtocol:
        if self.text_api == TextApiModuleEnum.GIGACHAT.value:
            text_request_model = GigaChatRequest()
        elif self.text_api == TextApiModuleEnum.YANDEXGPT.value:
            text_request_model = YandexRequest()
        elif self.text_api == TextApiModuleEnum.OPENAI.value:
            text_request_model = OpenAIRequest()
        else:
            raise InvalidFactoryNameError(
                f"Incorrect text api module in settings: {self.text_api}"
            )

        return text_request_model

    def get_generation_model(self, text_generation_model: str) -> TextGeneratorProtocol:
        if text_generation_model == TextGenModuleEnum.TEXTINTWOSTEP.value:
            generation_model: TextGeneratorProtocol = TextInTwoSteps()
        elif text_generation_model == TextGenModuleEnum.FROMTEXT.value:
            generation_model = TextInOneStep(
                prompt=PROMPT_GENERATION_FROM_TEXT_ONE_STEP,
                theme=False)
        elif text_generation_model == TextGenModuleEnum.TEXTINONESTEP.value:
            generation_model = TextInOneStep(
                prompt=PROMPT_ONE_STEP_GENERATION,
                theme=True)
        else:
            raise InvalidFactoryNameError(
                f"Incorrect text generation module in settings: {text_generation_model}"
            )

        return generation_model
