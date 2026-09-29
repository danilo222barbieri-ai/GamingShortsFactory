#!/usr/bin/env python3
import http.cookiejar
import json
import os
import struct
import time
import urllib.error
import urllib.request

base=f"http://127.0.0.1:{int(os.environ.get('PORT','8080'))}"
jar=http.cookiejar.CookieJar()
opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))


def get(path, attempts=30):
    last=None
    for _ in range(attempts):
        try:
            req=urllib.request.Request(base+path,headers={"User-Agent":"GSF-V107-Runtime-Smoke/1.0"})
            with opener.open(req,timeout=4) as r:
                return int(r.status),r.headers, r.read(2*1024*1024)
        except Exception as exc:
            last=exc
            time.sleep(1)
    raise RuntimeError(f"{path}: {last}")


status,headers,body=get("/")
if status!=200 or b"streamlit" not in body.lower():
    raise SystemExit("V107 runtime smoke FAIL: root")

status,headers,body=get("/manifest.webmanifest",5)
manifest=json.loads(body.decode("utf-8"))
if status!=200 or manifest.get("short_name")!="GSF":
    raise SystemExit("V107 runtime smoke FAIL: manifest")
icons=manifest.get("icons") or []
if not icons or icons[0].get("sizes")!="180x180":
    raise SystemExit("V107 runtime smoke FAIL: manifest icon")

for path in ("/app-icon.png","/apple-touch-icon.png","/apple-touch-icon-180x180.png"):
    status,headers,body=get(path,5)
    if status!=200 or body[:8]!=b"\x89PNG\r\n\x1a\n":
        raise SystemExit(f"V107 runtime smoke FAIL: {path}")
    if len(body)<24 or struct.unpack(">II",body[16:24])!=(180,180):
        raise SystemExit(f"V107 runtime smoke FAIL: {path} dimensions")

for path,needle in (
    ("/privacy",b"Gaming Shorts Factory"),
    ("/terms",b"Gaming Shorts Factory"),
    ("/account",b"Gaming Shorts Factory"),
    ("/social-connect",b"Gaming Shorts Factory"),
):
    status,headers,body=get(path,5)
    if status!=200 or needle.lower() not in body.lower():
        raise SystemExit(f"V107 runtime smoke FAIL: {path}")

print("V107 runtime smoke: PASS",flush=True)
