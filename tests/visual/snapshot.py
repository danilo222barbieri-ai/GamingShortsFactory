"""GSF visual snapshot: screenshots of the running app and of every UI component.

Usage: python tests/visual/snapshot.py <base_url> <materialized_dir> <out_dir>

- <base_url>: the running frontend (e.g. http://127.0.0.1:8080)
- <materialized_dir>: folder with the component directories copied out of the
  built image (each `*_component/index.html` is rendered standalone)
- <out_dir>: where PNGs and a summary.json are written

Best effort by design: a step that fails is recorded in summary.json and the
run continues, so one broken screen never hides the others.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

VIEWPORTS = {
    "mobile": {"width": 390, "height": 844, "device_scale_factor": 2, "is_mobile": True, "has_touch": True},
    "desktop": {"width": 1440, "height": 900, "device_scale_factor": 1},
}

# Tiles/buttons on the Home that open the main areas, tried in every frame.
NAV_TARGETS = ["Crea con IA", "Game Editor", "Crea Short", "Creator Hub"]


def _settle(page, ms: int = 2500) -> None:
    try:
        page.wait_for_load_state("networkidle", timeout=20000)
    except Exception:
        pass
    page.wait_for_timeout(ms)


def _click_text(page, text: str) -> bool:
    for frame in page.frames:
        try:
            loc = frame.get_by_text(text, exact=False).first
            if loc.count() and loc.is_visible():
                loc.click(timeout=4000)
                return True
        except Exception:
            continue
    return False


def main() -> int:
    base_url, materialized, out = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    out.mkdir(parents=True, exist_ok=True)
    summary: dict[str, str] = {}

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for vp_name, vp in VIEWPORTS.items():
            ctx = browser.new_context(**vp)
            page = ctx.new_page()

            # 1) Live app: Home, then each main area.
            try:
                page.goto(base_url + "/", timeout=60000)
                _settle(page, 6000)
                page.screenshot(path=str(out / f"{vp_name}-01-home.png"), full_page=True)
                summary[f"{vp_name}-home"] = "ok"
            except Exception as exc:  # noqa: BLE001
                summary[f"{vp_name}-home"] = f"error: {exc}"[:300]

            for idx, target in enumerate(NAV_TARGETS, start=2):
                key = f"{vp_name}-{target}"
                try:
                    page.goto(base_url + "/", timeout=60000)
                    _settle(page, 5000)
                    if not _click_text(page, target):
                        summary[key] = "not found"
                        continue
                    _settle(page, 4000)
                    slug = target.lower().replace(" ", "-")
                    page.screenshot(path=str(out / f"{vp_name}-{idx:02d}-{slug}.png"), full_page=True)
                    summary[key] = "ok"
                except Exception as exc:  # noqa: BLE001
                    summary[key] = f"error: {exc}"[:300]

            # 2) Every component rendered standalone (styling only, no backend data).
            for index in sorted(materialized.glob("*_component/index.html")):
                name = index.parent.name
                key = f"{vp_name}-component-{name}"
                try:
                    page.goto(index.resolve().as_uri(), timeout=30000)
                    page.wait_for_timeout(1500)
                    page.screenshot(path=str(out / f"{vp_name}-component-{name}.png"), full_page=True)
                    summary[key] = "ok"
                except Exception as exc:  # noqa: BLE001
                    summary[key] = f"error: {exc}"[:300]
            ctx.close()
        browser.close()

    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
