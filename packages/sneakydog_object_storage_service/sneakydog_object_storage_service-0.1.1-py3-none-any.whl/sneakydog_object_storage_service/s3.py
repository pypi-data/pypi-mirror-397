from typing import AsyncIterator, BinaryIO, Dict, Optional

import aioboto3
from mypy_boto3_s3 import S3Client

from sneakydog_object_storage_service.abc import AsyncObjectStorageService


class AsyncS3StorageService(AsyncObjectStorageService):
    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        region: str = None,
        ssl: bool = False,
    ):
        self.session = aioboto3.Session()
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.ssl = ssl

    async def _client(self) -> S3Client:
        return self.session.client(
            "s3",
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            use_ssl=self.ssl,
        )

    async def put_object(
        self,
        bucket: str,
        object_name: str,
        data: BinaryIO,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> str:
        async with await self._client() as s3:
            await s3.upload_fileobj(
                data,
                bucket,
                object_name,
                ExtraArgs={
                    "ContentType": content_type or "application/octet-stream",
                    "Metadata": metadata or {},
                },
            )

            return object_name

    async def get_object(
        self, bucket: str, object_name: str, chunk_size: int = 8192
    ) -> AsyncIterator[bytes]:
        async def stream():
            async with await self._client() as s3:
                response = await s3.get_object(Bucket=bucket, Key=object_name)
                body = response["Body"]  # type: ignore # type: StreamingBody
                async for chunk in body.iter_chunks(chunk_size=chunk_size):
                    if chunk:
                        yield chunk

        return stream()
