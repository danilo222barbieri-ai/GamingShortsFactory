from pathlib import Path
import ast

src=Path('/app/GamingShortsFactory_V104_DIRECT_SOCIAL.py')
out=Path('/app/GamingShortsFactory_V104_1_RENDER_DIAGNOSTICS.py')
s=src.read_text(encoding='utf-8')

tree=ast.parse(s)
node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_gsf_render_core')
core=ast.get_source_segment(s,node) or ''

# Diagnostic-only instrumentation. Do not change encoder, CRF, preset,
# resolution, filters, threads, timeout or output validation.
old='''        for encoder,cmd in attempts:
            try:
                r=subprocess.run(
                    cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                    text=True,timeout=max(420.0,min(3600.0,duration*36.0))
                )
            except Exception as e:
                last_error=str(e)
                continue
'''
new='''        for encoder,cmd in attempts:
            _diag_timeout=max(420.0,min(3600.0,duration*36.0))
            _diag_started=time.perf_counter()
            _diag_safe_cmd=[]
            for _arg in cmd:
                _txt=str(_arg)
                if len(_txt)>900:
                    _txt=_txt[:900]+"...[truncated]"
                _diag_safe_cmd.append(_txt)
            print(
                "GSF_FINAL_RENDER_START",
                f"encoder={encoder}",
                f"fmt={fmt}",
                f"start={float(start):.3f}",
                f"duration={float(duration):.3f}",
                f"timeout={_diag_timeout:.1f}",
                f"input={source_path}",
                f"output={output_path}",
                "cmd="+repr(_diag_safe_cmd),
                flush=True,
            )
            try:
                r=subprocess.run(
                    cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                    text=True,timeout=_diag_timeout
                )
                _diag_elapsed=time.perf_counter()-_diag_started
                _diag_stderr=(r.stderr or "")[-5000:].replace("\\r","\\n")
                _diag_stdout=(r.stdout or "")[-1500:].replace("\\r","\\n")
                _diag_size=(
                    os.path.getsize(output_path)
                    if os.path.exists(output_path) else 0
                )
                print(
                    "GSF_FINAL_RENDER_EXIT",
                    f"encoder={encoder}",
                    f"returncode={r.returncode}",
                    f"elapsed={_diag_elapsed:.2f}",
                    f"output_bytes={_diag_size}",
                    "stderr_tail="+repr(_diag_stderr),
                    "stdout_tail="+repr(_diag_stdout),
                    flush=True,
                )
            except subprocess.TimeoutExpired as e:
                _diag_elapsed=time.perf_counter()-_diag_started
                _diag_stderr=e.stderr or ""
                _diag_stdout=e.stdout or ""
                if isinstance(_diag_stderr,bytes):
                    _diag_stderr=_diag_stderr.decode("utf-8","replace")
                if isinstance(_diag_stdout,bytes):
                    _diag_stdout=_diag_stdout.decode("utf-8","replace")
                _diag_stderr=str(_diag_stderr)[-5000:].replace("\\r","\\n")
                _diag_stdout=str(_diag_stdout)[-1500:].replace("\\r","\\n")
                _diag_size=(
                    os.path.getsize(output_path)
                    if os.path.exists(output_path) else 0
                )
                print(
                    "GSF_FINAL_RENDER_TIMEOUT",
                    f"encoder={encoder}",
                    f"elapsed={_diag_elapsed:.2f}",
                    f"timeout={_diag_timeout:.1f}",
                    f"output_bytes={_diag_size}",
                    "stderr_tail="+repr(_diag_stderr),
                    "stdout_tail="+repr(_diag_stdout),
                    flush=True,
                )
                last_error=(
                    f"Render timeout dopo {_diag_elapsed:.1f}s "
                    f"(limite {_diag_timeout:.0f}s). "
                    +(_diag_stderr[-1800:] or "FFmpeg non ha restituito altri dettagli.")
                )
                continue
            except Exception as e:
                _diag_elapsed=time.perf_counter()-_diag_started
                print(
                    "GSF_FINAL_RENDER_EXCEPTION",
                    f"encoder={encoder}",
                    f"elapsed={_diag_elapsed:.2f}",
                    f"type={type(e).__name__}",
                    "error="+repr(str(e)),
                    flush=True,
                )
                last_error=str(e)
                continue
'''
if old not in core:
    raise RuntimeError('V104.1 render subprocess anchor not found')
core=core.replace(old,new,1)

old='''            if r.returncode==0 and os.path.exists(output_path) and os.path.getsize(output_path)>0:
                social_master=_gsf_validate_social_master(output_path,fmt=fmt)
                if not social_master.get("ok"):
                    last_error=(
                        "Master MP4 non compatibile: "
                        + "; ".join(social_master.get("errors") or ["verifica fallita"])
                    )
                    continue
'''
new='''            if r.returncode==0 and os.path.exists(output_path) and os.path.getsize(output_path)>0:
                social_master=_gsf_validate_social_master(output_path,fmt=fmt)
                if not social_master.get("ok"):
                    last_error=(
                        "Master MP4 non compatibile: "
                        + "; ".join(social_master.get("errors") or ["verifica fallita"])
                    )
                    print(
                        "GSF_FINAL_RENDER_VALIDATION_FAIL",
                        f"encoder={encoder}",
                        "errors="+repr(social_master.get("errors") or []),
                        "video="+repr(social_master.get("video") or {}),
                        "audio="+repr(social_master.get("audio") or {}),
                        flush=True,
                    )
                    continue
'''
if old not in core:
    raise RuntimeError('V104.1 validator anchor not found')
core=core.replace(old,new,1)

old='''            last_error=(r.stderr or "")[-3500:] or f"{encoder} non riuscito"
'''
new='''            last_error=(r.stderr or "")[-3500:] or f"{encoder} non riuscito"
            print(
                "GSF_FINAL_RENDER_FAIL",
                f"encoder={encoder}",
                f"returncode={r.returncode}",
                "error_tail="+repr(last_error[-3500:]),
                flush=True,
            )
'''
if old not in core:
    raise RuntimeError('V104.1 final error anchor not found')
core=core.replace(old,new,1)

lines=s.splitlines(keepends=True)
s=''.join(lines[:node.lineno-1])+core.rstrip()+'\n\n'+''.join(lines[node.end_lineno:])

marker='Gaming Shorts Factory · V104 Direct Social'
if marker not in s:
    raise RuntimeError('V104.1 marker missing')
s=s.replace(marker,'Gaming Shorts Factory · V104.1 Render Diagnostics',1)

out.write_text(s,encoding='utf-8')
print(f'V104.1 render diagnostics applied: {out}')
