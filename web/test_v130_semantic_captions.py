from pathlib import Path
import sys

app_path=Path(sys.argv[1] if len(sys.argv)>1 else "/app/GamingShortsFactory_V130_SEMANTIC_CAPTIONS.py")
app=app_path.read_text(encoding="utf-8")
editor=Path("/app/web/editor_2027_component/index.html").read_text(encoding="utf-8")

for marker in (
    "const textPlan=(plan.text&&typeof plan.text==='object')?plan.text:{}",
    "const captionStyle=String(textPlan.caption_style||'clean').toLowerCase()",
    "if(captionStyle==='impact')",
    "state.captionMode='Auto'",
    "state.captionOn=true",
    "state.captionY=Math.max(15,Math.min(88",
    "state.activeColor='#ffd400'",
):
    if marker not in editor:
        raise SystemExit("V130 semantic caption marker missing: "+marker)

for marker in (
    "APPLICA AI DIRECTOR",
    "directorPlanFromBrain",
    "semanticFocusFromBrain",
):
    if marker not in editor:
        raise SystemExit("V130 Director integration regressed: "+marker)

compile(app,str(app_path),"exec")
print("V130 semantic captions contracts: PASS")
