from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from langchain.schema import HumanMessage
from langchain_community.llms.gigachat import GigaChat

from make_presentation.api_models.errors import BlacklistError
from make_presentation.api_models.interfaces import TextAPIProtocol
from make_presentation.config import DEFAULT_TEMPERATURE

load_dotenv()
logger = logging.getLogger(__name__)


class GigaChatRequest(TextAPIProtocol):
    def __init__(self):
        self.api = GigaChat(
            credentials=os.getenv("GIGACHAT_API_KEY"),
            scope="GIGACHAT_API_B2B",
            verify_ssl_certs=False
        )
        self.api.temperature = DEFAULT_TEMPERATURE

    async def request(
        self,
        text: str
    ) -> str | list[str | dict]:
        request_cost = await self.api.atokens_count(input_=[text])
        response = await self.api.ainvoke([HumanMessage(content=text)])
        response_cost = await self.api.atokens_count(input_=[response])

        logger.info(
            f'Request costs [{request_cost[0]}] tokens.'
            f'Response costs [{response_cost[0]}] tokens.'
        )
        if "я совсем не хочу говорить на эту тему" in response:
            raise BlacklistError("Request content is in a blacklist")
        return response
