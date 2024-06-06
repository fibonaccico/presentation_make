from __future__ import annotations

from typing import TYPE_CHECKING, Union

from api_models import GigaChatRequest
from generator_models import TextInTwoSteps

from ..errors import InvalidFactoryNameError
from .text_module_enum import TextApiModuleEnum, TextGenModuleEnum

if TYPE_CHECKING:
    from api_models.interfaces import TextAPIProtocol
    from generator_models.interfaces import TextGeneratorProtocol


class TextFactory:
    def __init__(self, settings: dict[str, Union[str, bool]]) -> None:
        self.text_generation_model = None
        self.settings = settings

    def get_api(self) -> TextAPIProtocol:
        text_api = self.settings.get("API")

        if text_api == TextApiModuleEnum.GIGACHAT.value:
            text_request_model = GigaChatRequest()
        else:
            raise InvalidFactoryNameError(
                f"Incorrect text api module in settings: {text_api}"
            )

        return text_request_model

    def get_generation_model(self) -> TextGeneratorProtocol:
        text_generation_model = self.settings.get("GENMODEL")

        if text_generation_model == TextGenModuleEnum.TEXTINTWOSTEP.value:
            text_generation_model: TextGeneratorProtocol = TextInTwoSteps()
        else:
            raise InvalidFactoryNameError(
                f"Incorrect text generation module in settings: {text_generation_model}"
            )

        return text_generation_model
