#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "/app")
EDITOR = ROOT / "web" / "editor_2027_component" / "index.html"
EMBED = ROOT / "web" / "editor_2027_embed.py"

html = EDITOR.read_text(encoding="utf-8")
embed = EMBED.read_text(encoding="utf-8")

marker = "V305 EDITOR DESKTOP SINGLE SURFACE"
assert marker in html, "desktop single-surface override is missing"

# The normal embedded desktop editor must size itself to the component host,
# not to the browser viewport. Fullscreen mode remains explicitly excluded.
assert "@media (min-width:901px)" in html, "desktop-only breakpoint missing"
assert "#ng27:not(.gsfFullscreen):not(.gsfFullscreenFallback):not(:fullscreen)" in html, "normal embedded editor selector does not protect fullscreen"
assert "height:100%!important" in html, "embedded editor is not bound to its host height"
assert "min-height:0!important" in html, "legacy viewport minimum is still active"
assert "max-height:100%!important" in html, "embedded editor can still exceed its host"

# The parent Streamlit page already owns the page title and guide space.
# The component must not render a second page header/mural on desktop.
assert ".topline:before" in html and "content:none!important" in html, "duplicate internal GAME EDITOR title is still visible"
assert ".gsfGuide" in html and "display:none!important" in html, "legacy desktop mural can still bleed outside the component"

# Mobile and explicit fullscreen contracts are intentionally preserved.
assert "@media(max-width:900px){#ng27{height:auto;min-height:100dvh" in html, "legacy mobile layout was modified"
assert "#ng27.gsfFullscreen" in html and "#ng27:fullscreen" in html, "fullscreen contract was removed"

# Force browsers to receive the corrected component instead of a cached copy.
assert '"gsf_editor_2027_v305"' in embed, "V305 editor component cache key missing"

# V299's cleanup must remain true.
for forbidden in ("V297 DESK REBUILD — EDITOR", "v297EditorGrid", "V298 EDITOR GRAPHIC ONLY"):
    assert forbidden not in html, f"obsolete editor overlay returned: {forbidden}"

print("V305 editor desktop single-surface PASS")
