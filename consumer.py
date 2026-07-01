import asyncio
import os
from datetime import datetime, timedelta

import aiohttp
import aiormq
from dotenv import load_dotenv
from PIL import Image

from config.logger import get_logger
from config.messages import (FREE_PRES_ENDED_MESSAGE_EN,
                             FREE_PRES_ENDED_MESSAGE_RU,
                             GENERATION_ERROR_MESSAGE_EN,
                             GENERATION_ERROR_MESSAGE_RU, SENDING_FAIL_EN,
                             SENDING_FAIL_RU, TELEGRAM_CLOSING_MESSAGE_EN,
                             TELEGRAM_CLOSING_MESSAGE_RU)
from make_presentation import Presentation
from make_presentation.DTO import ImageInfoDTO, PresentationDTO, SlideDTO
from queue_manager.db_queries import (create_auto_pay, create_pay,
                                      create_presentation_adapter,
                                      get_image_by_uuid, get_last_user_payment,
                                      get_locale_by_user_uuid,
                                      get_presentation_dto_or_none,
                                      get_tariff_data, get_user_by_user_uuid,
                                      reduce_balance_by_user_uuid,
                                      remove_auto_pay_for_user,
                                      set_presentation_local_file_path,
                                      telegram_id_by_user_uuid,
                                      update_candidate_image_db)
from queue_manager.event_message import (EventMessage, EventType,
                                         PresentationType,
                                         RegenerateImageEventMessage)
from queue_manager.queue_exceptions import EventTypeException
from queue_manager.schemas import PaymentService, PayStatus, TariffTitle
from queue_manager.services import DodoPayments, YookassaPayment
from queue_manager.SQL_responses import PresentationSQL

load_dotenv()
logger = get_logger()

GENERATOR_EVENT_TYPE = ["web", "telegram", "max", "autopayment"]
DOWNLOAD_EVENT_TYPE = ["download"]


async def send_document(chat_id: str, file_path: str, token: str = os.getenv("TELEGRAM_API_KEY")) -> None:
    filename = file_path.split('/')[-1]
    logger.info(f"Sending file {file_path} to {chat_id}")

    async with aiohttp.ClientSession() as session:
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


async def send_document_max(user_id: str, file_path: str, token: str = os.getenv("MAX_API_KEY")) -> None:
    filename = file_path.split('/')[-1]
    logger.info(f"Пользователь [user_id: {user_id}]. Sending file {file_path} to {user_id} into MAX")
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }
    # получение ссылки для загрузки файла
    async with aiohttp.ClientSession() as session:
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


async def send_message(chat_id: str, message: str, token: str = os.getenv("TELEGRAM_API_KEY")) -> None:
    async with aiohttp.ClientSession() as session:
        url = f'https://api.telegram.org/bot{token}/sendMessage'
        data = aiohttp.FormData()
        data.add_field('chat_id', chat_id)
        data.add_field('text', message)

        async with session.post(url, data=data) as response:
            await response.text()


async def send_message_max(user_id: str, message: str, token: str = os.getenv("MAX_API_KEY")) -> None:
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }
    data = {'text': message}

    async with aiohttp.ClientSession() as session:
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


def delete_presentation_file(file_path: str):
    root_directory = "/app/presentations_files"

    if os.path.isfile(file_path):
        os.remove(file_path)

    parent_directory = os.path.dirname(file_path)

    while parent_directory != root_directory:
        if os.path.isdir(parent_directory):
            try:
                os.rmdir(parent_directory)
            except OSError:
                logger.warning(f"Папка не пустая, удаление остановлено: {parent_directory}")
                break

        parent_directory = os.path.dirname(parent_directory)


def create_presentation_dto(presentation_sql: PresentationSQL) -> PresentationDTO:
    slides_dto = []
    for slide in presentation_sql.slides:
        images_dto = [
            ImageInfoDTO(
                path=image.local_file_path, description=image.description, style=image.style
            ) for image in slide.images
        ]
        slide_dto = SlideDTO(
            number=slide.number,
            title=slide.title,
            text=slide.text,
            images=images_dto,
            subtitle_1=slide.subtitle1,
            subtitle_2=slide.subtitle2,
            subtitle_3=slide.subtitle3,
        )
        slides_dto.append(slide_dto)
    finish_title = presentation_sql.slides[len(presentation_sql.slides) - 1].title

    return PresentationDTO(
        template_name=presentation_sql.template,
        theme=presentation_sql.title,
        finish_title=finish_title,
        slides=slides_dto
    )


async def on_autopayment_message(message: aiormq.abc.DeliveredMessage):
    event_message = EventMessage(message)
    logger.info(f"Start checking AUTOPAYMENT from message {event_message.__dict__}")
    if event_message.event_type not in GENERATOR_EVENT_TYPE:
        logger.warning(f"Получено сообщение с неизвестным типом: {event_message.event_type}")
        await message.channel.basic_ack(delivery_tag=message.delivery_tag)
        return

    try:
        last_pay = await get_last_user_payment(user_uuid=event_message.user_uuid)
        tariff_data = await get_tariff_data(tariff_id=last_pay.tariff_id)
        if tariff_data.subscription:
            try:
                if event_message.auto_pay and event_message.auto_pay_id:
                    logger.debug(
                            f"Пользователь {event_message.telegram_id}-{event_message.username}: "
                            f"проведение автоплатежа. Платежный сервис: {last_pay.payment_service}. Последний платеж тариф - {tariff_data.title}"
                        )
                    if last_pay.payment_service == PaymentService.YOOKASSA.value:
                        payment_data = YookassaPayment(
                            tariff=tariff_data.title,
                            amount=tariff_data.price,
                            email=event_message.email,
                            save_payment_method=event_message.auto_pay,
                            payment_method_id=event_message.auto_pay_id,
                            create_pay=True
                        )

                        new_auto_payment = await create_auto_pay(
                            user_uuid=event_message.user_uuid,
                            payment_data=payment_data,
                            status=PayStatus.PENDING.value,
                            paid_qty=tariff_data.presentation_qty,
                            tariff_id=tariff_data.id
                        )
                        await asyncio.sleep(1)
                        logger.debug(
                            f"Пользователь {event_message.telegram_id}-{event_message.username}: "
                            f"создание автоплатежа [uuid -- {new_auto_payment.uuid}, "
                            f"yookassa_id -- {new_auto_payment.yookassa_pay_id}] "
                            f"со статусом {PayStatus.PENDING}")

                    # if last_pay.payment_service == PaymentService.DODOPAYMENTS.value:

                    #     new_auto_payment = await create_pay(
                    #         user_uuid=event_message.user_uuid,
                    #         yookassa_pay_id=PaymentService.DODOPAYMENTS.value,
                    #         amount=tariff_data.price,
                    #         status=PayStatus.PENDING.value,
                    #         paid_qty=tariff_data.presentation_qty,
                    #         tariff_id=tariff_data.id
                    #     )
                    #     await asyncio.sleep(1)

                    #     payment_data = DodoPayments(
                    #         amount=tariff_data.price,
                    #         payment_method_id=event_message.auto_pay_id
                    #     )
                    #     await payment_data.create_payment(payment_uuid=new_auto_payment.uuid)

            except Exception as e:
                logger.error(
                    f"Проблема автоплатежа на пользователе UUID: {event_message.user_uuid}. "
                    f"Причина: {e}")
        else:
            logger.debug(
                f"Пользователь {event_message.telegram_id}-{event_message.username} сброс тарифа."
                f"Тариф: id - {tariff_data.id}, title - {tariff_data.title}, без подписки.")
            await remove_auto_pay_for_user(user_uuid=event_message.user_uuid)

        await message.channel.basic_ack(delivery_tag=message.delivery_tag)
    except Exception as err:
        await asyncio.sleep(1)
        logger.debug(
                f"Пользователь ошибка автоплатежа. Причина {err}.")
        await message.channel.basic_ack(delivery_tag=message.delivery_tag)


# b'{"event_type":"telegram","generation_data":{"save_presentation_path": /path/to/pres, "type":"topic","user_uuid":"ogo","presentation_uuid":"gogo","text_generation_model":"wdef","template":"dsf","no_logo":true, "language": "ru", "save_path_for_images":"sds","context":"dfds"}}'  # noqa E800, E501
async def on_generator_message(message):
    event_message = EventMessage(message)

    logger.info(f"Starting generate from message {event_message.__dict__}")
    user_telegram_id = await telegram_id_by_user_uuid(user_uuid=event_message.user_uuid)
    locale = await get_locale_by_user_uuid(user_uuid=event_message.user_uuid)
    if event_message.event_type not in GENERATOR_EVENT_TYPE:
        raise EventTypeException

    presentation_data = await create_presentation_adapter(message=event_message)
    if presentation_data:
        is_paid = False
        if event_message.presentation_type == PresentationType.TEXT.value:
            is_paid = True
        await message.channel.basic_ack(
            message.delivery.delivery_tag
        )
        db_pay = await reduce_balance_by_user_uuid(user_uuid=event_message.user_uuid,
                                          is_paid=is_paid)
        tariff_data = await get_tariff_data(tariff_id=db_pay.tariff_id)

        if event_message.event_type == EventType.TELEGRAM.value or event_message.event_type == EventType.MAX.value:
            file_path_pdf = Presentation.save(
                data=presentation_data,
                save_path=event_message.save_presentation_path,
                no_logo=event_message.no_logo,
                format=event_message.format_file
            )
            if locale == "ru":
                TELEGRAM_CLOSING_MESSAGE = TELEGRAM_CLOSING_MESSAGE_RU
                FREE_PRES_ENDED_MESSAGE = FREE_PRES_ENDED_MESSAGE_RU
            else:
                TELEGRAM_CLOSING_MESSAGE = TELEGRAM_CLOSING_MESSAGE_EN
                FREE_PRES_ENDED_MESSAGE = FREE_PRES_ENDED_MESSAGE_EN

            if event_message.event_type == EventType.TELEGRAM.value:
                for file in [file_path_pdf, file_path_pdf.replace("pdf", "pptx")]:
                    await send_document(
                        user_telegram_id,
                        file
                    )
                await send_message(user_telegram_id, TELEGRAM_CLOSING_MESSAGE)
                if db_pay and db_pay.paid_qty == 0 and tariff_data.title == TariffTitle.AFTER_REGISTRATION.value:
                    await send_message(user_telegram_id, TELEGRAM_CLOSING_MESSAGE)
            else:
                for file in [file_path_pdf, file_path_pdf.replace("pdf", "pptx")]:
                    await send_document_max(
                        user_telegram_id,
                        file
                    )
                await send_message_max(user_telegram_id, TELEGRAM_CLOSING_MESSAGE)

    else:
        if locale == "ru":
            generation_error_text = GENERATION_ERROR_MESSAGE_RU
        else:
            generation_error_text = GENERATION_ERROR_MESSAGE_EN
        if event_message.event_type == EventType.TELEGRAM.value:
            await send_message(user_telegram_id, message=generation_error_text)
        if event_message.event_type == EventType.MAX.value:
            await send_message_max(user_telegram_id, message=generation_error_text)

        logger.error(f"Пользователь [user_id = {user_telegram_id}]. Presentation generation failed: {event_message.presentation_uuid}. ")
        await message.channel.basic_nack(
            message.delivery.delivery_tag,
            requeue=False
        )


async def on_download_message(message):
    event_message = EventMessage(message)
    await message.channel.basic_ack(
        message.delivery.delivery_tag
    )

    logger.info(f"Starting download from message {event_message.__dict__}")

    match event_message.event_type:
        case EventType.DOWNLOAD.value:
            if db_presentation := await get_presentation_dto_or_none(presentation_uuid=event_message.presentation_uuid):      # noqa E501
                logger.info(f"Getting telegram of user {event_message.user_uuid} for send presentation")  # noqa E501
                telegram_id = await telegram_id_by_user_uuid(user_uuid=event_message.user_uuid)
                locale = await get_locale_by_user_uuid(user_uuid=event_message.user_uuid)

                try:
                    logger.info(f"Save presentation to {event_message.save_presentation_path}")
                    presentation_path = Presentation.save(
                        data=create_presentation_dto(db_presentation),
                        save_path=event_message.save_presentation_path,
                        no_logo=event_message.no_logo,
                        format=event_message.format_file
                    )

                    logger.info(f"Sending presentation {event_message.save_presentation_path} to {telegram_id}")   # noqa E501
                    await send_document(
                        telegram_id,
                        presentation_path
                    )
                except Exception as e:
                    if locale == "ru":
                        sending_fail_text = SENDING_FAIL_RU
                    else:
                        sending_fail_text = SENDING_FAIL_EN
                    await send_message(telegram_id, sending_fail_text)
                    logger.error(f"Presentation sending failed: {e}")

        case _:
            logger.warning(f"Unknown event type {event_message.event_type} in download_presentation_queue")    # noqa E501


async def on_download_message_directly(message):
    event_message = EventMessage(message)
    await message.channel.basic_ack(
        message.delivery.delivery_tag
    )

    logger.info(f"Starting download directly from message {event_message.__dict__}")

    match event_message.event_type:
        case EventType.DOWNLOAD.value:
            if db_presentation := await get_presentation_dto_or_none(presentation_uuid=event_message.presentation_uuid):      # noqa E501
                try:
                    logger.info(f"Save presentation to {event_message.save_presentation_path}")
                    presentation_path = Presentation.save(
                        data=create_presentation_dto(db_presentation),
                        save_path=event_message.save_presentation_path,
                        no_logo=True,
                        format=event_message.format_file
                    )

                    logger.info(f"Save presentation path {presentation_path} in DB")   # noqa E501
                    await set_presentation_local_file_path(
                        presentation_uuid=event_message.presentation_uuid,
                        local_file_path=presentation_path)
                except Exception as e:
                    logger.error(f"Presentation save failed or presentation local file path save failed: {e}")

        case _:
            logger.warning(f"Unknown event type {event_message.event_type} in download_presentation_directly_queue")    # noqa E501


async def on_regenerate_image(message):
    event_message = RegenerateImageEventMessage(message)
    await message.channel.basic_ack(message.delivery.delivery_tag)

    logger.info(f"Starting regenerate image {event_message.__dict__}")

    current_image_db = await get_image_by_uuid(image_uuid=event_message.current_image_uuid)
    with Image.open(current_image_db.local_file_path) as img:
        width, height = img.size

    new_image = await Presentation.generate_picture(
        current_image_db.description,
        width, height,
        current_image_db.style,
        os.path.dirname(current_image_db.local_file_path)
    )

    logger.debug(f"Create new image in db {new_image.__dict__}")
    await update_candidate_image_db(image_uuid=event_message.candidate_image_uuid, new_image_data=new_image)


async def main():
    connection = await aiormq.connect(
        f"amqp://{os.getenv('RABBIT_LOGIN')}:{os.getenv('RABBIT_PASS')}@{os.getenv('RABBIT_HOST')}/"
    )

    logger.info("Start consuming")
    channel_generator = await connection.channel()
    await channel_generator.basic_qos(prefetch_count=40)
    declare_ok_generator = await channel_generator.queue_declare("generator_queue", durable=True)
    await channel_generator.basic_consume(declare_ok_generator.queue, on_generator_message)

    channel_autopayment = await connection.channel()
    await channel_autopayment.basic_qos(prefetch_count=1)
    declare_ok_payment = await channel_autopayment.queue_declare("autopayment_queue", durable=True)
    await channel_autopayment.basic_consume(declare_ok_payment.queue, on_autopayment_message)

    channel_download = await connection.channel()
    declare_ok_download = await channel_download.queue_declare("download_presentation_queue", durable=True)    # noqa E501
    await channel_download.basic_consume(declare_ok_download.queue, on_download_message)

    channel_download = await connection.channel()
    declare_ok_download = await channel_download.queue_declare("regenerate_image", durable=True)  # noqa E501
    await channel_download.basic_consume(declare_ok_download.queue, on_regenerate_image)

    channel_download = await connection.channel()
    declare_ok_download = await channel_download.queue_declare("download_presentation_directly_queue", durable=True)  # noqa E501
    await channel_download.basic_consume(declare_ok_download.queue, on_download_message_directly)

    try:
        await connection.closing
    except asyncio.CancelledError:
        await connection.close()

    # async with AsyncSessionLocal() as db:                                                 # noqa E800
        # a = await get_presentation_or_none("165a57b3-0ef3-4cb2-8818-e91854a68b1b", db)    # noqa E116
        # await reduce_balance_by_user_uuid("5ef0c392-8a5b-41bd-92d1-8344ca5837e5", db)     # noqa E116
    # print(a.title)                                                                        # noqa E800
    # print(await db_query())                                                               # noqa E800
    # await create_db_presentation("5ef0c392-8a5b-41bd-92d1-8344ca5837e5", "huy", "classic")   # noqa E800


# loop = asyncio.get_event_loop()
# loop.run_until_complete(main())
# loop.run_forever()

if __name__ == "__main__":
    try:
        # Современный способ запуска asyncio (заменяет get_event_loop, run_until_complete и run_forever)
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Консьюмер остановлен пользователем")
