import os
from contextlib import asynccontextmanager

from aiobotocore.session import get_session
from dotenv import load_dotenv

from config.logger import get_logger

session = get_session()
logger = get_logger()
load_dotenv()


class S3Client:
    def __init__(self):
        self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.region_name = os.getenv("AWS_REGION_NAME")
        self.bucket_name = os.getenv("AWS_BUCKET_NAME")
        self.session = get_session()

    @asynccontextmanager
    async def get_client(self):
        async with self.session.create_client(
            's3',
            region_name=self.region_name,
            aws_secret_access_key=self.aws_secret_access_key,
            aws_access_key_id=self.aws_access_key_id
        ) as client:
            yield client

    async def upload_file(
        self,
        data: bytes,
        object_name: str
    ) -> None:
        async with self.get_client() as client:
            await client.put_object(
                Bucket=self.bucket_name,
                Key=object_name,
                Body=data,
            )

    async def download_file(
        self,
        key: str
    ) -> bytes:
        async with self.get_client() as client:
            resp = await client.get_object(
                Bucket=self.bucket_name,
                Key=key
            )
            async with resp['Body'] as stream:
                data = await stream.read()
        return data
