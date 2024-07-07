import asyncio
import base64
import json
import logging
import time
from io import BytesIO
from typing import Optional

import aiohttp
from PIL import Image

from make_presentation.api_models.interfaces import ImageAPIProtocol
from make_presentation.config import (BASE_KANDINSKY_URL, KANDINSKY_URLS,
                                      MAX_TIME_IMAGE_GENERATION)
from make_presentation.DTO import ImageDTO

from ..errors import BadRequestError, ImageGenerationFailedError, TimeOutError

logger = logging.getLogger(name=__name__)


class KandinskyAPI(ImageAPIProtocol):
    def __init__(self, api_key: str, secret_key: str) -> None:
        self.base_url = BASE_KANDINSKY_URL
        self.urls = KANDINSKY_URLS
        self.AUTH_HEADERS = {
            "X-Key": f"Key {api_key}",
            "X-Secret": f"Secret {secret_key}",
        }

    async def get_model(self) -> int:
        """
        Retriev the list of available models and select Kandinsky 3.0
        (currently this is the only model available for API connection)
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=self.urls["models"], headers=self.AUTH_HEADERS
            ) as response:
                data = await response.json()
                return data[0]["id"]

    async def create_image(
        self,
        save_path: str,
        promt: str = "Cat",
        width_height="1024 1024",
        negative_prompt: str = "",
        images: int = 1,
        model: Optional[int] = None,
        style: str = "DEFAULT",
        art_gpt: bool = False,
        max_time: int = MAX_TIME_IMAGE_GENERATION,
    ) -> ImageDTO:
        """
        The main function for image generation.
        Return image data transfer object.

        Arguments:
        style    - a style of generated image. You can select particular style
                   from get_styles() function;
        images   - the number of images You can only request at a time for the same request;
        model    - by default select Kandinsky 3.1 (currently this is the
                   only model available for API connection);
        max_time - max time generation max time before function returns error
        """

        if not model:
            model = await self.get_model()

        width, height = map(int, width_height.split(" "))

        params = {
            "type": "GENERATE",
            "numImages": images,
            "style": style,
            "width": width,
            "height": height,
            "censor": {"useGigaBeautificator": art_gpt},
            "generateParams": {"query": promt},
            "negativePromptDecoder": negative_prompt,
        }

        data = aiohttp.FormData()
        data.add_field(
            "params",
            json.dumps(params),
            content_type="application/json",
        )

        data.add_field("model_id", str(model))

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=self.urls["run"], headers=self.AUTH_HEADERS, data=data
            ) as response:
                result = await response.json()

        if "error" in result:
            raise BadRequestError(f"Not found: data {result}")

        uuid = result["uuid"]
        image_result = await self._check_status(uuid=uuid, max_time=max_time)
        image_data = BytesIO(image_result["data"].getvalue())
        path = f"{save_path}/{uuid}.png"
        image = Image.open(image_data)
        image.save(fp=path)

        return ImageDTO(image=image, path=path, description=promt)

    async def get_styles(self) -> list[dict[str, str]]:
        async with aiohttp.ClientSession() as session:
            async with session.get(url=self.urls["styles"]) as response:
                return await response.json()

    async def _check_status(self, uuid: str, max_time: int) -> dict[str, BytesIO]:
        """
        To check the status of image generation. When a task is done
        the function returns a dictionary where 'data' parameter is BytesIO object.

        Possible values of the status field:
        INITIAL- the request has been received, is in the queue for processing
        PROCESSING - the request is being processed
        DONE- task completed
        FAIL- the task could not be completed.

        """
        start_time = time.time()
        while time.time() - (start_time + max_time) < 0:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url=self.urls["status"].replace("$uuid", uuid),
                    headers=self.AUTH_HEADERS,
                ) as resp:
                    data = await resp.read()
                    result = json.loads(data)
                    if result["status"] == "DONE":
                        if result["censored"]:
                            logger.info(f"CENSORED PICTURE: UUID = {uuid}")
                            return {
                                "data": BytesIO(base64.b64decode(result["images"][0])),
                            }
                        else:
                            logger.info(f"PICTURE HAS BEEN GENERATED: UUID = {uuid}")
                            return {
                                "data": BytesIO(base64.b64decode(result["images"][0])),
                            }
                    elif result["status"] == "FAIL":
                        logger.error(f"FATAL GENERATION PICTURE: UUID = {uuid}")
                        raise ImageGenerationFailedError(
                            "The image generation could not be completed."
                        )

            await asyncio.sleep(4)

        raise TimeOutError(f"Max allowed time is {max_time} seconds")
