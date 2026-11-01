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
    pr = Presentation(text_generation_model="FROMTEXT", template="premium")
    task2 = await pr.make_presentation(
        context="""Забронировать тур онлайн, заказать билеты и трансфер в приложении, изучить окрестности нового города с аудиогидом — все это давно превратилось в обыденность для современного туриста. Цифровизация не обошла стороной туризм. Перспективы развития технологий в данной сфере видят и IT-специалисты, и урбанисты.
            О предпочтениях современных туристов, популярных мировых сервисах и перспективных идеях для цифровизации туристической отрасли в России рассказала руководитель проектов консалтингового бюро ATLAS Дарья Коваленко.
            Мировой рынок туристических сервисов
            TravelTech — это относительно новая индустрия, использующая цифровые технологии для совершенствования опыта туристов и путешественников. Хотя сфера цифровых решений для индустрии туризма отстает от финансовой и образовательных решений, темпы роста этого рынка достаточно высокие. Так, по данным Statista, к 2026 году мировой рынок TravelTech может достигнуть $12,5 млрд — это на 45% больше, чем в 2020 году.
            Функциональность туристических сервисов позволяет бесшовно спланировать путешествие онлайн с использованием платформ и приложений для бронирования полноценных туров или жилья и билетов отдельно.
            Появляется все больше сопутствующих сервисов, от ускоренной регистрации в гостиницах благодаря биометрическим технологиям до умных роботов-чемоданов, которые самостоятельно следуют за хозяином и добираются до нужной локации.
            Граница между виртуальным миром и реальностью стирается за счет самостоятельных экскурсий через приложения.
            На рынке уже несколько лет существуют сервисы-компаньоны для свободных и независимых путешественников. Один из них — онлайн-карта Tmatic.travel, где собрано множество готовых маршрутов, аудиогидов, отелей, туров и экскурсий, местных экспертов. Или приложение WeGoTrip — международный маркетплейс аудиоэкскурсий с билетами в музеи, который предлагает более 500 экскурсий в 183 городах мира.
            Особенности цифровизации туристической индустрии в России
            Ежегодно в России создают около 30 новых TravelTech-стартапов. RB.ru при поддержке Комитета по туризму города Москвы создали карту рынка, где собраны компании, которые меняют туристическую индустрию с помощью технологий, — сейчас их более 300. Сегодня в связи с уходом многих мировых игроков — создателей туристических сервисов — российские разработчики, основатели стартапов и предприниматели получили высокие шансы популяризации своих TravelTech-проектов.""",
        # number_of_slides=2,
        save_path_for_images="images",
        language="en"
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
        import time
        st = time.time()
        task1 = await make_pres()
        print(task1)                                   # noqa T201
        task2 = await Presentation.save(
            data=task1,
            no_logo=True,
            save_path=path_to_file,
            format="pdf"
        )
        print(task2)                                  # noqa T201
        print(f"TIME : {(time.time() - st)/60}")      # noqa T201

        # DB_HOST = os.getenv("DB_HOST")
        # DB_PORT = os.getenv("DB_PORT")
        # DB_NAME = os.getenv("DB_NAME")
        # DB_USER = os.getenv("DB_USER")
        # DB_PASS = os.getenv("DB_PASS")

        # SQLALCHEMY_DATABASE_URL = (
        #     f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        # )
        # async_engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
        # AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
        # user_uuid = '2efa3846-2de6-4118-aad0-ac035bfdc627'
        # try:
        #     lp = await remove_auto_pay_for_user(
        #         user_uuid=user_uuid
        #         )
        #     # print(lp.created_at)
        # except Exception as err:
        #     print(f"Fail reason : {err}")


if __name__ == "__main__":
    asyncio.run(main())
