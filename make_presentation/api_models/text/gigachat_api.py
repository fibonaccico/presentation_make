from __future__ import annotations

import asyncio
import logging
import os

from dotenv import load_dotenv
from langchain.chat_models.gigachat import GigaChat
from langchain.schema import HumanMessage

from make_presentation.api_models.interfaces import TextAPIProtocol
from make_presentation.config import (DEFAULT_REQUEST_NUMBER,
                                      DEFAULT_TEMPERATURE)

load_dotenv()
logger = logging.getLogger(__name__)


class GigaChatRequest(TextAPIProtocol):
    def __init__(self):
        self.api = GigaChat(
            credentials=os.getenv("GIGACHAT_API_KEY"),
            verify_ssl_certs=False
        )
        self.semaphore = asyncio.Semaphore(value=DEFAULT_REQUEST_NUMBER)
        self.api.temperature = DEFAULT_TEMPERATURE
        # self.history = []  # noqa E800

    async def request(
        self,
        text: str
    ) -> str | list[str | dict]:
        async with self.semaphore:
        # self.history.append(HumanMessage(content=text))   # noqa E800
        # response = await self.api.ainvoke(self.history)   # noqa E800
        # self.history.append(response)                     # noqa E800
            response = await self.api.ainvoke([HumanMessage(content=text)])

        return response.content
