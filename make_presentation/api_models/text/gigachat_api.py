from __future__ import annotations

from typing import TYPE_CHECKING, Sequence

from langchain.chat_models.gigachat import GigaChat
from langchain.schema import HumanMessage

from make_presentation.api_models.interfaces import TextAPIProtocol
from make_presentation.config import DEFAULT_TEMPERATURE

if TYPE_CHECKING:
    from langchain_core.messages import BaseMessage


class GigaChatRequest(TextAPIProtocol):
    def __init__(self, api_key: str):
        self.api = GigaChat(credentials=api_key, verify_ssl_certs=False)
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
