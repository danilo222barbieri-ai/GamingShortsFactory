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

# V285: repair Creator Hub collection selectors before Nginx/Streamlit serve the page.
python /app/web/fix_v285_creator_hub_clicks.py
python /app/web/test_v285_creator_hub_clicks.py /app/web/creator_hub_v156_component/index.html

# V286: keep the Game Bar global and guarantee Creator Hub receives Hub/Shorts/Drafts routes.
python /app/web/fix_v286_global_gamebar.py
python /app/web/test_v286_global_gamebar.py /app/web/creator_hub_v156_component/index.html /app/GamingShortsFactory_V154_STRUCTURAL_HOME.py

# V105.7: publish ads.txt only when a real Google publisher id is configured.
python - <<'PY'
import os,re
from pathlib import Path
path=Path("/tmp/gsf-ads.txt")
path.unlink(missing_ok=True)
client=str(os.environ.get("GSF_ADSENSE_CLIENT","") or "").strip()
m=re.fullmatch(r"ca-(pub-\d{10,20})",client)
if m:
    path.write_text(
        f"google.com, {m.group(1)}, DIRECT, f08c47fec0942fa0\\n",
        encoding="utf-8",
    )
PY

rm -f /etc/nginx/sites-enabled/default /etc/nginx/conf.d/default.conf
envsubst '${PORT}' < /app/web/nginx.conf.template > /etc/nginx/conf.d/default.conf
python /app/web/direct_upload_server.py &
python /app/web/contact_server.py &
nginx
python /app/web/runtime_smoke_v107.py &
exec python -m streamlit run /app/GamingShortsFactory_V154_STRUCTURAL_HOME.py \
  --server.address=127.0.0.1 --server.port=8501 --server.maxUploadSize=4096 --server.maxMessageSize=4096 --server.headless=true
