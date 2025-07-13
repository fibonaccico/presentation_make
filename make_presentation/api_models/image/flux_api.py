# import asyncio
# import base64
# import json
import os
# import time
# from io import BytesIO
from typing import Optional

# from uuid import UUID
from openai import OpenAI

# import aiohttp
# from dotenv import load_dotenv
# from PIL import Image

# from config.logger import get_logger
# from make_presentation.api_models.interfaces import ImageAPIProtocol
# from make_presentation.config import (BASE_FLUX_URL, FLUX_URLS,
#                                       MAX_TIME_IMAGE_GENERATION)
# from make_presentation.DTO import ImageDTO

# from ..errors import BadRequestError, ImageGenerationFailedError, TimeOutError

# logger = get_logger()

# load_dotenv()


BASE_FLUX_URL = "https://api.studio.nebius.com/v1/"
FLUX_URLS: dict[str, str] = {
    "run": f"{BASE_FLUX_URL}images/generations",
}


class FluxAPI():
    def __init__(self) -> None:
        self.base_url = BASE_FLUX_URL
        self.urls = FLUX_URLS

    def create_image(
        self,
        # save_path: Optional[str],
        promt: str = "Cat",
        width_height="1024 1024",
        images: int = 1,
        model: Optional[int] = None,
        style: str = "DEFAULT",
        negative_prompt="",
        max_time: int = 2,
    ):
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

        width, height = map(int, width_height.split(" "))
        client = OpenAI(
            base_url=self.base_url,
            api_key=os.environ.get("NEBIUS_API_KEY"),
        )

        completion = client.images.generate(
            model="black-forest-labs/flux-schnell",
            prompt=promt,
            response_format="b64_json",
            extra_body={
                "response_extension": "jpeg",
                "width": width,
                "height": height,
                "num_inference_steps": 1,
                "seed": -1,
                "negative_prompt": negative_prompt
            }
        )

        print(completion.to_json())


d = FluxAPI()
d.create_image(promt="Котик в очках и ковбойской шляпе", width_height="1024 1024")