import asyncio
import logging
import os

import aiormq
from dotenv import load_dotenv

from queue_manager.db_queries import reduce_balance_by_user_uuid, create_presentation_adapter
from queue_manager.event_message import EventMessage


load_dotenv()
logger = logging.getLogger(__name__)

# b'{"event_type":"telegram","generation_data":{"type":"topic","user_uuid":"ogo","presentation_uuid":"gogo","text_generation_model":"wdef","template":"dsf","save_path_for_images":"sds","context":"dfds"}}'
async def on_message(message):
    event_message = EventMessage(message)

    if await create_presentation_adapter(event_message):
        await reduce_balance_by_user_uuid(event_message.user_uuid)

    await message.channel.basic_ack(
        message.delivery.delivery_tag
    )


async def main():
    connection = await aiormq.connect(
        f"amqp://{os.getenv('RABBIT_LOGIN')}:{os.getenv('RABBIT_PASS')}@{os.getenv('RABBIT_HOST')}/"
    )

    channel = await connection.channel()
    await channel.basic_qos(prefetch_count=10)

    declare_ok = await channel.queue_declare("generator_queue", durable=True)
    await channel.basic_consume(declare_ok.queue, on_message)
    # async with AsyncSessionLocal() as db:
        # a = await get_presentation_or_none("165a57b3-0ef3-4cb2-8818-e91854a68b1b", db)
        # await reduce_balance_by_user_uuid("5ef0c392-8a5b-41bd-92d1-8344ca5837e5", db)
    # print(a.title)
    # print(await db_query())
    # await create_db_presentation("5ef0c392-8a5b-41bd-92d1-8344ca5837e5", "huy", "classic")

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.run_forever()
