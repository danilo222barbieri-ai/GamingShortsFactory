import re
from pathlib import Path

HUB = Path("/app/web/creator_hub_v156_component/index.html")
APP = Path("/app/GamingShortsFactory_V154_STRUCTURAL_HOME.py")


_CACHE_RE = re.compile(r'/creator-hub-v156/\?v=(\d+)')


def patch_hub() -> None:
    text = HUB.read_text(encoding="utf-8")
    before = text

    # Any call shaped as $(selector).forEach is invalid because $ is querySelector.
    # Convert every such collection use to $$ (querySelectorAll) so one missed
    # selector cannot abort the Hub script before GSF_HUB_FOCUS is installed.
    pattern = re.compile(r'(?<!\$)\$\((?P<q>["\'])(?P<selector>[^"\'\n]+)(?P=q)\)\.forEach')

    def repl(match: re.Match) -> str:
        q = match.group("q")
        selector = match.group("selector")
        return f"$$({q}{selector}{q}).forEach"

    text = pattern.sub(repl, text)

    required = [
        '$$("[data-view]").forEach',
        '$$("[data-project-pane]").forEach',
        '$$(".socialDot").forEach',
        'e.data.type!=="GSF_HUB_FOCUS"',
        'openView(raw);',
    ]
    missing = [marker for marker in required if marker not in text]
    if missing:
        raise RuntimeError("V286: Creator Hub navigation markers missing: " + ", ".join(missing))

    leftovers = pattern.findall(text)
    if leftovers:
        raise RuntimeError("V286: querySelector().forEach misuse remains in Creator Hub")

    HUB.write_text(text, encoding="utf-8")
    print("V286 Creator Hub Game Bar receiver repaired:", HUB, "changed=", text != before, flush=True)


def patch_shell() -> None:
    if not APP.is_file():
        return

    text = APP.read_text(encoding="utf-8")

    # V286 is an old bootstrap step and must remain safe when newer releases
    # have already bumped the Creator Hub cache version. Upgrade only older
    # versions; never downgrade V287+ back to V286.
    def bump_cache(match: re.Match) -> str:
        current = int(match.group(1))
        return f'/creator-hub-v156/?v={max(current, 286)}'

    patched = _CACHE_RE.sub(bump_cache, text)
    cache_versions = [int(v) for v in _CACHE_RE.findall(patched)]

    required = [
        'data-target="hub" data-section="dashboard"',
        'data-target="hub" data-section="shorts"',
        'data-target="hub" data-section="drafts"',
        "type:'GSF_HUB_FOCUS',section",
    ]
    missing = [marker for marker in required if marker not in patched]
    if not cache_versions or max(cache_versions) < 286:
        missing.append('/creator-hub-v156/?v>=286')
    if missing:
        raise RuntimeError("V286: global Game Bar shell markers missing: " + ", ".join(missing))

    APP.write_text(patched, encoding="utf-8")
    print(
        "V286 global Game Bar shell verified; Creator Hub cache version=",
        max(cache_versions),
        flush=True,
    )


if __name__ == "__main__":
    patch_hub()
    patch_shell()
