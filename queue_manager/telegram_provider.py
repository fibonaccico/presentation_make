import asyncio
import json
import os
from typing import Optional

import aiohttp
from dotenv import load_dotenv

from config.logger import get_logger

load_dotenv()
logger = get_logger()


async def send_document(session: aiohttp.ClientSession, chat_id: str, file_path: str, token: str = os.getenv("TELEGRAM_API_KEY")) -> None:
    filename = file_path.split('/')[-1]
    logger.info(f"Sending file {file_path} to {chat_id}")

    url = f'https://api.telegram.org/bot{token}/sendDocument'
    with open(file_path, 'rb') as file:
        data = aiohttp.FormData()
        # reply_markup = [
        #     [
        #         {'text': '⭐Поставьте оценку/Rate⭐', 'callback_data': 'none'},
        #     ],
        #     [
        #         {'text': '1', 'callback_data': 'rev_1'},
        #         {'text': '2', 'callback_data': 'rev_2'},
        #         {'text': '3', 'callback_data': 'rev_3'},
        #         {'text': '4', 'callback_data': 'rev_4'},
        #         {'text': '5', 'callback_data': 'rev_5'},
        #     ]
        # ]

        # data.add_field('inline_keyboard', reply_markup)
        data.add_field('chat_id', chat_id)
        data.add_field('document', file, filename=filename)
        try:
            async with session.post(url, data=data) as response:
                result = await response.text()
                logger.info(f"Send file: [{file_path}] to user {chat_id}. Result: {result}")

        except Exception as err:
            logger.error(f"Cannot send file: [{file_path}] to user {chat_id}. Reason: {err}")


async def send_document_max(session: aiohttp.ClientSession, user_id: str, file_path: str, token: str = os.getenv("MAX_API_KEY")) -> None:
    filename = file_path.split('/')[-1]
    logger.info(f"Пользователь [user_id: {user_id}]. Sending file {file_path} to {user_id} into MAX")
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }
    # получение ссылки для загрузки файла
    url_to_get_link = "https://platform-api.max.ru/uploads?type=file"
    try:
        async with session.post(url=url_to_get_link, headers=headers) as response:
            res = await response.json()
            link_to_upload = dict(res).get("url")
            logger.info(f'Пользователь [user_id: {user_id}]. Got link to file upload. link: {link_to_upload}')
    except Exception as err:
        logger.error(f"Пользователь [user_id: {user_id}]. Cannot get link to upload. Reason: {err}")

    # загрузка файла по полученной ссылке link_to_upload
    with open(file_path, 'rb') as file:
        data = aiohttp.FormData()
        data.add_field('document', file, filename=filename)
        try:
            async with session.post(link_to_upload, data=data) as response:
                result = await response.json()
                file_token = dict(result).get("token")
                logger.info(f"Пользователь [user_id: {user_id}]. Файл загружен: [{file_path}]. Result: {result}")
        except Exception as err:
            logger.error(f"Пользователь [user_id: {user_id}]. Cannot upload file: [{file_path}]. Reason: {err}")

    await asyncio.sleep(2.0)
    data_message = {
        "text": "",
        "attachments": [
            {
                "type": "file",
                "payload": {
                    "token": file_token
                }
            }
        ]
    }

    url = f'https://platform-api.max.ru/messages?user_id={user_id}'
    async with session.post(url, json=data_message, headers=headers) as response:
        status = response.status
        if status == 200:
            logger.debug(f'Сообщение [{data_message}] отправлено пользователю в MAX [user_id: {user_id}]')
            await response.text()
        else:
            logger.error(
                f'Ошибка отправки сообщения польователю в MAX [user_id: {user_id}]. '
                f'Сообщение: [{data_message}]. Причина: {response.reason}')


async def send_message(session: aiohttp.ClientSession, chat_id: str, message: str, token: str = os.getenv("TELEGRAM_API_KEY"), reply_markup: Optional[dict] = None):
    logger.debug(f"Sending message {message} to {chat_id}. Reply markup: {reply_markup}")

    url = f'https://api.telegram.org/bot{token}/sendMessage'
    data = aiohttp.FormData()
    data.add_field('chat_id', chat_id)
    data.add_field('text', message)

    if reply_markup:
        logger.debug('Сообщение c клавиатурой')
        data.add_field("reply_markup", json.dumps(reply_markup))
    try:
        async with session.post(url, data=data) as response:
            result = await response.text()
            logger.info(f"Send message {message} to {chat_id}. Result: {result}")
            status = response.status
            try:
                result_json = await response.json()
            except Exception as err:
                logger.error(f'Ошибка json. Reason: {err}')
                result_json = {}
            return status, result_json

    except Exception as err:
        logger.error(f'Ошибка отправки сообщения. Reason: {err}')


async def send_message_max(session: aiohttp.ClientSession, user_id: str, message: str, token: str = os.getenv("MAX_API_KEY")) -> None:
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }
    data = {'text': message}

    url = f'https://platform-api.max.ru/messages?user_id={user_id}'
    async with session.post(url, json=data, headers=headers) as response:
        status = response.status
        if status == 200:
            logger.debug(f'Сообщение [{message}] отправлено пользователю в MAX [user_id: {user_id}]')
            await response.text()
        else:
            logger.error(
                f'Ошибка отправки сообщения польователю в MAX [user_id: {user_id}]. '
                f'Сообщение: [{message}]. Причина: {response.reason}')
