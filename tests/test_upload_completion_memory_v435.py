from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "web" / "direct_upload_server.py"


def test_upload_completion_materialization_is_serial_and_low_memory():
    source = SERVER.read_text(encoding="utf-8")

    # The 1 GB frontend must never run multiple bucket materializations at once.
    assert "_MATERIALIZE_GATE=threading.BoundedSemaphore(1)" in source
    assert "with _MATERIALIZE_GATE:" in source

    # Upload completion is the RAM-critical boundary. Keep boto3's transfer
    # manager single-threaded and its read-ahead queue deliberately tiny.
    assert "max_concurrency=1" in source
    assert "max_io_queue=2" in source
    assert "io_chunksize=256*1024" in source
    assert "use_threads=False" in source
