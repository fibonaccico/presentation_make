import asyncio
import logging
import os

from make_presentation import Presentation
from make_presentation.config import path_to_file

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
        context="Статистика добычи нефти в 2025 году и от чего зависило изменение цены на нефть в 2022 - 2025 годах",
        number_of_slides=5
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
        task2 = Presentation.save(
            data=task1,
            no_logo=False,
            save_path=path_to_file,
            format="pdf"
        )
        print(task2)                                  # noqa T201

        print(f"TIME : {(time.time() - st)/60}")      # noqa T201


if __name__ == "__main__":
    asyncio.run(main())
