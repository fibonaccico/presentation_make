import asyncio
import base64
import json
import os
import time
from io import BytesIO
from typing import Optional
from uuid import UUID

import aiohttp
from dotenv import load_dotenv
from PIL import Image

from config.logger import get_logger
from make_presentation.api_models.interfaces import ImageAPIProtocol
from make_presentation.config import (BASE_KANDINSKY_URL, KANDINSKY_URLS,
                                      MAX_TIME_IMAGE_GENERATION)
from make_presentation.DTO import ImageDTO

from ..errors import BadRequestError, ImageGenerationFailedError, TimeOutError

logger = get_logger()

load_dotenv()


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)


class KandinskyAPI(ImageAPIProtocol):
    def __init__(self) -> None:
        self.base_url = BASE_KANDINSKY_URL
        self.urls = KANDINSKY_URLS
        self.AUTH_HEADERS = {
            "X-Key": f"Key {os.getenv('KANDINSKY_API_KEY')}",
            "X-Secret": f"Secret {os.getenv('KANDINSKY_SECRET_KEY')}",
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
                logger.info(f"Response after get model: = {response}")
                data = await response.json()
                logger.info(f"Kandinsky used model: = {data[1].get('version')}")
                return data[1]["id"]

    async def create_image(
        self,
        save_path: Optional[str],
        promt: str = "Cat",
        width_height="1024 1024",
        images: int = 1,
        model: Optional[int] = None,
        style: str = "DEFAULT",
        negative_prompt="",
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
        logger.warning("Start create image using Kandinsky")

        if model is None:
            model = await self.get_model()
        logger.warning(f"Kandinsky model is {model}")

        width, height = map(int, width_height.split(" "))
        params = {
            "type": "GENERATE",
            "numImages": images,
            "style": style,
            "width": width,
            "height": height,
            "generateParams": {"query": promt},
        }
        pipeline_id = str(model)

        data = aiohttp.FormData()
        data.add_field(
            "params",
            json.dumps(params),
            content_type="application/json",
        )

        data.add_field("pipeline_id", pipeline_id)

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=self.urls["run"], headers=self.AUTH_HEADERS, data=data
            ) as response:
                result = await response.json()

        if "error" in result:
            raise BadRequestError(f"Not found: data {result}. Cannot generate image - {promt}")

        uuid = result["uuid"]
        image_result = await self._check_status(uuid=uuid, max_time=max_time)
        image_data = BytesIO(image_result["data"].getvalue())
        image = Image.open(image_data).convert('RGB')

        if save_path:
            path = f"{save_path}/{uuid}.jpg"
            image.save(fp=path)
        else:
            path = None

        return ImageDTO(image=image, path=path, description=promt, style=style)

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
            url = self.urls["status"].replace("$uuid", uuid)
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url=url,
                    headers=self.AUTH_HEADERS,
                ) as resp:
                    if not resp.ok:
                        logger.info(
                            f"Response error: url = {url}"
                        )
                        continue
                    else:
                        result = await resp.json()
                    if result["status"] == "DONE":
                        if result["result"]["censored"]:
                            logger.info(f"CENSORED PICTURE: UUID = {uuid}")
                            return {
                                "data": BytesIO(base64.b64decode(result["result"]["files"][0])),
                            }
                        else:
                            logger.info(f"PICTURE HAS BEEN GENERATED: UUID = {uuid}")
                            return {
                                "data": BytesIO(base64.b64decode(result["result"]["files"][0])),
                            }
                    elif result["status"] == "FAIL":
                        logger.error(f"FATAL GENERATION PICTURE: UUID = {uuid}")
                        raise ImageGenerationFailedError(
                            "The image generation could not be completed."
                        )

            await asyncio.sleep(4)

        raise TimeOutError(f"Max allowed time is {max_time} seconds")
