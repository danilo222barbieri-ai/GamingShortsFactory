from pathlib import Path
import ast

src=Path('/app/GamingShortsFactory_V104_7_INSTAGRAM_LOGIN.py')
out=Path('/app/GamingShortsFactory_V105_HARDENED.py')
s=src.read_text(encoding='utf-8')

tree=ast.parse(s)
core=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_gsf_render_core')

helpers=r'''
def _gsf_v105_render_worker_config():
    return (
        str(os.environ.get("GSF_WORKER_URL","") or "").rstrip("/"),
        str(os.environ.get("GSF_WORKER_TOKEN","") or ""),
    )


def _gsf_v105_bucket_source_key(path):
    try:
        marker=GSF_PREVIEW_DIR/".direct_upload_ready.json"
        data=json.loads(marker.read_text(encoding="utf-8"))
        marker_path=str(data.get("path","") or "")
        key=str(data.get("bucket_key","") or "")
        if marker_path and key and Path(marker_path).resolve()==Path(path).resolve():
            return key
    except Exception:
        pass
    return ""


def _gsf_v105_command_files(cmd,output_path):
    roots=[]
    for candidate in (
        globals().get("GSF_PREVIEW_DIR"),
        globals().get("GSF_SESSION_TMP_DIR"),
        globals().get("GSF_SESSION_EXPORT_DIR"),
    ):
        try:
            p=Path(candidate)
            if p.is_dir():
                roots.append(p)
        except Exception:
            pass

    tokens=[str(x) for x in (cmd or [])]
    output_abs=str(Path(output_path))
    found={}
    for token in tokens:
        if token==output_abs:
            continue
        try:
            p=Path(token)
            if p.is_file():
                found[str(p)]=p
        except Exception:
            pass

    # ASS/subtitle paths often live inside a filter token rather than as a
    # standalone argv entry. Search only this anonymous session's directories.
    for root in roots:
        try:
            for p in root.rglob("*"):
                if not p.is_file():
                    continue
                sp=str(p)
                if sp==output_abs:
                    continue
                if any(sp in token for token in tokens):
                    found[sp]=p
        except Exception:
            pass

    return list(found.values())


def _gsf_v105_worker_request(url,payload,token="",timeout=45):
    import urllib.request as _ur
    raw=json.dumps(payload,separators=(",",":"),ensure_ascii=False).encode("utf-8")
    headers={"Content-Type":"application/json"}
    if token:
        headers["X-GSF-Worker-Token"]=token
    req=_ur.Request(url,data=raw,headers=headers,method="POST")
    with _ur.urlopen(req,timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _gsf_v105_worker_status(url,job_id,token="",timeout=30):
    import urllib.parse as _up
    import urllib.request as _ur
    headers={}
    if token:
        headers["X-GSF-Worker-Token"]=token
    req=_ur.Request(
        url+"/render/status?"+_up.urlencode({"job_id":job_id}),
        headers=headers,
        method="GET",
    )
    with _ur.urlopen(req,timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _gsf_v105_remote_render(cmd,output_path,timeout):
    import secrets as _secrets
    worker_url,worker_token=_gsf_v105_render_worker_config()
    if not worker_url:
        raise RuntimeError("worker URL non configurato")

    client,bucket=_gsf_shared_tiktok_s3()
    if client is None or not bucket:
        raise RuntimeError("storage S3 non disponibile")

    command=[str(x) for x in (cmd or [])]
    if len(command)<2:
        raise RuntimeError("comando FFmpeg non valido")
    args=command[1:]
    if str(args[-1])!=str(output_path):
        raise RuntimeError("output FFmpeg non riconosciuto")
    args[-1]="{OUTPUT}"

    job_tag=_secrets.token_hex(12)
    files={}
    cleanup_keys=[]
    paths=_gsf_v105_command_files(command,output_path)
    if not paths:
        raise RuntimeError("input render non individuato")

    for idx,p in enumerate(paths):
        placeholder=f"FILE{idx}"
        key=_gsf_v105_bucket_source_key(p)
        cleanup=False
        if not key:
            suffix=p.suffix.lower()
            key=f"render-stage/{GSF_SESSION_ID}/{job_tag}/{placeholder}{suffix}"
            client.upload_file(
                str(p),bucket,key,
                ExtraArgs={"CacheControl":"no-store"}
            )
            cleanup=True
        marker="{"+placeholder+"}"
        original=str(p)
        args=[token.replace(original,marker) for token in args]
        files[placeholder]={"key":key,"name":p.name}
        if cleanup:
            cleanup_keys.append(key)

    # Every existing local input must have been replaced by a worker placeholder.
    for p in paths:
        if any(str(p) in token for token in args):
            raise RuntimeError("path locale non sostituito nel render remoto")

    result_key=f"render-results/{GSF_SESSION_ID}/{job_tag}.mp4"
    terminal=False
    try:
        queued=_gsf_v105_worker_request(
            worker_url+"/render",
            {
                "args":args,
                "files":files,
                "result_key":result_key,
                "timeout":float(timeout),
            },
            token=worker_token,
            timeout=45,
        )
        job_id=str((queued or {}).get("job_id","") or "")
        if not job_id:
            raise RuntimeError("worker non ha restituito job_id")

        deadline=time.time()+max(90.0,float(timeout)+120.0)
        last={}
        while time.time()<deadline:
            status=_gsf_v105_worker_status(worker_url,job_id,worker_token,timeout=30)
            last=dict((status or {}).get("job") or {})
            state=str(last.get("state","") or "")
            if state=="done":
                terminal=True
                remote_key=str(last.get("result_key","") or result_key)
                tmp=Path(str(output_path)+".v105.remote")
                with open(tmp,"wb") as out_f:
                    client.download_fileobj(bucket,remote_key,out_f)
                    out_f.flush()
                if not tmp.is_file() or tmp.stat().st_size<=1024:
                    tmp.unlink(missing_ok=True)
                    raise RuntimeError("master remoto vuoto")
                os.replace(tmp,output_path)
                try:
                    client.delete_object(Bucket=bucket,Key=remote_key)
                except Exception:
                    pass
                print(
                    "GSF_REMOTE_RENDER_DONE",
                    f"job_id={job_id}",
                    f"bytes={Path(output_path).stat().st_size}",
                    f"render_seconds={last.get('render_seconds','')}",
                    f"threads={last.get('threads','')}",
                    flush=True,
                )
                return subprocess.CompletedProcess(command,0,stdout=b"",stderr=b"")
            if state=="error":
                terminal=True
                raise RuntimeError(str(last.get("error","worker render error"))[:700])
            time.sleep(.8)

        raise subprocess.TimeoutExpired(command,float(timeout))
    finally:
        # Do not delete staging while a timed-out worker could still be reading it.
        if terminal:
            for key in cleanup_keys:
                try:
                    client.delete_object(Bucket=bucket,Key=key)
                except Exception:
                    pass


def _gsf_v105_run_render(cmd,output_path,timeout):
    worker_url,_worker_token=_gsf_v105_render_worker_config()
    if GSF_WEB_MODE and worker_url:
        try:
            return _gsf_v105_remote_render(cmd,output_path,timeout)
        except subprocess.TimeoutExpired:
            print("GSF_REMOTE_RENDER_FALLBACK reason=timeout",flush=True)
        except Exception as exc:
            print(
                "GSF_REMOTE_RENDER_FALLBACK",
                "reason="+repr(str(exc)[:320]),
                flush=True,
            )

    # Exact V104.7 execution path kept as a safe fallback.
    return subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )


'''

lines=s.splitlines(keepends=True)
s=''.join(lines[:core.lineno-1])+helpers+''.join(lines[core.lineno-1:])

# Reparse after inserting helpers and replace only the real final
# subprocess.run(cmd, ...) inside _gsf_render_core.
tree=ast.parse(s)
core=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_gsf_render_core')
render_calls=[]
for node in ast.walk(core):
    if not isinstance(node,ast.Call):
        continue
    fn=node.func
    if (
        isinstance(fn,ast.Attribute)
        and isinstance(fn.value,ast.Name)
        and fn.value.id=="subprocess"
        and fn.attr=="run"
        and node.args
        and isinstance(node.args[0],ast.Name)
        and node.args[0].id=="cmd"
    ):
        render_calls.append(node)
if len(render_calls)!=1:
    raise RuntimeError(f"V105 expected one final subprocess.run(cmd), found {len(render_calls)}")

target=render_calls[0]
target.func=ast.Name(id="_gsf_v105_run_render",ctx=ast.Load())
target.args=[
    ast.Name(id="cmd",ctx=ast.Load()),
    ast.Name(id="output_path",ctx=ast.Load()),
    ast.Name(id="_diag_timeout",ctx=ast.Load()),
]
target.keywords=[]
ast.fix_missing_locations(core)
new_core=ast.unparse(core)

lines=s.splitlines(keepends=True)
s=''.join(lines[:core.lineno-1])+new_core.rstrip()+"\n\n"+''.join(lines[core.end_lineno:])

marker="Gaming Shorts Factory · V104.7 Instagram Login"
if marker in s:
    s=s.replace(marker,"Gaming Shorts Factory · V105 Hardening",1)

compile(s,str(out),"exec")
out.write_text(s,encoding="utf-8")
print(f"V105 render offload applied: {out}")
