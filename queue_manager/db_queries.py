import os
import typing as t
import uuid
from datetime import datetime
from enum import Enum

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from config.logger import get_logger
from make_presentation import Presentation
from make_presentation.DTO import PresentationDTO
from make_presentation.DTO.image_dto import ImageDTO, ImageInfoDTO
from queue_manager.event_message import EventMessage
from queue_manager.schemas import PaySchema, PresentationSchema
from queue_manager.services import YookassaPayment
from queue_manager.SQL_responses import (ImageInfoSQL, ImageSQL,
                                         PresentationSQL, SlideSQL)

load_dotenv()
logger = get_logger()

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


async def get_image_by_uuid(image_uuid: str) -> t.Optional[ImageSQL]:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            text(
                """
                    SELECT 
                        uuid,
                        local_file_path, 
                        description, 
                        slide_uuid,
                        number,
                        style, 
                        regenerate_status, 
                        regenerate_attempts 
                    FROM 
                        image 
                    WHERE 
                        uuid = :image_uuid
                """
            ),
            {"image_uuid": image_uuid}
        )
        if row := result.mappings().first():
            return ImageSQL(**row)
        return None


async def set_presentation_local_file_path(presentation_uuid: str, local_file_path: str):
    update_query = text(
            """
                UPDATE presentation
                SET local_file_path = :local_file_path
                WHERE uuid = :presentation_uuid
            """
        )
    update_params = {"local_file_path": local_file_path, "presentation_uuid": presentation_uuid}
    async with AsyncSessionLocal() as db:
        await db.execute(update_query, update_params)
        await db.commit()


async def _get_presentation_or_none(presentation_uuid: str, db: AsyncSession):
    result = await db.execute(
        text("SELECT * FROM presentation WHERE uuid = :presentation_uuid"),
        {"presentation_uuid": presentation_uuid}
    )
    if row := result.mappings().first():
        return PresentationSchema(**row)
    return None


async def get_images_dto_list(db: AsyncSessionLocal, slide_uuid: str) -> t.List[ImageInfoSQL | None]:
    images: t.List[ImageInfoSQL] = []

    result = await db.execute(
        text(
            "SELECT local_file_path, description, style "
            "FROM image WHERE slide_uuid = :slide_uuid"
        ),
        {"slide_uuid": slide_uuid}
    )
    for row in result:
        image = ImageInfoSQL(
            local_file_path=row[0],
            description=row[1],
            style=row[2]
        )
        images.append(image)

    return images


async def get_slides_dto_list(db: AsyncSessionLocal, presentation_uuid: str) -> t.List[SlideSQL | None]:
    slides: t.List[SlideSQL] = []

    result = await db.execute(
        text(
            "SELECT uuid, number, title, text, subtitle1, subtitle2, subtitle3 "
            "FROM slide WHERE presentation_uuid = :presentation_uuid"
        ),
        {"presentation_uuid": presentation_uuid}
    )
    for row in result:
        slide_uuid = row[0]
        slide = SlideSQL(
            uuid=slide_uuid,
            number=row[1],
            title=row[2],
            text=row[3],
            subtitle1=row[4],
            subtitle2=row[5],
            subtitle3=row[6],
            images=await get_images_dto_list(db, slide_uuid)
        )
        slides.append(slide)

    return slides


async def get_presentation_dto_or_none(presentation_uuid: str) -> t.Optional[PresentationSQL]:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            text("SELECT template, title FROM presentation WHERE uuid = :presentation_uuid"),
            {"presentation_uuid": presentation_uuid}
        )
        if row := result.mappings().first():
            return PresentationSQL(slides=await get_slides_dto_list(db, presentation_uuid), **row)
        return None


async def create_image_db(new_image_data: ImageInfoDTO, slide_uuid: str, slide_number: int) -> None:
    path_list = new_image_data.path.split("/")
    user_dir, presentation_dir, filename = (
        path_list[-3],
        path_list[-2],
        path_list[-1],
    )
    image_query = text("""
        INSERT INTO image (uuid, slide_uuid, number, description, local_file_path, api_url, style, regenerate_status)
        VALUES (:uuid, :slide_uuid, :number, :description, :local_file_path, :api_url, :style, :regenerate_status)
    """)
    image_params = {
        "uuid": str(uuid.uuid4()),
        "slide_uuid": slide_uuid,
        "number": slide_number,
        "description": new_image_data.description,
        "local_file_path": new_image_data.path,
        "api_url": f"https://fibonaccico.ru/api/image/{user_dir}/{presentation_dir}/{filename}",
        "style": new_image_data.style,
        "regenerate_status": "ACTIV"
    }

    async with AsyncSessionLocal() as db:
        await db.execute(image_query, image_params)
        await db.commit()


async def update_candidate_image_db(image_uuid: str, new_image_data: ImageDTO) -> None:
    path_list = new_image_data.path.split("/")
    user_dir, presentation_dir, filename = (
        path_list[-3],
        path_list[-2],
        path_list[-1],
    )
    update_image_query = text("""
            UPDATE image
            SET local_file_path = :local_file_path, api_url = :api_url
            WHERE uuid = :image_uuid
        """)
    update_image_params = {
        "local_file_path": new_image_data.path,
        "api_url": f"https://fibonaccico.ru/api/image/{user_dir}/{presentation_dir}/{filename}",
        "image_uuid": image_uuid
    }

    async with AsyncSessionLocal() as db:
        await db.execute(update_image_query, update_image_params)
        await db.commit()


async def _create_presentation_raw(
    presentation_uuid: uuid.UUID,
    presentation: PresentationDTO,
    db: AsyncSession,
):
    for slide in presentation.slides:
        # Insert slide into the database
        slide_query = text("""
            INSERT INTO slide (uuid, presentation_uuid, number, title, text, subtitle1, subtitle2, subtitle3)
            VALUES (:uuid, :presentation_uuid, :number, :title, :text, :subtitle1, :subtitle2, :subtitle3)
            RETURNING uuid
        """)
        db_slide_uuid = str(uuid.uuid4())
        slide_params = {
            "uuid": db_slide_uuid,
            "presentation_uuid": str(presentation_uuid),
            "number": slide.number,
            "title": slide.title,
            "text": slide.text,
            "subtitle1": slide.subtitle_1,
            "subtitle2": slide.subtitle_2,
            "subtitle3": slide.subtitle_3
        }
        await db.execute(slide_query, slide_params)
        await db.commit()

        image_count = 1
        if slide.images:
            for image in slide.images:
                await create_image_db(image, db_slide_uuid, image_count)

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
        "uuid": str(presentation_uuid)
    }
    await db.execute(update_presentation_query, update_presentation_params)
    await db.commit()


async def reduce_balance_by_user_uuid(user_uuid: str, is_paid: bool, *, qty: int = -1):
    query = text("""
    SELECT * FROM pay
    WHERE user_uuid = :user_uuid AND status = 'succeeded' AND paid_qty != 0
    ORDER BY created_at ASC
    LIMIT 1
    """)
    if is_paid:
        query = text("""
        SELECT * FROM pay
        WHERE user_uuid = :user_uuid AND status = 'succeeded' AND paid_qty != 0 AND sum > 0
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


async def create_presentation_adapter(message: EventMessage) -> PresentationDTO:
    os.makedirs(message.save_path_for_images, exist_ok=True)
    pr = None

    async with AsyncSessionLocal() as db:
        try:
            logger.warning(message.__dict__)
            pr = await Presentation(
                text_generation_model=message.gen_model, template=message.template
            ).make_presentation(
                save_path_for_images=message.save_path_for_images,
                context=message.context,
                number_of_slides=message.number_of_slides,
                image_style=message.image_style,
                language=message.language
            )

            db_presentation = await _get_presentation_or_none(message.presentation_uuid, db)
            await _create_presentation_raw(
                presentation_uuid=db_presentation.uuid,
                presentation=pr,
                db=db,
            )

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

            logger.error(f"Presentation {message.presentation_uuid} not generated. Reason: {e}")

    return pr


async def telegram_id_by_user_uuid(user_uuid: str):
    async with AsyncSessionLocal() as db:
        return (await db.execute(
            text("SELECT telegram_id FROM public.user WHERE uuid = :user_uuid"),
            {"user_uuid": user_uuid}
        )).scalars().first()


async def get_user_by_user_uuid(user_uuid: str):
    async with AsyncSessionLocal() as db:
        return (await db.execute(
            text("SELECT * FROM public.user WHERE uuid = :user_uuid"),
            {"user_uuid": user_uuid}
        )).first()


async def get_locale_by_user_uuid(user_uuid: str) -> str:
    async with AsyncSessionLocal() as db:
        return (await db.execute(
            text("SELECT settings FROM public.user WHERE uuid = :user_uuid"),
            {"user_uuid": user_uuid}
        )).scalars().first().get("locale")


async def get_last_user_payment(user_uuid: str):
    async with AsyncSessionLocal() as db:
        return (await db.execute(
            text("SELECT * FROM pay WHERE user_uuid = :user_uuid AND status = 'succeeded' AND payment_service = 'yookassa' AND sum > 0 ORDER BY created_at DESC"),
            {"user_uuid": user_uuid}
        )).first()


async def get_tariff_data(tariff_id: str):
    async with AsyncSessionLocal() as db:
        return (await db.execute(
            text("SELECT * FROM tariff WHERE id = :tariff_id"),
            {"tariff_id": tariff_id}
        )).first()


async def get_user_referral_code(user_uuid: str):
    async with AsyncSessionLocal() as db:
        return (await db.execute(
            text("SELECT * FROM referral_code WHERE user_uuid = :user_uuid"),
            {"user_uuid": user_uuid}
        )).first()


async def create_auto_pay(
    user_uuid: str,
    payment_data: YookassaPayment,
    status: str,
    paid_qty: int,
    tariff_id: int
):
    payment_query = text("""
        INSERT INTO pay (uuid, user_uuid, yookassa_pay_id, status, sum, paid_qty, tariff_id, created_at)
        VALUES (:uuid, :user_uuid, :yookassa_pay_id, :status, :sum, :paid_qty, :tariff_id, :created_at)
    """)
    payment_params = {
        "uuid": str(uuid.uuid4()),
        "user_uuid": user_uuid,
        "yookassa_pay_id": payment_data.id,
        "status": status,
        "sum": payment_data.amount,
        "paid_qty": paid_qty,
        "tariff_id": tariff_id,
        "created_at": datetime.now()
    }

    async with AsyncSessionLocal() as db:
        await db.execute(payment_query, payment_params)
        await db.commit()


async def create_pay(
    user_uuid: str,
    yookassa_pay_id: str,
    amount: int,
    status: str,
    paid_qty: int,
    tariff_id: int
):
    payment_query = text("""
        INSERT INTO pay (uuid, user_uuid, yookassa_pay_id, status, sum, paid_qty, tariff_id, created_at)
        VALUES (:uuid, :user_uuid, :yookassa_pay_id, :status, :sum, :paid_qty, :tariff_id, :created_at)
    """)
    payment_params = {
        "uuid": str(uuid.uuid4()),
        "user_uuid": user_uuid,
        "yookassa_pay_id": yookassa_pay_id,
        "status": status,
        "sum": amount,
        "paid_qty": paid_qty,
        "tariff_id": tariff_id,
        "created_at": datetime.now()
    }

    async with AsyncSessionLocal() as db:
        await db.execute(payment_query, payment_params)
        await db.commit()





async def remove_auto_pay_for_user(user_uuid: str):
    update_query = text("""
                UPDATE public.user
                SET auto_pay = false, auto_pay_id = NULL, tariff = 'NONE'
                WHERE uuid = :user_uuid
                """)
    params = {"user_uuid": user_uuid}
    async with AsyncSessionLocal() as db:
        await db.execute(update_query, params)
        await db.commit()
