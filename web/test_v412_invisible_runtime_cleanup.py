#!/usr/bin/env python3
from pathlib import Path
import ast
import importlib.util
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
module_path = root / "web" / "fix_v411_queue_runtime.py"
spec = importlib.util.spec_from_file_location("fix_v411_queue_runtime", module_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

patch = getattr(module, "patch_streamlit_shell_bridge")

legacy = '''import streamlit as st\nimport streamlit.components.v1 as _gsf_components_v343\n\n_V343_GLOBAL_SHELL_JS = "<script>window.parent.__GSF_GLOBAL_SHELL_V343=1</script>"\n_gsf_components_v343.html(_V343_GLOBAL_SHELL_JS, height=0, scrolling=False)\n'''
modern = patch(legacy)

assert "import streamlit.components.v1 as _gsf_components_v343" not in modern
assert "_gsf_components_v343.html(" not in modern
assert "st.iframe(_V343_GLOBAL_SHELL_JS, height=0, scrolling=False)" in modern
assert modern.count("_V343_GLOBAL_SHELL_JS") == legacy.count("_V343_GLOBAL_SHELL_JS")
assert "<script>window.parent.__GSF_GLOBAL_SHELL_V343=1</script>" in modern
assert patch(modern) == modern, "cleanup must be idempotent"
ast.parse(modern)

# Refuse partial or ambiguous rewrites: this bridge is global navigation chrome,
# so silently changing anything else would risk visible behaviour.
try:
    patch(legacy.replace("height=0", "height=1"))
except RuntimeError:
    pass
else:
    raise AssertionError("V412 must reject an unexpected global-shell renderer")

print("V412 invisible runtime cleanup contract: PASS", flush=True)
