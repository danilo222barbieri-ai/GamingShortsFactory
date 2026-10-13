#!/usr/bin/env python3
import re
import sys
from pathlib import Path

MARKER = "GSF_V401_STREAM_UPLOAD_HELPER"
MAX_STREAM_CHUNK = 4 * 1024 * 1024


def stream_uploaded_file(uploaded, target, chunk_size=MAX_STREAM_CHUNK):
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        chunk_size = int(chunk_size or MAX_STREAM_CHUNK)
    except Exception:
        chunk_size = MAX_STREAM_CHUNK
    chunk_size = max(1, min(MAX_STREAM_CHUNK, chunk_size))

    original_pos = None
    try:
        original_pos = uploaded.tell()
    except Exception:
        pass

    written = 0
    try:
        try:
            uploaded.seek(0)
        except Exception:
            pass
        with open(target, "wb") as out:
            while True:
                chunk = uploaded.read(chunk_size)
                if not chunk:
                    break
                out.write(chunk)
                written += len(chunk)
    finally:
        if original_pos is not None:
            try:
                uploaded.seek(original_pos)
            except Exception:
                pass
    return written


HELPER_SOURCE = r'''
# GSF_V401_STREAM_UPLOAD_HELPER
def _gsf_v401_stream_upload_to_path(uploaded, target, chunk_size=4 * 1024 * 1024):
    try:
        chunk_size = int(chunk_size or (4 * 1024 * 1024))
    except Exception:
        chunk_size = 4 * 1024 * 1024
    chunk_size = max(1, min(4 * 1024 * 1024, chunk_size))
    original_pos = None
    try:
        original_pos = uploaded.tell()
    except Exception:
        pass
    written = 0
    try:
        try:
            uploaded.seek(0)
        except Exception:
            pass
        with open(target, "wb") as out:
            while True:
                chunk = uploaded.read(chunk_size)
                if not chunk:
                    break
                out.write(chunk)
                written += len(chunk)
    finally:
        if original_pos is not None:
            try:
                uploaded.seek(original_pos)
            except Exception:
                pass
    return written
'''.strip()


def _replace_write_block(text, handle_name, path_name):
    pattern = re.compile(
        rf'(?m)^(?P<indent>[ \t]*)with open\({re.escape(path_name)},\s*["\']wb["\']\) as {re.escape(handle_name)}:\s*\n'
        rf'(?P=indent)[ \t]+{re.escape(handle_name)}\.write\(video\.getvalue\(\)\)'
    )
    return pattern.sub(
        lambda m: f'{m.group("indent")}_gsf_v401_stream_upload_to_path(video, {path_name})',
        text,
        count=1,
    )


def patch_runtime_source(text):
    source = str(text)
    if MARKER not in source:
        anchor = "\n\nst.markdown("
        if anchor not in source:
            raise RuntimeError("V401 frontend helper insertion anchor missing")
        source = source.replace(anchor, "\n\n" + HELPER_SOURCE + anchor, 1)

    source = _replace_write_block(source, "_mf", "_main_probe_path")
    source = _replace_write_block(source, "ef", "editor_input")

    if "video.getvalue()" in source:
        raise RuntimeError("V401 found an unbounded video.getvalue() fallback copy")
    return source


def patch_runtime_file(path):
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    patched = patch_runtime_source(text)
    compile(patched, str(path), "exec")
    if patched != text:
        path.write_text(patched, encoding="utf-8")
        print("V401 frontend upload memory patch applied", flush=True)
    else:
        print("V401 frontend upload memory patch already active", flush=True)
    return patched != text


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/app/GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py")
    patch_runtime_file(target)
