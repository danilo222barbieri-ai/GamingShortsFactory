#!/usr/bin/env python3
import base64,gzip,hashlib,sys
from pathlib import Path

def emit(label,path,chunk_size=6000):
    raw=Path(path).read_bytes()
    packed=gzip.compress(raw,compresslevel=9)
    b64=base64.b64encode(packed).decode("ascii")
    chunks=[b64[i:i+chunk_size] for i in range(0,len(b64),chunk_size)]
    print(
        f"GSF_CANON_{label}_META count={len(chunks)} "
        f"sha256={hashlib.sha256(raw).hexdigest()} raw={len(raw)} gzip={len(packed)}",
        flush=True
    )
    for i,chunk in enumerate(chunks):
        print(f"GSF_CANON_{label}_{i:03d}={chunk}",flush=True)

emit("APP",sys.argv[1])
emit("CORE",sys.argv[2])
