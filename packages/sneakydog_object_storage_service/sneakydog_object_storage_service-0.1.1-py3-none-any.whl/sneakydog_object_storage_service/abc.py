from abc import ABC, abstractmethod
from typing import AsyncIterator, BinaryIO, Dict, Optional


class AsyncObjectStorageService(ABC):
    @abstractmethod
    async def put_object(
        self,
        bucket: str,
        object_name: str,
        data: BinaryIO,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> str: ...

    @abstractmethod
    async def get_object(
        self, bucket: str, object_name: str, chunk_size: int = 8192
    ) -> AsyncIterator[bytes]: ...
