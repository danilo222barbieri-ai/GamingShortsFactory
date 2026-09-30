from pathlib import Path
import sys

path=Path(sys.argv[1] if len(sys.argv)>1 else "/app/GamingShortsFactory_V110_HUB_SOLID.py")
s=path.read_text(encoding="utf-8")

required=[
    "gsf-creator-hub-solid-v110",
    "background:#EAF2F7 !important",
    "background:#F7FBFF !important",
    "-webkit-backdrop-filter:none !important",
    "backdrop-filter:none !important",
    "transition:none !important",
    "contain:paint !important",
    "gsf-creator-hub-portal-v107",
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V110 Creator Hub solid test failed: "+repr(missing))

for bad in [
    "background:rgba(27,48,64,.72)!important;-webkit-backdrop-filter:blur(12px)!important",
    "background:rgba(24,43,59,.62) !important;\n  -webkit-backdrop-filter:blur(11px)",
]:
    if bad in s:
        raise SystemExit("V110 Creator Hub still contains active translucent blur rule: "+bad[:80])

compile(s,str(path),"exec")
print("V110 Creator Hub solid: PASS")
