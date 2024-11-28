from __future__ import annotations

from typing import TYPE_CHECKING

from make_presentation.api_models.image.kandinsky_api import KandinskyAPI
from make_presentation.config import IMAGE_API

from ..errors import InvalidFactoryNameError
from .image_module_enum import ImgGenModuleEnum

if TYPE_CHECKING:
    from ...api_models.interfaces import ImageAPIProtocol


class ImgFactory:
    def __init__(self) -> None:
        self.image_api = IMAGE_API

    def get_img_api(self) -> ImageAPIProtocol:
        if self.image_api == ImgGenModuleEnum.KANDINSKY.value:
            api: ImageAPIProtocol = KandinskyAPI()
        else:
            raise InvalidFactoryNameError(
                f"Incorrect data for the factory, for the image creation module: \
                {str(self.image_api)}"
            )

        return api
