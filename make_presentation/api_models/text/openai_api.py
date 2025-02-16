import logging
import os

from dotenv import load_dotenv
from openai import AsyncOpenAI

from make_presentation.api_models.interfaces import TextAPIProtocol
from make_presentation.config import DEFAULT_TEMPERATURE

load_dotenv()
logger = logging.getLogger(__name__)


class OpenAIRequest(TextAPIProtocol):
    def __init__(self):
        self.api = AsyncOpenAI(
            api_key=os.getenv("PROXY_API"),
            base_url="https://api.proxyapi.ru/openai/v1",
        )

    async def request(
        self,
        text: str
    ) -> str | list[str | dict]:
        chat_completion = await self.api.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": text}],
            temperature=DEFAULT_TEMPERATURE
        )
        request_cost = chat_completion.usage.prompt_tokens
        response_cost = chat_completion.usage.completion_tokens

        logger.info(
            f'Request costs [{request_cost}] tokens.'
            f'Response costs [{response_cost}] tokens.'
        )

        return chat_completion.choices[0].message.content
