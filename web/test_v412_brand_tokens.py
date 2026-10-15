"""V412 contract: after fix_v412_brand_tokens.py every UI surface uses the kit.

Usage: python test_v412_brand_tokens.py [app_root]   (default /app)
"""
from __future__ import annotations

import py_compile
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fix_v412_brand_tokens as v412  # noqa: E402

root = Path(sys.argv[1] if len(sys.argv) > 1 else "/app")
html, py = v412.targets(root)
assert html, "no UI documents found"
mains = sorted(root.glob("GamingShortsFactory_V*.py"))
assert mains, "no Streamlit main page found"

ALLOWED = v412.TOKEN_HEX | v412.PROTECTED
failures: list[str] = []

for path in html + py:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".html":
        if v412.MARKER not in text:
            failures.append(f"{path}: token sheet missing")
    chunks = [m.group(2) for m in v412.STYLE_BLOCK_RE.finditer(text)]
    chunks += [m.group(2)[1:-1] for m in v412.STYLE_ATTR_RE.finditer(text)]
    for css in chunks:
        css = v412.RULE_RE.sub(lambda r: "" if v412.PREVIEW_SELECTOR_RE.search(r.group(1)) else r.group(0), css)
        for m in v412.HEX_RE.finditer(css):
            val = m.group(0).upper()
            full = val if len(val) == 7 else "#" + "".join(c * 2 for c in val[1:])
            if full in ALLOWED or v412.map_hex(full) is None:
                continue
            failures.append(f"{path.name}: off-token color {val}")
        for m in v412.FONT_RE.finditer(css):
            value = m.group(2).strip()
            if value != v412.FONT_STACK and v412._font_value(value) != value:
                failures.append(f"{path.name}: off-brand font {value[:60]}")
        for m in v412.SPACE_RE.finditer(css):
            for n in v412.PX_RE.finditer(m.group(2)):
                num = float(n.group(2))
                if 2 < num <= 48 and num not in v412.SPACE_SCALE:
                    failures.append(f"{path.name}: off-scale spacing {n.group(0)}")
        for m in v412.RADIUS_RE.finditer(css):
            for n in v412.PX_RE.finditer(m.group(2)):
                num = float(n.group(2))
                if 8 < num < 999 and num not in v412.RADIUS_SCALE:
                    failures.append(f"{path.name}: off-scale radius {n.group(0)}")

for main in mains:
    text = main.read_text(encoding="utf-8")
    if v412.MARKER not in text:
        failures.append(f"{main.name}: Streamlit token sheet missing")
    py_compile.compile(str(main), doraise=True)
for p in py:
    py_compile.compile(str(p), doraise=True)

# Idempotent: a second pass changes nothing.
for path in html:
    text = path.read_text(encoding="utf-8")
    if v412.rewrite_document(text, {}, inject=True) != text:
        failures.append(f"{path.name}: second pass is not a no-op")

# Classifier sanity on known roles.
assert v412.map_hex("#0D2A66") == v412.TOKENS["ink"]
assert v412.map_hex("#F7FCFF") == v412.TOKENS["surface"]
assert v412.map_hex("#7185A6") == v412.TOKENS["muted"]
assert v412.map_hex("#1877F2") is None  # Facebook stays
assert v412.map_hex("#000000") is None  # video backdrops stay
assert v412.map_hex("#CFF4DD").startswith("rgba(94,214,160")  # green tint keeps its hue

if failures:
    print("\n".join(sorted(set(failures))[:80]))
    print(f"V412 brand tokens: FAIL ({len(set(failures))} issues)")
    sys.exit(1)
print(f"V412 brand tokens: PASS ({len(html)} documents, {len(py)} python sources)")
