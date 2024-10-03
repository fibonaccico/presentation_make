from __future__ import annotations

from typing import TYPE_CHECKING

from make_presentation.api_models.image.kandinsky_api import KandinskyAPI

from ..errors import InvalidFactoryNameError
from .image_module_enum import ImgGenModuleEnum

if TYPE_CHECKING:
    from ...api_models.interfaces import ImageAPIProtocol


class ImgFactory:
    def __init__(self, settings: dict[str, str]) -> None:
        self.settings = settings

    def get_img_api(self) -> ImageAPIProtocol:
        if self.settings.get("API") == ImgGenModuleEnum.KANDINSKY.value:
            self.image_api: ImageAPIProtocol = KandinskyAPI()
        else:
            raise InvalidFactoryNameError(
                f"Incorrect data for the factory, for the image creation module: \
                {str(self.settings.get('API'))}"
            )

        return self.image_api
