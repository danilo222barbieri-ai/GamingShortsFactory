from pathlib import Path
import ast

src=Path('/app/GamingShortsFactory_V104_2_LEGAL_FOOTER.py')
out=Path('/app/GamingShortsFactory_V104_3_MEMORY_SAFE_RENDER.py')
s=src.read_text(encoding='utf-8')

tree=ast.parse(s)
node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_gsf_render_core')

# V104.3 — memory safety, final renderer only.
# Change the libx264 command from two worker threads back to one while
# preserving CRF/preset/profile/level/fps and the bounded x264 parameters.
thread_changes=0
for n in ast.walk(node):
    if not isinstance(n,ast.List):
        continue
    elts=n.elts
    for i in range(len(elts)-1):
        a,b=elts[i],elts[i+1]
        if (
            isinstance(a,ast.Constant) and a.value=='-threads'
            and isinstance(b,ast.Constant) and b.value=='2'
        ):
            b.value='1'
            thread_changes+=1

if thread_changes!=1:
    raise RuntimeError(f'V104.3 expected one final -threads 2 entry, found {thread_changes}')

# Find the real final subprocess.run(cmd, ...) call inside _gsf_render_core.
def is_render_run(assign):
    if not isinstance(assign,ast.Assign):
        return False
    call=assign.value
    if not (
        isinstance(call,ast.Call)
        and isinstance(call.func,ast.Attribute)
        and isinstance(call.func.value,ast.Name)
        and call.func.value.id=='subprocess'
        and call.func.attr=='run'
        and call.args
        and isinstance(call.args[0],ast.Name)
        and call.args[0].id=='cmd'
    ):
        return False
    return any(isinstance(t,ast.Name) and t.id=='r' for t in assign.targets)

render_assigns=[n for n in ast.walk(node) if is_render_run(n)]
if len(render_assigns)!=1:
    raise RuntimeError(f'V104.3 expected one final subprocess.run(cmd), found {len(render_assigns)}')
render_assign=render_assigns[0]

# Build parent map so diagnostics are inserted around the exact render try/loop.
parents={}
for parent in ast.walk(node):
    for child in ast.iter_child_nodes(parent):
        parents[child]=parent

target_try=render_assign
while target_try is not node and not isinstance(target_try,ast.Try):
    target_try=parents.get(target_try)
if not isinstance(target_try,ast.Try):
    raise RuntimeError('V104.3 render subprocess is not inside try')

target_for=target_try
while target_for is not node and not isinstance(target_for,ast.For):
    target_for=parents.get(target_for)
if not isinstance(target_for,ast.For):
    raise RuntimeError('V104.3 render try is not inside attempts loop')

# Do not double-instrument if a later patch ever carries these markers forward.
core_before=ast.get_source_segment(s,node) or ''
if 'GSF_FINAL_RENDER_START' not in core_before:
    start_nodes=ast.parse(
        '_diag_timeout=max(420.0,min(3600.0,duration*36.0))\n'
        '_diag_started=time.perf_counter()\n'
        'print("GSF_FINAL_RENDER_START",f"encoder={encoder}",f"fmt={fmt}",'
        'f"timeout={_diag_timeout:.1f}",flush=True)\n'
    ).body
    idx=target_for.body.index(target_try)
    target_for.body[idx:idx]=start_nodes

    # Reuse the exact timeout value for the subprocess call.
    run_call=render_assign.value
    timeout_kw=next((kw for kw in run_call.keywords if kw.arg=='timeout'),None)
    if timeout_kw is None:
        raise RuntimeError('V104.3 render subprocess timeout keyword missing')
    timeout_kw.value=ast.Name(id='_diag_timeout',ctx=ast.Load())

    # Log every normal FFmpeg exit immediately after subprocess.run.
    exit_nodes=ast.parse(
        '_diag_elapsed=time.perf_counter()-_diag_started\n'
        'print("GSF_FINAL_RENDER_EXIT",f"encoder={encoder}",'
        'f"returncode={r.returncode}",f"elapsed={_diag_elapsed:.2f}",flush=True)\n'
    ).body
    ridx=target_try.body.index(render_assign)
    target_try.body[ridx+1:ridx+1]=exit_nodes

    # Keep every existing exception handler intact and prepend diagnostics.
    if not target_try.handlers:
        raise RuntimeError('V104.3 render try has no exception handlers')
    for _handler in target_try.handlers:
        if _handler.name:
            _err_name=str(_handler.name)
            _diag_src=f'''_diag_elapsed=time.perf_counter()-_diag_started
if isinstance({_err_name},subprocess.TimeoutExpired):
    print("GSF_FINAL_RENDER_TIMEOUT",f"encoder={encoder}",f"elapsed={_diag_elapsed:.2f}",flush=True)
else:
    print("GSF_FINAL_RENDER_EXCEPTION",f"encoder={encoder}","error="+repr(str({_err_name})),flush=True)
'''
        else:
            _diag_src='''_diag_elapsed=time.perf_counter()-_diag_started
_gsf_render_error=__import__("sys").exc_info()[1]
if isinstance(_gsf_render_error,subprocess.TimeoutExpired):
    print("GSF_FINAL_RENDER_TIMEOUT",f"encoder={encoder}",f"elapsed={_diag_elapsed:.2f}",flush=True)
else:
    print("GSF_FINAL_RENDER_EXCEPTION",f"encoder={encoder}","error="+repr(str(_gsf_render_error)),flush=True)
'''
        _handler.body[0:0]=ast.parse(_diag_src).body

ast.fix_missing_locations(node)
new_core=ast.unparse(node)

lines=s.splitlines(keepends=True)
s=''.join(lines[:node.lineno-1])+new_core.rstrip()+'\n\n'+''.join(lines[node.end_lineno:])

marker='Gaming Shorts Factory · V104 Direct Social'
if marker in s:
    s=s.replace(marker,'Gaming Shorts Factory · V104.3 Memory Safe Render',1)

compile(s,str(out),'exec')
out.write_text(s,encoding='utf-8')
print(f'V104.3 memory-safe render applied: {out} | threads={thread_changes}')
