import asyncio
import os

import aiohttp
import aiormq
from dotenv import load_dotenv

from config.logger import get_logger
from make_presentation import Presentation
from make_presentation.DTO import ImageInfoDTO, PresentationDTO, SlideDTO
from queue_manager.db_queries import (create_presentation_adapter,
                                      get_presentation_dto_or_none,
                                      reduce_balance_by_user_uuid,
                                      telegram_id_by_user_uuid)
from queue_manager.event_message import EventMessage, EventType
from queue_manager.SQL_responses import PresentationSQL
from queue_manager.queue_exceptions import EventTypeException

load_dotenv()
logger = get_logger()

GENERATOR_EVENT_TYPE = ["web", "telegram"]
DOWNLOAD_EVENT_TYPE = ["download"]


async def send_document(chat_id: str, file_path: str, token: str = os.getenv("TELEGRAM_API_KEY")) -> None:
    filename = file_path.split('/')[-1]
    logger.info(f"Sending file {file_path} to {chat_id}")

    async with aiohttp.ClientSession() as session:
        url = f'https://api.telegram.org/bot{token}/sendDocument'
        with open(file_path, 'rb') as file:
            data = aiohttp.FormData()
            data.add_field('chat_id', chat_id)
            data.add_field('document', file, filename=filename)

            async with session.post(url, data=data) as response:
                await response.text()


async def send_message(chat_id: str, message: str, token: str = os.getenv("TELEGRAM_API_KEY")) -> None:
    async with aiohttp.ClientSession() as session:
        url = f'https://api.telegram.org/bot{token}/sendMessage'
        data = aiohttp.FormData()
        data.add_field('chat_id', chat_id)
        data.add_field('text', message)

        async with session.post(url, data=data) as response:
            await response.text()


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
                path=image.local_file_path, description=image.description
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


# b'{"event_type":"telegram","generation_data":{"save_presentation_path": /path/to/pres, "type":"topic","user_uuid":"ogo","presentation_uuid":"gogo","text_generation_model":"wdef","template":"dsf","save_path_for_images":"sds","context":"dfds"}}'  # noqa E800, E501
async def on_generator_message(message):
    event_message = EventMessage(message)

    await message.channel.basic_ack(
        message.delivery.delivery_tag
    )

    logger.info(f"Starting generate from message {event_message.__dict__}")
    user_telegram_id = await telegram_id_by_user_uuid(event_message.user_uuid)

    if event_message.event_type not in GENERATOR_EVENT_TYPE:
        raise EventTypeException

    presentation_data = await create_presentation_adapter(event_message)
    if presentation_data:
        await reduce_balance_by_user_uuid(event_message.user_uuid)

        if EventType.TELEGRAM.value:
            file_path_pdf = Presentation.save(
                data=presentation_data,
                save_path=event_message.save_presentation_path,
                format=event_message.format_file
            )
            for file in [file_path_pdf, file_path_pdf.replace("pdf", "pptx")]:
                await send_document(
                    user_telegram_id,
                    file
                )

            delete_presentation_file(file)
    else:
        await send_message(
            user_telegram_id,
            message="""
                    Не удалось сгенерировать презентацию.
                    Сейчас у Giga Chat, с которым я работаю происходят технические сбои.
                    Мы решаем эту проблему вместе, а пока попробуй ввести свою тему ещё раз,
                    есть шанс, что тебе повезет😉"""
        )
        logger.error(f"Presentation sending failed: {event_message.presentation_uuid}")


async def on_download_message(message):
    event_message = EventMessage(message)
    await message.channel.basic_ack(
        message.delivery.delivery_tag
    )

    logger.info(f"Starting download from message {event_message.__dict__}")

    match event_message.event_type:
        case EventType.DOWNLOAD.value:
            if db_presentation := await get_presentation_dto_or_none(event_message.presentation_uuid):      # noqa E501
                logger.info(f"Getting telegram of user {event_message.user_uuid} for send presentation")  # noqa E501
                telegram_id = await telegram_id_by_user_uuid(event_message.user_uuid)

                try:
                    logger.info(f"Save presentation to {event_message.save_presentation_path}")
                    presentation_path = Presentation.save(
                        data=create_presentation_dto(db_presentation),
                        save_path=event_message.save_presentation_path,
                        format=event_message.format_file
                    )

                    logger.info(f"Sending presentation {event_message.save_presentation_path} to {telegram_id}")   # noqa E501
                    await send_document(
                        telegram_id,
                        presentation_path
                    )
                    delete_presentation_file(presentation_path)
                except Exception as e:
                    await send_message(
                        telegram_id,
                        f"Ошибка отправки презентации. Попробуй еще раз или обратись к администратору."    # noqa E501
                    )
                    logger.error(f"Presentation sending failed: {e}")

        case _:
            logger.warning(f"Unknown event type {event_message.event_type} in download_presentation_queue")    # noqa E501


async def main():
    connection = await aiormq.connect(
        f"amqp://{os.getenv('RABBIT_LOGIN')}:{os.getenv('RABBIT_PASS')}@{os.getenv('RABBIT_HOST')}/"
    )

    logger.info("Start consuming")

    channel_generator = await connection.channel()
    await channel_generator.basic_qos(prefetch_count=10)
    declare_ok_generator = await channel_generator.queue_declare("generator_queue", durable=True)
    await channel_generator.basic_consume(declare_ok_generator.queue, on_generator_message)

    channel_download = await connection.channel()
    declare_ok_download = await channel_download.queue_declare("download_presentation_queue", durable=True)    # noqa E501
    await channel_download.basic_consume(declare_ok_download.queue, on_download_message)
    # async with AsyncSessionLocal() as db:                                                 # noqa E800
        # a = await get_presentation_or_none("165a57b3-0ef3-4cb2-8818-e91854a68b1b", db)    # noqa E116
        # await reduce_balance_by_user_uuid("5ef0c392-8a5b-41bd-92d1-8344ca5837e5", db)     # noqa E116
    # print(a.title)                                                                        # noqa E800
    # print(await db_query())                                                               # noqa E800
    # await create_db_presentation("5ef0c392-8a5b-41bd-92d1-8344ca5837e5", "huy", "classic")   # noqa E800

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.run_forever()
