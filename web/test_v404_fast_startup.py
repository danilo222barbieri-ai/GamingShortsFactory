#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
web = root / "web"
fast = (web / "start_web_fast.sh").read_text(encoding="utf-8")
materializer = (web / "materialize_runtime_patches.sh").read_text(encoding="utf-8")
legacy = (web / "start_web.sh").read_text(encoding="utf-8")

# Fast startup may validate the materialized image, but must never replay the
# historical mutation/test chain on the production critical path.
assert "fix_v312_global_navigation.py" not in fast
assert "fix_v343_single_global_shell.py" not in fast
assert "test_v373_creator_hub_spacing.py" not in fast
assert "exec /app/web/start_web.sh" in fast  # compatibility fallback only
assert "/app/.gsf-ui-materialized" in fast
assert "direct_upload_server.py &" in fast
assert "contact_server.py &" in fast
assert "exec python -m streamlit run" in fast

# Build-time materialization must derive the exact existing legacy chain,
# rather than maintaining a divergent duplicate list of UI migrations.
assert "# V311_RESTART_SAFE" in legacy
assert "fix_v373_creator_hub_spacing.py" in legacy
assert "source.find(start_token)" in materializer
assert "source.find(end_token" in materializer
assert "touch \"$MARKER\"" in materializer
assert "rm -rf \"$GSF_RUNTIME_ROOT\"" in materializer

# When executed inside the production image after the materializer RUN step,
# the immutable completion marker must exist.
if root == Path("/app"):
    assert (root / ".gsf-ui-materialized").is_file(), "build-time materialization marker missing"
    hub = (web / "creator_hub_v156_component" / "index.html").read_text(encoding="utf-8")
    shell = (root / "GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py").read_text(encoding="utf-8")
    assert "V373_CREATOR_HUB_HEADER_BREATH" in hub
    assert "GSF_GLOBAL_SHELL_V343" in shell

print("V404 fast production startup contract: PASS")
