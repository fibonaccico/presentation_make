import asyncio
import os

from make_presentation.config import path_to_file
from make_presentation.presentation import Presentation  # noqa E800
from make_presentation.presentation_pptx import PresentationPPTX

choice = input("\n1. По теме\n2. По тексту\nВыберите тип генерации презентации: ")
if choice == "1":
    theme = input("Введите тему презентации: ")
    text = ''
    pr = PresentationPPTX(text_generation_model="TWOSTEP", theme=theme)
elif choice == "2":
    text = input("Введите текст: ")
    pr = PresentationPPTX(text_generation_model="FROMTEXT")


save_path_for_images = os.path.join(path_to_file, "images")


async def main():
        print("START")                                 # noqa T201
        import time
        st = time.time()
        task1 = asyncio.create_task(
            pr.make_presentation(
                save_path_for_images=save_path_for_images,
                text=text
            )
        )
        t = await task1
        print(t)                                       # noqa T201     
        print(f"TIME : {(time.time() - st)/60}")       # noqa T201


if __name__ == "__main__":
    asyncio.run(main())
