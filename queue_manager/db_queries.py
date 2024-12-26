import logging
import os
import uuid
from enum import Enum

from dotenv import load_dotenv
from sqlalchemy import text

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from make_presentation import Presentation
from make_presentation.DTO import PresentationDTO
from queue_manager.event_message import EventMessage
from queue_manager.schemas import PaySchema
from queue_manager.schemas import PresentationSchema

load_dotenv()
logger = logging.getLogger(__name__)

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

SQLALCHEMY_DATABASE_URL = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
async_engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


class PresentationStatus(str, Enum):
    IN_PROGRESS = "in progress"
    READY = "ready"
    ERROR = "error"


async def _get_presentation_or_none(presentation_uuid: str, db: AsyncSession):
    result = await db.execute(
        text("SELECT * FROM presentation WHERE uuid = :presentation_uuid"),
        {"presentation_uuid": presentation_uuid}
    )
    if row := result.mappings().first():
        return PresentationSchema(**row)
    return None


async def _create_presentation_raw(
    presentation_uuid: uuid.UUID,
    presentation: PresentationDTO,
    db: AsyncSession,
):
    for slide in presentation.slides:
        # Insert slide into the database
        slide_query = text("""
            INSERT INTO slide (uuid, presentation_uuid, number, title, text, subtitle1, subtitle2, subtitle3)
            VALUES (:uuid, :presentation_uuid, :number, :title, :text, :subtitle_1, :subtitle_2, :subtitle_3)
            RETURNING uuid
        """)
        slide_params = {
            "uuid": str(uuid.uuid4),
            "presentation_uuid": presentation_uuid,
            "number": slide.number,
            "title": slide.title,
            "text": slide.text,
            "subtitle_1": slide.subtitle_1,
            "subtitle_2": slide.subtitle_2,
            "subtitle_3": slide.subtitle_3
        }
        result = await db.execute(slide_query, slide_params)
        db_slide_uuid = result.scalar()

        image_count = 1
        if slide.images:
            for image in slide.images:
                path_list = image.path.split("/")
                user_dir, presentation_dir, filename = (
                    path_list[-3],
                    path_list[-2],
                    path_list[-1],
                )
                # Insert image into the database
                image_query = text("""
                    INSERT INTO image (uuid, slide_uuid, number, description, local_file_path, api_url)
                    VALUES (:uuid, :slide_uuid, :number, :description, :local_file_path, :api_url)
                """)
                image_params = {
                    "uuid": str(uuid.uuid4),
                    "slide_uuid": db_slide_uuid,
                    "number": image_count,
                    "description": image.description,
                    "local_file_path": image.path,
                    "api_url": f"https://fibonaccico.ru/api/image/{user_dir}/{presentation_dir}/{filename}",
                }
                await db.execute(image_query, image_params)
                image_count += 1

    # Update presentation title and status
    update_presentation_query = text("""
        UPDATE presentation
        SET title = :title, status = :status
        WHERE uuid = :uuid
    """)
    update_presentation_params = {
        "title": presentation.theme,
        "status": PresentationStatus.READY.value,
        "uuid": presentation_uuid
    }
    await db.execute(update_presentation_query, update_presentation_params)
    await db.commit()


async def reduce_balance_by_user_uuid(user_uuid: str, *, qty: int = -1):
    query = text("""
    SELECT * FROM pay
    WHERE user_uuid = :user_uuid AND status = 'succeeded' AND paid_qty != 0
    ORDER BY created_at ASC
    LIMIT 1
    """)
    query_param = {"user_uuid": user_uuid}

    async with AsyncSessionLocal() as db:
        if row := (await db.execute(query, query_param)).mappings().first():
            db_pay = PaySchema(**row)

            new_paid_qty = db_pay.paid_qty + qty
            update_query = text("""
            UPDATE pay
            SET paid_qty = :new_paid_qty
            WHERE uuid = :pay_uuid
            """)
            update_query_params = {"new_paid_qty": new_paid_qty, "pay_uuid": db_pay.uuid}
            await db.execute(update_query, update_query_params)
            await db.commit()

            return db_pay

    return None


async def create_presentation_adapter(message: EventMessage):
    os.makedirs(message.save_path_for_images, exist_ok=True)
    print(message.save_path_for_images)
    async with AsyncSessionLocal() as db:
        try:
            pr = await Presentation(
                text_generation_model=message.gen_model, template=message.template
            ).make_presentation(
                save_path_for_images=message.save_path_for_images,
                context=message.context
            )

            db_presentation = await _get_presentation_or_none(message.presentation_uuid, db)

            await _create_presentation_raw(
                presentation_uuid=db_presentation,
                presentation=pr,
                db=db,
            )

            generate_started = True

        except Exception as e:
            err_pr_status_query = text("""
                        UPDATE presentation
                        SET status = :status
                        WHERE uuid = :presentation_uuid
                        """)
            err_pr_status_query_params = {
                "status": PresentationStatus.ERROR.value,
                "presentation_uuid": message.presentation_uuid
            }
            await db.execute(err_pr_status_query, err_pr_status_query_params)
            await db.commit()
            generate_started = False
            logger.error(f"Presentation {message.presentation_uuid} not generated. Reason: {e}")

    return generate_started
