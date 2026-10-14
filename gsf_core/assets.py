from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class AssetKind(str, Enum):
    SOURCE = "source"
    PROXY = "proxy"
    AUDIO = "audio"
    THUMBNAIL = "thumbnail"
    ANALYSIS = "analysis"
    RENDER = "render"
    PUBLISH = "publish"
    OTHER = "other"


@dataclass(frozen=True, slots=True)
class AssetRef:
    """Lightweight storage reference. Raw media bytes never belong in app state."""

    asset_id: str
    backend: str
    key: str
    kind: AssetKind
    content_type: str = "application/octet-stream"
    size_bytes: int | None = None
    checksum_sha256: str | None = None
    created_at: str = field(default_factory=utcnow_iso)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.asset_id, str) or not self.asset_id.strip():
            raise ValueError("asset_id must be a non-empty string")
        if not isinstance(self.backend, str) or not self.backend.strip():
            raise ValueError("backend must be a non-empty string")
        if not isinstance(self.key, str) or not self.key.strip():
            raise TypeError("key must be a non-empty string, never raw bytes")
        if isinstance(self.kind, str) and not isinstance(self.kind, AssetKind):
            object.__setattr__(self, "kind", AssetKind(self.kind))
        if self.size_bytes is not None and self.size_bytes < 0:
            raise ValueError("size_bytes cannot be negative")
        if self.checksum_sha256 is not None:
            checksum = self.checksum_sha256.lower()
            if len(checksum) != 64 or any(c not in "0123456789abcdef" for c in checksum):
                raise ValueError("checksum_sha256 must be a 64-character hex digest")
            object.__setattr__(self, "checksum_sha256", checksum)
        object.__setattr__(self, "metadata", dict(self.metadata))

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "backend": self.backend,
            "key": self.key,
            "kind": self.kind.value,
            "content_type": self.content_type,
            "size_bytes": self.size_bytes,
            "checksum_sha256": self.checksum_sha256,
            "created_at": self.created_at,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "AssetRef":
        allowed = {
            "asset_id",
            "backend",
            "key",
            "kind",
            "content_type",
            "size_bytes",
            "checksum_sha256",
            "created_at",
            "metadata",
        }
        unknown = set(payload) - allowed
        if unknown:
            raise ValueError(f"unknown AssetRef fields: {sorted(unknown)}")
        return cls(
            asset_id=payload["asset_id"],
            backend=payload["backend"],
            key=payload["key"],
            kind=AssetKind(payload["kind"]),
            content_type=payload.get("content_type", "application/octet-stream"),
            size_bytes=payload.get("size_bytes"),
            checksum_sha256=payload.get("checksum_sha256"),
            created_at=payload.get("created_at") or utcnow_iso(),
            metadata=payload.get("metadata") or {},
        )
