#!/usr/bin/env python3
import os
import threading
import time
from contextlib import contextmanager


def _low_memory_frontend():
    return os.environ.get("GSF_LOW_MEMORY_WEB", "0").strip().lower() in {"1", "true", "yes", "on"}


def _configured_slots():
    if _low_memory_frontend():
        return 1
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


def _frontend_process_slot(timeout):
    """Extend the existing slot across frontend render subprocesses."""
    if not _low_memory_frontend() or os.name != "posix":
        return None
    import fcntl
    root = os.environ.get("GSF_RUNTIME_ROOT", "/tmp/gsf-runtime")
    os.makedirs(root, exist_ok=True)
    fd = os.open(os.path.join(root, ".frontend-final-render.lock"),
                 os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0), 0o600)
    handle = os.fdopen(fd, "r+")
    deadline = time.monotonic() + max(0.0, timeout)
    try:
        while True:
            try:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                return handle
            except BlockingIOError:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError("Render occupato: riprova tra poco (attesa massima raggiunta).")
                time.sleep(min(.05, remaining))
    except BaseException:
        handle.close()
        raise


@contextmanager
def render_slot(label="final"):
    global _ACTIVE
    # A final render invokes cinematic/audio/director stages synchronously.
    # They reuse the owning thread's slot; another job still has to acquire it.
    if getattr(threading.current_thread(), "_gsf_final_render_owns_slot", False):
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
    try:
        # The semaphore is process-local. All frontend subprocesses must share
        # this same admission boundary; nested stages retain the owning slot.
        process_slot = _frontend_process_slot(max(0.0, wait_timeout-(time.perf_counter()-wait_started)))
    except BaseException:
        _RENDER_GATE.release()
        raise
    _THREAD_STATE.owns_slot = True
    # Streamlit can reload modules while a render is active. Nested stages on
    # this same thread must retain admission across those module identities.
    threading.current_thread()._gsf_final_render_owns_slot = True
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
        threading.current_thread()._gsf_final_render_owns_slot = False
        try:
            if process_slot is not None:
                process_slot.close()
        finally:
            _RENDER_GATE.release()
        print(
            "GSF_FINAL_RENDER_RELEASED",
            f"label={label}",
            f"active={active}",
            flush=True,
        )
