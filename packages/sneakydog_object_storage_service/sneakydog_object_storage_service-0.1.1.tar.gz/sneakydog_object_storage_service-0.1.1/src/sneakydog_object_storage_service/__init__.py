import os
from importlib.metadata import entry_points
from typing import Type

from sneakydog_object_storage_service.abc import AsyncObjectStorageService


def NewInstance(**kwargs) -> AsyncObjectStorageService:
    oss_type = os.getenv("OSS_TYPE") or kwargs.pop("oss_type", None)
    if not oss_type:
        raise RuntimeError(
            "OSS_TYPE is required. "
            "Set environment variable OSS_TYPE or pass oss_type=..."
        )

    oss_type = oss_type.lower()
    eps = entry_points(group="storage")
    if oss_type not in eps.names:
        raise RuntimeError(
            f"Storage provider '{oss_type}' not found. Available: {list(eps.names)}"
        )

    cls: Type[AsyncObjectStorageService] = eps[oss_type].load()
    return cls(**kwargs)


__all__ = [
    "AsyncObjectStorageService",
    "NewInstance",
]
