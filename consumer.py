import asyncio
import os

import aiohttp
import aiormq
from dotenv import load_dotenv

from config.logger import get_logger
from make_presentation import Presentation
from make_presentation.DTO import ImageInfoDTO
from make_presentation.DTO import PresentationDTO
from make_presentation.DTO import SlideDTO
from queue_manager.SQL_responses import PresentationSQL
from queue_manager.db_queries import create_presentation_adapter
from queue_manager.db_queries import get_presentation_dto_or_none
from queue_manager.db_queries import reduce_balance_by_user_uuid
from queue_manager.db_queries import telegram_id_by_user_uuid
from queue_manager.event_message import EventMessage
from queue_manager.event_message import EventType


load_dotenv()
logger = get_logger()


async def send_document(token: str, chat_id: str, file_path: str) -> None:
    url = f'https://api.telegram.org/bot{token}/sendDocument'

    async with aiohttp.ClientSession() as session:
        with open(file_path, 'rb') as file:
            data = aiohttp.FormData()
            data.add_field('chat_id', chat_id)
            data.add_field('document', file, filename=file_path.split('/')[-1])

            async with session.post(url, data=data) as response:
                await response.text()


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


# b'{"event_type":"telegram","generation_data":{"save_presentation_path": /path/to/pres, "type":"topic","user_uuid":"ogo","presentation_uuid":"gogo","text_generation_model":"wdef","template":"dsf","save_path_for_images":"sds","context":"dfds"}}'
async def on_generator_message(message):
    event_message = EventMessage(message)
    logger.info(f"Starting generate from message {event_message.__dict__}")

    match event_message.event_type:
        case EventType.WEB.value:
            generate_started, presentation_data = await create_presentation_adapter(event_message)
            if generate_started:
                await reduce_balance_by_user_uuid(event_message.user_uuid)

            await message.channel.basic_ack(
                message.delivery.delivery_tag
            )

        case EventType.TELEGRAM.value:
            generate_started, presentation_data = await create_presentation_adapter(event_message)
            if generate_started:
                await reduce_balance_by_user_uuid(event_message.user_uuid)

            await message.channel.basic_ack(
                message.delivery.delivery_tag
            )

            try:
                await send_document(
                    os.getenv("TELEGRAM_API_KEY"),
                    await telegram_id_by_user_uuid(event_message.user_uuid),
                    Presentation.save(
                        data=presentation_data,
                        save_path=event_message.save_presentation_path,
                        format=event_message.format_file
                    ),

                )
            except Exception as e:
                logger.error(f"Presentation sending failed: {e}")

        case _:
            logger.warning(f"Unknown event type {event_message.event_type} in generator_queue")



async def on_download_message(message):
    event_message = EventMessage(message)
    logger.info(f"Starting download from message {event_message.__dict__}")

    match event_message.event_type:
        case EventType.DOWNLOAD.value:
            if db_presentation := await get_presentation_dto_or_none(event_message.presentation_uuid):
                try:
                    logger.info(f"Save presentation to {event_message.save_presentation_path}")
                    presentation_path = Presentation.save(
                        data=create_presentation_dto(db_presentation),
                        save_path=event_message.save_presentation_path,
                        format=event_message.format_file
                    )

                    logger.info(f"Getting telegram of user {event_message.user_uuid} for send presentation")
                    telegram_id = await telegram_id_by_user_uuid(event_message.user_uuid)

                    logger.info(f"Sending presentation {event_message.save_presentation_path} to {telegram_id}")
                    await send_document(
                        os.getenv("TELEGRAM_API_KEY"),
                        telegram_id,
                        presentation_path
                    )
                except Exception as e:
                    logger.error(f"Presentation sending failed: {e}")

        case _:
            logger.warning(f"Unknown event type {event_message.event_type} in download_presentation_queue")

    await message.channel.basic_ack(
        message.delivery.delivery_tag
    )


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
    declare_ok_download = await channel_download.queue_declare("download_presentation_queue", durable=True)
    await channel_download.basic_consume(declare_ok_download.queue, on_download_message)
    # async with AsyncSessionLocal() as db:
        # a = await get_presentation_or_none("165a57b3-0ef3-4cb2-8818-e91854a68b1b", db)
        # await reduce_balance_by_user_uuid("5ef0c392-8a5b-41bd-92d1-8344ca5837e5", db)
    # print(a.title)
    # print(await db_query())
    # await create_db_presentation("5ef0c392-8a5b-41bd-92d1-8344ca5837e5", "huy", "classic")

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.run_forever()
