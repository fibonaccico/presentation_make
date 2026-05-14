import asyncio
import logging
import os

import aiohttp

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
        print(f"Sending file {task2} into MAX")
        filename = task2.split('/')[-1]
        headers = {
            'Authorization': os.getenv('MAX_API_KEY'),
            'Content-Type': 'application/json'
        }
        # получение ссылки для загрузки файла
        async with aiohttp.ClientSession() as session:
            url_to_get_link = "https://platform-api.max.ru/uploads?type=file"
            try:
                async with session.post(url=url_to_get_link, headers=headers) as response:
                    res = await response.json()
                    # status = await response.status
                    # f = await response.text()
                    print(res)
                    link_to_upload = dict(res).get("url")
                    print(f'Got link to file upload. link: {link_to_upload}')
            except Exception as err:
                print(f"Cannot get link to upload. Reason: {err}")

        async with aiohttp.ClientSession() as session:
            with open(task2, 'rb') as file:
                data = aiohttp.FormData()
                data.add_field('document', file, filename=filename)
                try:
                    async with session.post(link_to_upload, data=data) as response:
                        result = await response.json()
                        file_token = dict(result).get("token")
                        print(f"Пользователь [user_id: ]. Файл загружен: [{task2}]. Result: {result}")
                except Exception as err:
                    print(f"Пользователь [user_i]. Cannot upload file: [{task2}]. Reason: {err}")
        await asyncio.sleep(2.0)
        data_message = {
            "text": "",
            "attachments": [
                {
                    "type": "file",
                    "payload": {
                        "token": file_token
                    }
                }
            ]
        }

        async with aiohttp.ClientSession() as session:
            url = 'https://platform-api.max.ru/messages?user_id=248895493'
            async with session.post(url, json=data_message, headers=headers) as response:
                status = response.status
                if status == 200:
                    print(f'Сообщение [{data_message}] отправлено пользователю в MAX [user_id:]')
                    await response.text()
                else:
                    print(
                        f'Ошибка отправки сообщения польователю в MAX [user_id: ]. '
                        f'Сообщение: [{data_message}]. Причина: {response.reason}')
        print(f"TIME : {(time.time() - st)/60}")      # noqa T201


if __name__ == "__main__":
    asyncio.run(main())
