#!/usr/bin/env python3
"""Guard: the repository UI files are the runtime UI, and nothing may rewrite them.

Fails if:
  * the Docker build or any startup script runs a legacy fix_/apply_ migration,
    the V77 payload, the retired materializer or the V269 build hook;
  * the startup path transforms files instead of only verifying + launching;
  * the manifest guard stops detecting an old version being reinjected;
  * an approved mobile surface loses its canonical markers;
  * session / CSRF security on the Creator Hub state route is weakened.

Run: python tests/test_canonical_ui_pipeline.py   (or pytest)
"""
from __future__ import annotations

import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"

LEGACY_RE = re.compile(
    r"(fix_v\d|apply_v\d|materialize_runtime_patches\.sh\s*(&&|;|$)|test_v269_creator_hub_recovery"
    r"|src_payload|gsf_v77\.py\.gz|GamingShortsFactory_V77|v404_legacy_runtime_compat|start_web_legacy)",
    re.M,
)


def _load_manifest_tool():
    spec = importlib.util.spec_from_file_location("gsf_ui_manifest", ROOT / "tools" / "gsf_ui_manifest.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _dockerfile_commands() -> str:
    text = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    return "\n".join(l for l in text.splitlines() if not l.lstrip().startswith("#"))


def test_dockerfile_runs_no_legacy_chain():
    cmds = _dockerfile_commands()
    hits = sorted({m.group(1) for m in LEGACY_RE.finditer(cmds)})
    assert not hits, f"Dockerfile must not execute legacy migrations/payloads: {hits}"
    assert "COPY app.py /app/app.py" in cmds
    assert "COPY web /app/web" in cmds
    assert "gsf_ui_manifest.py write" in cmds and "gsf_ui_manifest.py verify" in cmds
    # the only allowed in-image mutation of a non-repo file
    runs = re.findall(r"^RUN .*$", cmds, re.M)
    py_scripts = sorted(set(re.findall(r"python (/app/web/[\w./-]+\.py)", cmds)))
    allowed = {"/app/web/install_adsense_bridge.py", "/app/web/test_v410_security_hardening.py"}
    assert set(py_scripts) <= allowed, f"unexpected build-time scripts: {sorted(set(py_scripts) - allowed)}"
    assert runs, "no RUN steps parsed"
    assert re.search(r'^CMD \["/app/web/start_web\.sh"\]', cmds, re.M)


def test_startup_only_verifies_and_launches():
    start = (WEB / "start_web.sh").read_text(encoding="utf-8")
    fast = (WEB / "start_web_fast.sh").read_text(encoding="utf-8")
    body = "\n".join(l for l in start.splitlines() if not l.lstrip().startswith("#"))
    assert not LEGACY_RE.search(body), "start_web.sh must not run legacy migrations"
    assert "python /app/gsf_ui_manifest.py verify" in body
    assert "exec python -m streamlit run /app/app.py" in body
    launched = re.findall(r"^python (\S+)", body, re.M)
    assert set(launched) <= {"/app/gsf_ui_manifest.py", "-", "/app/web/direct_upload_server.py",
                             "/app/web/contact_server.py"}, launched
    for forbidden in (".replace(", "sed -i", "cp /app/web", "mv /app/web", "> /app/", "rm -f /app/"):
        assert forbidden not in body, f"startup must not transform files ({forbidden})"
    # the only file the startup writes is runtime config outside /app
    writes = re.findall(r'Path\("([^"]+)"\)', body)
    assert writes == ["/tmp/gsf-ads.txt"], writes
    assert "exec /bin/sh /app/web/start_web.sh" in fast and len(fast.splitlines()) < 8


def test_materializer_is_retired_and_fails_closed():
    script = WEB / "materialize_runtime_patches.sh"
    r = subprocess.run(["/bin/sh", str(script)], capture_output=True, text=True)
    assert r.returncode != 0 and "retired" in r.stderr


def test_manifest_detects_reinjected_old_ui():
    """Simulate a legacy migration restoring an older Creator Hub: the guard must fail."""
    import os
    tool = _load_manifest_tool()
    # The drift below is simulated on purpose: keep it out of GitHub annotations
    # so it is never mistaken for a real "Canonical UI drift" error.
    saved = os.environ.pop("GITHUB_ACTIONS", None)
    try:
        _simulate_reinjection(tool)
    finally:
        if saved is not None:
            os.environ["GITHUB_ACTIONS"] = saved


def _simulate_reinjection(tool):
    with tempfile.TemporaryDirectory() as tmp:
        image = Path(tmp) / "app"
        for src, dst in tool.CANONICAL_MAP:
            s, d = ROOT / src, image / dst
            if s.is_dir():
                shutil.copytree(s, d, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__"))
            else:
                d.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(s, d)
        assert tool.main(["write", "--root", str(image)]) == 0
        assert tool.main(["verify", "--root", str(image)]) == 0
        image_manifest = image / tool.MANIFEST_NAME
        assert tool.main(["compare", "--repo", str(ROOT), "--image-json", str(image_manifest)]) == 0
        hub = image / "web/creator_hub_v156_component/index.html"
        hub.write_text("<!-- legacy V311 hub reinjected -->\n" + hub.read_text(encoding="utf-8"), encoding="utf-8")
        assert tool.main(["verify", "--root", str(image)]) == 1, "reinjected legacy UI was not detected"
        (image / "web/legacy_overlay.css").write_text("body{}", encoding="utf-8")
        recorded = json.loads(image_manifest.read_text(encoding="utf-8"))
        problems = tool.diff(recorded["files"], tool.files_from_image(image))
        assert problems["modified"] == ["web/creator_hub_v156_component/index.html"]
        assert problems["unexpected"] == ["web/legacy_overlay.css"]


def test_mobile_game_editor_is_manifested_and_untouchable_by_legacy_scripts():
    import os
    tool = _load_manifest_tool()
    files = tool.files_from_repo(ROOT)
    prefix = "web/game_editor_mobile_component/"
    expected = {
        prefix + "index.html",
        prefix + "editor.css",
        prefix + "editor.mjs",
        prefix + "editor_state.mjs",
    }
    assert expected <= files.keys(), "canonical mobile editor must be covered by the existing recursive manifest"

    candidates = [ROOT / "Dockerfile", WEB / "start_web.sh", WEB / "start_web_fast.sh",
                  WEB / "materialize_runtime_patches.sh"]
    candidates.extend(WEB.glob("fix_v*.py"))
    candidates.extend(WEB.glob("apply_v*.py"))
    candidates.extend((ROOT / "scripts").glob("apply_v*.py"))
    offenders = []
    for path in candidates:
        source = path.read_text(encoding="utf-8")
        if "game_editor_mobile_component" in source:
            offenders.append(path.relative_to(ROOT).as_posix())
    assert not offenders, f"legacy/build scripts must never target the canonical mobile editor: {offenders}"

    with tempfile.TemporaryDirectory() as tmp:
        image = Path(tmp) / "app"
        for src, dst in tool.CANONICAL_MAP:
            source, destination = ROOT / src, image / dst
            if source.is_dir():
                shutil.copytree(source, destination, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__"))
            else:
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
        assert tool.main(["write", "--root", str(image)]) == 0
        target = image / prefix / "index.html"
        target.write_text("<!-- forbidden legacy editor -->\n" + target.read_text(encoding="utf-8"), encoding="utf-8")
        saved = os.environ.pop("GITHUB_ACTIONS", None)
        try:
            assert tool.main(["verify", "--root", str(image)]) == 1
        finally:
            if saved is not None:
                os.environ["GITHUB_ACTIONS"] = saved


def test_every_editor_navigation_owner_selects_mobile_without_changing_desktop():
    app = (ROOT / "app.py").read_text(encoding="utf-8")
    mobile_owner_start = app.index("/* GSF_MOBILE_EDITOR_2026_BRIDGE */")
    mobile_open = app.index("const open=(remember=true)=>{", mobile_owner_start)
    assert "selectedEditorSource()" in app[mobile_open:]
    assert "frame.dataset.loaded='1'" in app[mobile_open:]
    assert "const MOBILE_EDITOR_SRC='/game-editor-mobile/';" in app
    assert "const DESKTOP_EDITOR_SRC='/editor-live/';" in app
    assert "const ensureEditorSurface=()=>{" not in app, "a second source owner must not overwrite the mobile editor"
    assert "registerSurface('editor'" in app
    assert "const route=data=>P.GSFNavigation.navigate(data);" in app


def test_ci_and_production_gate_execute_mobile_editor_contracts():
    ci = (ROOT / ".github/workflows/gsf-ci.yml").read_text(encoding="utf-8")
    gate = (ROOT / ".github/workflows/v397-production-gate.yml").read_text(encoding="utf-8")
    runtime = (WEB / "runtime_smoke_v411.py").read_text(encoding="utf-8")
    for workflow in (ci, gate):
        assert "node --test tests/js/mobile_game_editor_state.test.mjs" in workflow
        assert "node --check web/game_editor_mobile_component/editor.mjs" in workflow
        assert "node --check web/game_editor_mobile_component/editor_state.mjs" in workflow
    assert "game_editor_mobile_component:/game-editor-mobile/" in gate
    for asset in ("/game-editor-mobile/", "/game-editor-mobile/editor.css",
                  "/game-editor-mobile/editor.mjs", "/game-editor-mobile/editor_state.mjs"):
        assert asset in runtime
    assert "sha256" in runtime


def test_canonical_mobile_surfaces_keep_approved_markers():
    hub = (WEB / "creator_hub_v156_component/index.html").read_text(encoding="utf-8")
    ai = (WEB / "ai_v221_component/index.html").read_text(encoding="utf-8")
    editor = (WEB / "editor_2027_component/index.html").read_text(encoding="utf-8")
    app = (ROOT / "app.py").read_text(encoding="utf-8")
    for marker in ("V373_CREATOR_HUB_HEADER_BREATH", "V357_CREATOR_HUB_HIERARCHY", "V359_CREATOR_HUB_GAMEBAR_FIT"):
        assert marker in hub, marker
    assert 'id="ai404"' in ai, "Crea con IA V404 must stay canonical"
    for marker in ("V360_MOBILE_EDITOR_REFERENCE", "V389_MOBILE_EDITOR_BOUNDED_RESET",
                   "V393_MOBILE_EDITOR_CLEAN_TRANSPORT", "V394_MOBILE_EDITOR_FOOTER_RESTORE"):
        assert marker in editor, marker
    for marker in ("GSF_GLOBAL_SHELL_V343", "GSF_V351_FOOTER_BRAND_GLASS", "GSF_V362_VISIBLE_VERSION"):
        assert marker in app, marker
    compile(app, "app.py", "exec")


def test_creator_hub_state_security_is_not_weakened():
    server = (WEB / "direct_upload_server.py").read_text(encoding="utf-8")
    nginx = (WEB / "nginx.conf.template").read_text(encoding="utf-8")
    start = server.index('if clean=="/creator-hub/state":')
    block = server[start:server.index('if clean=="/account":', start)]
    assert "sid=_social_sid(self)" in block
    assert re.search(r"if not sid:\s*_json\(self,400", block), "missing-session must still be rejected"
    assert '"csrf_token":_security_csrf_token(sid)' in block
    loc = nginx[nginx.index("location = /creator-hub/state {"):]
    loc = loc[:loc.index("}") + 1]
    assert "proxy_set_header X-GSF-Session-ID $gsf_session_cookie;" in loc
    assert "gsf_sid=$gsf_session_cookie;" in loc and "HttpOnly" in loc and "Secure" in loc
    assert re.search(r'map \$cookie_gsf_sid \$gsf_session_cookie \{\s*"~\^\[A-Za-z0-9_-\]\{1,80\}\$" \$cookie_gsf_sid;\s*default\s+\$request_id;', nginx)
    # every companion (8502) proxy forwards the edge session id
    for m in re.finditer(r"location ([^{]+)\{(.*?)\n    \}", nginx, re.S):
        if "proxy_pass http://127.0.0.1:8502" in m.group(2) and "/healthz" not in m.group(1) \
                and not any(p in m.group(1) for p in ("manifest.webmanifest", "gsf-sw.js", "gsf-push.js", "push/public-key", "app-icon", "favicon", "apple-touch")):
            assert "X-GSF-Session-ID" in m.group(2), f"{m.group(1).strip()} lost the session header"


def test_game_bar_and_navigation_contracts_on_canonical_files():
    """Historical Game Bar / Hub-state contracts still hold on what is served."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        shutil.copytree(WEB, root / "web", ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copy2(ROOT / "app.py", root / "app.py")
        for alias in ("GamingShortsFactory_V154_STRUCTURAL_HOME.py", "GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py"):
            (root / alias).symlink_to("app.py")
        runs = (
            ["web/test_v286_global_gamebar.py", "web/creator_hub_v156_component/index.html",
             "GamingShortsFactory_V154_STRUCTURAL_HOME.py"],
            ["web/test_v302_global_live_gamebar.py", str(root)],
            ["web/test_v366_creator_hub_state_stability.py", str(root)],
        )
        for cmd in runs:
            r = subprocess.run([sys.executable, *cmd], cwd=root, capture_output=True, text=True, timeout=120)
            assert r.returncode == 0, f"{cmd[0]} failed on canonical files: {(r.stdout + r.stderr)[-600:]}"
    # V370 runtime contract: exactly one executable V343 shell, lightweight header state only.
    import ast
    spec = importlib.util.spec_from_file_location("fix_v370", WEB / "fix_v370_single_navigation_owner.py")
    fix = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fix)
    values = [n.value for n in ast.walk(ast.parse((ROOT / "app.py").read_text(encoding="utf-8")))
              if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    shells = [v for v in values if "__GSF_GLOBAL_SHELL_V343" in v and "/creator-hub/state" in v]
    assert len(shells) == 1, f"expected one executable V343 shell, found {len(shells)}"
    assert fix.HEADER_STATE_NEW in shells[0] and fix.HEADER_STATE_OLD not in shells[0]


def test_worker_image_runs_canonical_files_only():
    """The worker ships web/gsf_worker_app.py and web/ai_worker_server.py as committed."""
    text = (WEB / "Dockerfile.worker").read_text(encoding="utf-8")
    cmds = "\n".join(l for l in text.splitlines() if not l.lstrip().startswith("#"))
    hits = sorted({m.group(1) for m in LEGACY_RE.finditer(cmds)})
    assert not hits, f"worker Dockerfile must not execute legacy migrations/payloads: {hits}"
    assert "COPY web/gsf_worker_app.py /app/GamingShortsFactory_V99_FINAL_ARCH.py" in cmds
    assert "GSF_AI_APP_PATH=/app/GamingShortsFactory_V99_FINAL_ARCH.py" in cmds
    server = (WEB / "ai_worker_server.py").read_text(encoding="utf-8")
    assert "GSF_V401_PERSISTENT_JOB_STATE" in server, "V401 worker state must live in the canonical server"
    compile((WEB / "gsf_worker_app.py").read_text(encoding="utf-8"), "gsf_worker_app.py", "exec")


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn(); print(f"PASS {name}")
            except AssertionError as exc:
                failures += 1; print(f"FAIL {name}: {exc}")
    print("canonical UI pipeline guard:", "PASS" if not failures else f"{failures} FAILED")
    sys.exit(1 if failures else 0)
