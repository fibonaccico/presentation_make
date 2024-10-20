from __future__ import annotations

import json
import os

import aiohttp
from dotenv import load_dotenv

from make_presentation.api_models.interfaces import TextAPIProtocol

load_dotenv()


class YandexRequest(TextAPIProtocol):
    async def request(
        self,
        text: str
    ) -> str | list[str | dict]:
        params = {
            "modelUri": f"gpt://{os.getenv('YANDEX_FOLDER_ID')}/yandexgpt-lite",
            "completionOptions": {
                "stream": False,
                "temperature": 0.6,
                "maxTokens": "2000"
            },
            "messages": [
                {
                    "role": "user",
                    "text": text
                }
            ]
        }
        headers = {
            "Authorization": f"Api-Key {os.getenv('YANDEX_API_KEY')}",
            "x-folder-id": os.getenv('YANDEX_FOLDER_ID')
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url="https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
                headers=headers,
                data=json.dumps(params)
            ) as response:
                res = await response.json()

        return res['result']['alternatives'][0]['message']['text']
