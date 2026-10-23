import os

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_API_KEY: str = os.getenv("TELEGRAM_API_KEY")
MAX_API_KEY = os.getenv("MAX_API_KEY")

TG_BASE_URL = f'https://api.telegram.org/bot{TELEGRAM_API_KEY}'

TG_URLS = {
    "document": f'{TG_BASE_URL}/sendDocument',
    "photo": f'{TG_BASE_URL}/sendPhoto',
    "video": f'{TG_BASE_URL}/sendVideo',
    "animation": f'{TG_BASE_URL}/sendAnimation',
    "message": f'{TG_BASE_URL}/sendMessage',
}
