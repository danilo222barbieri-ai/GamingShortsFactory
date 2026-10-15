#!/usr/bin/env python3
"""GSF visual + runtime-health check against a running image (Safari engine, iPhone).

Produces, in OUT_DIR:
  *.png         full screenshots of every mobile surface (deterministic names)
  metrics.json  MutationObservers attached to the top page after each navigation
                cycle, observer callbacks fired, console errors, timings

Run: BASE=http://127.0.0.1:18080 OUT_DIR=out python tests/visual/gsf_visual_check.py
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = os.environ.get("BASE", "http://127.0.0.1:18080").rstrip("/")
OUT = Path(os.environ.get("OUT_DIR", "visual-out"))
CYCLES = int(os.environ.get("CYCLES", "8"))
OUT.mkdir(parents=True, exist_ok=True)

# Counts observers that watch the TOP document, wherever (iframe or page) they were created.
INSTRUMENT = r"""
(() => {
  let topWin; try { topWin = window.top; void topWin.document; } catch (e) { topWin = window; }
  const S = topWin.__gsfObs || (topWin.__gsfObs = {active: 0, created: 0, callbacks: 0, disconnects: 0, callbackMs: 0});
  const Native = window.MutationObserver;
  if (!Native || Native.__gsfWrapped) return;
  function Wrapped(cb) {
    const self = new Native(function (records, obs) { S.callbacks += 1; const t = performance.now(); try { return cb.call(this, records, obs); } finally { S.callbackMs += performance.now() - t; } });
    let topTargets = 0;
    const observe = self.observe.bind(self), disconnect = self.disconnect.bind(self);
    self.observe = function (target, opts) {
      try { if (target && target.ownerDocument === topWin.document || target === topWin.document) { topTargets += 1; S.active += 1; S.created += 1; } } catch (e) {}
      return observe(target, opts);
    };
    self.disconnect = function () { S.active -= topTargets; S.disconnects += topTargets; topTargets = 0; return disconnect(); };
    return self;
  }
  Wrapped.prototype = Native.prototype;
  Wrapped.__gsfWrapped = true;
  window.MutationObserver = Wrapped;
})();
"""


def settle(page, ms=2500):
    page.wait_for_timeout(ms)


def stats(page):
    return page.evaluate("() => Object.assign({}, window.__gsfObs || {})")


def shot(page, name):
    page.screenshot(path=str(OUT / f"{name}.png"), full_page=False)


def nav(page, target, section=""):
    page.evaluate(
        "([t, s]) => window.postMessage({type: 'GSF_SHELL_NAV', target: t, section: s}, window.location.origin)",
        [target, section],
    )
    settle(page)


def check_mobile_editor(ctx, metrics):
    page = ctx.new_page()
    errors = []
    page.on("console", lambda message: message.type == "error" and errors.append(message.text[:300]))
    page.on("pageerror", lambda error: errors.append(("pageerror: " + str(error))[:300]))
    page.goto(BASE + "/game-editor-mobile/", wait_until="load")
    page.wait_for_selector("#gameEditorApp")
    page.evaluate(
        """() => {
          window.__editorMessages = [];
          window.addEventListener('message', event => {
            if (event.origin === location.origin && event.data?.type === 'GSF_GAME_EDITOR_UI') {
              window.__editorMessages.push(structuredClone(event.data));
            }
          });
          document.querySelector('#gameEditorApp').requestFullscreen = () => Promise.reject(new Error('test fallback'));
          window.postMessage({
            type: 'GSF_GAME_EDITOR_INIT',
            session: {sid: 'visual-session'},
            project: {title: 'Visual Game Editor'},
            media: {url: ''},
            initial_state: {sourceDuration: 18, inPoint: 1, outPoint: 14, zoom: 1},
            event_map: [{time: 4.2, label: 'Eliminazione'}],
            brain_context: {game: 'Test Arena'},
            ai_suggestions: [{id: 'focus-action', label: 'Focus azione', reason: 'Porta il duello al centro', impact: 'Zoom 1.8×', patch: {zoom: 1.8, panX: 8}}]
          }, location.origin);
        }"""
    )
    page.wait_for_function("() => document.querySelector('#projectTitle').textContent === 'Visual Game Editor'")
    assert page.locator("[data-tool]").count() == 5
    assert page.locator("#eventMarkers .event-marker").count() == 1

    page.locator("#fullscreenButton").click()
    page.wait_for_function("() => document.querySelector('#fullscreenButton').getAttribute('aria-pressed') === 'true'")
    page.locator("#fullscreenButton").click()
    page.wait_for_function("() => document.querySelector('#fullscreenButton').getAttribute('aria-pressed') === 'false'")
    fullscreen_signals = page.evaluate(
        "() => window.__editorMessages.filter(message => message.action === 'fullscreen_changed').map(message => message.active)"
    )
    assert fullscreen_signals[-2:] == [True, False]

    page.evaluate(
        """() => {
          const stage = document.querySelector('#previewStage');
          const emit = (type, id, x, y) => stage.dispatchEvent(new PointerEvent(type, {bubbles: true, pointerId: id, pointerType: 'touch', clientX: x, clientY: y}));
          emit('pointerdown', 1, 90, 180); emit('pointerdown', 2, 190, 180);
          emit('pointermove', 2, 245, 180); emit('pointerup', 2, 245, 180);
        }"""
    )
    page.wait_for_function("() => window.GSFGameEditor2026.getState().zoom > 1")
    gesture_state = page.evaluate("() => window.GSFGameEditor2026.getState()")
    page.evaluate(
        """() => {
          const stage = document.querySelector('#previewStage');
          const before = window.GSFGameEditor2026.getState();
          const emit = (type, id, x, y) => stage.dispatchEvent(new PointerEvent(type, {bubbles: true, pointerId: id, pointerType: 'touch', clientX: x, clientY: y}));
          emit('pointerdown', 7, 120, 210); emit('pointermove', 7, 180, 210); emit('pointercancel', 7, 180, 210);
          window.__cancelledGestureBefore = before;
        }"""
    )
    cancelled_state = page.evaluate("() => window.GSFGameEditor2026.getState()")
    cancelled_before = page.evaluate("() => window.__cancelledGestureBefore")
    assert cancelled_state == cancelled_before
    assert not page.locator("#previewStage").evaluate("node => node.classList.contains('is-gesturing')")

    page.locator('[data-tool="ai"]').click()
    state_before_ai = page.evaluate("() => window.GSFGameEditor2026.getState()")
    page.locator('[data-ai-action="preview"]').click()
    assert page.evaluate("() => window.GSFGameEditor2026.getState()") == state_before_ai
    assert page.locator('[data-ai-action="apply"]').is_enabled()
    page.locator('[data-ai-action="apply"]').click()
    state_after_ai = page.evaluate("() => window.GSFGameEditor2026.getState()")
    assert state_after_ai["zoom"] == 1.8
    page.locator("#undoButton").click()
    assert page.evaluate("() => window.GSFGameEditor2026.getState()") == state_before_ai

    page.locator("#saveDraftButton").click()
    page.locator("#continueButton").click()
    actions = page.evaluate("() => window.__editorMessages.map(message => message.action)")
    assert "save_draft" in actions and "continue_to_short" in actions
    assert not errors, errors
    page.screenshot(path=str(OUT / "14-mobile-game-editor.png"), full_page=False)
    metrics["surfaces"]["mobile-game-editor"] = {
        "gesture_state": gesture_state,
        "fullscreen_signals": fullscreen_signals,
        "console_errors": errors,
    }
    page.close()


def main():
    metrics = {"base": BASE, "cycles": [], "console_errors": [], "surfaces": {}}
    with sync_playwright() as p:
        browser = p.webkit.launch()
        ctx = browser.new_context(**p.devices["iPhone 13"])
        ctx.add_init_script(INSTRUMENT)
        page = ctx.new_page()
        page.on("console", lambda m: m.type == "error" and metrics["console_errors"].append(m.text[:300]))
        page.on("pageerror", lambda e: metrics["console_errors"].append(("pageerror: " + str(e))[:300]))

        t0 = time.time()
        page.goto(BASE + "/", wait_until="domcontentloaded")
        page.wait_for_selector("button[data-page='hub']", timeout=120_000)
        settle(page, 6000)
        metrics["home_ready_seconds"] = round(time.time() - t0, 1)
        shot(page, "01-home")
        metrics["surfaces"]["home"] = stats(page)

        for name, target, section in (("02-hub", "hub", "dashboard"), ("03-projects", "projects", ""),
                                      ("04-live", "live", ""), ("05-hub-profile", "hub", "profile"),
                                      ("06-editor", "editor", ""), ("07-home-again", "home", "")):
            nav(page, target, section)
            shot(page, name)
            metrics["surfaces"][name] = stats(page)

        for i in range(CYCLES):
            for target, section in (("hub", "dashboard"), ("editor", ""), ("live", ""), ("home", "")):
                nav(page, target, section)
            s = stats(page)
            s["cycle"] = i + 1
            metrics["cycles"].append(s)

        # Standalone mobile surfaces served by nginx (same bytes the app embeds).
        for name, path in (("10-creator-hub-page", "/creator-hub-v156/"), ("11-crea-con-ia", "/ai-v221/"),
                           ("12-editor-page", "/editor-live/"), ("13-share", "/share-v156/")):
            q = ctx.new_page()
            q.goto(BASE + path, wait_until="load")
            settle(q, 2500)
            q.screenshot(path=str(OUT / f"{name}.png"), full_page=False)
            q.close()
        check_mobile_editor(ctx, metrics)
        browser.close()

    for c in metrics["cycles"]:
        c["callbackMs"] = round(c.get("callbackMs", 0), 1)
    first, last = metrics["cycles"][0], metrics["cycles"][-1]
    metrics["callback_ms_per_cycle"] = round((last["callbackMs"] - first["callbackMs"]) / max(1, CYCLES - 1), 1)
    metrics["observer_growth_per_cycle"] = round((last["active"] - first["active"]) / max(1, CYCLES - 1), 2)
    (OUT / "metrics.json").write_text(json.dumps(metrics, indent=1), encoding="utf-8")
    print(json.dumps({k: metrics[k] for k in ("home_ready_seconds", "observer_growth_per_cycle", "callback_ms_per_cycle")}),
          "active after cycles:", [c["active"] for c in metrics["cycles"]])


if __name__ == "__main__":
    main()
