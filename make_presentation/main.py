import asyncio
import os

from config import path_to_file
from presentation import Presentation
from presentation_pptx import PresentationPPTX

theme = "Поэзия Росии золотой век"

pr = PresentationPPTX(theme=theme)
save_path_for_images = os.path.join(path_to_file, "images")

pr1 = Presentation(theme=theme)


async def main():
    if __name__ == "__main__":
        task1 = asyncio.create_task(
            pr1.make_presentation(save_path_for_images=save_path_for_images)
        )
        await task1


asyncio.run(main())
