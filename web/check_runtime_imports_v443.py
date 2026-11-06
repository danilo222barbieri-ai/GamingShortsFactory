#!/usr/bin/env python3
"""Fail the build when a lazy ``from web.x import y`` cannot resolve at runtime.

Run it as a script from the web directory, exactly like start_web.sh launches the
companion servers: sys.path[0] is then /app/web, where ``web`` means the inner
compatibility package. Lazy imports only fail at request time, so byte-compiling
or a health check can never catch them.
"""
import ast
import importlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENTRYPOINTS = ("direct_upload_server.py", "direct_upload_server_lowmem.py", "contact_server.py")


def lazy_web_modules():
    found = set()
    for name in ENTRYPOINTS:
        for node in ast.walk(ast.parse((HERE / name).read_text(encoding="utf-8"))):
            if isinstance(node, ast.ImportFrom) and node.level == 0 and (node.module or "").startswith("web."):
                found.add((node.module, tuple(alias.name for alias in node.names)))
    return sorted(found)


def main():
    assert Path(sys.path[0]).resolve() == HERE, "must run as a script from the web directory"
    modules = lazy_web_modules()
    assert modules, "no lazy web imports found: the scanner is broken"
    for module, names in modules:
        loaded = importlib.import_module(module)
        for name in names:
            getattr(loaded, name)
    print(f"GSF runtime imports: PASS ({len(modules)} from web.* statements)")


if __name__ == "__main__":
    main()
