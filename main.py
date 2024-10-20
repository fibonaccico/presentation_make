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
    pr = Presentation(text_generation_model="TWOSTEP", template="focus")
    task2 = await pr.make_presentation(
        theme="Венчурные инвестиции",
        number_of_slides=10
    )
    return task2


async def main():
        print("START")                                 # noqa T201
        import time
        st = time.time()
        task1 = await make_pres()
        print(task1)                                   # noqa T201
        task2 = Presentation.save(
            data=task1,
            save_path=path_to_file
        )
        print(task2)                                  # noqa T201

        print(f"TIME : {(time.time() - st)/60}")      # noqa T201


if __name__ == "__main__":
    asyncio.run(main())
