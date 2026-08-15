import os

from dotenv import load_dotenv
from openai import APIError, AsyncOpenAI

from config.logger import get_logger
from make_presentation.api_models.interfaces import TextAPIProtocol
from make_presentation.config import DEFAULT_TEMPERATURE
from make_presentation.errors import TextAPIError

load_dotenv()
logger = get_logger()


class ForbiddenContent(Exception):
    ...


class OpenAIRequest(TextAPIProtocol):
    def __init__(self):
        self.api = AsyncOpenAI(
            api_key=os.getenv("PROXY_API"),
            base_url="https://api.proxyapi.ru/openai/v1",
        )
        self.moderation_api = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )

    async def request(
        self,
        text: str
    ) -> str | list[str | dict]:
        try:

            # response = await self.moderation_api.moderations.create(
            #     model="omni-moderation-latest",
            #     input=text
            # )
            # result = response.results[0]
            # if result.flagged:
            #     logger.warning(f'ЗАПРЕЩЕННЫЙ КОНТЕНТ!!! Content: [{text}]')
            #     violated_categories = [
            #         cat for cat, flagged in result.categories.model_dump().items() if flagged
            #     ]
            #     raise ForbiddenContent(f"ЗАПРЕЩЕННЫЙ КОНТЕНТ!!! Категории нарушений: {violated_categories}")

            chat_completion = await self.api.chat.completions.create(
                model="gpt-4.1-nano",
                messages=[{"role": "user", "content": text}],
                temperature=DEFAULT_TEMPERATURE
            )
            request_cost = chat_completion.usage.prompt_tokens
            response_cost = chat_completion.usage.completion_tokens

            logger.info(
                f'Request costs [{request_cost}] tokens.'
                f'Response costs [{response_cost}] tokens.'
                f'Total costs [{request_cost + response_cost}] tokens.'
            )
        except ForbiddenContent as err:
            logger.warning(f"{err}")
            raise ForbiddenContent(f'{err}')

        except Exception as err:
            logger.error(f"APIConnection error: [{err}]")
            raise TextAPIError(f"{err}")

        return chat_completion.choices[0].message.content
