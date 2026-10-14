from __future__ import annotations

import json
import os
import threading
import uuid
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Mapping

from .assets import AssetRef


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class InvalidJobTransition(RuntimeError):
    pass


_ALLOWED_TRANSITIONS: dict[JobStatus, set[JobStatus]] = {
    JobStatus.QUEUED: {JobStatus.RUNNING, JobStatus.CANCELLED},
    JobStatus.RUNNING: {JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED},
    JobStatus.COMPLETED: set(),
    JobStatus.FAILED: set(),
    JobStatus.CANCELLED: set(),
}


@dataclass(frozen=True, slots=True)
class JobRecord:
    job_id: str
    project_id: str
    kind: str
    status: JobStatus = JobStatus.QUEUED
    inputs: tuple[AssetRef, ...] = ()
    outputs: tuple[AssetRef, ...] = ()
    progress: float = 0.0
    attempts: int = 0
    max_attempts: int = 3
    worker_id: str | None = None
    error: str | None = None
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)
    started_at: str | None = None
    finished_at: str | None = None
    heartbeat_at: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.job_id or not self.project_id or not self.kind:
            raise ValueError("job_id, project_id and kind are required")
        if isinstance(self.status, str) and not isinstance(self.status, JobStatus):
            object.__setattr__(self, "status", JobStatus(self.status))
        if not 0.0 <= float(self.progress) <= 1.0:
            raise ValueError("progress must be between 0 and 1")
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")
        if self.attempts < 0:
            raise ValueError("attempts cannot be negative")
        object.__setattr__(self, "inputs", tuple(self.inputs))
        object.__setattr__(self, "outputs", tuple(self.outputs))
        object.__setattr__(self, "metadata", dict(self.metadata))

    @classmethod
    def new(
        cls,
        project_id: str,
        kind: str,
        *,
        inputs: Iterable[AssetRef] = (),
        max_attempts: int = 3,
        metadata: Mapping[str, Any] | None = None,
        job_id: str | None = None,
    ) -> "JobRecord":
        return cls(
            job_id=job_id or f"job_{uuid.uuid4().hex}",
            project_id=project_id,
            kind=kind,
            inputs=tuple(inputs),
            max_attempts=max_attempts,
            metadata=metadata or {},
        )

    @property
    def can_retry(self) -> bool:
        return self.status is JobStatus.FAILED and self.attempts < self.max_attempts

    def to_dict(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id,
            "project_id": self.project_id,
            "kind": self.kind,
            "status": self.status.value,
            "inputs": [asset.to_dict() for asset in self.inputs],
            "outputs": [asset.to_dict() for asset in self.outputs],
            "progress": self.progress,
            "attempts": self.attempts,
            "max_attempts": self.max_attempts,
            "worker_id": self.worker_id,
            "error": self.error,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "heartbeat_at": self.heartbeat_at,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "JobRecord":
        return cls(
            job_id=payload["job_id"],
            project_id=payload["project_id"],
            kind=payload["kind"],
            status=JobStatus(payload.get("status", JobStatus.QUEUED.value)),
            inputs=tuple(AssetRef.from_dict(v) for v in payload.get("inputs", [])),
            outputs=tuple(AssetRef.from_dict(v) for v in payload.get("outputs", [])),
            progress=float(payload.get("progress", 0.0)),
            attempts=int(payload.get("attempts", 0)),
            max_attempts=int(payload.get("max_attempts", 3)),
            worker_id=payload.get("worker_id"),
            error=payload.get("error"),
            created_at=payload.get("created_at") or _now(),
            updated_at=payload.get("updated_at") or _now(),
            started_at=payload.get("started_at"),
            finished_at=payload.get("finished_at"),
            heartbeat_at=payload.get("heartbeat_at"),
            metadata=payload.get("metadata") or {},
        )


class JsonJobStore:
    """Atomic persistent job state for dev/single-host use, not a distributed scheduler."""

    def __init__(self, root: str | os.PathLike[str]):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()

    def _path(self, job_id: str) -> Path:
        safe = "".join(ch for ch in job_id if ch.isalnum() or ch in "-_")
        if safe != job_id or not safe:
            raise ValueError("unsafe job_id")
        return self.root / f"{safe}.json"

    def create(self, job: JobRecord) -> JobRecord:
        path = self._path(job.job_id)
        with self._lock:
            if path.exists():
                raise FileExistsError(job.job_id)
            self._atomic_write(path, job.to_dict())
        return job

    def get(self, job_id: str) -> JobRecord:
        path = self._path(job_id)
        with self._lock:
            if not path.exists():
                raise KeyError(job_id)
            return JobRecord.from_dict(json.loads(path.read_text(encoding="utf-8")))

    def list(self, *, status: JobStatus | None = None, project_id: str | None = None) -> list[JobRecord]:
        with self._lock:
            jobs = []
            for path in sorted(self.root.glob("*.json")):
                job = JobRecord.from_dict(json.loads(path.read_text(encoding="utf-8")))
                if status is not None and job.status is not status:
                    continue
                if project_id is not None and job.project_id != project_id:
                    continue
                jobs.append(job)
            return jobs

    def transition(
        self,
        job_id: str,
        target: JobStatus,
        *,
        worker_id: str | None = None,
        progress: float | None = None,
        error: str | None = None,
        outputs: Iterable[AssetRef] | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> JobRecord:
        target = JobStatus(target)
        with self._lock:
            current = self.get(job_id)
            if target not in _ALLOWED_TRANSITIONS[current.status]:
                raise InvalidJobTransition(f"{current.status.value} -> {target.value}")
            if target is JobStatus.RUNNING and not worker_id:
                raise InvalidJobTransition("running jobs require a worker_id")
            if (
                current.status is JobStatus.RUNNING
                and target in {JobStatus.COMPLETED, JobStatus.FAILED}
                and worker_id != current.worker_id
            ):
                raise InvalidJobTransition("worker does not own this running job")

            now = _now()
            next_progress = current.progress if progress is None else float(progress)
            if not 0 <= next_progress <= 1:
                raise ValueError("progress must be between 0 and 1")

            kwargs: dict[str, Any] = {
                "status": target,
                "updated_at": now,
                "progress": next_progress,
            }
            if worker_id is not None:
                kwargs["worker_id"] = worker_id
            if metadata is not None:
                kwargs["metadata"] = {**dict(current.metadata), **dict(metadata)}

            if target is JobStatus.RUNNING:
                kwargs["attempts"] = current.attempts + 1
                kwargs["started_at"] = now
                kwargs["finished_at"] = None
                kwargs["heartbeat_at"] = now
                kwargs["error"] = None
            elif target is JobStatus.COMPLETED:
                kwargs["progress"] = 1.0
                kwargs["finished_at"] = now
                kwargs["error"] = None
                if outputs is not None:
                    kwargs["outputs"] = tuple(outputs)
            elif target is JobStatus.FAILED:
                kwargs["finished_at"] = now
                kwargs["error"] = error or "job failed"
            elif target is JobStatus.CANCELLED:
                kwargs["finished_at"] = now
                kwargs["error"] = error

            updated = replace(current, **kwargs)
            self._atomic_write(self._path(job_id), updated.to_dict())
            return updated

    def heartbeat(
        self,
        job_id: str,
        *,
        worker_id: str,
        progress: float | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> JobRecord:
        with self._lock:
            current = self.get(job_id)
            if current.status is not JobStatus.RUNNING:
                raise InvalidJobTransition("only running jobs can heartbeat")
            if not current.worker_id or current.worker_id != worker_id:
                raise InvalidJobTransition("heartbeat worker does not own this job")
            next_progress = current.progress if progress is None else float(progress)
            if not 0 <= next_progress <= 1:
                raise ValueError("progress must be between 0 and 1")
            now = _now()
            updated = replace(
                current,
                progress=next_progress,
                heartbeat_at=now,
                updated_at=now,
                metadata=(
                    {**dict(current.metadata), **dict(metadata)}
                    if metadata is not None
                    else current.metadata
                ),
            )
            self._atomic_write(self._path(job_id), updated.to_dict())
            return updated

    def retry(self, job_id: str) -> JobRecord:
        with self._lock:
            current = self.get(job_id)
            if not current.can_retry:
                raise InvalidJobTransition(
                    f"job {job_id} cannot retry after {current.attempts}/{current.max_attempts} attempts"
                )
            updated = replace(
                current,
                status=JobStatus.QUEUED,
                progress=0.0,
                worker_id=None,
                error=None,
                updated_at=_now(),
                started_at=None,
                finished_at=None,
                heartbeat_at=None,
                outputs=(),
            )
            self._atomic_write(self._path(job_id), updated.to_dict())
            return updated

    @staticmethod
    def _atomic_write(path: Path, payload: Mapping[str, Any]) -> None:
        tmp = path.with_suffix(path.suffix + f".{uuid.uuid4().hex}.tmp")
        try:
            with tmp.open("w", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(tmp, path)
        finally:
            if tmp.exists():
                tmp.unlink(missing_ok=True)
