from contextlib import asynccontextmanager
from typing import AsyncIterator

from aiobotocore.session import get_session, AioSession
from botocore.exceptions import ClientError


class S3Client:
    """
    Универсальный асинхронный клиент для S3‑совместимых хранилищ.

    Использование:

        s3 = S3Client(
            access_key=...,
            secret_key=...,
            endpoint_url=...,
            bucket_name=...,
        )
        await s3.upload_bytes("path/to.obj", b"...")
        url = s3.object_url("path/to.obj")
    """

    def __init__(
        self,
        access_key: str,
        secret_key: str,
        endpoint_url: str,
        bucket_name: str,
    ) -> None:
        self._config = {
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "endpoint_url": endpoint_url,
        }
        self.bucket_name = bucket_name
        self._session: AioSession = get_session()

    @asynccontextmanager
    async def get_client(self) -> AsyncIterator:
        async with self._session.create_client("s3", **self._config) as client:
            yield client

    async def upload_bytes(self, object_name: str, data: bytes) -> str:
        """Загрузить байты под указанным ключом и вернуть прямой URL объекта."""
        async with self.get_client() as client:
            await client.put_object(
                Bucket=self.bucket_name,
                Key=object_name,
                Body=data,
            )
        return self.object_url(object_name)

    def object_url(self, object_name: str) -> str:
        base = (self._config.get("endpoint_url") or "").rstrip("/")
        return f"{base}/{self.bucket_name}/{object_name}"

    async def print_bucket_location(self) -> None:
        try:
            async with self.get_client() as client:
                resp = await client.get_bucket_location(Bucket=self.bucket_name)
                location = resp.get("LocationConstraint")
                print(f"Bucket location: {location}")
        except ClientError as e:
            print(f"Error getting bucket location: {e}")

    async def delete_file(self, object_name: str) -> None:
        try:
            async with self.get_client() as client:
                await client.delete_object(Bucket=self.bucket_name, Key=object_name)
                print(f"File {object_name} deleted from {self.bucket_name}")
        except ClientError as e:
            print(f"Error deleting file: {e}")

    async def get_file(self, object_name: str, destination_path: str) -> None:
        try:
            async with self.get_client() as client:
                response = await client.get_object(Bucket=self.bucket_name, Key=object_name)
                data = await response["Body"].read()
                with open(destination_path, "wb") as file:
                    file.write(data)
                print(f"File {object_name} downloaded to {destination_path}")
        except ClientError as e:
            print(f"Error downloading file: {e}")


