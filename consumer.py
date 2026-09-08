import asyncio
import functools
import os

import aiohttp
import aiormq
from aiolimiter import AsyncLimiter
from aiormq.abc import DeliveredMessage
from dotenv import load_dotenv
from PIL import Image

from config.logger import get_logger
from config.messages import (FORBBIDEN_ERROR_MESSAGE_EN,
                             FORBBIDEN_ERROR_MESSAGE_RU,
                             FREE_PRES_ENDED_MESSAGE_EN,
                             FREE_PRES_ENDED_MESSAGE_RU,
                             GENERATION_ERROR_MESSAGE_EN,
                             GENERATION_ERROR_MESSAGE_RU, INLINE_MESSAGE_EN,
                             INLINE_MESSAGE_RU, INVITE_FRIEND_BUTTON_EN,
                             INVITE_FRIEND_BUTTON_RU, SENDING_FAIL_EN,
                             SENDING_FAIL_RU, TARIFF_BUTTON_EN,
                             TARIFF_BUTTON_RU, TELEGRAM_CLOSING_MESSAGE_EN,
                             TELEGRAM_CLOSING_MESSAGE_RU)
from make_presentation import Presentation
from make_presentation.api_models.text.openai_api import ForbiddenContent
from make_presentation.DTO import ImageInfoDTO, PresentationDTO, SlideDTO
from queue_manager.db_queries import (create_auto_pay,
                                      create_presentation_adapter,
                                      get_image_by_uuid, get_last_user_payment,
                                      get_locale_by_user_uuid,
                                      get_presentation_dto_or_none,
                                      get_tariff_data, get_user_referral_code,
                                      reduce_balance_by_user_uuid,
                                      remove_auto_pay_for_user,
                                      set_presentation_local_file_path,
                                      telegram_id_by_user_uuid,
                                      update_candidate_image_db,
                                      update_user_is_deleted_status_to_false)
from queue_manager.event_message import (EventMessage, EventType,
                                         PresentationType,
                                         RegenerateImageEventMessage,
                                         SendMessgeEventMessage)
from queue_manager.queue_exceptions import EventTypeException
from queue_manager.schemas import PaymentService, PayStatus, TariffTitle
from queue_manager.services import YookassaPayment
from queue_manager.SQL_responses import PresentationSQL
from queue_manager.telegram_provider import (send_document, send_document_max,
                                             send_message, send_message_max)

load_dotenv()
logger = get_logger()

GENERATOR_EVENT_TYPE = ["web", "telegram", "max", "autopayment", "telegram_sender"]
DOWNLOAD_EVENT_TYPE = ["download"]

telegram_ratelimiter = AsyncLimiter(max_rate=27, time_period=1.0)


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


async def on_telegram_sender(message: DeliveredMessage, session: aiohttp.ClientSession):
    event_message = SendMessgeEventMessage(message)
    logger.info(f"Start sending from message {event_message.__dict__}")
    # if event_message.from_source not in GENERATOR_EVENT_TYPE:
    #     logger.warning(f"Получено сообщение с неизвестным типом: {event_message.from_source}")
    #     await message.channel.basic_ack(delivery_tag=message.delivery_tag)
    #     return
    async with telegram_ratelimiter:
        try:
            status, body = await send_message(
                session=session,
                chat_id=event_message.telegram_id,
                message=event_message.text,
                reply_markup=event_message.reply_markup)

            if status == 200:
                await message.channel.basic_ack(delivery_tag=message.delivery_tag)
            elif status == 429:
                retry_after = await body.get("parameters", {}).get("retry_after", 5)
                logger.error(f"Поймали 429 от Telegram! Спим {retry_after} сек.")
                await asyncio.sleep(retry_after)
                await message.channel.basic_nack(delivery_tag=message.delivery_tag, requeue=True)
            elif status == 403 or status == 400:
                logger.warning(f"Ошибка отправки (пользователь недоступен, статус {status}), пользователь {event_message.telegram_id}. Удаляем задачу.")
                await update_user_is_deleted_status_to_false(telegram_id=event_message.telegram_id)
                await message.channel.basic_ack(delivery_tag=message.delivery_tag)
            else:
                logger.error(f"Telegram вернул странный статус: {status}. Возврат в очередь.")
                await asyncio.sleep(1.0)
                await message.channel.basic_nack(delivery_tag=message.delivery_tag, requeue=True)

        except aiohttp.ClientError as net_err:
            logger.error(f"Сетевая ошибка aiohttp: {net_err}. Повторим позже.")
            await asyncio.sleep(2.0)
            await message.channel.basic_nack(delivery_tag=message.delivery_tag, requeue=True)

        except Exception as err:
            logger.error(f"Message sending failed. Reason: {err}")
            await message.channel.basic_nack(delivery_tag=message.delivery_tag, requeue=True)


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
async def on_generator_message(message: aiormq.abc.DeliveredMessage, session: aiohttp.ClientSession):
    event_message = EventMessage(message)

    logger.info(f"Starting generate from message {event_message.__dict__}")
    user_telegram_id = await telegram_id_by_user_uuid(user_uuid=event_message.user_uuid)
    locale = await get_locale_by_user_uuid(user_uuid=event_message.user_uuid)
    if event_message.event_type not in GENERATOR_EVENT_TYPE:
        raise EventTypeException
    try:
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
                    TARIFF_BUTTON = TARIFF_BUTTON_RU
                    INVITE_FRIEND_BUTTON = INVITE_FRIEND_BUTTON_RU
                    INLINE_MESSAGE = INLINE_MESSAGE_RU
                else:
                    TELEGRAM_CLOSING_MESSAGE = TELEGRAM_CLOSING_MESSAGE_EN
                    FREE_PRES_ENDED_MESSAGE = FREE_PRES_ENDED_MESSAGE_EN
                    TARIFF_BUTTON = TARIFF_BUTTON_EN
                    INVITE_FRIEND_BUTTON = INVITE_FRIEND_BUTTON_EN
                    INLINE_MESSAGE = INLINE_MESSAGE_EN

                if event_message.event_type == EventType.TELEGRAM.value:
                    logger.info(f"Платеж: {db_pay.uuid}, presentation quantity {db_pay.paid_qty}, tariff - {tariff_data.title}")
                    for file in [file_path_pdf, file_path_pdf.replace("pdf", "pptx")]:
                        await send_document(
                            session=session,
                            chat_id=user_telegram_id,
                            file_path=file
                        )
                    await send_message(session=session, chat_id=user_telegram_id, message=TELEGRAM_CLOSING_MESSAGE)
                    if db_pay.paid_qty == 1 and tariff_data.title == TariffTitle.AFTER_REGISTRATION.value:
                        logger.info(f"The last free presentation has been used. {db_pay.uuid}")
                        referral_code = await get_user_referral_code(user_uuid=event_message.user_uuid)
                        logger.info(f"user referral code: {referral_code.referral_code}")
                        link = f"https://t.me/fibonacci_presentation_bot?start={referral_code.referral_code}"
                        reply_markup = {
                            "inline_keyboard": [
                                [
                                    {
                                        'text': TARIFF_BUTTON,
                                        "callback_data": "tariffs"
                                    },
                                    {
                                        'text': INVITE_FRIEND_BUTTON,
                                        'switch_inline_query': INLINE_MESSAGE.format(link=link)
                                    }
                                ]
                            ]
                        }
                        await send_message(session=session, chat_id=user_telegram_id, message=FREE_PRES_ENDED_MESSAGE, reply_markup=reply_markup)
                else:
                    for file in [file_path_pdf, file_path_pdf.replace("pdf", "pptx")]:
                        await send_document_max(
                            session=session,
                            user_id=user_telegram_id,
                            file_path=file
                        )
                    await send_message_max(session=session, user_id=user_telegram_id, message=TELEGRAM_CLOSING_MESSAGE)
        else:
            if locale == "ru":
                generation_error_text = GENERATION_ERROR_MESSAGE_RU
            else:
                generation_error_text = GENERATION_ERROR_MESSAGE_EN
            if event_message.event_type == EventType.TELEGRAM.value:
                await send_message(session=session, chat_id=user_telegram_id, message=generation_error_text)
            if event_message.event_type == EventType.MAX.value:
                await send_message_max(session=session, user_id=user_telegram_id, message=generation_error_text)

            logger.error(f"Пользователь [user_id = {user_telegram_id}]. No generation data. Error is into creating presentation. Presentation generation failed: {event_message.presentation_uuid}. ")
            await message.channel.basic_nack(
                message.delivery.delivery_tag,
                requeue=False
            )
    except ForbiddenContent as err:
        logger.error(f"Пользователь [user_id = {user_telegram_id}]. Presentation generation failed: FORBBIDEN CONTENT: {err}. TEXT: {event_message.context} ")
        if locale == "ru":
            generation_error_text = FORBBIDEN_ERROR_MESSAGE_RU
        else:
            generation_error_text = FORBBIDEN_ERROR_MESSAGE_EN
        if event_message.event_type == EventType.TELEGRAM.value:
            await send_message(session=session, chat_id=user_telegram_id, message=generation_error_text)
        if event_message.event_type == EventType.MAX.value:
            await send_message_max(session=session, user_id=user_telegram_id, message=generation_error_text)
        await message.channel.basic_nack(
            message.delivery.delivery_tag,
            requeue=False
        )

    except Exception as err:
        if locale == "ru":
            generation_error_text = GENERATION_ERROR_MESSAGE_RU
        else:
            generation_error_text = GENERATION_ERROR_MESSAGE_EN
        if event_message.event_type == EventType.TELEGRAM.value:
            await send_message(session=session, chat_id=user_telegram_id, message=generation_error_text)
        if event_message.event_type == EventType.MAX.value:
            await send_message_max(session=session, user_id=user_telegram_id, message=generation_error_text)

        logger.error(f"Пользователь [user_id = {user_telegram_id}]. Presentation generation failed: {event_message.presentation_uuid}. Reason: [{err}]")
        await message.channel.basic_nack(
            message.delivery.delivery_tag,
            requeue=False
        )


async def on_download_message(message, session: aiohttp.ClientSession):
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
                        session=session,
                        chat_id=telegram_id,
                        file_path=presentation_path
                    )
                except Exception as e:
                    if locale == "ru":
                        sending_fail_text = SENDING_FAIL_RU
                    else:
                        sending_fail_text = SENDING_FAIL_EN
                    await send_message(session=session, chat_id=telegram_id, message=sending_fail_text)
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
    async with aiohttp.ClientSession() as session:
        channel_generator = await connection.channel()
        await channel_generator.basic_qos(prefetch_count=40)
        declare_ok_generator = await channel_generator.queue_declare("generator_queue", durable=True)
        bound_callback_generator_queue = functools.partial(on_generator_message, session=session)
        await channel_generator.basic_consume(declare_ok_generator.queue, bound_callback_generator_queue)

        channel_autopayment = await connection.channel()
        await channel_autopayment.basic_qos(prefetch_count=1)
        declare_ok_payment = await channel_autopayment.queue_declare("autopayment_queue", durable=True)
        await channel_autopayment.basic_consume(declare_ok_payment.queue, on_autopayment_message)

        channel_download = await connection.channel()
        declare_ok_download = await channel_download.queue_declare("download_presentation_queue", durable=True)    # noqa E501
        bound_callback_download_presentation = functools.partial(on_download_message, session=session)
        await channel_download.basic_consume(declare_ok_download.queue, bound_callback_download_presentation)

        channel_download = await connection.channel()
        declare_ok_download = await channel_download.queue_declare("regenerate_image", durable=True)  # noqa E501
        await channel_download.basic_consume(declare_ok_download.queue, on_regenerate_image)

        channel_download = await connection.channel()
        declare_ok_download = await channel_download.queue_declare("download_presentation_directly_queue", durable=True)  # noqa E501
        await channel_download.basic_consume(declare_ok_download.queue, on_download_message_directly)

        channel_telegram_sender = await connection.channel()
        await channel_telegram_sender.basic_qos(prefetch_count=30)
        declare_ok_sender = await channel_telegram_sender.queue_declare("telegram_sender", durable=True)  # noqa E501
        bound_callback_tg_sender = functools.partial(on_telegram_sender, session=session)
        await channel_telegram_sender.basic_consume(declare_ok_sender.queue, bound_callback_tg_sender)

        await asyncio.Event().wait()

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
