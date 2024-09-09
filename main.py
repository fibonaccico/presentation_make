import asyncio
import os

from dotenv import load_dotenv

from make_presentation import Presentation
from make_presentation.config import path_to_file

load_dotenv()

save_path_for_images = os.path.join(path_to_file, "images")
text_api_key = os.getenv("GIGACHAT_API_KEY")
image_api_key = os.getenv("KANDINSKY_API_KEY")
image_secret_key = os.getenv("KANDINSKY_SECRET_KEY")


async def make_pres():
    pr = Presentation(text_generation_model="TWOSTEP", template="classic")
    task2 = await pr.make_presentation(
        save_path_for_images=save_path_for_images,
        text_api_key=text_api_key,
        image_api_key=image_api_key,
        image_secret_key=image_secret_key,
        theme="Средневековая Россия"
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
            format="pptx",
            save_path=path_to_file
        )
        print(task2)                                  # noqa T201
        print(f"TIME : {(time.time() - st)/60}")      # noqa T201


if __name__ == "__main__":
    asyncio.run(main())
