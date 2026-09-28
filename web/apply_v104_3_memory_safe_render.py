from pathlib import Path
import ast

src=Path('/app/GamingShortsFactory_V104_2_LEGAL_FOOTER.py')
out=Path('/app/GamingShortsFactory_V104_3_MEMORY_SAFE_RENDER.py')
s=src.read_text(encoding='utf-8')

tree=ast.parse(s)
node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_gsf_render_core')
core=ast.get_source_segment(s,node) or ''

# 1) Memory safety: revert only the final libx264 worker count.
old_threads='''                    "-threads","2",
                    "-x264-params","rc-lookahead=16:ref=2:bframes=2",
'''
new_threads='''                    "-threads","1",
                    "-x264-params","rc-lookahead=16:ref=2:bframes=2",
'''
if old_threads not in core:
    raise RuntimeError('V104.3 expected 2-thread final render block not found')
core=core.replace(old_threads,new_threads,1)

# 2) Restore diagnostic logging around the real final FFmpeg process.
old_run='''        for encoder,cmd in attempts:
            try:
                r=subprocess.run(
                    cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                    text=True,timeout=max(420.0,min(3600.0,duration*36.0))
                )
            except Exception as e:
                last_error=str(e)
                continue
'''
new_run='''        for encoder,cmd in attempts:
            _diag_timeout=max(420.0,min(3600.0,duration*36.0))
            _diag_started=time.perf_counter()
            print("GSF_FINAL_RENDER_START",f"encoder={encoder}",f"fmt={fmt}",f"timeout={_diag_timeout:.1f}",flush=True)
            try:
                r=subprocess.run(
                    cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                    text=True,timeout=_diag_timeout
                )
                _diag_elapsed=time.perf_counter()-_diag_started
                print("GSF_FINAL_RENDER_EXIT",f"encoder={encoder}",f"returncode={r.returncode}",f"elapsed={_diag_elapsed:.2f}",flush=True)
            except subprocess.TimeoutExpired as e:
                _diag_elapsed=time.perf_counter()-_diag_started
                _diag_stderr=e.stderr or ""
                if isinstance(_diag_stderr,bytes):
                    _diag_stderr=_diag_stderr.decode("utf-8","replace")
                last_error=f"Render timeout dopo {_diag_elapsed:.1f}s. "+str(_diag_stderr)[-1800:]
                print("GSF_FINAL_RENDER_TIMEOUT",f"encoder={encoder}",f"elapsed={_diag_elapsed:.2f}",flush=True)
                continue
            except Exception as e:
                last_error=str(e)
                print("GSF_FINAL_RENDER_EXCEPTION",f"encoder={encoder}","error="+repr(last_error),flush=True)
                continue
'''
if old_run not in core:
    raise RuntimeError('V104.3 final render subprocess block not found')
core=core.replace(old_run,new_run,1)

lines=s.splitlines(keepends=True)
s=''.join(lines[:node.lineno-1])+core.rstrip()+'\n\n'+''.join(lines[node.end_lineno:])

marker='Gaming Shorts Factory · V104 Direct Social'
if marker in s:
    s=s.replace(marker,'Gaming Shorts Factory · V104.3 Memory Safe Render',1)

compile(s,str(out),'exec')
out.write_text(s,encoding='utf-8')
print(f'V104.3 memory-safe render applied: {out}')
