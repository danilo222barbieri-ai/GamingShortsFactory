import re
from pathlib import Path

HUB = Path("/app/web/creator_hub_v156_component/index.html")
APP = Path("/app/GamingShortsFactory_V154_STRUCTURAL_HOME.py")


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
    patched = text.replace('/creator-hub-v156/?v=284', '/creator-hub-v156/?v=286')
    patched = patched.replace('/creator-hub-v156/?v=285', '/creator-hub-v156/?v=286')

    required = [
        'data-target="hub" data-section="dashboard"',
        'data-target="hub" data-section="shorts"',
        'data-target="hub" data-section="drafts"',
        "type:'GSF_HUB_FOCUS',section",
        '/creator-hub-v156/?v=286',
    ]
    missing = [marker for marker in required if marker not in patched]
    if missing:
        raise RuntimeError("V286: global Game Bar shell markers missing: " + ", ".join(missing))

    APP.write_text(patched, encoding="utf-8")
    print("V286 global Game Bar shell verified and Creator Hub cache busted", flush=True)


if __name__ == "__main__":
    patch_hub()
    patch_shell()
