import asyncio
import os

from config import path_to_file
from presentation_pptx import PresentationPPTX

#from presentation import Presentation       # noqa E800
theme = input("Введите тему презентации: ")

pr = PresentationPPTX(theme=theme)   # pr1 = Presentation(theme=theme)
save_path_for_images = os.path.join(path_to_file, "images")


async def main():
    if __name__ == "__main__":
        print("START")                                 # noqa T201
        import time
        st = time.time()
        task1 = asyncio.create_task(
            pr.make_presentation(
                save_path_for_images=save_path_for_images
            )
        )
        t = await task1
        print(t)                                       # noqa T201     
        print(f"TIME : {(time.time() - st)/60}")       # noqa T201


asyncio.run(main())
