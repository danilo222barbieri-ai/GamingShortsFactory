#!/usr/bin/env python3
import ast
import importlib.util
import os
import py_compile
import sys
import threading
import time
from pathlib import Path


def need(ok, msg):
    if not ok:
        raise AssertionError(msg)
    print("PASS:", msg)


app = Path(sys.argv[1] if len(sys.argv) > 1 else "/app/GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py")
upload_server = Path(sys.argv[2] if len(sys.argv) > 2 else "/app/web/direct_upload_server.py")
gate = Path(sys.argv[3] if len(sys.argv) > 3 else "/app/web/render_gate_v293.py")
original_app = Path(sys.argv[4] if len(sys.argv) > 4 else "/app/GamingShortsFactory_V154_STRUCTURAL_HOME.py")
web_root = gate.parent

need(gate.is_file(), "V293 render gate module exists")
gate_src = gate.read_text(encoding="utf-8")
need("BoundedSemaphore" in gate_src, "render gate uses a process-wide bounded semaphore")
need("GSF_FINAL_RENDER_SLOTS" in gate_src, "render gate is explicitly configurable")
need("GSF_FINAL_RENDER_WAIT" in gate_src, "render gate logs queue wait")
need("GSF_FINAL_RENDER_ACQUIRED" in gate_src, "render gate logs acquisition")
need("GSF_FINAL_RENDER_RELEASED" in gate_src, "render gate logs release")

# Runtime behavior: two callers must never enter the guarded section together
# with the production-safe default of one slot.
os.environ["GSF_FINAL_RENDER_SLOTS"] = "1"
spec = importlib.util.spec_from_file_location("render_gate_v293_test", gate)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
state = {"active": 0, "max_active": 0}
lock = threading.Lock()


def guarded_probe():
    with mod.render_slot("test"):
        with lock:
            state["active"] += 1
            state["max_active"] = max(state["max_active"], state["active"])
        time.sleep(0.08)
        with lock:
            state["active"] -= 1


threads = [threading.Thread(target=guarded_probe) for _ in range(2)]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join(timeout=3)
need(all(not thread.is_alive() for thread in threads), "render gate releases all waiting callers")
need(state["max_active"] == 1, "render gate serializes concurrent final renders")

need(upload_server.is_file(), "direct upload server exists")
upload_src = upload_server.read_text(encoding="utf-8")
compact_upload = upload_src.replace(" ", "")
need('GSF_MATERIALIZE_CONCURRENCY","1"' in compact_upload, "materialization defaults to one transfer worker")
need("returnmax(1,min(2,value))" in compact_upload, "materialization concurrency is hard-capped at two")

need(app.is_file(), "V293 guarded production app exists")
need(original_app.is_file(), "V154 source app exists for semantic comparison")
app_src = app.read_text(encoding="utf-8")
original_src = original_app.read_text(encoding="utf-8")
tree = ast.parse(app_src)
original_tree = ast.parse(original_src)
core = next((n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_gsf_render_core"), None)
original_core = next((n for n in original_tree.body if isinstance(n, ast.FunctionDef) and n.name == "_gsf_render_core"), None)
need(core is not None, "final render core still exists")
need(original_core is not None, "original final render core exists")
segment = ast.get_source_segment(app_src, core) or ""
need("_gsf_render_slot_v293" in segment, "final render core acquires V293 render slot")


def is_gate_with(node):
    if not isinstance(node, ast.With) or len(node.items) != 1:
        return False
    expr = node.items[0].context_expr
    return (
        isinstance(expr, ast.Call)
        and isinstance(expr.func, ast.Name)
        and expr.func.id == "_gsf_render_slot_v293"
    )


gate_nodes = [node for node in ast.walk(core) if is_gate_with(node)]
need(len(gate_nodes) == 1, "exactly one base final render execution is guarded")
need(len(gate_nodes[0].body) == 1 and isinstance(gate_nodes[0].body[0], ast.Assign), "base gate wraps only the final render assignment")

# Strong regression check: remove only the V293 guard and verify the complete
# render function is AST-equivalent to V154. This proves preset/CRF/threading,
# crop/scale, audio, timeout and fallback behavior were not changed by V293.
class StripV293Guard(ast.NodeTransformer):
    def visit_With(self, node):
        node = self.generic_visit(node)
        if is_gate_with(node):
            if len(node.body) != 1:
                raise AssertionError("V293 guard unexpectedly wraps multiple statements")
            return node.body[0]
        return node


def normalized_function(node):
    return ast.parse(ast.unparse(node)).body[0]


guarded_norm = normalized_function(core)
guarded_without_gate = StripV293Guard().visit(guarded_norm)
ast.fix_missing_locations(guarded_without_gate)
original_norm = normalized_function(original_core)
need(
    ast.dump(guarded_without_gate, include_attributes=False)
    == ast.dump(original_norm, include_attributes=False),
    "V293 leaves base final render semantics unchanged except serialization gate",
)
need("GSF_FINAL_RENDER_SLOTS" in app_src, "production app exposes the render slot setting")

# V125/V126/V143/V149 can run FFmpeg after the base render. They must share
# the same process-wide gate or two sessions could overlap in a later stage.
post_render_targets = {
    "cinematic_render_v125.py": "_run",
    "creative_render_v126.py": "apply_sound_design",
    "director_render_exec_v143.py": "_run",
    "privacy_cleanup_v149.py": "_run",
}
for filename, function_name in post_render_targets.items():
    path = web_root / filename
    need(path.is_file(), f"{filename} exists")
    source = path.read_text(encoding="utf-8")
    module_tree = ast.parse(source)
    fn = next((n for n in module_tree.body if isinstance(n, ast.FunctionDef) and n.name == function_name), None)
    need(fn is not None, f"{filename} target function exists")
    fn_gates = [n for n in ast.walk(fn) if is_gate_with(n)]
    need(len(fn_gates) == 1, f"{filename} FFmpeg execution shares V293 render gate")
    need("_gsf_render_slot_v293" in source, f"{filename} imports V293 render gate")
    py_compile.compile(str(path), doraise=True)

py_compile.compile(str(gate), doraise=True)
py_compile.compile(str(upload_server), doraise=True)
py_compile.compile(str(app), doraise=True)
print("V293 render memory guard: PASS")
