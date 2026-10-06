#!/usr/bin/env python3
import ast
from pathlib import Path

APP_SRC = Path("/app/GamingShortsFactory_V154_STRUCTURAL_HOME.py")
APP_OUT = Path("/app/GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py")
UPLOAD_SERVER = Path("/app/web/direct_upload_server.py")


# 1) Keep bucket materialization intentionally narrow on the 1 GB web service.
upload_src = UPLOAD_SERVER.read_text(encoding="utf-8")
old_materialize = '''def _materialize_concurrency():
    try:
        value=int(os.environ.get("GSF_MATERIALIZE_CONCURRENCY","6") or 6)
    except Exception:
        value=6
    return max(1,min(8,value))
'''
new_materialize = '''def _materialize_concurrency():
    try:
        value=int(os.environ.get("GSF_MATERIALIZE_CONCURRENCY","1") or 1)
    except Exception:
        value=1
    return max(1,min(2,value))
'''
if new_materialize not in upload_src:
    if old_materialize not in upload_src:
        raise RuntimeError("V293 materialization concurrency block not found")
    upload_src = upload_src.replace(old_materialize, new_materialize, 1)
    compile(upload_src, str(UPLOAD_SERVER), "exec")
    UPLOAD_SERVER.write_text(upload_src, encoding="utf-8")


# 2) Serialize the real final FFmpeg execution across Streamlit sessions.
# Later GSF versions may wrap subprocess.run in a helper, so anchor on the
# established render result variable `r` plus the command object `cmd` instead
# of depending on a specific callable name.
s = APP_SRC.read_text(encoding="utf-8")
tree = ast.parse(s)
core = next(
    (node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "_gsf_render_core"),
    None,
)
if core is None:
    raise RuntimeError("V293 _gsf_render_core missing")


def is_render_run(assign):
    if not isinstance(assign, ast.Assign):
        return False
    if not any(isinstance(target, ast.Name) and target.id == "r" for target in assign.targets):
        return False
    call = assign.value
    if not isinstance(call, ast.Call):
        return False
    return any(isinstance(node, ast.Name) and node.id == "cmd" for node in ast.walk(call))


render_assigns = [node for node in ast.walk(core) if is_render_run(node)]
if len(render_assigns) != 1:
    candidates = []
    for node in ast.walk(core):
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "r" for target in node.targets
        ):
            candidates.append(ast.unparse(node)[:500])
    raise RuntimeError(
        f"V293 expected one final r=<call using cmd>, found {len(render_assigns)}; "
        f"r_candidates={candidates}"
    )
render_assign = render_assigns[0]

parents = {}
for parent in ast.walk(core):
    for child in ast.iter_child_nodes(parent):
        parents[child] = parent
parent = parents.get(render_assign)
if parent is None or not hasattr(parent, "body") or render_assign not in parent.body:
    raise RuntimeError("V293 render execution parent body missing")

with_node = ast.With(
    items=[
        ast.withitem(
            context_expr=ast.Call(
                func=ast.Name(id="_gsf_render_slot_v293", ctx=ast.Load()),
                args=[ast.Constant(value="final")],
                keywords=[],
            ),
            optional_vars=None,
        )
    ],
    body=[render_assign],
    type_comment=None,
)
ast.copy_location(with_node, render_assign)
idx = parent.body.index(render_assign)
parent.body[idx] = with_node
ast.fix_missing_locations(core)
new_core = ast.unparse(core)

lines = s.splitlines(keepends=True)
s = "".join(lines[: core.lineno - 1]) + new_core.rstrip() + "\n\n" + "".join(lines[core.end_lineno :])

header = '''# V293 RENDER MEMORY GUARD\nfrom web.render_gate_v293 import render_slot as _gsf_render_slot_v293\nGSF_FINAL_RENDER_SLOTS=max(1,min(2,int(__import__("os").environ.get("GSF_FINAL_RENDER_SLOTS","1") or 1)))\n'''
if "# V293 RENDER MEMORY GUARD" not in s:
    s = header + s

compile(s, str(APP_OUT), "exec")
APP_OUT.write_text(s, encoding="utf-8")
print(
    "V293 render memory guard applied:",
    APP_OUT,
    "materialize_default=1 materialize_cap=2 final_render_slots_default=1",
    flush=True,
)
