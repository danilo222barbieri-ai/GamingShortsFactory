from pathlib import Path
import ast

src=Path('/app/GamingShortsFactory_V104_DIRECT_SOCIAL.py')
out=Path('/app/GamingShortsFactory_V104_1_RENDER_DIAGNOSTICS.py')
s=src.read_text(encoding='utf-8')

# V104.1 is diagnostic-only. Keep the deploy compatible when the render core
# evolves: instrumentation is applied only when the exact known anchor exists.
# A stale diagnostic anchor must never block production or later legal pages.
try:
    tree=ast.parse(s)
    node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_gsf_render_core')
    core=ast.get_source_segment(s,node) or ''
except Exception:
    node=None
    core=''

old='''        for encoder,cmd in attempts:\n            try:\n                r=subprocess.run(\n                    cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,\n                    text=True,timeout=max(420.0,min(3600.0,duration*36.0))\n                )\n            except Exception as e:\n                last_error=str(e)\n                continue\n'''
new='''        for encoder,cmd in attempts:\n            _diag_timeout=max(420.0,min(3600.0,duration*36.0))\n            _diag_started=time.perf_counter()\n            print("GSF_FINAL_RENDER_START",f"encoder={encoder}",f"fmt={fmt}",f"timeout={_diag_timeout:.1f}",flush=True)\n            try:\n                r=subprocess.run(\n                    cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,\n                    text=True,timeout=_diag_timeout\n                )\n                _diag_elapsed=time.perf_counter()-_diag_started\n                print("GSF_FINAL_RENDER_EXIT",f"encoder={encoder}",f"returncode={r.returncode}",f"elapsed={_diag_elapsed:.2f}",flush=True)\n            except subprocess.TimeoutExpired as e:\n                _diag_elapsed=time.perf_counter()-_diag_started\n                _diag_stderr=e.stderr or ""\n                if isinstance(_diag_stderr,bytes): _diag_stderr=_diag_stderr.decode("utf-8","replace")\n                last_error=f"Render timeout dopo {_diag_elapsed:.1f}s. "+str(_diag_stderr)[-1800:]\n                print("GSF_FINAL_RENDER_TIMEOUT",f"encoder={encoder}",f"elapsed={_diag_elapsed:.2f}",flush=True)\n                continue\n            except Exception as e:\n                last_error=str(e)\n                print("GSF_FINAL_RENDER_EXCEPTION",f"encoder={encoder}","error="+repr(last_error),flush=True)\n                continue\n'''

if node is not None and old in core:
    core=core.replace(old,new,1)
    lines=s.splitlines(keepends=True)
    s=''.join(lines[:node.lineno-1])+core.rstrip()+'\n\n'+''.join(lines[node.end_lineno:])
    print('V104.1 render diagnostics instrumentation applied')
else:
    print('V104.1 diagnostic anchor changed; preserving current render core')

# Graphic-only spacing. Apply when the known anchors exist; never fail a deploy
# for cosmetic/diagnostic patches.
final_anchor='''    if _show_final_flow:\n        st.divider()\n        st.markdown('<div class="gsf-icon-title">' + _gsf_v67_badge("play", "Crea lo Short finale", "peach") + '</div>', unsafe_allow_html=True)\n'''
final_new='''    if _show_final_flow:\n        st.divider()\n        st.markdown('<div class="gsf-section-gap-final" style="height:30px"></div>', unsafe_allow_html=True)\n        st.markdown('<div class="gsf-icon-title">' + _gsf_v67_badge("play", "Crea lo Short finale", "peach") + '</div>', unsafe_allow_html=True)\n'''
if final_anchor in s:
    s=s.replace(final_anchor,final_new,1)

# Preserve the indentation of the Pubblicazione diretta block. The previous
# substring replacement added the second st.markdown at column 0 and made the
# generated application invalid Python.
social_line='st.markdown(\'<div class="gsf-icon-title">\' + _gsf_v67_badge("publish", "Pubblicazione diretta", "indigo") + \'</div>\', unsafe_allow_html=True)'
lines=s.splitlines(keepends=True)
for i,line in enumerate(lines):
    if social_line in line and 'gsf-section-gap-social' not in ''.join(lines[i+1:i+2]):
        indent=line[:len(line)-len(line.lstrip())]
        had_newline=line.endswith('\n')
        base=line.rstrip('\n')
        lines[i]=base+'\n'+indent+'st.markdown(\'<div class="gsf-section-gap-social" style="height:30px"></div>\', unsafe_allow_html=True)'+'\n'
        break
s=''.join(lines)

marker='Gaming Shorts Factory · V104 Direct Social'
if marker in s:
    s=s.replace(marker,'Gaming Shorts Factory · V104.1 Render Diagnostics',1)

# V104.1 itself must always be valid before any later patch consumes it.
compile(s,str(out),'exec')
out.write_text(s,encoding='utf-8')
print(f'V104.1 compatibility patch applied and compiled: {out}')
