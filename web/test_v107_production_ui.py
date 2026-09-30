from pathlib import Path
import sys

path=Path(sys.argv[1] if len(sys.argv)>1 else "/app/GamingShortsFactory_V107_PRODUCTION_UI.py")
s=path.read_text(encoding="utf-8")

required=[
    "PERSONALIZZA IL TUO GAMEPLAY",
    "APRI GAME EDITOR",
    "CREA CON IA",
    "CREA SHORT FINALE",
    "Scegli il tuo momento",
    "Sottotitoli automatici",
    "editor_2027_embed",
    "v1055_ad_manual_before_editor",
    "v1055_ad_manual_after_editor",
    "gsf-major-personalize",
    "gsf-major-create-ai",
    "gsf-major-game-editor_",
    "gsf-major-create-short",
    "Scegli il tuo motore IA o crea il tuo gameplay",
    "gsf_editor_2027_inline_open",
    "Anteprima sorgente caricata nascosta per UX",
]
for marker in required:
    if marker not in s:
        raise SystemExit(f"FAIL missing V107 marker: {marker}")

for marker in (
    "GSF_FINAL_CREATE_CLICK",
    "gsf-final-ready",
    "gsf-final-social-row",
    "gsf-layout-hygiene",
    "Short finale pronto",
    "CREATOR HUB",
):
    if marker not in s:
        raise SystemExit(f"FAIL missing V107 final/layout marker: {marker}")

if "gsf_v107_final_click_pending" in s or "gsf_v107_final_recipe_snapshot" in s:
    raise SystemExit("FAIL obsolete V107 final-click trampoline survived")
if "GSF_ENGINE_SWITCH" in s or "_gsf_v107_last_modalita" in s:
    raise SystemExit("FAIL V107 must not rewrite the engine selector state")
if 'content:"→"' in s:
    raise SystemExit("FAIL duplicate personalize arrow survived")
if "GSF_MANUAL_EDITOR_OPEN" not in s:
    raise SystemExit("FAIL Scegli scena is not instrumented as immediate-open Editor 2027")
if 'st.markdown("\\\\n\\\\n")' in s or "st.markdown('\\\\n\\\\n')" in s:
    raise SystemExit("FAIL literal newline markdown survived")

for forbidden in [
    "_GSF_REAL_DEMO",
    "/app/demo_assets/",
    "DEMO FUNZIONALE",
    "demo_gameplay.mp4",
    "Nella demo restano visibili anche senza account collegati.",
    "Collega un account social per pubblicare davvero.",
]:
    if forbidden in s:
        raise SystemExit(f"FAIL demo-only runtime leaked into production: {forbidden}")

# Manual/Scegli scena: five approved visible positions are 1,2,3,4,6.
for slot in (1,2,3,4,6):
    marker=f"_gsf_v1057_ad_markup({slot})"
    if marker not in s:
        raise SystemExit(f"FAIL missing approved manual ad slot {slot}")

compile(s,str(path),"exec")
print("V107 production UI/demo parity smoke: PASS")
