import os
import uuid
from typing import Optional

import aiohttp
from dotenv import load_dotenv

from config.logger import get_logger
from make_presentation.api_models.interfaces import ImageAPIProtocol
from make_presentation.config import NEGATIVE_PROMPT_SILICONFLOW
from make_presentation.DTO import ImageDTO

logger = get_logger()
load_dotenv()


BASE_SILICONFLOW_URL = "https://api.siliconflow.com/v1/"
SILICONFLOW_URLS: dict[str, str] = {
    "run": f"{BASE_SILICONFLOW_URL}images/generations",
}


class SiliconflowAPI(ImageAPIProtocol):
    def __init__(self) -> None:
        self.base_url = BASE_SILICONFLOW_URL
        self.urls = SILICONFLOW_URLS

    async def create_image(
        self,
        save_path: Optional[str],
        promt: str = "Cat",
        width_height: str = "1024 1024",
        images: int = 1,
        model: Optional[int] = None,
        style: str = "DEFAULT",
        negative_prompt="",
        max_time: int = 2
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
        logger.warning("Start create image using Siliconflow")

        width, height = map(int, width_height.split(" "))
        api_key = os.getenv("SILICONFLOW_TOKEN")

        if not api_key:
            logger.error("SILICONFLOW_TOKEN is not set.")
            return None

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        }

        data = {
            'model': 'Tongyi-MAI/Z-Image-Turbo',
            'prompt': promt + " /n" + NEGATIVE_PROMPT_SILICONFLOW,
            # 'negative_prompt': NEGATIVE_PROMPT_SILICONFLOW,
            'image_size': f"{width}x{height}",
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.urls.get("run"),
                headers=headers,
                json=data
            ) as response:
                if response.status == 200:
                    response_json = await response.json()
                    image_url = response_json['images'][0]['url']
                else:
                    logger.error(f'Error: {response.status} - {await response.text()}')

            async with session.get(image_url) as response:
                if response.status == 200:
                    path = f"{save_path}/{uuid.uuid4()}.jpg"
                    with open(path, 'wb') as file:
                        file.write(await response.read())
                    logger.info(f'Изображение сохранено как {path}')
                else:
                    logger.error(f'Ошибка при скачивании изображения: {response.status} - {await response.text()}')

        return ImageDTO(image=image_url, path=path, description=promt, style=style)
