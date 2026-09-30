from pathlib import Path
import re
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
    "gsf-layout-hygiene",
    "SHORT PRONTO",
    "gsf-final-status",
    "CONDIVIDI O SCARICA",
    "v69_social_facebook",
    "Dettagli Facebook",
    "COLLEGA FACEBOOK",
    "CREATOR HUB",
    "Modifica scena, look, sottotitoli e audio prima di continuare.",
    "gsf-irreversible-share-ux",
    "Short in lavorazione",
    "push/notify",
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
if "gsf_personalize_display" in s:
    raise SystemExit("FAIL PERSONALIZZA display button still uses forbidden explicit widget key")
if 'st.markdown("\\\\n\\\\n")' in s or "st.markdown('\\\\n\\\\n')" in s:
    raise SystemExit("FAIL literal newline markdown survived")
if "v1054_ad_after_final_result" in s and not re.search(
    r"\.st-key-v1054_ad_after_final_result\s*\{[^}]*display\s*:\s*none",
    s,
    flags=re.S,
):
    raise SystemExit("FAIL final publication ad is still visible")
if "gsf-v107-final-publish-v3" in s or "new MutationObserver(tune)" in s:
    raise SystemExit("FAIL final publication still injects executable JS into markdown")
if "v69_social_facebook" not in s or "gsf_final_download_after_social" not in s:
    raise SystemExit("FAIL native Facebook/download final layout missing")
if s.count("CONDIVIDI O SCARICA") != 1:
    raise SystemExit("FAIL final action title must appear exactly once")
if "gsf_share_download_top" not in s:
    raise SystemExit("FAIL final top CTA lacks stable CREA CON IA styling key")
if "with _download_col:" in s:
    raise SystemExit("FAIL obsolete top SCARICA block survived")
for _icon_marker in ('content:"f"','content:"◎"','content:"▶"','content:"♪"'):
    if _icon_marker not in s:
        raise SystemExit("FAIL high-contrast social icon missing: "+_icon_marker)
if "gsf-share-cta-exact-create-short" not in s:
    raise SystemExit("FAIL CONDIVIDI O SCARICA does not inherit exact CREA SHORT CTA skin")
if "gsf-share-hub-glass" not in s or "gsfHubIn" not in s:
    raise SystemExit("FAIL futuristic glass Share Hub skin missing")
if "SHARE HUB" not in s or "gsf-hub-state" not in s:
    raise SystemExit("FAIL Share Hub notification state missing")
if "background:linear-gradient(135deg,#78D7F3 0%,#50B9E9 100%)" not in s:
    raise SystemExit("FAIL final SCARICA is not blue")
if "st-key-v1055_ad_manual_after_editor" not in s:
    raise SystemExit("FAIL editor-to-ad spacing reduction missing")
if "gsf-major-publish-download" in s:
    raise SystemExit("FAIL duplicate lower CONDIVIDI O SCARICA milestone survived")
for _ad_key in ("v1053_ad_before_final","v1054_ad_after_ai","v1055_ad_after_ai","v1054_ad_after_final_action","v1054_ad_after_final_result"):
    if _ad_key in s and not re.search(r"\.st-key-"+re.escape(_ad_key)+r"\s*[,\{][\s\S]{0,220}?display\s*:\s*none",s):
        raise SystemExit("FAIL final publication ad is still visible: "+_ad_key)

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

if 'st.session_state.pop("gsf_v107_final_render_pending",False)' not in s:
    raise SystemExit("FAIL final render job is not claimed exactly once")
if "gsf_v107_final_render_running" not in s:
    raise SystemExit("FAIL final render does not retain independent running state")
if "GSF_FINAL_STABLE_READY" not in s or "gaming_short_finale_share.mp4" not in s:
    raise SystemExit("FAIL completed FFmpeg render is not persisted before Streamlit return")

if "render_job.json" not in s or "GSF_FINAL_JOB_READY_WARN" not in s:
    raise SystemExit("FAIL durable final render state missing")
if "SALVA BOZZA" not in s or "/drafts/save" not in s:
    raise SystemExit("FAIL save draft UI missing")
