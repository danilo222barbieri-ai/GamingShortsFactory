from __future__ import annotations

import ast
import sys
from pathlib import Path

IMPORT_LINE = "from gsf_alive import render_alive, sync_alive_from_session"
BOOT_MARKER = "# GSF Alive Core V405"
BOOT_BLOCK = f'''\n\n{BOOT_MARKER}\n_gsf_alive_state = sync_alive_from_session(st.session_state)\nrender_alive(\n    st,\n    _gsf_alive_state,\n    show_status=_gsf_alive_state.mode.value in {{"working", "celebrate", "error"}},\n)\n'''


def _top_level_import_end(tree: ast.Module) -> int:
    end = 0
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            end = max(end, node.end_lineno or node.lineno)
            continue
        break
    if not end:
        raise RuntimeError("No top-level import block found in app.py")
    return end


def _page_config_end(tree: ast.Module) -> int:
    for node in tree.body:
        if not isinstance(node, ast.Expr) or not isinstance(node.value, ast.Call):
            continue
        func = node.value.func
        if (
            isinstance(func, ast.Attribute)
            and isinstance(func.value, ast.Name)
            and func.value.id == "st"
            and func.attr == "set_page_config"
        ):
            return node.end_lineno or node.lineno
    raise RuntimeError("st.set_page_config(...) not found in app.py")


def patch_app_source(source: str) -> str:
    result = source

    if IMPORT_LINE not in result:
        tree = ast.parse(result)
        lines = result.splitlines(keepends=True)
        idx = _top_level_import_end(tree)
        lines.insert(idx, IMPORT_LINE + "\n")
        result = "".join(lines)

    if BOOT_MARKER not in result:
        tree = ast.parse(result)
        lines = result.splitlines(keepends=True)
        idx = _page_config_end(tree)
        lines.insert(idx, BOOT_BLOCK)
        result = "".join(lines)

    ast.parse(result)
    return result


def main() -> int:
    target = Path(sys.argv[1] if len(sys.argv) > 1 else "app.py")
    source = target.read_text(encoding="utf-8")
    patched = patch_app_source(source)
    if patched == source:
        print("GSF Alive V405 already integrated; no changes.")
        return 0
    target.write_text(patched, encoding="utf-8")
    print(f"GSF Alive V405 integrated into {target}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
