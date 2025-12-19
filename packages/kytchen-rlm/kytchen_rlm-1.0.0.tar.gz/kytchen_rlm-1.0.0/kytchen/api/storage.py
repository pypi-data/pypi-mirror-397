"""Storage backends for Kytchen Cloud.

This module provides async file operations for storing dataset content.

Supported backends:
- Supabase Storage (recommended for hosted deployments)
- Local filesystem (development/testing fallback)
"""

from __future__ import annotations

import asyncio
import hashlib
import io
import os
from pathlib import Path
from typing import Protocol

import httpx


class StorageBackend(Protocol):
    async def write_dataset(self, workspace_id: str, dataset_id: str, content: bytes) -> str: ...

    async def read_dataset(self, workspace_id: str, dataset_id: str) -> bytes: ...

    async def delete_dataset(self, workspace_id: str, dataset_id: str) -> bool: ...

    async def exists(self, workspace_id: str, dataset_id: str) -> bool: ...

    async def get_size(self, workspace_id: str, dataset_id: str) -> int: ...

    async def compute_hash(self, content: bytes, algorithm: str = "sha256") -> str: ...

    async def verify_hash(self, workspace_id: str, dataset_id: str, expected_hash: str) -> bool: ...

    async def cleanup_workspace(self, workspace_id: str) -> int: ...


class FilesystemStorage:
    """Filesystem storage backend.

    This is intended for local development/testing.
    """

    def __init__(self, base_path: str | None = None) -> None:
        """Initialize storage backend.

        Args:
            base_path: Root path for storage.
        """
        if base_path is None:
            base_path = os.getenv("KYTCHEN_STORAGE_PATH", ".kytchen")

        self.base_path = Path(base_path)
        self.pantry_path = self.base_path / "pantry"

        # Ensure base directories exist
        self.pantry_path.mkdir(parents=True, exist_ok=True)

    async def write_dataset(
        self,
        workspace_id: str,
        dataset_id: str,
        content: bytes,
    ) -> str:
        """Write dataset content to storage.

        Args:
            workspace_id: UUID of the workspace
            dataset_id: UUID of the dataset
            content: Binary content to store

        Returns:
            Storage path (relative to base_path)
        """
        path = self.pantry_path / workspace_id / dataset_id
        path.parent.mkdir(parents=True, exist_ok=True)

        # Write atomically using temp file + rename
        temp_path = path.with_suffix(".tmp")
        temp_path.write_bytes(content)
        temp_path.rename(path)

        # Return relative path for storage_path column
        return str(path.relative_to(self.base_path))

    async def read_dataset(
        self,
        workspace_id: str,
        dataset_id: str,
    ) -> bytes:
        """Read dataset content from storage.

        Args:
            workspace_id: UUID of the workspace
            dataset_id: UUID of the dataset

        Returns:
            Binary content

        Raises:
            FileNotFoundError: If dataset doesn't exist
        """
        path = self.pantry_path / workspace_id / dataset_id
        return path.read_bytes()

    async def delete_dataset(
        self,
        workspace_id: str,
        dataset_id: str,
    ) -> bool:
        """Delete dataset content from storage.

        Args:
            workspace_id: UUID of the workspace
            dataset_id: UUID of the dataset

        Returns:
            True if deleted, False if not found
        """
        path = self.pantry_path / workspace_id / dataset_id
        if path.exists():
            path.unlink()
            return True
        return False

    async def exists(
        self,
        workspace_id: str,
        dataset_id: str,
    ) -> bool:
        """Check if dataset exists in storage.

        Args:
            workspace_id: UUID of the workspace
            dataset_id: UUID of the dataset

        Returns:
            True if exists, False otherwise
        """
        path = self.pantry_path / workspace_id / dataset_id
        return path.exists()

    async def get_size(
        self,
        workspace_id: str,
        dataset_id: str,
    ) -> int:
        """Get size of dataset in bytes.

        Args:
            workspace_id: UUID of the workspace
            dataset_id: UUID of the dataset

        Returns:
            Size in bytes

        Raises:
            FileNotFoundError: If dataset doesn't exist
        """
        path = self.pantry_path / workspace_id / dataset_id
        return path.stat().st_size

    async def compute_hash(
        self,
        content: bytes,
        algorithm: str = "sha256",
    ) -> str:
        """Compute hash of content.

        Args:
            content: Binary content
            algorithm: Hash algorithm (sha256, md5, etc.)

        Returns:
            Hash string with algorithm prefix (e.g., "sha256:abc123...")
        """
        hasher = hashlib.new(algorithm)
        hasher.update(content)
        return f"{algorithm}:{hasher.hexdigest()}"

    async def verify_hash(
        self,
        workspace_id: str,
        dataset_id: str,
        expected_hash: str,
    ) -> bool:
        """Verify dataset content matches expected hash.

        Args:
            workspace_id: UUID of the workspace
            dataset_id: UUID of the dataset
            expected_hash: Expected hash with algorithm prefix

        Returns:
            True if hash matches, False otherwise
        """
        try:
            content = await self.read_dataset(workspace_id, dataset_id)
            algorithm = expected_hash.split(":", 1)[0] if ":" in expected_hash else "sha256"
            actual_hash = await self.compute_hash(content, algorithm)
            return actual_hash == expected_hash
        except FileNotFoundError:
            return False

    async def cleanup_workspace(self, workspace_id: str) -> int:
        """Delete all datasets for a workspace.

        Args:
            workspace_id: UUID of the workspace

        Returns:
            Number of datasets deleted
        """
        workspace_dir = self.pantry_path / workspace_id
        if not workspace_dir.exists():
            return 0

        count = 0
        for dataset_file in workspace_dir.iterdir():
            if dataset_file.is_file():
                dataset_file.unlink()
                count += 1

        # Remove empty workspace directory
        try:
            workspace_dir.rmdir()
        except OSError:
            pass  # Directory not empty (shouldn't happen)

        return count


class SupabaseStorage:
    """Supabase Storage backend.

    Requires:
    - SUPABASE_URL
    - SUPABASE_SERVICE_ROLE_KEY

    Optionally:
    - SUPABASE_STORAGE_BUCKET (default: "pantry")
    """

    def __init__(self) -> None:
        self.supabase_url = os.environ["SUPABASE_URL"].rstrip("/")
        self.service_role_key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
        self.bucket = os.getenv("SUPABASE_STORAGE_BUCKET", "pantry")

    def _object_path(self, workspace_id: str, dataset_id: str) -> str:
        return f"{workspace_id}/{dataset_id}"

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.service_role_key}",
            "apikey": self.service_role_key,
        }

    def _object_url(self, workspace_id: str, dataset_id: str) -> str:
        path = self._object_path(workspace_id, dataset_id)
        return f"{self.supabase_url}/storage/v1/object/{self.bucket}/{path}"

    async def write_dataset(self, workspace_id: str, dataset_id: str, content: bytes) -> str:
        url = self._object_url(workspace_id, dataset_id)
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.put(url, headers=self._headers(), content=content)
            resp.raise_for_status()
        return self._object_path(workspace_id, dataset_id)

    async def read_dataset(self, workspace_id: str, dataset_id: str) -> bytes:
        url = self._object_url(workspace_id, dataset_id)
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.get(url, headers=self._headers())
            resp.raise_for_status()
            return resp.content

    async def delete_dataset(self, workspace_id: str, dataset_id: str) -> bool:
        url = self._object_url(workspace_id, dataset_id)
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.delete(url, headers=self._headers())
            if resp.status_code == 404:
                return False
            resp.raise_for_status()
        return True

    async def exists(self, workspace_id: str, dataset_id: str) -> bool:
        url = self._object_url(workspace_id, dataset_id)
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.head(url, headers=self._headers())
            if resp.status_code == 404:
                return False
            resp.raise_for_status()
        return True

    async def get_size(self, workspace_id: str, dataset_id: str) -> int:
        url = self._object_url(workspace_id, dataset_id)
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.head(url, headers=self._headers())
            if resp.status_code == 404:
                raise FileNotFoundError(dataset_id)
            resp.raise_for_status()
            size = resp.headers.get("content-length")
            return int(size) if size is not None else 0

    async def compute_hash(self, content: bytes, algorithm: str = "sha256") -> str:
        hasher = hashlib.new(algorithm)
        hasher.update(content)
        return f"{algorithm}:{hasher.hexdigest()}"

    async def verify_hash(self, workspace_id: str, dataset_id: str, expected_hash: str) -> bool:
        try:
            content = await self.read_dataset(workspace_id, dataset_id)
            algorithm = expected_hash.split(":", 1)[0] if ":" in expected_hash else "sha256"
            actual_hash = await self.compute_hash(content, algorithm)
            return actual_hash == expected_hash
        except FileNotFoundError:
            return False

    async def cleanup_workspace(self, workspace_id: str) -> int:
        # Supabase Storage does not provide an efficient recursive delete over REST.
        # For now, leave as a no-op.
        return 0


class MinioStorage:
    def __init__(self) -> None:
        try:
            from minio import Minio
        except ImportError as e:
            raise RuntimeError("MinIO storage backend requires `minio`. Install with: pip install 'kytchen[api]'") from e

        self.client = Minio(
            os.getenv("MINIO_ENDPOINT", "localhost:9000"),
            access_key=os.getenv("MINIO_ACCESS_KEY"),
            secret_key=os.getenv("MINIO_SECRET_KEY"),
            secure=os.getenv("MINIO_SECURE", "false").lower() == "true",
        )
        self.bucket = os.getenv("MINIO_BUCKET", "pantry")
        self._bucket_ready = False
        self._bucket_lock = asyncio.Lock()

    def _object_path(self, workspace_id: str, dataset_id: str) -> str:
        return f"{workspace_id}/{dataset_id}"

    async def _ensure_bucket(self) -> None:
        if self._bucket_ready:
            return
        async with self._bucket_lock:
            if self._bucket_ready:
                return

            def _ensure() -> None:
                if not self.client.bucket_exists(self.bucket):
                    self.client.make_bucket(self.bucket)

            await asyncio.to_thread(_ensure)
            self._bucket_ready = True

    async def write_dataset(self, workspace_id: str, dataset_id: str, content: bytes) -> str:
        await self._ensure_bucket()
        object_name = self._object_path(workspace_id, dataset_id)

        def _put() -> None:
            self.client.put_object(
                self.bucket,
                object_name,
                io.BytesIO(content),
                length=len(content),
                content_type="application/octet-stream",
            )

        await asyncio.to_thread(_put)
        return object_name

    async def read_dataset(self, workspace_id: str, dataset_id: str) -> bytes:
        await self._ensure_bucket()
        object_name = self._object_path(workspace_id, dataset_id)

        def _get() -> bytes:
            resp = self.client.get_object(self.bucket, object_name)
            try:
                return resp.read()
            finally:
                resp.close()
                resp.release_conn()

        return await asyncio.to_thread(_get)

    async def delete_dataset(self, workspace_id: str, dataset_id: str) -> bool:
        await self._ensure_bucket()
        object_name = self._object_path(workspace_id, dataset_id)

        def _delete() -> bool:
            try:
                self.client.remove_object(self.bucket, object_name)
                return True
            except Exception as e:
                try:
                    from minio.error import S3Error

                    if isinstance(e, S3Error) and e.code in {"NoSuchKey", "NoSuchObject"}:
                        return False
                except Exception:
                    pass
                raise

        return await asyncio.to_thread(_delete)

    async def exists(self, workspace_id: str, dataset_id: str) -> bool:
        await self._ensure_bucket()
        object_name = self._object_path(workspace_id, dataset_id)

        def _exists() -> bool:
            try:
                self.client.stat_object(self.bucket, object_name)
                return True
            except Exception as e:
                try:
                    from minio.error import S3Error

                    if isinstance(e, S3Error) and e.code in {"NoSuchKey", "NoSuchObject"}:
                        return False
                except Exception:
                    pass
                raise

        return await asyncio.to_thread(_exists)

    async def get_size(self, workspace_id: str, dataset_id: str) -> int:
        await self._ensure_bucket()
        object_name = self._object_path(workspace_id, dataset_id)

        def _size() -> int:
            try:
                obj = self.client.stat_object(self.bucket, object_name)
                return int(obj.size)
            except Exception as e:
                try:
                    from minio.error import S3Error

                    if isinstance(e, S3Error) and e.code in {"NoSuchKey", "NoSuchObject"}:
                        raise FileNotFoundError(dataset_id)
                except Exception:
                    pass
                raise

        return await asyncio.to_thread(_size)

    async def compute_hash(self, content: bytes, algorithm: str = "sha256") -> str:
        hasher = hashlib.new(algorithm)
        hasher.update(content)
        return f"{algorithm}:{hasher.hexdigest()}"

    async def verify_hash(self, workspace_id: str, dataset_id: str, expected_hash: str) -> bool:
        try:
            content = await self.read_dataset(workspace_id, dataset_id)
            algorithm = expected_hash.split(":", 1)[0] if ":" in expected_hash else "sha256"
            actual_hash = await self.compute_hash(content, algorithm)
            return actual_hash == expected_hash
        except FileNotFoundError:
            return False

    async def cleanup_workspace(self, workspace_id: str) -> int:
        await self._ensure_bucket()
        prefix = f"{workspace_id}/"

        def _cleanup() -> int:
            count = 0
            for obj in self.client.list_objects(self.bucket, prefix=prefix, recursive=True):
                self.client.remove_object(self.bucket, obj.object_name)
                count += 1
            return count

        return await asyncio.to_thread(_cleanup)


# Global storage instance
# Can be overridden for testing or alternative storage backends
_storage: StorageBackend | None = None


def get_storage() -> StorageBackend:
    """Get global storage instance (singleton pattern).

    Returns:
        Storage backend instance
    """
    global _storage
    if _storage is None:
        backend = os.getenv("STORAGE_BACKEND")
        if backend is None:
            backend = "supabase" if (os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_SERVICE_ROLE_KEY")) else "filesystem"

        backend = backend.lower()
        if backend == "supabase":
            _storage = SupabaseStorage()
        elif backend == "minio":
            _storage = MinioStorage()
        else:
            _storage = FilesystemStorage()
    return _storage


def set_storage(storage: StorageBackend) -> None:
    """Override global storage instance (for testing).

    Args:
        storage: Custom storage instance
    """
    global _storage
    _storage = storage
