#!/usr/bin/env python3
import os
import threading
import time
from contextlib import contextmanager


def _configured_slots():
    try:
        value = int(os.environ.get("GSF_FINAL_RENDER_SLOTS", "1") or 1)
    except Exception:
        value = 1
    return max(1, min(2, value))


_RENDER_SLOTS = _configured_slots()
_RENDER_GATE = threading.BoundedSemaphore(_RENDER_SLOTS)
_STATE_LOCK = threading.Lock()
_ACTIVE = 0
_THREAD_STATE = threading.local()


@contextmanager
def render_slot(label="final"):
    global _ACTIVE
    # A final render invokes cinematic/audio/director stages synchronously.
    # They reuse the owning thread's slot; another job still has to acquire it.
    if getattr(_THREAD_STATE, "owns_slot", False):
        yield
        return
    label = str(label or "final")[:80]
    wait_started = time.perf_counter()
    print(
        "GSF_FINAL_RENDER_WAIT",
        f"label={label}",
        f"slots={_RENDER_SLOTS}",
        flush=True,
    )
    try:
        wait_timeout = max(.05, min(300, float(os.environ.get("GSF_RENDER_QUEUE_TIMEOUT", "120"))))
    except (TypeError, ValueError):
        wait_timeout = 120
    if not _RENDER_GATE.acquire(timeout=wait_timeout):
        raise TimeoutError("Render occupato: riprova tra poco (attesa massima raggiunta).")
    _THREAD_STATE.owns_slot = True
    waited = time.perf_counter() - wait_started
    with _STATE_LOCK:
        _ACTIVE += 1
        active = _ACTIVE
    print(
        "GSF_FINAL_RENDER_ACQUIRED",
        f"label={label}",
        f"waited={waited:.3f}",
        f"active={active}",
        f"slots={_RENDER_SLOTS}",
        flush=True,
    )
    try:
        yield
    finally:
        with _STATE_LOCK:
            _ACTIVE = max(0, _ACTIVE - 1)
            active = _ACTIVE
        _THREAD_STATE.owns_slot = False
        _RENDER_GATE.release()
        print(
            "GSF_FINAL_RENDER_RELEASED",
            f"label={label}",
            f"active={active}",
            flush=True,
        )
