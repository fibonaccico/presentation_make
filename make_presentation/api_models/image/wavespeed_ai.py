import asyncio
import os
import uuid
from typing import Optional

import aiohttp
from aiohttp import ClientError, ClientResponseError, ClientSession
from dotenv import load_dotenv

from config.logger import get_logger
from make_presentation.api_models.interfaces import ImageAPIProtocol
from make_presentation.config import ADDITIONAL_PROMPT_FOR_IMAGE_GENERATION
from make_presentation.DTO import ImageDTO

logger = get_logger()
load_dotenv()


BASE_WAVESPEEDAI_URL = "https://api.wavespeed.ai/api/v3/"
WAVESPEEDAI_URLS: dict[str, str] = {
    "run": f"{BASE_WAVESPEEDAI_URL}wavespeed-ai/z-image/turbo",
}


class WaveSpeedAI(ImageAPIProtocol):
    def __init__(self) -> None:
        self.base_url = BASE_WAVESPEEDAI_URL
        self.urls = WAVESPEEDAI_URLS

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
        logger.warning("Start create image using WaveSpeedAI")

        async def safe_get(session: ClientSession, url: str) -> dict:
            max_retries = 5
            backoff_factor = 0.5
            retry_statuses = {429, 500, 502, 503, 504}

            for attempt in range(max_retries):
                try:
                    async with session.get(url, headers=headers, timeout=30.0) as response:
                        if response.status in retry_statuses:
                            response.raise_for_status()  # Вызовет ClientResponseError
                        
                        response.raise_for_status()  # Для всех остальных ошибок (например, 400, 401, 403, 404)
                        return await response.json()
                        
                except (ClientResponseError, ClientError) as e:
                    # Если это ошибка из списка ретраев и попытки не исчерпаны — ждем и повторяем
                    is_retryable = isinstance(e, ClientResponseError) and e.status in retry_statuses
                    is_network_error = not isinstance(e, ClientResponseError)  # Ошибки соединения
                    
                    if (is_retryable or is_network_error) and attempt < max_retries - 1:
                        sleep_time = backoff_factor * (2 ** attempt)
                        print(f"Запрос не удался ({e}). Повтор {attempt + 1}/{max_retries} через {sleep_time}с...")
                        await asyncio.sleep(sleep_time)
                        continue
                    raise  # Если попытки исчерпаны или ошибка критическая (401, 404) — пробрасываем выше

        # Внутренняя функция для бесконечного опроса (polling) статуса задачи
        async def poll_result(task_id: str, session: ClientSession):
            poll_interval = 2.0
            url = f"{self.base_url}/api/v3/predictions/{task_id}/result"
            
            while True:
                try:
                    body = await safe_get(session, url)
                    
                    if body.get("code") != 200:
                        logger.error(f'WaveSpeedAI error. status code - {body.get("code")}, message - {body.get("message", "Result query failed")}')
                        raise RuntimeError(body.get("message", "Result query failed"))
                    
                    data = body["data"]
                    
                    if data["status"] == "completed":
                        logger.info(f'WaveSpeedAI result. Status - {data["status"]}, data - [{data}]')
                        return data["outputs"]
                        
                    if data["status"] in {"failed", "cancelled", "timeout", "deleted"}:
                        logger.error(f'WaveSpeedAI error.  Status - {data["status"]}, data - [{data}]')
                        raise RuntimeError(data.get("error") or f"Task ended with {data['status']}")
                
                except Exception as e:
                    logger.error(f"Ошибка при опросе статуса: {e}. Следующая попытка через {poll_interval}с...")
                
                await asyncio.sleep(poll_interval)
                poll_interval = min(10.0, poll_interval + 1.0)


        width, height = map(int, width_height.split(" "))
        headers={
            "Authorization": f"Bearer {os.getenv('WAVESPEED_API_KEY')}",
            "Content-Type": "application/json"
        }

        data = {
            'prompt': promt + " /n" + ADDITIONAL_PROMPT_FOR_IMAGE_GENERATION,
            'size': f"{width}*{height}",
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.urls.get("run"),
                headers=headers,
                json=data,
                timeout=(10, 60),
            ) as response:
                response.raise_for_status()
                body = response.json()
                if body.get("code") != 200:
                    image_url = body['data']['urls']['get']
                    image_id = body['data']['id']
                    logger.info(f"WavaSpeedAI image generation. DATA: status - {body['data']['status']}, id - {image_id}, urls - {image_url}")
                else:
                    logger.error(f'WavaSpeedAI image generation. Error: {body.get("code")} - {body.get("message", "Task submission failed")}')

            timeout_seconds = max_time * 60

            try:
                outputs = await asyncio.wait_for(
                    poll_result(image_id, session),
                    timeout=float(timeout_seconds)
                )
            except asyncio.TimeoutError:
                logger.error(f"Timed out waiting for prediction {image_id} after {max_time} minutes")
                raise TimeoutError(f"Timed out waiting for prediction {image_id} after {max_time} minutes")

            # --- ШАГ 3: Возврат ImageDTO ---
            return ImageDTO(
                task_id=image_id,
                urls=outputs,
                status="completed"
            )


        #     async with session.get(image_url) as response:
        #         if response.status == 200:
        #             path = f"{save_path}/{uuid.uuid4()}.jpg"
        #             with open(path, 'wb') as file:
        #                 file.write(await response.read())
        #             logger.info(f'Изображение сохранено как {path}')
        #         else:
        #             logger.error(f'Ошибка при скачивании изображения: {response.status} - {await response.text()}')

        # return ImageDTO(image=image_url, path=path, description=promt, style=style)
