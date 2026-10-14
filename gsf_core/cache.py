from __future__ import annotations

import hashlib
import json
import os
import threading
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from .assets import AssetRef


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


@dataclass(frozen=True, slots=True)
class ArtifactCacheKey:
    digest: str
    operation: str
    version: str

    @classmethod
    def build(
        cls,
        *,
        source_checksum: str,
        operation: str,
        version: str,
        params: Mapping[str, Any] | None = None,
    ) -> "ArtifactCacheKey":
        identity = {
            "source_checksum": source_checksum,
            "operation": operation,
            "version": version,
            "params": dict(params or {}),
        }
        digest = hashlib.sha256(_canonical_json(identity).encode("utf-8")).hexdigest()
        return cls(digest=digest, operation=operation, version=version)


class JsonArtifactCache:
    """Atomic metadata cache mapping deterministic work identities to assets."""

    def __init__(self, path: str | os.PathLike[str]):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()

    def _read(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"version": 1, "entries": {}}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def get(self, key: ArtifactCacheKey) -> AssetRef | None:
        with self._lock:
            payload = self._read()
            entry = payload.get("entries", {}).get(key.digest)
            return AssetRef.from_dict(entry["asset"]) if entry else None

    def put(self, key: ArtifactCacheKey, asset: AssetRef) -> None:
        with self._lock:
            payload = self._read()
            entries = payload.setdefault("entries", {})
            entries[key.digest] = {
                "operation": key.operation,
                "version": key.version,
                "asset": asset.to_dict(),
            }
            self._atomic_write(payload)

    def invalidate(self, key: ArtifactCacheKey) -> bool:
        with self._lock:
            payload = self._read()
            entries = payload.setdefault("entries", {})
            existed = entries.pop(key.digest, None) is not None
            if existed:
                self._atomic_write(payload)
            return existed

    def _atomic_write(self, payload: Mapping[str, Any]) -> None:
        tmp = self.path.with_suffix(self.path.suffix + f".{uuid.uuid4().hex}.tmp")
        try:
            with tmp.open("w", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(tmp, self.path)
        finally:
            if tmp.exists():
                tmp.unlink(missing_ok=True)


@dataclass(frozen=True, slots=True)
class ProxyProfile:
    max_height: int
    max_fps: int
    video_codec: str
    audio_codec: str
    video_crf: int
    purpose: str = "editor_proxy"

    @classmethod
    def editor_default(cls) -> "ProxyProfile":
        return cls(
            max_height=720,
            max_fps=30,
            video_codec="libx264",
            audio_codec="aac",
            video_crf=24,
        )

    def cache_params(self) -> dict[str, Any]:
        return {
            "purpose": self.purpose,
            "max_height": self.max_height,
            "max_fps": self.max_fps,
            "video_codec": self.video_codec,
            "audio_codec": self.audio_codec,
            "video_crf": self.video_crf,
        }
