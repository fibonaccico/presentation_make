import base64
import os
from io import BytesIO
from typing import Optional

from dotenv import load_dotenv
from openai import AsyncOpenAI
from PIL import Image

from config.logger import get_logger
from make_presentation.api_models.interfaces import ImageAPIProtocol
from make_presentation.DTO import ImageDTO

from ..errors import ImageGenerationFailedError

logger = get_logger()
load_dotenv()


BASE_FLUX_URL = "https://api.studio.nebius.com/v1/"
FLUX_URLS: dict[str, str] = {
    "run": f"{BASE_FLUX_URL}images/generations",
}


class FluxAPI(ImageAPIProtocol):
    def __init__(self) -> None:
        self.base_url = BASE_FLUX_URL
        self.urls = FLUX_URLS

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
        logger.warning("Start create image using Flux")

        width, height = map(int, width_height.split(" "))
        api_key = os.getenv("NEBIUS_API_KEY")

        if not api_key:
            logger.error("NEBIUS_API_KEY is not set.")
            return None

        client = AsyncOpenAI(
            base_url=self.base_url,
            api_key=api_key
        )
        try:
            completion = await client.images.generate(
                model="black-forest-labs/flux-schnell",
                prompt=promt,
                n=images,
                response_format="b64_json",
                quality='standard',
                extra_body={
                    "response_extension": "jpg",
                    "width": width,
                    "height": height,
                    "num_inference_steps": 1,
                    "seed": -1,
                    "negative_prompt": negative_prompt
                }
            )
        except Exception as err:
            logger.error(f"Image generation error. Reason: {err}")
            raise ImageGenerationFailedError(f"Image generation error: {err}. Cannot generate image - {promt}")

        result = completion.data[0]
        image_data = BytesIO(base64.b64decode(result.b64_json))
        image = Image.open(image_data).convert('RGB')

        if save_path:
            path = f"{save_path}/{result.get('id')}.jpg"
            image.save(fp=path)
        else:
            path = None

        logger.warning(f"Flux result {ImageDTO(image=image, path=path, description=promt, style=style)}")
        return ImageDTO(image=image, path=path, description=promt, style=style)
