#!/bin/sh
set -eu
export PORT="${PORT:-8080}"
export GSF_WEB_MODE="${GSF_WEB_MODE:-1}"
export GSF_LOW_MEMORY_WEB="${GSF_LOW_MEMORY_WEB:-1}"
export GSF_AI_VOICE_TRANSCRIPTION="${GSF_AI_VOICE_TRANSCRIPTION:-0}"
export GSF_MEDIA_BIND="${GSF_MEDIA_BIND:-0.0.0.0}"
export GSF_MEDIA_PORT="${GSF_MEDIA_PORT:-8765}"
export GSF_MEDIA_BASE_URL="${GSF_MEDIA_BASE_URL:-/media}"
export GSF_RUNTIME_ROOT="${GSF_RUNTIME_ROOT:-/tmp/gsf-runtime}"
export GSF_DIRECT_UPLOAD_PORT="${GSF_DIRECT_UPLOAD_PORT:-8502}"
export GSF_CONTACT_PORT="${GSF_CONTACT_PORT:-8503}"
export GSF_SESSION_TTL_SECONDS="${GSF_SESSION_TTL_SECONDS:-21600}"
export HF_HOME="${HF_HOME:-/app/.cache/huggingface}"
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-1}"
export OPENBLAS_NUM_THREADS="${OPENBLAS_NUM_THREADS:-1}"
export MKL_NUM_THREADS="${MKL_NUM_THREADS:-1}"
mkdir -p "$GSF_RUNTIME_ROOT"

# V311_RESTART_SAFE
GSF_V311_READY="$GSF_RUNTIME_ROOT/.v311-runtime-ready"
GSF_HUB_HTML="/app/web/creator_hub_v156_component/index.html"
GSF_SHELL_APP="/app/GamingShortsFactory_V154_STRUCTURAL_HOME.py"
GSF_HISTORY_READY=0
if [ -f "$GSF_V311_READY" ]; then
  GSF_HISTORY_READY=1
elif grep -q 'V311 APPROVED CREATOR REFERENCE' "$GSF_HUB_HTML" 2>/dev/null; then
  GSF_HISTORY_READY=1
fi

if [ "$GSF_HISTORY_READY" -eq 0 ]; then
  python /app/web/fix_v285_creator_hub_clicks.py
  python /app/web/test_v285_creator_hub_clicks.py /app/web/creator_hub_v156_component/index.html
  python /app/web/fix_v286_global_gamebar.py
  python /app/web/test_v286_global_gamebar.py /app/web/creator_hub_v156_component/index.html /app/GamingShortsFactory_V154_STRUCTURAL_HOME.py
  python /app/web/fix_v287_profile_overview.py
  python /app/web/test_v287_profile_overview.py /app/web/creator_hub_v156_component/index.html /app/GamingShortsFactory_V154_STRUCTURAL_HOME.py
  python /app/web/fix_v288_ai_journey.py
  python /app/web/test_v288_ai_journey.py /app/web/ai_v221_component/index.html /app/web/home_v154_component/index.html /app/web/editor_2027_component/index.html /app/GamingShortsFactory_V154_STRUCTURAL_HOME.py
  python /app/web/fix_v289_share_final.py
  python /app/web/test_v289_share_final.py /app/web/share_v156_component/index.html /app/GamingShortsFactory_V154_STRUCTURAL_HOME.py
  python /app/web/fix_v291_ai_engine_bridge.py
  python /app/web/test_v291_ai_engine_bridge.py /app/web/home_v154_component/index.html /app/GamingShortsFactory_V154_STRUCTURAL_HOME.py
  python /app/web/fix_v293_share_state_resilience.py /app/web/direct_upload_server.py
  python /app/web/test_v293_share_state_resilience.py /app/web/direct_upload_server.py
  python /app/web/fix_v295_internal_pages_responsive.py
  python /app/web/fix_v300_creator_hub_clean.py
  python /app/web/test_v300_creator_hub_clean.py /app
  python /app/web/fix_v302_global_live_gamebar.py
  python /app/web/test_v302_global_live_gamebar.py /app
  python /app/web/fix_v306_home_visual_lock.py
  python /app/web/fix_v303_mobile_hub_compact.py
  python /app/web/test_v303_mobile_hub_compact.py
  python /app/web/fix_v304_project_draft_api.py
  python /app/web/fix_v304_project_draft_details.py
  python /app/web/test_v304_project_draft_details.py /app
  python /app/web/fix_v307_mobile_visual_source.py /app
  python /app/web/test_v307_mobile_visual_source.py /app
  python /app/web/fix_v308_mobile_ai_flow.py /app/web/ai_v221_component/index.html
  python /app/web/test_v308_mobile_ai_flow.py /app
  python /app/web/fix_v310_creator_hub_mobile_cleanup.py /app/web/creator_hub_v156_component/index.html
  python /app/web/test_v310_creator_hub_mobile_cleanup.py /app
else
  echo "V311 restart-safe: historical runtime migrations already applied"
fi

if grep -q 'GSF_GLOBAL_SHELL_V343' "$GSF_SHELL_APP" 2>/dev/null; then
  echo "V311 restart-safe: V343 shell already finalized"
else
  python /app/web/fix_v311_mobile_hub_clean_pass.py /app/web/creator_hub_v156_component/index.html
  python /app/web/test_v311_mobile_hub_clean_pass.py /app
fi
touch "$GSF_V311_READY"

python /app/web/fix_v312_global_navigation.py /app
python /app/web/test_v312_navigation_contract.py /app
python /app/web/fix_v313_mobile_profile_fit.py /app/web/creator_hub_v156_component/index.html
python /app/web/test_v313_mobile_profile_fit.py /app
python /app/web/fix_v314_hub_context_fill.py /app/web/creator_hub_v156_component/index.html
python /app/web/test_v314_hub_context_fill.py /app
python /app/web/fix_v316_creator_hub_dashboard_ad.py /app/web/creator_hub_v156_component/index.html
python /app/web/test_v316_creator_hub_dashboard_ad.py /app
python /app/web/test_v319_ai_results_bridge.py /app
python /app/web/test_v320_ai_mobile_stability.py /app
python /app/web/test_v322_mobile_hub_live_fill.py /app
python /app/web/fix_v323_mobile_editor_player_actions.py /app
python /app/web/test_v323_mobile_editor_player_actions.py /app
python /app/web/fix_v324_editor_action_placement.py /app/web/editor_2027_component/index.html
python /app/web/test_v324_editor_action_placement.py /app
python /app/web/fix_v325_mobile_editor_viewport_fit.py /app/web/editor_2027_component/index.html
python /app/web/test_v325_mobile_editor_viewport_fit.py /app
python /app/web/fix_v326_mobile_editor_home_speed.py /app
python /app/web/test_v326_mobile_editor_home_speed.py /app

# V337: V327 delegates to V328 during restart. Make V328 accept the newer
# canonical Short route from V331 before V327 can invoke it.
python /app/web/fix_v337_restart_safe_v328.py /app
python /app/web/test_v337_restart_safe_v328.py /app

python /app/web/fix_v327_editor_open_bridge.py /app
python /app/web/test_v327_editor_open_bridge.py /app
# V328 remains only as a Home/Live layout migration. V343 removes its old
# parent chrome block before Streamlit starts.
python /app/web/fix_v328_global_balance.py /app
python /app/web/fix_v329_worker_cost_guard.py /app
python /app/web/test_v329_worker_cost_guard.py /app
python /app/web/fix_v331_primary_actions_routing.py /app
python /app/web/test_v331_primary_actions_routing.py /app

# V333: murals never eat taps; Editor and Crea Short keep direct touch handlers.
python /app/web/fix_v333_home_cta_touch_fix.py /app
python /app/web/test_v333_home_cta_touch_fix.py /app

# V343: the only parent-owned global header, Game Bar and footer.
python /app/web/fix_v343_single_global_shell.py /app
python /app/web/test_v343_single_global_shell.py /app
python /app/web/test_v328_global_balance.py /app

# V336: convert only remaining legacy executable bridges; V343 is executable itself.
python /app/web/fix_v336_executable_shell_bridge.py /app

# V335: remove unsupported layout kwargs only from remaining st.html calls.
python /app/web/fix_v335_runtime_shell_recovery.py /app
python /app/web/test_v336_executable_shell_bridge.py /app
python /app/web/test_v335_runtime_shell_recovery.py /app
python /app/web/test_v343_single_global_shell.py /app

# V343/V293 compatibility: keep V293 render-memory protection but do not let
# its legacy shell normalizers rewrite the V343 executable component string.
python /app/web/apply_v343_v293_compat.py
python /app/web/test_v343_single_global_shell.py /app
python -m py_compile /app/GamingShortsFactory_V154_STRUCTURAL_HOME.py
python -m py_compile /app/GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py
grep -q 'GSF_GLOBAL_SHELL_V343' /app/GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py
python /app/web/test_v343_v293_compat.py /app

# V348: user-approved immediate cosmetic hotfix. Transparent brand mark + visible footer.
python /app/web/fix_v348_logo_footer.py /app

python - <<'PY'
import os,re
from pathlib import Path
path=Path("/tmp/gsf-ads.txt")
path.unlink(missing_ok=True)
client=str(os.environ.get("GSF_ADSENSE_CLIENT","") or "").strip()
m=re.fullmatch(r"ca-(pub-\d{10,20})",client)
if m:
    path.write_text(f"google.com, {m.group(1)}, DIRECT, f08c47fec0942fa0\n",encoding="utf-8")
PY

rm -f /etc/nginx/sites-enabled/default /etc/nginx/conf.d/default.conf
envsubst '${PORT}' < /app/web/nginx.conf.template > /etc/nginx/conf.d/default.conf
python /app/web/direct_upload_server.py &
python /app/web/contact_server.py &
nginx
python /app/web/runtime_smoke_v107.py &
exec python -m streamlit run /app/GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py \
  --server.address=127.0.0.1 --server.port=8501 --server.maxUploadSize=4096 --server.maxMessageSize=4096 --server.headless=true
