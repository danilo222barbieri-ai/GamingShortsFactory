#!/usr/bin/env python3
import json
import os
import re
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import threading
from pathlib import Path
from urllib.parse import unquote

ROOT=Path(os.environ.get("GSF_RUNTIME_ROOT","/tmp/gsf-runtime"))
PORT=int(os.environ.get("GSF_DIRECT_UPLOAD_PORT","8502"))
MAX_FILE_BYTES=4*1024*1024*1024
MAX_CHUNK_BYTES=64*1024*1024
ID_RE=re.compile(r"^[A-Za-z0-9_-]{1,80}$")
ALLOWED_EXT={".mp4",".mov",".mkv"}
_FINALIZE_LOCK=threading.Lock()

def _safe_id(value):
    value=str(value or "")
    return value if ID_RE.fullmatch(value) else ""

def _safe_filename(value):
    try:
        value=unquote(str(value or "video.mp4"))
    except Exception:
        value="video.mp4"
    name=Path(value).name
    ext=Path(name).suffix.lower()
    if ext not in ALLOWED_EXT:
        raise ValueError("unsupported extension")
    stem=re.sub(r"[^A-Za-z0-9_.-]+","_",Path(name).stem)[:80] or "video"
    return name,stem,ext

def _json(handler,status,payload):
    body=json.dumps(payload,ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type","application/json; charset=utf-8")
    handler.send_header("Content-Length",str(len(body)))
    handler.send_header("Cache-Control","no-store")
    handler.end_headers()
    handler.wfile.write(body)

class Handler(BaseHTTPRequestHandler):
    server_version="GSFDirectUpload/1.0"

    def log_message(self,fmt,*args):
        return

    def do_GET(self):
        if self.path.rstrip("/") in ("","/health"):
            _json(self,200,{"ok":True})
        else:
            _json(self,404,{"ok":False,"error":"not found"})

    def do_PUT(self):
        if self.path.split("?",1)[0].rstrip("/") != "/chunk":
            _json(self,404,{"ok":False,"error":"not found"})
            return

        sid=_safe_id(self.headers.get("X-GSF-Session-ID"))
        upload_id=_safe_id(self.headers.get("X-GSF-Upload-ID"))
        if not sid or not upload_id:
            _json(self,400,{"ok":False,"error":"invalid session or upload id"})
            return

        try:
            original_name,safe_stem,ext=_safe_filename(self.headers.get("X-GSF-Filename"))
            total=int(self.headers.get("X-GSF-File-Size","0"))
            start=int(self.headers.get("X-GSF-Chunk-Start","0"))
            index=int(self.headers.get("X-GSF-Chunk-Index","0"))
            count=int(self.headers.get("X-GSF-Chunk-Count","0"))
            length=int(self.headers.get("Content-Length","0"))
        except Exception:
            _json(self,400,{"ok":False,"error":"invalid upload metadata"})
            return

        if total<=0 or total>MAX_FILE_BYTES or start<0 or start>=total:
            _json(self,413,{"ok":False,"error":"file size not allowed"})
            return
        if length<=0 or length>MAX_CHUNK_BYTES or start+length>total:
            _json(self,413,{"ok":False,"error":"chunk size not allowed"})
            return
        if count<=0 or index<0 or index>=count:
            _json(self,400,{"ok":False,"error":"invalid chunk index"})
            return

        media=ROOT/"sessions"/sid/"media"
        tmp_dir=ROOT/"sessions"/sid/"direct_upload"/upload_id
        media.mkdir(parents=True,exist_ok=True)
        tmp_dir.mkdir(parents=True,exist_ok=True)
        part_path=tmp_dir/f"{index:06d}.part"

        try:
            remaining=length
            with open(part_path,"wb",buffering=1024*1024) as out:
                while remaining>0:
                    block=self.rfile.read(min(1024*1024,remaining))
                    if not block:
                        raise IOError("client disconnected")
                    out.write(block)
                    remaining-=len(block)
                out.flush()

            completed=False
            with _FINALIZE_LOCK:
                parts=[tmp_dir/f"{i:06d}.part" for i in range(count)]
                if all(p.is_file() for p in parts):
                    final_tmp=media/f".source_direct_{safe_stem}_{upload_id}{ext}.tmp"
                    actual=0
                    with open(final_tmp,"wb",buffering=4*1024*1024) as dst:
                        for p in parts:
                            with open(p,"rb",buffering=4*1024*1024) as src:
                                while True:
                                    block=src.read(4*1024*1024)
                                    if not block:
                                        break
                                    dst.write(block)
                                    actual+=len(block)
                        dst.flush()
                        os.fsync(dst.fileno())
                    if actual!=total:
                        final_tmp.unlink(missing_ok=True)
                        _json(self,409,{"ok":False,"error":"incomplete upload","bytes":actual})
                        return

                    final=media/f"source_direct_{safe_stem}_{upload_id}{ext}"
                    os.replace(final_tmp,final)
                    marker=media/".direct_upload_ready.json"
                    marker_tmp=media/".direct_upload_ready.json.tmp"
                    marker_data={
                        "path":str(final),
                        "name":original_name,
                        "size":total,
                        "upload_id":upload_id,
                        "completed_at":time.time(),
                    }
                    marker_tmp.write_text(json.dumps(marker_data,ensure_ascii=False),encoding="utf-8")
                    os.replace(marker_tmp,marker)
                    for p in parts:
                        p.unlink(missing_ok=True)
                    try:
                        tmp_dir.rmdir()
                    except OSError:
                        pass
                    try:
                        os.utime(ROOT/"sessions"/sid/".active",None)
                    except Exception:
                        pass
                    completed=True

            _json(self,200,{
                "ok":True,
                "completed":completed,
                "index":index,
                "bytes":start+length
            })
        except Exception as exc:
            _json(self,500,{"ok":False,"error":str(exc)[:160]})

if __name__=="__main__":
    ROOT.mkdir(parents=True,exist_ok=True)
    server=ThreadingHTTPServer(("127.0.0.1",PORT),Handler)
    print(f"GSF direct upload server listening on 127.0.0.1:{PORT}",flush=True)
    server.serve_forever()
