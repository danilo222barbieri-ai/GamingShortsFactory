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

STARTUP=/app/web/start_web.sh
PATCH_SCRIPT=/tmp/gsf-runtime-patches-build.sh
MARKER=/app/.gsf-ui-materialized

mkdir -p "$GSF_RUNTIME_ROOT"
rm -f "$MARKER" "$PATCH_SCRIPT"

python - <<'PY'
from pathlib import Path

source_path = Path('/app/web/start_web.sh')
out_path = Path('/tmp/gsf-runtime-patches-build.sh')
source = source_path.read_text(encoding='utf-8')
start_token = '# V311_RESTART_SAFE'
end_token = "python - <<'PY'\nimport os,re\nfrom pathlib import Path\npath=Path(\"/tmp/gsf-ads.txt\")"

start = source.find(start_token)
end = source.find(end_token, start if start >= 0 else 0)
if start < 0 or end < 0 or end <= start:
    raise SystemExit('V404 materializer: startup migration boundaries not found')

snippet = source[start:end].rstrip() + '\n'
required = (
    'fix_v312_global_navigation.py',
    'fix_v343_single_global_shell.py',
    'fix_v360_mobile_editor_reference.py',
    'fix_v373_creator_hub_spacing.py',
)
missing = [token for token in required if token not in snippet]
if missing:
    raise SystemExit('V404 materializer: incomplete migration block: ' + ', '.join(missing))

out_path.write_text('#!/bin/sh\nset -eu\n' + snippet, encoding='utf-8')
print('V404 materializer: extracted runtime patch chain', len(snippet), 'bytes')
PY

chmod +x "$PATCH_SCRIPT"
"$PATCH_SCRIPT"

# The marker is written only after every migration/test above completed.
touch "$MARKER"

# Runtime state must start empty in the deployed container. Only the patched
# application files are baked into the image layer.
rm -rf "$GSF_RUNTIME_ROOT" "$PATCH_SCRIPT"
mkdir -p "$GSF_RUNTIME_ROOT"

echo "V404 build-time UI materialization: PASS"
