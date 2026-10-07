#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
EDITOR = ROOT / "editor_2027_component" / "index.html"
EMBED = ROOT / "editor_2027_embed.py"
MARKER = "V305 EDITOR DESKTOP SINGLE SURFACE"

css = r'''
<style id="v305-editor-desktop-single-surface">
/* V305 EDITOR DESKTOP SINGLE SURFACE
   The Streamlit route already owns the page frame. On desktop the Editor
   custom component is an embedded workspace, not a second 100dvh page. */
@media (min-width:901px){
  html,
  body{
    width:100%!important;
    height:100%!important;
    min-height:0!important;
    margin:0!important;
    padding:0!important;
    overflow:hidden!important;
    background:transparent!important;
  }

  #ng27:not(.gsfFullscreen):not(.gsfFullscreenFallback):not(:fullscreen){
    width:100%!important;
    max-width:100%!important;
    height:100%!important;
    min-height:0!important;
    max-height:100%!important;
    margin:0!important;
    padding:0!important;
    border:0!important;
    border-radius:0!important;
    box-shadow:none!important;
    overflow:hidden!important;
    background:transparent!important;
  }

  #ng27:not(.gsfFullscreen):not(.gsfFullscreenFallback):not(:fullscreen) .shell{
    width:100%!important;
    max-width:1440px!important;
    height:100%!important;
    min-height:0!important;
    margin:0 auto!important;
    padding:6px 14px 8px!important;
    border:0!important;
    border-radius:0!important;
    box-shadow:none!important;
    overflow:hidden!important;
    background:transparent!important;
  }

  /* The parent page already says Game Editor. Do not draw a second page title. */
  #ng27:not(.gsfFullscreen):not(.gsfFullscreenFallback):not(:fullscreen) .topline:before{
    content:none!important;
    display:none!important;
  }

  /* Legacy V156 page mural lived outside the editor rail and bleeds into the
     parent shell when the component is embedded. Keep it off on desktop only. */
  #ng27:not(.gsfFullscreen):not(.gsfFullscreenFallback):not(:fullscreen) .gsfGuide{
    display:none!important;
  }
}
</style>
'''.strip()

html = EDITOR.read_text(encoding="utf-8")
if MARKER not in html:
    if "</body>" not in html:
        raise SystemExit("V305: editor component has no </body> anchor")
    html = html.replace("</body>", css + "\n</body>", 1)
    EDITOR.write_text(html, encoding="utf-8")

embed = EMBED.read_text(encoding="utf-8")
new_embed, count = re.subn(
    r'components\.declare_component\(\s*"gsf_editor_2027_v[^"]+"',
    'components.declare_component(\n    "gsf_editor_2027_v305"',
    embed,
    count=1,
)
if count != 1:
    # V299 may already have rewritten the name but the declaration must remain
    # structurally recognizable. Fail closed rather than serving a stale UI.
    if '"gsf_editor_2027_v305"' not in embed:
        raise SystemExit("V305: editor component declaration anchor not found")
else:
    EMBED.write_text(new_embed, encoding="utf-8")

print("V305 desktop Editor single-surface patch applied")
