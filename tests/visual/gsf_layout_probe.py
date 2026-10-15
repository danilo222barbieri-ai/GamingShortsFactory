#!/usr/bin/env python3
"""GSF mobile layout probe (WebKit, iPhone): what overlaps the shell header and Game Bar.

For Home and Hub it writes OUT_DIR/layout-<surface>.json and a screenshot with:
  - the shell header, Game Bar and footer rectangles on the top page;
  - every iframe on the top page (rect, src);
  - inside each same-origin iframe, every visible element that intersects the
    header or Game Bar band, mapped to top-page coordinates, with its selector,
    text, opacity and computed position.

Run: BASE=http://127.0.0.1:18080 OUT_DIR=out python tests/visual/gsf_layout_probe.py
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = os.environ.get("BASE", "http://127.0.0.1:18080").rstrip("/")
OUT = Path(os.environ.get("OUT_DIR", "layout-out"))
OUT.mkdir(parents=True, exist_ok=True)

DUMP = r"""
() => {
  const r2 = (r) => ({x: Math.round(r.left), y: Math.round(r.top), w: Math.round(r.width), h: Math.round(r.height)});
  const D = document;
  const pick = (sel) => { const el = D.querySelector(sel); return el ? r2(el.getBoundingClientRect()) : null; };
  const header = pick('#gsf-global-header') || pick('header');
  const gamebar = pick('#gsf-global-gamebar');
  const footer = pick('#gsf-global-footer');
  const vh = window.innerHeight;
  const bands = [];
  if (header) bands.push(['header', header.y, header.y + header.h]);
  if (gamebar) bands.push(['gamebar', gamebar.y, vh]);
  const desc = (el) => {
    let s = el.tagName.toLowerCase();
    if (el.id) s += '#' + el.id;
    if (el.classList && el.classList.length) s += '.' + [...el.classList].slice(0, 3).join('.');
    return s;
  };
  const frames = [...D.querySelectorAll('iframe')].map((f) => {
    const fr = f.getBoundingClientRect();
    const out = {src: (f.getAttribute('src') || '').slice(0, 120), title: f.title || '', rect: r2(fr), hits: []};
    if (fr.width < 2 || fr.height < 2) return out;
    let doc; try { doc = f.contentDocument; void doc.body; } catch (e) { out.crossOrigin = true; return out; }
    if (!doc || !doc.body) return out;
    out.innerHeight = f.contentWindow.innerHeight;
    out.scrollHeight = doc.documentElement.scrollHeight;
    const W = f.contentWindow;
    for (const el of doc.body.querySelectorAll('*')) {
      const r = el.getBoundingClientRect();
      if (r.width < 4 || r.height < 4) continue;
      const cs = W.getComputedStyle(el);
      if (cs.display === 'none' || cs.visibility === 'hidden' || Number(cs.opacity) === 0) continue;
      const top = fr.top + r.top, bottom = fr.top + r.bottom;
      if (bottom <= fr.top || top >= fr.bottom) continue;  // clipped by the iframe
      const band = bands.find(([, a, b]) => top < b && bottom > a);
      if (!band) continue;
      const own = [...el.childNodes].filter((n) => n.nodeType === 3).map((n) => n.textContent).join(' ').trim();
      if (!own && !/^(IMG|SVG|CANVAS|VIDEO|BUTTON)$/.test(el.tagName) && cs.backgroundColor === 'rgba(0, 0, 0, 0)' && cs.backgroundImage === 'none') continue;
      out.hits.push({band: band[0], el: desc(el), text: own.slice(0, 60), rect: {x: Math.round(fr.left + r.left), y: Math.round(top), w: Math.round(r.width), h: Math.round(r.height)},
                     opacity: cs.opacity, position: cs.position, z: cs.zIndex});
      if (out.hits.length > 80) break;
    }
    return out;
  });
  // Top-page elements (outside the shell) whose own text sits under the header or Game Bar.
  const topHits = [];
  for (const el of D.body.querySelectorAll('*')) {
    if (el.closest('#gsf-global-header,#gsf-global-gamebar,#gsf-global-footer,header')) continue;
    const own = [...el.childNodes].filter((n) => n.nodeType === 3).map((n) => n.textContent).join(' ').trim();
    if (!own) continue;
    const r = el.getBoundingClientRect(); if (r.width < 4 || r.height < 4) continue;
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || Number(cs.opacity) === 0) continue;
    const band = bands.find(([, a, b]) => r.top < b && r.bottom > a);
    if (band) topHits.push({band: band[0], el: desc(el), text: own.slice(0, 60), rect: r2(r), opacity: cs.opacity, position: cs.position});
    if (topHits.length > 40) break;
  }
  // Geometry of every ancestor of each visible iframe (which layer decides where a surface sits).
  const chains = [...D.querySelectorAll('iframe')].filter((f) => { const r = f.getBoundingClientRect(); return r.width > 2 && r.height > 2; }).map((f) => {
    const out = [];
    for (let el = f; el && el !== D.documentElement; el = el.parentElement) {
      const cs = getComputedStyle(el);
      out.push({el: desc(el), rect: r2(el.getBoundingClientRect()), position: cs.position, top: cs.top, bottom: cs.bottom, height: cs.height,
                padding: cs.padding, transform: cs.transform === 'none' ? '' : cs.transform, visibility: cs.visibility, opacity: cs.opacity});
      if (out.length > 8) break;
    }
    return {title: f.title || '', chain: out};
  });
  return {viewport: {w: window.innerWidth, h: vh}, header, gamebar, footer, frames, topHits, chains};
}
"""


def nav(page, target, section=""):
    page.evaluate("([t, s]) => window.postMessage({type: 'GSF_SHELL_NAV', target: t, section: s}, window.location.origin)",
                  [target, section])
    page.wait_for_timeout(3000)


def main():
    with sync_playwright() as p:
        browser = p.webkit.launch()
        ctx = browser.new_context(**p.devices["iPhone 13"])
        page = ctx.new_page()
        errors = []
        page.on("pageerror", lambda e: errors.append({"message": str(e)[:300], "stack": (getattr(e, "stack", "") or "")[:1500]}))
        page.goto(BASE + "/", wait_until="domcontentloaded")
        page.wait_for_selector("button[data-page='hub']", timeout=120_000)
        page.wait_for_timeout(6000)
        summary = {}
        for name, target, section in (("home", None, ""), ("hub", "hub", "dashboard"), ("editor", "editor", ""),
                                      ("ai", "ai", ""), ("home-again", "home", "")):
            if target:
                nav(page, target, section)
            data = page.evaluate(DUMP)
            (OUT / f"layout-{name}.json").write_text(json.dumps(data, indent=1), encoding="utf-8")
            page.screenshot(path=str(OUT / f"layout-{name}.png"))
            summary[name] = {"gamebar": data["gamebar"], "frames": [(f["rect"], len(f["hits"])) for f in data["frames"]],
                             "topHits": len(data["topHits"])}
        (OUT / "page-errors.json").write_text(json.dumps(errors, indent=1), encoding="utf-8")
        summary["page_errors"] = len(errors)
        browser.close()
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
