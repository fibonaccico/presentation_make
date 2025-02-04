from __future__ import annotations

import asyncio
import os

from dotenv import load_dotenv
from langchain.chat_models.gigachat import GigaChat
from langchain.schema import HumanMessage

from make_presentation.api_models.errors import BlacklistError
from make_presentation.api_models.interfaces import TextAPIProtocol
from make_presentation.config import (DEFAULT_REQUEST_NUMBER,
                                      DEFAULT_TEMPERATURE)
from make_presentation.logger import logger

load_dotenv()


class GigaChatRequest(TextAPIProtocol):
    def __init__(self):
        self.api = GigaChat(
            credentials=os.getenv("GIGACHAT_API_KEY"),
            scope="GIGACHAT_API_B2B",
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
            request_cost = await self.api.atokens_count(input_=[text])
            response = await self.api.ainvoke([HumanMessage(content=text)])
            response_cost = await self.api.atokens_count(input_=[response.content])

        logger.info(
            f'Request costs [{request_cost[0]}] tokens.'
            f'Response costs [{response_cost[0]}] tokens.'
        )
        if "я совсем не хочу говорить на эту тему" in response.content.lower():
            raise BlacklistError("Request content is in a blacklist")
        return response.content
