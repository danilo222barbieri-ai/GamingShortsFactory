#!/usr/bin/env python3
import http.cookiejar
import json
import os
import struct
import subprocess
import tempfile
import time
import urllib.request

base=f"http://127.0.0.1:{int(os.environ.get('PORT','8080'))}"
jar=http.cookiejar.CookieJar()
opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
# Root is intentionally mobile-gated. Exercise the canonical production path
# instead of being classified as desktop and mistaking the desktop gate page
# for a broken Streamlit root.
UA="Mozilla/5.0 (iPhone; CPU iPhone OS 19_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1 GSF-V107-Runtime-Smoke/1.0"
SESSION_COOKIE=""


def request(path, method="GET", data=None, headers=None, attempts=1, timeout=8):
    global SESSION_COOKIE
    last=None
    headers=dict(headers or {})
    headers.setdefault("User-Agent",UA)
    if SESSION_COOKIE:
        headers.setdefault("Cookie",f"gsf_sid={SESSION_COOKIE}")
    for _ in range(max(1,int(attempts))):
        try:
            req=urllib.request.Request(base+path,data=data,headers=headers,method=method)
            with opener.open(req,timeout=timeout) as r:
                body=r.read(8*1024*1024)
                set_cookie=str(r.headers.get("Set-Cookie","") or "")
                if "gsf_sid=" in set_cookie and not SESSION_COOKIE:
                    SESSION_COOKIE=set_cookie.split("gsf_sid=",1)[1].split(";",1)[0].strip()
                return int(r.status),r.headers,body
        except Exception as exc:
            last=exc
            time.sleep(1)
    raise RuntimeError(f"{method} {path}: {last}")


status,headers,body=request("/healthz",attempts=30,timeout=4)
health=json.loads(body.decode("utf-8"))
if status!=200 or not health.get("ok") or not health.get("companion") or not health.get("streamlit"):
    raise SystemExit("V107 runtime smoke FAIL: composite health")
print("V107 composite health smoke: PASS",flush=True)

status,headers,body=request("/",attempts=30,timeout=4)
if status!=200 or b"streamlit" not in body.lower():
    raise SystemExit("V107 runtime smoke FAIL: root")
if not SESSION_COOKIE:
    raise SystemExit("V107 runtime smoke FAIL: session cookie")

status,headers,body=request("/editor-media/current",attempts=3,timeout=4)
if status!=204 or body:
    raise SystemExit("V107 runtime smoke FAIL: empty editor media state")
print("V107 empty editor media smoke: PASS",flush=True)

status,headers,body=request("/manifest.webmanifest",attempts=5)
manifest=json.loads(body.decode("utf-8"))
if status!=200 or manifest.get("short_name")!="GSF":
    raise SystemExit("V107 runtime smoke FAIL: manifest")
icons=manifest.get("icons") or []
icon_sizes={str(item.get("sizes") or "") for item in icons}
if not {"192x192","512x512"}.issubset(icon_sizes):
    raise SystemExit("V107 runtime smoke FAIL: PWA manifest icons")

for path,expected in (
    ("/app-icon.png",(180,180)),
    ("/apple-touch-icon.png",(180,180)),
    ("/apple-touch-icon-180x180.png",(180,180)),
    ("/app-icon-192.png",(192,192)),
    ("/app-icon-512.png",(512,512)),
):
    status,headers,body=request(path,attempts=5)
    if status!=200 or body[:8]!=b"\x89PNG\r\n\x1a\n":
        raise SystemExit(f"V107 runtime smoke FAIL: {path}")
    if len(body)<24 or struct.unpack(">II",body[16:24])!=expected:
        raise SystemExit(f"V107 runtime smoke FAIL: {path} dimensions")

for path,needle in (
    ("/privacy",b"Gaming Shorts Factory"),
    ("/terms",b"Gaming Shorts Factory"),
    ("/account",b"Gaming Shorts Factory"),
    ("/social-connect",b"Gaming Shorts Factory"),
):
    status,headers,body=request(path,attempts=5)
    if status!=200 or needle.lower() not in body.lower():
        raise SystemExit(f"V107 runtime smoke FAIL: {path}")

# Real HTTP fallback upload through Nginx -> companion server -> secure /media route.
with tempfile.TemporaryDirectory(prefix="gsf_v107_smoke_") as td:
    src=os.path.join(td,"smoke.mp4")
    subprocess.run(
        [
            "/usr/bin/ffmpeg","-hide_banner","-loglevel","error","-y",
            "-f","lavfi","-i","testsrc2=size=160x90:rate=15",
            "-f","lavfi","-i","sine=frequency=660:sample_rate=48000",
            "-t","0.4","-c:v","libx264","-preset","ultrafast","-crf","30",
            "-pix_fmt","yuv420p","-c:a","aac","-b:a","64k","-shortest",
            "-movflags","+faststart",src,
        ],
        check=True,timeout=30,
    )
    raw=open(src,"rb").read()
    upload_id="smokev107"
    h={
        "X-GSF-Upload-ID":upload_id,
        "X-GSF-Filename":"smoke.mp4",
        "X-GSF-File-Size":str(len(raw)),
        "X-GSF-Chunk-Start":"0",
        "X-GSF-Chunk-Index":"0",
        "X-GSF-Chunk-Count":"1",
        "Content-Type":"application/octet-stream",
        "Content-Length":str(len(raw)),
    }
    status,headers,reply=request("/direct-upload/chunk",method="PUT",data=raw,headers=h,timeout=30)
    payload=json.loads(reply.decode("utf-8"))
    if status!=200 or not payload.get("ok") or not payload.get("completed"):
        raise SystemExit("V107 runtime smoke FAIL: direct upload fallback")
    media_path=f"/media/{SESSION_COOKIE}/media/source_direct_smoke_{upload_id}.mp4"
    status,headers,roundtrip=request(media_path,timeout=10)
    if status!=200 or roundtrip!=raw:
        raise SystemExit("V107 runtime smoke FAIL: secure media roundtrip")

    # Safari, Chrome and Android players rely heavily on byte-range requests.
    status,headers,partial=request(
        media_path,
        headers={"Range":"bytes=0-31"},
        timeout=10,
    )
    content_range=str(headers.get("Content-Range","") or "")
    if status!=206 or partial!=raw[:32] or not content_range.startswith("bytes 0-31/"):
        raise SystemExit(
            "V107 runtime smoke FAIL: media byte-range support "
            f"status={status} range={content_range!r}"
        )
print("V107 direct-upload/media + Range smoke: PASS",flush=True)

# Device-specific upload policy over the actual HTTP route.
for ua,expected,label in (
    ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/154 Safari/537.36",8,"desktop"),
    ("Mozilla/5.0 (iPhone; CPU iPhone OS 19_0 like Mac OS X) Mobile/15E148 Safari/605.1",3,"iPhone"),
    ("Mozilla/5.0 (iPad; CPU OS 19_0 like Mac OS X) Mobile/15E148 Safari/605.1",3,"iPad"),
    ("Mozilla/5.0 (Linux; Android 16; Pixel 10) Chrome/154 Mobile Safari/537.36",3,"Android"),
):
    status,headers,body=request(
        "/direct-upload/capabilities",
        headers={"User-Agent":ua},
        attempts=5,
    )
    device_caps=json.loads(body.decode("utf-8"))
    if status!=200 or not device_caps.get("ok") or int(device_caps.get("concurrency",0))!=expected:
        raise SystemExit(f"V107 runtime smoke FAIL: {label} upload policy")
print("V107 desktop/iOS/iPadOS/Android upload policy smoke: PASS",flush=True)

# If production S3 is connected, verify credentials/permissions with multipart init + abort.
status,headers,body=request("/direct-upload/capabilities",attempts=5)
caps=json.loads(body.decode("utf-8"))
if status!=200 or not caps.get("ok"):
    raise SystemExit("V107 runtime smoke FAIL: upload capabilities")
if caps.get("bucket"):
    init_body=json.dumps(
        {"name":"smoke-s3.mp4","size":1024,"type":"video/mp4"},
        separators=(",",":"),
    ).encode("utf-8")
    status,headers,body=request(
        "/direct-upload/bucket/init",
        method="POST",
        data=init_body,
        headers={"Content-Type":"application/json","Content-Length":str(len(init_body))},
        timeout=20,
    )
    init=json.loads(body.decode("utf-8"))
    if status!=200 or not init.get("ok") or not init.get("multipart_id"):
        raise SystemExit("V107 runtime smoke FAIL: S3 multipart init")
    abort_body=json.dumps(
        {
            "upload_id":init["upload_id"],
            "key":init["key"],
            "multipart_id":init["multipart_id"],
        },
        separators=(",",":"),
    ).encode("utf-8")
    status,headers,body=request(
        "/direct-upload/bucket/abort",
        method="POST",
        data=abort_body,
        headers={"Content-Type":"application/json","Content-Length":str(len(abort_body))},
        timeout=20,
    )
    aborted=json.loads(body.decode("utf-8"))
    if status!=200 or not aborted.get("ok"):
        raise SystemExit("V107 runtime smoke FAIL: S3 multipart abort")
    print("V107 S3 init/abort smoke: PASS",flush=True)
else:
    print("V107 S3 smoke: SKIP (bucket not configured on this service)",flush=True)

print("V107 runtime smoke: PASS",flush=True)
