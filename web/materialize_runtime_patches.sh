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

PATCH_SCRIPT=/tmp/gsf-runtime-patches-build.sh
MARKER=/app/.gsf-ui-materialized

mkdir -p "$GSF_RUNTIME_ROOT"
rm -f "$MARKER" "$PATCH_SCRIPT"

python - <<'PY'
from pathlib import Path

source_path = Path('/app/web/start_web.sh')
out_path = Path('/tmp/gsf-runtime-patches-build.sh')
ai_path = Path('/app/web/ai_v221_component/index.html')
compat_path = Path('/app/web/v404_legacy_runtime_compat.py')
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

# The new two-screen Crea con IA page intentionally replaced the V288/V308/
# V317/V319/V320 ai221 DOM. Keep the legacy migration chain for the other
# surfaces, but route the obsolete AI-specific steps through a compatibility
# layer so build-time materialization cannot rewrite ai404 back to ai221.
ai = ai_path.read_text(encoding='utf-8') if ai_path.is_file() else ''
if 'id="ai404"' in ai:
    if not compat_path.is_file():
        raise SystemExit('V404 materializer: compatibility helper missing')
    replacements = (
        ('  python /app/web/fix_v288_ai_journey.py\n', '  python /app/web/v404_legacy_runtime_compat.py v288\n'),
        ('  python /app/web/test_v288_ai_journey.py /app/web/ai_v221_component/index.html /app/web/home_v154_component/index.html /app/web/editor_2027_component/index.html /app/GamingShortsFactory_V154_STRUCTURAL_HOME.py\n', '  python /app/web/v404_legacy_runtime_compat.py test-v288\n'),
        ('  python /app/web/fix_v308_mobile_ai_flow.py /app/web/ai_v221_component/index.html\n', '  python /app/web/v404_legacy_runtime_compat.py v308\n'),
        ('  python /app/web/test_v308_mobile_ai_flow.py /app\n', '  python /app/web/v404_legacy_runtime_compat.py test-v308\n'),
        ('python /app/web/fix_v316_creator_hub_dashboard_ad.py /app/web/creator_hub_v156_component/index.html\n', 'python /app/web/v404_legacy_runtime_compat.py v316\n'),
        ('python /app/web/test_v316_creator_hub_dashboard_ad.py /app\n', 'python /app/web/v404_legacy_runtime_compat.py test-v316\n'),
    )
    for old, new in replacements:
        if old not in snippet:
            raise SystemExit('V404 materializer: expected legacy command missing: ' + old.strip())
        snippet = snippet.replace(old, new, 1)
    print('V404 materializer: ai404 compatibility routing enabled')

# -x is intentional: if a build-time migration fails, the Production Gate
# artifact records the exact command immediately before the failure.
out_path.write_text('#!/bin/sh\nset -eux\n' + snippet, encoding='utf-8')
print('V404 materializer: extracted runtime patch chain', len(snippet), 'bytes')
PY

chmod +x "$PATCH_SCRIPT"
"$PATCH_SCRIPT"

# Written only after every migration/test above completed successfully.
touch "$MARKER"
rm -f "$PATCH_SCRIPT"

# Deliberately preserve the readiness files created under GSF_RUNTIME_ROOT.
# They become part of the immutable Docker image layer, so start_web.sh sees
# the already-materialized state immediately after every fresh Railway boot.
test -d "$GSF_RUNTIME_ROOT"
find "$GSF_RUNTIME_ROOT" -maxdepth 1 -type f -name '.v*-runtime-ready' -print | sort || true

echo "V404 build-time UI materialization: PASS"
