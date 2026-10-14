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

# V404: production images must already contain the fully materialized UI.
# A preserved legacy startup remains available as a safe fallback.
if [ ! -f /app/.gsf-ui-materialized ]; then
  echo "V404 fast-start marker missing; falling back to legacy safe startup" >&2
  if [ -f /app/web/start_web_legacy.sh ]; then
    exec /bin/sh /app/web/start_web_legacy.sh
  fi
  echo "V404 fatal: neither materialized marker nor legacy startup is available" >&2
  exit 78
fi

# Fail closed if the build marker exists but a critical materialized artifact
# is missing. This catches a stale/corrupt image before it can report ready.
grep -q 'V373_CREATOR_HUB_HEADER_BREATH' /app/web/creator_hub_v156_component/index.html
grep -q 'GSF_GLOBAL_SHELL_V343' /app/GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py
python -m py_compile /app/GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py /app/web/direct_upload_server.py /app/web/contact_server.py

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

echo "V404 fast startup: services launched; waiting for real Streamlit readiness"
exec python -m streamlit run /app/GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py \
  --server.address=127.0.0.1 --server.port=8501 --server.maxUploadSize=4096 --server.maxMessageSize=4096 --server.headless=true
