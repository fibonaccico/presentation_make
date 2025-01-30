import json

import aiohttp
from config.logger import get_logger
from dotenv import load_dotenv

load_dotenv()
logger = get_logger()


async def send_document(
    token: str,
    chat_id: str,
    file_path: str,
    add_keyboard: bool = False
) -> None:
    filename = file_path.split('/')[-1]
    logger.info(f"Sending file {file_path} to {chat_id}")

    async with aiohttp.ClientSession() as session:
        url = f'https://api.telegram.org/bot{token}/sendDocument'
        with open(file_path, 'rb') as file:
            data = aiohttp.FormData()
            data.add_field('chat_id', chat_id)
            data.add_field('document', file, filename=filename)

            if add_keyboard:
                keyboard = {
                    "inline_keyboard": [
                        [
                            {"text": "⭐Поставьте оценку⭐", "callback_data": "none"}
                        ],
                        [
                            {"text": "1", "callback_data": "rev_1"},
                            {"text": "2", "callback_data": "rev_2"},
                            {"text": "3", "callback_data": "rev_3"},
                            {"text": "4", "callback_data": "rev_4"},
                            {"text": "5", "callback_data": "rev_5"}
                        ]
                    ]
                }
                data.add_field('reply_markup', json.dumps(keyboard))

            async with session.post(url, data=data) as response:
                await response.text()


async def send_message(token: str, chat_id: str, message: str) -> None:
    async with aiohttp.ClientSession() as session:
        url = f'https://api.telegram.org/bot{token}/sendMessage'
        data = aiohttp.FormData()
        data.add_field('chat_id', chat_id)
        data.add_field('text', message)

        async with session.post(url, data=data) as response:
            await response.text()
