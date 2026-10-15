#!/usr/bin/env python3
"""GSF freeze probe (WebKit, iPhone): find WHERE and WHEN the page stops responding.

Repeats Game Bar navigations with a hard per-step deadline. After every step it
appends one JSON line to OUT_DIR/freeze.jsonl:
  step, target, seconds the step took, observers attached to the top page,
  observer callbacks and milliseconds spent in them, long main-thread stalls.
A step that misses its deadline is recorded as {"hung": true} with a screenshot,
and the probe stops (a frozen main thread does not come back).

Run: BASE=http://127.0.0.1:18080 OUT_DIR=out STEPS=40 python tests/visual/gsf_freeze_probe.py
"""
from __future__ import annotations

import asyncio
import json
import os
import time
from pathlib import Path

from playwright.async_api import async_playwright

BASE = os.environ.get("BASE", "http://127.0.0.1:18080").rstrip("/")
OUT = Path(os.environ.get("OUT_DIR", "freeze-out"))
STEPS = int(os.environ.get("STEPS", "40"))
DEADLINE = float(os.environ.get("STEP_DEADLINE", "20"))
OUT.mkdir(parents=True, exist_ok=True)
LOG = OUT / "freeze.jsonl"

INSTRUMENT = r"""
(() => {
  let topWin; try { topWin = window.top; void topWin.document; } catch (e) { topWin = window; }
  const S = topWin.__gsfObs || (topWin.__gsfObs = {active: 0, created: 0, callbacks: 0, callbackMs: 0, stalls: 0, stallMs: 0});
  if (window === topWin && !topWin.__gsfStallLoop) {
    topWin.__gsfStallLoop = true;
    let last = performance.now();
    setInterval(() => { const now = performance.now(), gap = now - last - 250; if (gap > 200) { S.stalls += 1; S.stallMs += gap; } last = now; }, 250);
  }
  const Native = window.MutationObserver;
  if (!Native || Native.__gsfWrapped) return;
  function Wrapped(cb) {
    const self = new Native(function (records, obs) { S.callbacks += 1; const t = performance.now(); try { return cb.call(this, records, obs); } finally { S.callbackMs += performance.now() - t; } });
    let topTargets = 0;
    const observe = self.observe.bind(self), disconnect = self.disconnect.bind(self);
    self.observe = function (target, opts) {
      try { if (target && (target === topWin.document || target.ownerDocument === topWin.document)) { topTargets += 1; S.active += 1; S.created += 1; } } catch (e) {}
      return observe(target, opts);
    };
    self.disconnect = function () { S.active -= topTargets; topTargets = 0; return disconnect(); };
    return self;
  }
  Wrapped.prototype = Native.prototype;
  Wrapped.__gsfWrapped = true;
  window.MutationObserver = Wrapped;
})();
"""

ROUTE = (("hub", "dashboard"), ("projects", ""), ("live", ""), ("hub", "profile"), ("home", ""))


def log(row):
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")
    print(json.dumps(row), flush=True)


async def main():
    LOG.write_text("", encoding="utf-8")
    async with async_playwright() as p:
        browser = await p.webkit.launch()
        ctx = await browser.new_context(**p.devices["iPhone 13"])
        await ctx.add_init_script(INSTRUMENT)
        page = await ctx.new_page()
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)[:200]))
        t0 = time.time()
        await page.goto(BASE + "/", wait_until="domcontentloaded")
        await page.wait_for_selector("button[data-page='hub']", timeout=120_000)
        await page.wait_for_timeout(5000)
        log({"step": 0, "target": "load", "seconds": round(time.time() - t0, 1)})

        for i in range(1, STEPS + 1):
            target, section = ROUTE[(i - 1) % len(ROUTE)]
            t = time.time()
            try:
                stats = await asyncio.wait_for(page.evaluate(
                    """async ([t, s]) => {
                        window.postMessage({type: 'GSF_SHELL_NAV', target: t, section: s}, window.location.origin);
                        await new Promise(r => setTimeout(r, 1500));
                        return Object.assign({}, window.top.__gsfObs || {});
                    }""", [target, section]), timeout=DEADLINE)
            except asyncio.TimeoutError:
                row = {"step": i, "target": target, "section": section, "hung": True,
                       "seconds": round(time.time() - t, 1), "errors": errors[-5:]}
                try:
                    await asyncio.wait_for(page.screenshot(path=str(OUT / f"hung-step-{i}.png")), timeout=15)
                    row["screenshot"] = f"hung-step-{i}.png"
                except Exception as exc:  # screenshot may need the same frozen thread
                    row["screenshot_error"] = type(exc).__name__
                log(row)
                break
            stats["callbackMs"] = round(stats.get("callbackMs", 0), 1)
            stats["stallMs"] = round(stats.get("stallMs", 0), 1)
            log({"step": i, "target": target, "section": section, "seconds": round(time.time() - t, 1), **stats})
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
