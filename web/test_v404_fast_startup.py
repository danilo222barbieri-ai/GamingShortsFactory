#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
web = root / "web"
fast = (web / "start_web_fast.sh").read_text(encoding="utf-8")
materializer = (web / "materialize_runtime_patches.sh").read_text(encoding="utf-8")
compat = (web / "v404_legacy_runtime_compat.py").read_text(encoding="utf-8")
legacy = (web / "start_web.sh").read_text(encoding="utf-8")
build_hook = (web / "test_v269_creator_hub_recovery.py").read_text(encoding="utf-8")

# Fast startup may validate the materialized image, but must never replay the
# historical mutation/test chain on the production critical path.
assert "fix_v312_global_navigation.py" not in fast
assert "fix_v343_single_global_shell.py" not in fast
assert "test_v373_creator_hub_spacing.py" not in fast
assert "start_web_legacy.sh" in fast
assert "exec /bin/sh /app/web/start_web_legacy.sh" in fast
assert "/app/.gsf-ui-materialized" in fast
assert "direct_upload_server.py &" in fast
assert "contact_server.py &" in fast
assert "exec python -m streamlit run" in fast

# Build-time materialization derives the existing legacy chain rather than
# maintaining a second copy, but current rewritten surfaces may route obsolete
# historical steps through an explicit compatibility layer.
assert "# V311_RESTART_SAFE" in legacy
assert "fix_v373_creator_hub_spacing.py" in legacy
assert "source.find(start_token)" in materializer
assert "source.find(end_token" in materializer
assert 'id=\"ai404\"' in materializer
assert "v404_legacy_runtime_compat.py" in materializer
assert "touch \"$MARKER\"" in materializer
assert "preserve the readiness files" in materializer

# The compatibility layer must preserve the V404 AI component while retaining
# the still-valid Home/Editor/Hub/server migrations and the dedicated V404 UI
# regression contract.
assert "def migrate_v288" in compat
assert "mod.patch_home()" in compat and "mod.patch_editor()" in compat and "mod.patch_app()" in compat
assert "def migrate_v308" in compat
assert "obsolete ai221 mutation skipped" in compat
assert "def migrate_v316" in compat
assert "mod._apply_v318(HUB)" in compat
assert "mod._apply_v321(HUB)" in compat
assert "mod._apply_v322(HUB)" in compat
assert "test_v404_crea_con_ia_simple.py" in compat
assert "mod.patch_ai()" not in compat
assert "mod._apply_v317(HUB)" not in compat
assert "mod._apply_v320(HUB)" not in compat

# The already-existing Docker build test is the hook that preserves legacy,
# materializes the UI, and swaps only the image copy to the fast startup.
assert "start_web_legacy.sh" in build_hook
assert "materialize_runtime_patches.sh" in build_hook
assert "shutil.copyfile(fast_start, legacy_start)" in build_hook

# When executed inside the production image after the V269 build hook, the
# immutable completion marker and final UI artifacts must exist.
if root == Path("/app"):
    assert (root / ".gsf-ui-materialized").is_file(), "build-time materialization marker missing"
    hub = (web / "creator_hub_v156_component" / "index.html").read_text(encoding="utf-8")
    ai = (web / "ai_v221_component" / "index.html").read_text(encoding="utf-8")
    shell = (root / "GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py").read_text(encoding="utf-8")
    baked_start = (web / "start_web.sh").read_text(encoding="utf-8")
    assert "V373_CREATOR_HUB_HEADER_BREATH" in hub
    assert 'id="ai404"' in ai, "V404 AI component was overwritten during materialization"
    assert "GSF_GLOBAL_SHELL_V343" in shell
    assert "V404 fast startup" in baked_start

print("V404 fast production startup contract: PASS")
