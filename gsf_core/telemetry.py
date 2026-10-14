from __future__ import annotations

import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Iterator


_GB = 1024**3


@dataclass(slots=True)
class JobMetrics:
    phase_seconds: dict[str, float] = field(default_factory=dict)
    cpu_seconds: float = 0.0
    gpu_seconds: float = 0.0
    bytes_in: int = 0
    bytes_out: int = 0
    egress_bytes: int = 0

    def add_phase(self, name: str, seconds: float) -> None:
        if seconds < 0:
            raise ValueError("phase duration cannot be negative")
        self.phase_seconds[name] = self.phase_seconds.get(name, 0.0) + float(seconds)

    def to_dict(self) -> dict[str, object]:
        return {
            "phase_seconds": dict(self.phase_seconds),
            "cpu_seconds": self.cpu_seconds,
            "gpu_seconds": self.gpu_seconds,
            "bytes_in": self.bytes_in,
            "bytes_out": self.bytes_out,
            "egress_bytes": self.egress_bytes,
        }


@contextmanager
def phase_timer(metrics: JobMetrics, name: str) -> Iterator[None]:
    started = time.perf_counter()
    try:
        yield
    finally:
        metrics.add_phase(name, time.perf_counter() - started)


@dataclass(frozen=True, slots=True)
class CostModel:
    cpu_eur_per_hour: float = 0.0
    gpu_eur_per_hour: float = 0.0
    egress_eur_per_gb: float = 0.0

    def estimate(self, metrics: JobMetrics) -> dict[str, float]:
        cpu = metrics.cpu_seconds / 3600.0 * self.cpu_eur_per_hour
        gpu = metrics.gpu_seconds / 3600.0 * self.gpu_eur_per_hour
        egress = metrics.egress_bytes / _GB * self.egress_eur_per_gb
        result = {"cpu": cpu, "gpu": gpu, "egress": egress}
        result["total"] = sum(result.values())
        return result
