from pathlib import Path

HUB = Path("/app/web/creator_hub_v156_component/index.html")
APP = Path("/app/GamingShortsFactory_V154_STRUCTURAL_HOME.py")


def patch_hub() -> None:
    text = HUB.read_text(encoding="utf-8")
    before = text
    text = text.replace('$(["[data-view]"])', '$$(["[data-view]"])')
    text = text.replace('$(["[data-project-pane]"])', '$$(["[data-project-pane]"])')
    # Exact source emitted by V284 uses querySelector ($) where a collection is required.
    text = text.replace('$("[data-view]").forEach', '$$("[data-view]").forEach')
    text = text.replace('$("[data-project-pane]").forEach', '$$("[data-project-pane]").forEach')
    if '$$("[data-view]").forEach' not in text:
        raise RuntimeError("V285: data-view collection selector was not repaired")
    if '$$("[data-project-pane]").forEach' not in text:
        raise RuntimeError("V285: project-pane collection selector was not repaired")
    HUB.write_text(text, encoding="utf-8")
    print("V285 Creator Hub folder click selectors repaired:", HUB, "changed=", text != before, flush=True)


def bust_hub_cache() -> None:
    if not APP.is_file():
        return
    text = APP.read_text(encoding="utf-8")
    patched = text.replace('/creator-hub-v156/?v=284', '/creator-hub-v156/?v=285')
    if patched == text and '/creator-hub-v156/?v=285' not in text:
        print("V285 cache-bust marker not found; continuing with repaired static Hub", flush=True)
        return
    APP.write_text(patched, encoding="utf-8")
    print("V285 Creator Hub iframe cache-bust applied", flush=True)


if __name__ == "__main__":
    patch_hub()
    bust_hub_cache()
