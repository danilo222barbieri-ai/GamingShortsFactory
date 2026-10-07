#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import sys

HERE = Path(__file__).resolve().parent
MODULE = HERE / "fix_v307_mobile_visual_source.py"


def load_module():
    spec = importlib.util.spec_from_file_location("v307_mobile_visual_source", MODULE)
    if spec is None or spec.loader is None:
        raise RuntimeError("V307 sanitizer module could not be loaded")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def unit_contract(mod) -> None:
    sample = '''<style>
.base{color:red}
@media (min-width:761px){.desk{display:grid}}
@media (max-width:760px){.mobile{display:block}}
@media (prefers-reduced-motion:reduce){.anim{transition:none}}
/* V267 GLOBAL DESKTOP POLISH — AI surface, desktop only. */
@media (min-width:761px){.legacy{opacity:.5}}
/* END V267 GLOBAL DESKTOP POLISH */
</style><script>const KEEP_LOGIC = true;</script>'''
    out = mod.sanitize_text(sample)
    checks = [
        ("desktop media removed", ".desk{" not in out and "min-width:761px" not in out),
        ("legacy desktop marker removed", ".legacy{" not in out and "V267 GLOBAL DESKTOP POLISH" not in out),
        ("mobile media unwrapped", "@media (max-width:760px)" not in out and ".mobile{display:block}" in out),
        ("non-viewport media preserved", "@media (prefers-reduced-motion:reduce)" in out),
        ("logic preserved", "KEEP_LOGIC = true" in out),
    ]

    sample_runtime = '<div id="ng27" data-v297-layout="editor"><script id="v297EditorRuntime">window.BAD_DESK=true;</script><script>window.KEEP=true;</script></div>'
    runtime_out = mod.sanitize_text(sample_runtime)
    checks.extend([
        ("desktop runtime removed", "v297EditorRuntime" not in runtime_out and "BAD_DESK" not in runtime_out),
        ("desktop layout attribute removed", "data-v297-layout" not in runtime_out),
        ("unrelated runtime kept", "window.KEEP=true" in runtime_out),
    ])

    failed = [name for name, ok in checks if not ok]
    for name, ok in checks:
        print(("PASS" if ok else "FAIL") + ": " + name)
    if failed:
        raise SystemExit("V307 unit contract failed: " + ", ".join(failed))


def integration_contract(mod, root: Path) -> None:
    web = root / "web"
    home_embed = web / "home_v154_embed.py"
    editor_embed = web / "editor_2027_embed.py"
    targets = [
        web / "home_v154_component" / "index.html",
        web / "ai_v221_component" / "index.html",
        web / "creator_hub_v156_component" / "index.html",
        web / "editor_2027_component" / "index.html",
        web / "share_v156_component" / "index.html",
        root / "GamingShortsFactory_V154_STRUCTURAL_HOME.py",
        home_embed,
        editor_embed,
    ]
    missing = [str(path) for path in targets if not path.is_file()]
    if missing:
        raise SystemExit("V307 integration targets missing: " + ", ".join(missing))

    forbidden_markers = (
        "V267 GLOBAL DESKTOP POLISH",
        "V268 DESKTOP AESTHETIC CALIBRATION",
        "V294 HOME DESKTOP REALIGN",
        "V296 VISIBLE INTERNAL PAGES",
        "V297 DESK REBUILD",
        "V298 EDITOR GRAPHIC ONLY",
        "V301 HOME DESK REBALANCE",
        "V305 EDITOR DESKTOP SINGLE SURFACE",
        "v297EditorRuntime",
        "v298EditorGraphicOnly",
        "v298EditorWorkspace",
    )

    failures = []
    for path in targets[:6]:
        text = path.read_text(encoding="utf-8")
        if mod.has_viewport_min_width_media(text):
            failures.append(path.name + ": viewport min-width media remains")
        for marker in forbidden_markers:
            if marker in text:
                failures.append(path.name + ": legacy marker remains: " + marker)
        if "@media (max-width:760px)" in text or "@media(max-width:760px)" in text:
            failures.append(path.name + ": mobile 760px rules were not promoted")

    shell = targets[5].read_text(encoding="utf-8")
    home_embed_text = home_embed.read_text(encoding="utf-8")
    editor_embed_text = editor_embed.read_text(encoding="utf-8")
    logic_checks = {
        "Home upload logic": "GSF" in targets[0].read_text(encoding="utf-8") and "upload" in targets[0].read_text(encoding="utf-8").lower(),
        "AI engine logic": "engine" in targets[1].read_text(encoding="utf-8").lower(),
        "Hub folder logic": "data-folder" in targets[2].read_text(encoding="utf-8"),
        "Editor controls": 'data-panel="frame"' in targets[3].read_text(encoding="utf-8") and 'data-panel="caption"' in targets[3].read_text(encoding="utf-8"),
        "Share actions": "download" in targets[4].read_text(encoding="utf-8").lower(),
        "Home final cache": '"gsf_home_v154_live_307"' in home_embed_text,
        "Editor final cache": '"gsf_editor_2027_v307"' in editor_embed_text,
        "Hub final cache": '/creator-hub-v156/?v=307' in shell,
        "Share final cache": '/share-v156/?v=307' in shell,
        "AI final cache": '/ai-v221/?v=307' in shell,
    }
    for name, ok in logic_checks.items():
        print(("PASS" if ok else "FAIL") + ": " + name)
        if not ok:
            failures.append("logic/cache missing: " + name)

    if failures:
        raise SystemExit("V307 integration contract failed: " + " | ".join(failures))
    print("V307 production visual reset: PASS")


def main() -> None:
    mod = load_module()
    unit_contract(mod)
    if len(sys.argv) > 1:
        integration_contract(mod, Path(sys.argv[1]))


if __name__ == "__main__":
    main()
