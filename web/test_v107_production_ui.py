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
if "SHORT PRONTO" in s:
    raise SystemExit("FAIL obsolete final short-ready badge survived")
if "background:linear-gradient(135deg,#78D7F3 0%,#50B9E9 100%)" not in s:
    raise SystemExit("FAIL final SCARICA is not blue")
if "st-key-v1055_ad_manual_after_editor" not in s:
    raise SystemExit("FAIL editor-to-ad spacing reduction missing")
if "gsf-major-publish-download" in s:
    raise SystemExit("FAIL duplicate lower CONDIVIDI O SCARICA milestone survived")
if "gsf-sep30-polish" not in s:
    raise SystemExit("FAIL Sep30 final polish CSS missing")
if "gsf-editor-note" not in s:
    raise SystemExit("FAIL editor note spacing marker missing")
if "gsf_save_draft_compact_v107" not in s and "SALVA BOZZA" in s:
    raise SystemExit("FAIL ordinary draft action was not compacted")
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
if "SALVA BOZZA DELLO SHORT INTERROTTO" not in s or "/drafts/save" not in s:
    raise SystemExit("FAIL engine-change draft UI missing")

if '"gsf_save_draft_v107",' not in s or '"gsf_save_draft_before_engine_change_v107",' not in s:
    raise SystemExit("FAIL transient draft button keys are not excluded from persistent state")
if "GSF_DRAFT_RESUME_WARN" not in s or "Bozza ripristinata." not in s:
    raise SystemExit("FAIL draft resume hydration missing")
if "Hai cambiato motore: il lavoro precedente è ancora disponibile." not in s:
    raise SystemExit("FAIL engine-change draft warning missing")
if "gsf_v107_engine_change_draft_pending" not in s:
    raise SystemExit("FAIL engine-change draft does not survive Streamlit rerun")
if "gsf_v107_engine_snapshot_recipe" not in s or "gsf_v107_engine_snapshot_source" not in s:
    raise SystemExit("FAIL previous-engine snapshot missing")
if 'with st.container(key="gsf-save-draft")' in s:
    raise SystemExit("FAIL draft save is still always visible")
if '_job["status"]="stale"' not in s or '"status":"failed"' not in s:
    raise SystemExit("FAIL stale/failed render release missing")

if 'id="gsf-creator-hub-panel"' not in s or 'src="/account?embedded=1"' not in s:
    raise SystemExit("FAIL Creator Hub in-page overlay missing")
if 'target="gsf_creator_hub"' in s:
    raise SystemExit("FAIL Creator Hub still opens/reuses another browser page")
if "GSF_FINAL_RENDER_REUSED" not in s or "final_render.lock" not in s: raise SystemExit("FAIL final render rerun lock missing")
if "preview_cache_v107" not in s: raise SystemExit("FAIL preview cache missing")
if "Game Editor da ricaricare. Riprova Scegli scena." in s or "Game Editor in caricamento…" in s:
    raise SystemExit("FAIL editor reload/loading loop remains")
if "GSF_MANUAL_EDITOR_SOURCE_RESTORED" not in s or "/source/restore?" not in s:
    raise SystemExit("FAIL missing-source Editor recovery missing")
if "Attendi la fine dello Short in creazione" not in s: raise SystemExit("FAIL upload allowed during final render")

if "Short completato." not in s:
    raise SystemExit("FAIL final-ready message is not completion-only")
if "Short pronto · apro lo Share Hub." in s:
    raise SystemExit("FAIL obsolete automatic Share Hub wording remains")
if ".gsf-editor-note{\n  margin-bottom:48px !important;" not in s:
    raise SystemExit("FAIL requested Editor cloud/player spacing missing")

if "gsf-social-brand-tiles-v107" not in s:
    raise SystemExit("FAIL original-brand social tile override missing")
for _brand_marker in (
    "background:#1877F2 !important",
    "background:#FF0000 !important",
    "radial-gradient(circle at 30% 105%",
    "fill='%2325F4EE'",
):
    if _brand_marker not in s:
        raise SystemExit("FAIL social brand artwork missing: "+_brand_marker)
if "GSF_SOCIAL_META_READY" not in s:
    raise SystemExit("FAIL social metadata normalization missing")
for _meta_marker in (
    '"selected_title":_gsf_meta_title',
    '"selected_description":_gsf_meta_youtube_description',
    '"selected_hashtags":_gsf_meta_hash_text',
    '"selected_caption":_gsf_meta_caption',
):
    if _meta_marker not in s:
        raise SystemExit("FAIL social metadata mapping missing: "+_meta_marker)
