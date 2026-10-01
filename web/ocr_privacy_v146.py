from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter, ImageOps


_EMAIL=re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",re.I)
_IP=re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b")
_PHONE=re.compile(r"(?<!\d)(?:\+?\d[\d .()\-]{7,}\d)(?!\d)")
_URL=re.compile(r"\b(?:https?://|www\.)\S+\b",re.I)
_DISCORD=re.compile(r"(?:discord\.gg/|discord(?:app)?\.com/invite/)\S+",re.I)
_HANDLE=re.compile(r"(?<!\w)@[A-Za-z0-9_.]{3,32}")
_NOTIFICATION_WORDS=("notification","message","party invite","friend request","discord","xbox","playstation","steam")


def _clean_text(value):
    return " ".join(str(value or "").replace("\n"," ").replace("\r"," ").split())


def _prep_image(src, dst):
    img=Image.open(src).convert("L")
    img=ImageOps.autocontrast(img)
    img=ImageEnhance.Contrast(img).enhance(1.7)
    img=img.filter(ImageFilter.SHARPEN)
    w,h=img.size
    if max(w,h)<1400:
        scale=max(1.0,1400.0/max(w,h))
        img=img.resize((max(1,int(w*scale)),max(1,int(h*scale))),Image.Resampling.LANCZOS)
    img.save(dst,quality=95)
    return dst


def _run_text(cmd, timeout=20):
    p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=timeout,check=False)
    if p.returncode!=0:
        return ""
    return p.stdout or ""


def ocr_frame(path, languages="eng+ita"):
    src=Path(path)
    if not src.is_file() or not shutil.which("tesseract"):
        return {"path":str(src),"text":"","words":[],"engine":"unavailable"}
    with tempfile.TemporaryDirectory(prefix="gsf-ocr-") as td:
        pre=Path(td)/"frame.png"
        try:
            _prep_image(src,pre)
            txt=_run_text(["tesseract",str(pre),"stdout","-l",languages,"--psm","11"],timeout=25)
        except Exception:
            txt=""
    cleaned=_clean_text(txt)
    words=[x for x in re.split(r"\s+",cleaned) if x][:180]
    return {"path":str(src),"text":cleaned,"words":words,"engine":"tesseract"}


def qr_frame(path):
    src=Path(path)
    if not src.is_file() or not shutil.which("zbarimg"):
        return []
    try:
        raw=_run_text(["zbarimg","--quiet","--raw",str(src)],timeout=12)
        return [line.strip() for line in raw.splitlines() if line.strip()][:8]
    except Exception:
        return []


def classify_sensitive(text, qr_values=None):
    text=_clean_text(text)
    low=text.lower()
    findings=[]
    for kind,rx in (
        ("email",_EMAIL),("ip",_IP),("phone",_PHONE),("url",_URL),
        ("discord_invite",_DISCORD),("handle",_HANDLE),
    ):
        for m in rx.finditer(text):
            value=m.group(0)
            findings.append({"kind":kind,"value":value[:160]})
    for token in _NOTIFICATION_WORDS:
        if token in low:
            findings.append({"kind":"overlay_hint","value":token})
    for value in qr_values or []:
        findings.append({"kind":"qr_code","value":str(value)[:200]})
    unique=[]; seen=set()
    for row in findings:
        k=(row["kind"],row["value"])
        if k not in seen:
            seen.add(k); unique.append(row)
    return unique


def scan_frame(path,languages="eng+ita"):
    ocr=ocr_frame(path,languages=languages)
    qr=qr_frame(path)
    findings=classify_sensitive(ocr.get("text"),qr)
    return {
        "path":str(path),
        "ocr":[ocr.get("text") or ""],
        "ocr_words":ocr.get("words") or [],
        "privacy_findings":findings,
        "qr":qr,
        "sensitive":bool(findings),
        "engine":"v146-ocr-privacy",
    }


def scan_manifest(manifest,max_frames=12,languages="eng+ita"):
    frames=[dict(x) for x in (dict(manifest or {}).get("frames") or []) if isinstance(x,dict)]
    rows=[]
    for frame in frames[:max(1,int(max_frames))]:
        p=frame.get("path")
        if not p:
            continue
        row=scan_frame(p,languages=languages)
        row["time"]=frame.get("time")
        rows.append(row)
    return {
        "engine":"v146-ocr-privacy",
        "frames":rows,
        "sensitive_frames":[x for x in rows if x.get("sensitive")],
        "publish_guard":"review" if any(x.get("sensitive") for x in rows) else "clear",
        "frame_count":len(rows),
    }


def merge_provider_results(visual_rows,privacy_report):
    visual={str(x.get("path") or ""):dict(x) for x in (visual_rows or []) if isinstance(x,dict)}
    for row in (dict(privacy_report or {}).get("frames") or []):
        if not isinstance(row,dict):
            continue
        p=str(row.get("path") or "")
        base=visual.setdefault(p,{"path":p})
        base["ocr"]=row.get("ocr") or []
        labels=list(base.get("labels") or [])
        for finding in row.get("privacy_findings") or []:
            kind=str((finding or {}).get("kind") or "")
            if kind and kind not in labels:
                labels.append(kind)
        base["labels"]=labels
        base["privacy_findings"]=row.get("privacy_findings") or []
    return list(visual.values())
