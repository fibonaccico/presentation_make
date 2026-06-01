import asyncio
import logging
import os

import aiohttp
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from make_presentation import Presentation
from make_presentation.config import path_to_file
from queue_manager.db_queries import (create_auto_pay, get_last_user_payment,
                                      remove_auto_pay_for_user)
from queue_manager.services import YookassaPayment

absolute_path = os.path.dirname(os.path.dirname(__file__))
save_path_for_images = os.path.join(path_to_file, "images")
logging.basicConfig(
    level=logging.INFO,
    filename=os.path.join(absolute_path, "presentation_make", "log_file.log"),
    filemode="w",
    encoding="utf-8"
)


async def make_pres():
    pr = Presentation(text_generation_model="ONESTEP", template="creative")
    task2 = await pr.make_presentation(
        context="Москва",
        number_of_slides=2,
        save_path_for_images=save_path_for_images
    )
    return task2


async def main():
        print("START")                                 # noqa T201
        # pic = await Presentation.generate_picture(
        #      discription="природа Антарктиды",
        #      width=1024,
        #      height=825,
        #      style="DEFAULT",
        #      save_path=save_path_for_images
        # )
        # print(pic)
        # import time
        # st = time.time()
        # task1 = await make_pres()
        # print(task1)                                   # noqa T201
        # task2 = Presentation.save(
        #     data=task1,
        #     no_logo=False,
        #     save_path=path_to_file,
        #     format="pdf"
        # )
        # print(task2)                                  # noqa T201
        # print(f"TIME : {(time.time() - st)/60}")      # noqa T201

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
        user_uuid = '2efa3846-2de6-4118-aad0-ac035bfdc627'
        try:
            lp = await remove_auto_pay_for_user(
                user_uuid=user_uuid
                )
            # print(lp.created_at)
        except Exception as err:
            print(f"Fail reason : {err}")


if __name__ == "__main__":
    asyncio.run(main())
