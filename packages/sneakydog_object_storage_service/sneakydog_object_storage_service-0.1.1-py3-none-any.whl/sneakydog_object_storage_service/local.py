import asyncio
import os
import shutil
from typing import AsyncIterator, BinaryIO, Dict, Optional

import aiofiles

from sneakydog_object_storage_service.abc import AsyncObjectStorageService


class AsyncLocalStorageService(AsyncObjectStorageService):
    def __init__(self, root: str):
        self.root = os.path.abspath(root)

    def _path(self, bucket: str, object_name: str) -> str:
        return os.path.join(self.root, bucket, object_name)

    async def put_object(
        self,
        *,
        bucket: str,
        object_name: str,
        data: BinaryIO,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> str:
        path = self._path(bucket, object_name)
        os.makedirs(os.path.dirname(path), exist_ok=True)

        await asyncio.to_thread(
            shutil.copyfileobj,
            data,
            open(path, "wb"),
        )

        return path

    async def get_object(
        self,
        *,
        bucket: str,
        object_name: str,
        chunk_size: int = 8192,
    ) -> AsyncIterator[bytes]:
        path = self._path(bucket, object_name)

        async def stream():
            async with aiofiles.open(path, "rb") as f:
                while chunk := await f.read(chunk_size):
                    if chunk:
                        yield chunk

        return stream()
