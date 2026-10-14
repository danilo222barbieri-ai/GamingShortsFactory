from __future__ import annotations

import hashlib
import mimetypes
import os
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .assets import AssetKind, AssetRef


_CHUNK_SIZE = 1024 * 1024


def _safe_extension(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if not re.fullmatch(r"\.[a-z0-9]{1,8}", suffix):
        return ""
    return suffix


@dataclass(frozen=True, slots=True)
class UploadTarget:
    method: str
    url: str
    fields: dict[str, str]
    asset: AssetRef
    expires_at: str
    max_bytes: int


class LocalStorage:
    backend_name = "local"

    def __init__(self, root: str | os.PathLike[str]):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _target(self, key: str) -> Path:
        if not isinstance(key, str) or not key or key.startswith(("/", "\\")):
            raise ValueError("storage key must be relative")
        target = (self.root / key).resolve()
        try:
            target.relative_to(self.root)
        except ValueError as exc:
            raise ValueError("storage key escapes storage root") from exc
        return target

    def put_file(
        self,
        source_path: str | os.PathLike[str],
        *,
        key: str,
        kind: AssetKind,
        content_type: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AssetRef:
        source = Path(source_path)
        target = self._target(key)
        target.parent.mkdir(parents=True, exist_ok=True)

        digest = hashlib.sha256()
        size = 0
        tmp = target.with_suffix(target.suffix + f".{uuid.uuid4().hex}.tmp")
        try:
            with source.open("rb") as src, tmp.open("wb") as dst:
                while True:
                    chunk = src.read(_CHUNK_SIZE)
                    if not chunk:
                        break
                    digest.update(chunk)
                    size += len(chunk)
                    dst.write(chunk)
                dst.flush()
                os.fsync(dst.fileno())
            os.replace(tmp, target)
        finally:
            if tmp.exists():
                tmp.unlink(missing_ok=True)

        return AssetRef(
            asset_id=f"asset_{uuid.uuid4().hex}",
            backend=self.backend_name,
            key=key,
            kind=kind,
            content_type=content_type or mimetypes.guess_type(source.name)[0] or "application/octet-stream",
            size_bytes=size,
            checksum_sha256=digest.hexdigest(),
            metadata=metadata or {},
        )

    def path_for(self, asset: AssetRef) -> Path:
        if asset.backend != self.backend_name:
            raise ValueError(f"asset backend is {asset.backend!r}, expected local")
        return self._target(asset.key)


class S3Storage:
    """S3-compatible asset storage with browser-direct presigned uploads."""

    backend_name = "s3"

    def __init__(
        self,
        *,
        bucket: str,
        prefix: str = "",
        region_name: str | None = None,
        endpoint_url: str | None = None,
        client: Any | None = None,
    ):
        if not bucket:
            raise ValueError("bucket is required")
        self.bucket = bucket
        self.prefix = prefix.strip("/")
        if client is None:
            import boto3

            client = boto3.client("s3", region_name=region_name, endpoint_url=endpoint_url)
        self.client = client

    @staticmethod
    def _project_token(project_id: str) -> str:
        token = re.sub(r"[^A-Za-z0-9_-]", "_", project_id)
        if not token:
            raise ValueError("project_id is required")
        return token

    def create_presigned_upload(
        self,
        *,
        project_id: str,
        filename: str,
        kind: AssetKind,
        content_type: str,
        max_bytes: int,
        expires_in: int = 900,
    ) -> UploadTarget:
        if max_bytes < 1:
            raise ValueError("max_bytes must be positive")
        if expires_in < 1:
            raise ValueError("expires_in must be positive")
        project_token = self._project_token(project_id)
        ext = _safe_extension(filename)
        object_name = f"{uuid.uuid4().hex}{ext}"
        relative = f"projects/{project_token}/{kind.value}/{object_name}"
        key = f"{self.prefix}/{relative}" if self.prefix else relative

        fields = {"Content-Type": content_type}
        conditions: list[Any] = [
            {"Content-Type": content_type},
            ["content-length-range", 1, int(max_bytes)],
        ]
        signed = self.client.generate_presigned_post(
            Bucket=self.bucket,
            Key=key,
            Fields=fields,
            Conditions=conditions,
            ExpiresIn=int(expires_in),
        )

        asset = AssetRef(
            asset_id=f"asset_{uuid.uuid4().hex}",
            backend=self.backend_name,
            key=key,
            kind=kind,
            content_type=content_type,
            metadata={
                "bucket": self.bucket,
                "upload_state": "pending",
                "original_filename": Path(filename).name,
            },
        )
        expires_at = (datetime.now(timezone.utc) + timedelta(seconds=expires_in)).isoformat()
        return UploadTarget(
            method="POST",
            url=signed["url"],
            fields={str(k): str(v) for k, v in signed.get("fields", {}).items()},
            asset=asset,
            expires_at=expires_at,
            max_bytes=max_bytes,
        )

    def confirm_upload(self, asset: AssetRef, *, project_id: str, max_bytes: int) -> AssetRef:
        """Verify a browser-direct upload before it enters the processing graph."""
        if asset.backend != self.backend_name:
            raise ValueError(f"asset backend is {asset.backend!r}, expected s3")
        if max_bytes < 1:
            raise ValueError("max_bytes must be positive")
        project_token = self._project_token(project_id)
        expected_prefix = f"projects/{project_token}/"
        if self.prefix:
            expected_prefix = f"{self.prefix}/{expected_prefix}"
        if not asset.key.startswith(expected_prefix):
            raise ValueError("asset does not belong to this project namespace")
        head = self.client.head_object(Bucket=self.bucket, Key=asset.key)
        size = int(head.get("ContentLength", 0))
        if size < 1:
            raise ValueError("uploaded object is empty")
        if size > max_bytes:
            raise ValueError("uploaded object exceeds configured maximum")
        actual_type = head.get("ContentType") or asset.content_type
        checksum = (head.get("Metadata") or {}).get("sha256")
        if checksum is not None:
            checksum = checksum.lower()
            if len(checksum) != 64 or any(c not in "0123456789abcdef" for c in checksum):
                checksum = None
        metadata = {
            **dict(asset.metadata),
            "upload_state": "confirmed",
            "bucket": self.bucket,
            "etag": str(head.get("ETag", "")).strip('"'),
        }
        return AssetRef(
            asset_id=asset.asset_id,
            backend=asset.backend,
            key=asset.key,
            kind=asset.kind,
            content_type=actual_type,
            size_bytes=size,
            checksum_sha256=checksum,
            created_at=asset.created_at,
            metadata=metadata,
        )
