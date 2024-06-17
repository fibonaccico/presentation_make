from __future__ import annotations

import os
from typing import TYPE_CHECKING, Optional

from dotenv import load_dotenv
from langchain.chat_models.gigachat import GigaChat
from langchain.schema import HumanMessage, SystemMessage

from make_presentation.api_models.interfaces import TextAPIProtocol
from make_presentation.config import DEFAULT_TEMPERATURE

if TYPE_CHECKING:
    from langchain_core.messages import BaseMessage


class GigaChatRequest(TextAPIProtocol):
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("GIGACHAT_API_KEY")
        self.api = GigaChat(credentials=self.api_key, verify_ssl_certs=False)
        self.api.temperature = DEFAULT_TEMPERATURE

    async def request(self, text: str, assistant: Optional[str] = None) -> BaseMessage:
        messages = [HumanMessage(content=text)]
        if assistant:
            messages.append(SystemMessage(content=assistant))

        return await self.api.ainvoke(messages)
