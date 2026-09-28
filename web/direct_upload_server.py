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
MAX_CHUNK_BYTES=40*1024*1024
ID_RE=re.compile(r"^[A-Za-z0-9_-]{1,80}$")
ALLOWED_EXT={".mp4",".mov",".mkv"}
_STATE_LOCKS={}
_STATE_LOCKS_GUARD=threading.Lock()

def _state_lock(sid,upload_id):
    key=(str(sid),str(upload_id))
    with _STATE_LOCKS_GUARD:
        lock=_STATE_LOCKS.get(key)
        if lock is None:
            lock=threading.Lock()
            _STATE_LOCKS[key]=lock
        return lock

def _write_json_atomic(path,payload):
    tmp=Path(str(path)+".tmp")
    tmp.write_text(json.dumps(payload,ensure_ascii=False),encoding="utf-8")
    os.replace(tmp,path)


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
        upload_dir=ROOT/"sessions"/sid/"direct_upload"/upload_id
        media.mkdir(parents=True,exist_ok=True)
        upload_dir.mkdir(parents=True,exist_ok=True)
        data_path=upload_dir/"upload.tmp"
        state_path=upload_dir/"state.json"
        lock=_state_lock(sid,upload_id)

        try:
            # Register metadata under a very short lock. Network reads/writes happen
            # outside it so up to four chunks can arrive concurrently.
            with lock:
                if state_path.is_file():
                    state=json.loads(state_path.read_text(encoding="utf-8"))
                    if (
                        int(state.get("total",0))!=total
                        or int(state.get("count",0))!=count
                        or str(state.get("ext",""))!=ext
                    ):
                        _json(self,409,{"ok":False,"error":"upload metadata changed"})
                        return
                else:
                    state={
                        "total":total,
                        "count":count,
                        "name":original_name,
                        "stem":safe_stem,
                        "ext":ext,
                        "ranges":{},
                        "received":[],
                    }
                    with open(data_path,"wb") as seed:
                        seed.truncate(total)
                    _write_json_atomic(state_path,state)

                ranges=dict(state.get("ranges",{}) or {})
                this_range=[start,length]
                existing=ranges.get(str(index))
                if existing is not None and list(existing)!=this_range:
                    _json(self,409,{"ok":False,"error":"chunk metadata changed"})
                    return
                for other_index,other_range in ranges.items():
                    if str(other_index)==str(index):
                        continue
                    try:
                        other_start=int(other_range[0])
                        other_end=other_start+int(other_range[1])
                    except Exception:
                        continue
                    this_end=start+length
                    if start<other_end and other_start<this_end:
                        _json(self,409,{"ok":False,"error":"overlapping chunk ranges"})
                        return
                ranges[str(index)]=this_range
                state["ranges"]=ranges
                _write_json_atomic(state_path,state)

            # Positional writes avoid seek races between concurrent requests.
            fd=os.open(str(data_path),os.O_WRONLY)
            try:
                remaining=length
                offset=start
                while remaining>0:
                    block=self.rfile.read(min(1024*1024,remaining))
                    if not block:
                        raise IOError("client disconnected")
                    view=memoryview(block)
                    written=0
                    while written<len(view):
                        n=os.pwrite(fd,view[written:],offset+written)
                        if n<=0:
                            raise IOError("short positional write")
                        written+=n
                    offset+=len(block)
                    remaining-=len(block)
            finally:
                os.close(fd)

            completed=False
            with lock:
                state=json.loads(state_path.read_text(encoding="utf-8"))
                received={int(x) for x in (state.get("received",[]) or [])}
                received.add(index)
                state["received"]=sorted(received)
                _write_json_atomic(state_path,state)

                if len(received)==count and received==set(range(count)):
                    fd=os.open(str(data_path),os.O_RDONLY)
                    try:
                        os.fsync(fd)
                    finally:
                        os.close(fd)

                    if data_path.stat().st_size!=total:
                        _json(self,409,{"ok":False,"error":"incomplete upload"})
                        return

                    final=media/f"source_direct_{safe_stem}_{upload_id}{ext}"
                    os.replace(data_path,final)
                    marker=media/".direct_upload_ready.json"
                    marker_data={
                        "path":str(final),
                        "name":original_name,
                        "size":total,
                        "upload_id":upload_id,
                        "completed_at":time.time(),
                    }
                    _write_json_atomic(marker,marker_data)
                    state_path.unlink(missing_ok=True)
                    try:
                        upload_dir.rmdir()
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
