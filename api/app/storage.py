"""
Object storage abstraction. `LocalObjectStorage` is a real, working
implementation backed by the local filesystem — used for local dev and for
tests, since this sandbox has no MinIO to test against. Swap in a
boto3/MinIO-backed implementation behind the same three methods for a real
deployment; nothing calling this interface needs to change.

Path convention matches SYSTEM_DESIGN.md: {org_id}/{case_id}/{doc_id}/v{version}
— this is what prevents cross-tenant object traversal in a single bucket.
"""

import hashlib
import os
from abc import ABC, abstractmethod
from pathlib import Path


class ObjectStorage(ABC):
    @abstractmethod
    def put(self, key: str, data: bytes) -> None: ...

    @abstractmethod
    def get(self, key: str) -> bytes: ...

    @abstractmethod
    def exists(self, key: str) -> bool: ...


class LocalObjectStorage(ObjectStorage):
    """Disk-backed. Not encrypted at rest — SYSTEM_DESIGN.md's encryption
    requirement (AES-256 via MinIO server-side encryption) applies to the
    real deployment target, not this local/test stand-in."""

    def __init__(self, root: str):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        # key is always our own {org_id}/{case_id}/{doc_id}/v{version} —
        # reject anything that looks like it's trying to escape root.
        full = (self.root / key).resolve()
        if self.root.resolve() not in full.parents and full != self.root.resolve():
            raise ValueError(f"Refusing to write outside storage root: {key}")
        return full

    def put(self, key: str, data: bytes) -> None:
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)

    def get(self, key: str) -> bytes:
        with open(self._path(key), "rb") as f:
            return f.read()

    def exists(self, key: str) -> bool:
        return self._path(key).exists()


def object_key(org_id, case_id, doc_id, version: int) -> str:
    return f"{org_id}/{case_id}/{doc_id}/v{version}"


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


_default_storage = None


def get_storage() -> ObjectStorage:
    """FastAPI dependency. Local dir defaults to ./data/objects — override
    via OBJECT_STORAGE_LOCAL_DIR for tests so nothing pollutes the repo."""
    global _default_storage
    if _default_storage is None:
        root = os.environ.get("OBJECT_STORAGE_LOCAL_DIR", "./data/objects")
        _default_storage = LocalObjectStorage(root)
    return _default_storage
