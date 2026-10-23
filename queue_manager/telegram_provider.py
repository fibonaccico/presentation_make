import asyncio
import json
from typing import Optional

import aiohttp

from config.logger import get_logger
from queue_manager.config import MAX_API_KEY, TG_URLS

logger = get_logger()


async def send_document(
    session: aiohttp.ClientSession,
    chat_id: str,
    file_path: Optional[str] = None,
    file_id: Optional[str] = None,
    text: Optional[str] = None,
    parse_mode: Optional[str] = None,
    reply_markup: Optional[list[list[dict]]] = None,
    file_type: str = "document"
) -> None:
    logger.info(
        f"Sending document or media file to {chat_id}."
        f"File type: {file_type}, file path: {file_path}, file_id: {file_id}, "
        f"text: {text}, reply_mark_up: {reply_markup}"
    )

    data = aiohttp.FormData()
    data.add_field('chat_id', chat_id)
    if file_id:
        data.add_field(file_type, file_id)
    if reply_markup:
        keyboard = {
            "inline_keyboard": reply_markup
        }
        data.add_field("reply_markup", json.dumps(keyboard))
    if text:
        data.add_field("caption", text)
    if parse_mode:
        data.add_field("parse_mode", parse_mode)
    try:
        if file_path:
            filename = file_path.split('/')[-1]
            with open(file_path, 'rb') as file:
                data.add_field(file_type, file, filename=filename)
                async with session.post(url=TG_URLS.get(file_type), data=data) as response:
                    result = await response.text()
                    logger.info(
                        f"Send file: [{file_path}, {file_id}] to "
                        f"user {chat_id}. Result: {result}")
                    status = response.status
        else:
            async with session.post(url=TG_URLS.get(file_type), data=data) as response:
                result = await response.text()
                logger.info(
                    f"Send file: [{file_path}, {file_id}] to "
                    f"user {chat_id}. Result: {result}")
                status = response.status
        try:
            result_json = await response.json()
        except Exception as err:
            logger.error(f'Ошибка json. Reason: {err}')
            result_json = {}
        return status, result_json

    except Exception as err:
        logger.error(
            f"Cannot send file: [{file_path}, {file_id}] "
            f"to user {chat_id}. Reason: {err}")


async def send_document_max(
    session: aiohttp.ClientSession,
    user_id: str,
    file_path: str,
    token: str = MAX_API_KEY
) -> None:
    filename = file_path.split('/')[-1]
    logger.info(
        f"Пользователь [user_id: {user_id}]. Sending file "
        f"{file_path} to {user_id} into MAX")
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
            logger.info(
                f'Пользователь [user_id: {user_id}]. '
                f'Got link to file upload. link: {link_to_upload}')
    except Exception as err:
        logger.error(
            f"Пользователь [user_id: {user_id}]. Cannot get "
            f"link to upload. Reason: {err}")

    # загрузка файла по полученной ссылке link_to_upload
    with open(file_path, 'rb') as file:
        data = aiohttp.FormData()
        data.add_field('document', file, filename=filename)
        try:
            async with session.post(link_to_upload, data=data) as response:
                result = await response.json()
                file_token = dict(result).get("token")
                logger.info(
                    f"Пользователь [user_id: {user_id}]. "
                    f"Файл загружен: [{file_path}]. Result: {result}")
        except Exception as err:
            logger.error(
                f"Пользователь [user_id: {user_id}]. Cannot "
                f"upload file: [{file_path}]. Reason: {err}")

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
            logger.debug(
                f'Сообщение [{data_message}] отправлено пользователю в MAX '
                f'[user_id: {user_id}]')
            await response.text()
        else:
            logger.error(
                f'Ошибка отправки сообщения польователю в MAX [user_id: {user_id}]. '
                f'Сообщение: [{data_message}]. Причина: {response.reason}')


async def send_message(
    session: aiohttp.ClientSession,
    chat_id: str,
    message: str,
    reply_markup: Optional[list[list[dict]]] = None,
    parse_mode: str = None,
    media: Optional[dict[str, str]] = None
):
    logger.debug(
        f"Sending message {message} to {chat_id}. Reply markup: {reply_markup}."
        f"Media: {media}. Parse_mode: {parse_mode}. "
    )
    if media:
        status, result_json = await send_document(
            session=session,
            chat_id=chat_id,
            file_id=media.get("file_id"),
            file_type=media.get("type"),
            text=message,
            parse_mode=parse_mode,
            reply_markup=reply_markup
        )
        return status, result_json

    data = aiohttp.FormData()
    data.add_field('chat_id', chat_id)
    data.add_field('text', message)
    if parse_mode:
        data.add_field('parse_mode', parse_mode)

    if reply_markup:
        logger.debug('Сообщение c клавиатурой')
        keyboard = {
            "inline_keyboard": reply_markup
        }
        data.add_field("reply_markup", json.dumps(keyboard))
    try:
        async with session.post(TG_URLS.get("message"), data=data) as response:
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


async def send_message_max(
    session: aiohttp.ClientSession,
    user_id: str,
    message: str,
    token: str = MAX_API_KEY
) -> None:
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }
    data = {'text': message}

    url = f'https://platform-api.max.ru/messages?user_id={user_id}'
    async with session.post(url, json=data, headers=headers) as response:
        status = response.status
        if status == 200:
            logger.debug(
                f'Сообщение [{message}] отправлено пользователю '
                f'в MAX [user_id: {user_id}]')
            await response.text()
        else:
            logger.error(
                f'Ошибка отправки сообщения польователю в MAX [user_id: {user_id}]. '
                f'Сообщение: [{message}]. Причина: {response.reason}')
