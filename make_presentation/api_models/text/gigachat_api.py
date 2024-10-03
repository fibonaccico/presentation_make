from __future__ import annotations

import os
from typing import TYPE_CHECKING, Sequence

from dotenv import load_dotenv
from langchain.chat_models.gigachat import GigaChat
from langchain.schema import HumanMessage

from make_presentation.api_models.interfaces import TextAPIProtocol
from make_presentation.config import DEFAULT_TEMPERATURE

if TYPE_CHECKING:
    from langchain_core.messages import BaseMessage


load_dotenv()


class GigaChatRequest(TextAPIProtocol):
    def __init__(self):
        self.api = GigaChat(
            credentials=os.getenv("GIGACHAT_API_KEY"),
            verify_ssl_certs=False
        )
        self.api.temperature = DEFAULT_TEMPERATURE
        # self.history = []  # noqa E800

    async def request(
        self,
        text: str
    ) -> tuple[BaseMessage, Sequence[BaseMessage]]:

        # self.history.append(HumanMessage(content=text))   # noqa E800
        # response = await self.api.ainvoke(self.history)   # noqa E800
        # self.history.append(response)                     # noqa E800
        response = await self.api.ainvoke([HumanMessage(content=text)])
        return response
