from pathlib import Path
import ast

src=Path('/app/GamingShortsFactory_V104_7_INSTAGRAM_LOGIN.py')
out=Path('/app/GamingShortsFactory_V105_PERF_TELEMETRY.py')
s=src.read_text(encoding='utf-8')

# Import structured V105 telemetry once in the generated app.
if 'from gsf_perf import perf_event as _gsf_perf_event' not in s:
    insert='from gsf_perf import perf_event as _gsf_perf_event\n'
    # Place after standard imports without depending on a specific first import.
    pos=0
    lines=s.splitlines(keepends=True)
    for i,line in enumerate(lines):
        if line.startswith(('import ','from ')):
            pos=i+1
        elif pos and line.strip():
            break
    lines.insert(pos,insert)
    s=''.join(lines)

# Instrument local fallback scan. This exact block is intentionally narrow:
# worker prescan still wins; telemetry exists only if the web process really
# performs the expensive duplicate-capable fallback.
old='''    if scan is None:
        scan = _gsf_ai_scan_base(input_file)

    cache[key] = scan
'''
new='''    if scan is None:
        _gsf_local_scan_t0=time.perf_counter()
        _gsf_perf_event(
            "local_scan_start",
            source=str(input_file),
            engine_version=str(GSF_AI_ENGINE_VERSION),
        )
        scan = _gsf_ai_scan_base(input_file)
        _gsf_perf_event(
            "local_scan_end",
            source=str(input_file),
            engine_version=str(GSF_AI_ENGINE_VERSION),
            elapsed_seconds=round(time.perf_counter()-_gsf_local_scan_t0,3),
        )

    cache[key] = scan
'''
if old not in s:
    raise RuntimeError('V105 local scan telemetry anchor missing')
s=s.replace(old,new,1)

# Instrument final render using the existing V104.3 diagnostic points.
tree=ast.parse(s)
node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_gsf_render_core')
parents={}
for parent in ast.walk(node):
    for child in ast.iter_child_nodes(parent):
        parents[child]=parent

start_print=None
exit_print=None
for n in ast.walk(node):
    if not isinstance(n,ast.Expr) or not isinstance(n.value,ast.Call):
        continue
    vals=[
        x.value for x in ast.walk(n)
        if isinstance(x,ast.Constant) and isinstance(x.value,str)
    ]
    if 'GSF_FINAL_RENDER_START' in vals:
        start_print=n
    if 'GSF_FINAL_RENDER_EXIT' in vals:
        exit_print=n

if start_print is None or exit_print is None:
    raise RuntimeError('V105 render diagnostic anchors missing')

def containing_list(target):
    parent=parents.get(target)
    while parent is not None:
        for field in ('body','orelse','finalbody'):
            seq=getattr(parent,field,None)
            if isinstance(seq,list) and target in seq:
                return seq,seq.index(target)
        target=parent
        parent=parents.get(target)
    return None,None

seq,idx=containing_list(start_print)
if seq is None:
    raise RuntimeError('V105 render start parent list missing')
start_nodes=ast.parse('''_gsf_perf_event(
    "render_start",
    encoder=str(encoder),
    fmt=str(fmt),
    duration_seconds=round(float(duration),3),
    timeout_seconds=round(float(_diag_timeout),3),
)
''').body
seq[idx:idx]=start_nodes

# Rebuild parent relationships because the AST was mutated.
parents={}
for parent in ast.walk(node):
    for child in ast.iter_child_nodes(parent):
        parents[child]=parent
seq,idx=containing_list(exit_print)
if seq is None:
    raise RuntimeError('V105 render exit parent list missing')
end_nodes=ast.parse('''_gsf_perf_event(
    "render_end",
    encoder=str(encoder),
    fmt=str(fmt),
    duration_seconds=round(float(duration),3),
    elapsed_seconds=round(float(_diag_elapsed),3),
    returncode=int(r.returncode),
)
''').body
seq[idx+1:idx+1]=end_nodes

ast.fix_missing_locations(node)
new_core=ast.unparse(node)
lines=s.splitlines(keepends=True)
s=''.join(lines[:node.lineno-1])+new_core.rstrip()+'\n\n'+''.join(lines[node.end_lineno:])

marker='Gaming Shorts Factory · V104.7 Instagram Login'
if marker in s:
    s=s.replace(marker,'Gaming Shorts Factory · V105 Performance Telemetry',1)

compile(s,str(out),'exec')
out.write_text(s,encoding='utf-8')
print(f'V105 telemetry patch applied: {out}')
