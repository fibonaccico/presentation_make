import logging
import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from make_presentation.api_models.interfaces import TextAPIProtocol
from make_presentation.config import DEFAULT_TEMPERATURE

load_dotenv()
logger = logging.getLogger(__name__)


class OpenAIRequest(TextAPIProtocol):
    def __init__(self):
        self.api = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=DEFAULT_TEMPERATURE
        )

    async def request(
        self,
        text: str
    ) -> str | list[str | dict]:
        messages = [("human", text),]
        response = await self.api.ainvoke(messages)
        request_cost = response.response_metadata["token_usage"]["prompt_tokens"]
        response_cost = response.response_metadata["token_usage"]["completion_tokens"]

        logger.info(
            f'Request costs [{request_cost}] tokens.'
            f'Response costs [{response_cost}] tokens.'
        )

        return response.content
