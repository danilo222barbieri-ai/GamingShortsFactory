"""V412 — GSF brand tokens, app-wide.

Final build-time pass, run after every other UI patch has materialized the
app. It aligns every screen with the official kit in design/brand/:

* colors   -> the 12 official tokens (third-party brand colors are kept)
* font     -> the canonical GSF stack (monospace stays monospace)
* radius   -> the kit scale 13 / 18 / 28 / 999 px
* spacing  -> one 4 px based scale for padding / margin / gap

Only CSS is touched: <style> blocks and style="..." attributes in HTML and in
the Python sources that emit HTML. Python logic (render/subtitle colors, video
pipeline) is never rewritten.

Usage: python fix_v412_brand_tokens.py [app_root]        (default /app)
       python fix_v412_brand_tokens.py --report FILE...  (dry run, prints map)
"""
from __future__ import annotations

import colorsys
import json
import re
import sys
from pathlib import Path

MARKER = "GSF_BRAND_TOKENS_V412"

# --- Official tokens (design/brand/gsf-brand-tokens.json) -------------------
TOKENS = {
    "primary": "#27AEF3",
    "primary-light": "#79D2FF",
    "cyan": "#53E0EA",
    "ai": "#9D82FF",
    "short": "#5ED6A0",
    "warning": "#FFD84D",
    "danger": "#FF6673",
    "bg-soft": "#EEF9FF",
    "surface": "#FFFFFF",
    "line": "#D9EFFB",
    "ink": "#10283D",
    "muted": "#6D8497",
}
FONT_STACK = '"Avenir Next","SF Pro Display","SF Pro Text",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif'
RADIUS_SCALE = (13, 18, 28)
SPACE_SCALE = (2, 4, 8, 12, 16, 20, 24, 32, 40, 48)

# Third-party brand colors: logos/buttons of social platforms keep their color.
PROTECTED = {
    "#1877F2",  # Facebook
    "#FF0000", "#FF0033", "#CC0000",  # YouTube
    "#9146FF",  # Twitch
    "#25F4EE", "#FE2C55", "#010101",  # TikTok
    "#E1306C", "#C13584", "#833AB4", "#F56040", "#F77737", "#FCAF45", "#FFDC80", "#405DE6", "#5851DB", "#FD1D1D",  # Instagram
    "#5865F2",  # Discord
    "#1DA1F2",  # Twitter/X legacy
    "#4285F4", "#34A853", "#FBBC05", "#EA4335",  # Google
}

TOKEN_HEX = {v.upper() for v in TOKENS.values()}


def _rgb(hexv: str) -> tuple[int, int, int]:
    h = hexv.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def classify(r: int, g: int, b: int) -> str | None:
    """Return the token role for an RGB color, or None to keep it."""
    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    hue = h * 360
    # Pure neutrals at the extremes: blacks (video backdrops, shadows) stay.
    if l < 0.06:
        return None
    if l >= 0.975:
        return "surface"
    if s < 0.12 and l > 0.9:
        return "surface"
    # Pastel tints of a status/product hue (badge and chip backgrounds) become
    # that token at low opacity, so the meaning of the color survives.
    if l >= 0.82 and s >= 0.35 and not (185 <= hue <= 235):
        return "tint:" + _hue_role(hue) + (":0.14" if l >= 0.92 else ":0.24")
    # Light blue/neutral tints: backgrounds and borders.
    if l >= 0.935:
        return "bg-soft"
    if l >= 0.84:
        return "line"
    # Dark text tones, including dark status colors (light kit hues are not
    # readable as text on white, so text falls back to ink).
    if l < 0.30:
        return "ink"
    if l < 0.42 and not (185 <= hue <= 300 and s >= 0.55):
        return "ink"
    # Desaturated mid tones: secondary text.
    if s < 0.32:
        return "muted"
    role = _hue_role(hue)
    if role == "primary" and l >= 0.68:
        return "primary-light"
    return role


def _hue_role(hue: float) -> str:
    if hue < 18 or hue >= 330:
        return "danger"
    if hue < 65:
        return "warning"
    if hue < 165:
        return "short"
    if hue < 188:
        return "cyan"
    if hue < 245:
        return "primary"
    return "ai"


def map_hex(hexv: str) -> str | None:
    up = hexv.upper()
    if len(up) == 4:
        up = "#" + "".join(c * 2 for c in up[1:])
    if up in TOKEN_HEX or up in PROTECTED:
        return None
    role = classify(*_rgb(up))
    if role is None:
        return None
    if role.startswith("tint:"):
        _, base, alpha = role.split(":")
        r, g, b = _rgb(TOKENS[base])
        return f"rgba({r},{g},{b},{alpha})"
    return TOKENS[role]


# --- CSS rewriting ----------------------------------------------------------
HEX_RE = re.compile(r"#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})(?![0-9a-zA-Z_-])")
RGBA_RE = re.compile(r"rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*(,\s*[0-9.]+%?\s*)?\)")
FONT_RE = re.compile(r"(font-family\s*:\s*)([^;}\"]+?)(\s*(?:!important)?\s*[;}\"])", re.I)
FONT_SHORTHAND_RE = re.compile(r"(\bfont\s*:[^;}\"]*?\d(?:px|rem|em|%)(?:\s*/\s*[0-9.]+(?:px|rem|em|%)?)?\s+)([^;}\"]+?)(\s*(?:!important)?\s*[;}\"])", re.I)
RADIUS_RE = re.compile(r"((?:border(?:-[a-z]+)*-radius)\s*:\s*)([^;}\"]+)", re.I)
SPACE_RE = re.compile(r"((?<![a-z-])(?:padding|margin|gap|row-gap|column-gap)(?:-(?:top|right|bottom|left|inline|block)(?:-(?:start|end))?)?\s*:\s*)([^;}\"]+)", re.I)
RULE_RE = re.compile(r"([^{}]+)\{([^{}]*)\}")
# Selectors that preview what ends up burned into the video (subtitles,
# karaoke highlight): those colors must match the renderer, not the UI kit.
PREVIEW_SELECTOR_RE = re.compile(r"caption|subtitle|hotword|karaoke", re.I)
PX_RE = re.compile(r"(-?)(\d+(?:\.\d+)?)px")


def _snap(v: float, scale) -> float:
    return min(scale, key=lambda s: (abs(s - v), -s))


def _snap_radius(value: str) -> str:
    def rep(m):
        sign, num = m.group(1), float(m.group(2))
        if num <= 8:
            return m.group(0)  # small inner details keep their radius
        if num >= 60:
            return f"{sign}999px"
        return f"{sign}{_snap(num, RADIUS_SCALE)}px"
    return PX_RE.sub(rep, value)


def _snap_space(value: str) -> str:
    def rep(m):
        sign, num = m.group(1), float(m.group(2))
        if num <= 2 or num > 48:
            return m.group(0)  # hairlines and layout offsets keep their value
        return f"{sign}{_snap(num, SPACE_SCALE)}px"
    return PX_RE.sub(rep, value)


def _font_value(value: str) -> str:
    low = value.lower()
    if "var(--gsf-font" in low or "monospace" in low or "mono" in low or "inherit" in low or "material" in low or "icon" in low:
        return value
    return FONT_STACK


def rewrite_css(css: str, stats: dict) -> str:
    def hex_rep(m):
        new = map_hex(m.group(0))
        if new is None:
            return m.group(0)
        stats["colors"] = stats.get("colors", 0) + 1
        return new

    def rgba_rep(m):
        r, g, b = (int(m.group(i)) for i in (1, 2, 3))
        if max(r, g, b) > 255:
            return m.group(0)
        hexv = "#%02X%02X%02X" % (r, g, b)
        new = map_hex(hexv)
        if new is None:
            return m.group(0)
        stats["colors"] = stats.get("colors", 0) + 1
        alpha = m.group(4)
        if new.startswith("rgba("):
            if not alpha or "%" in alpha:
                return new
            nr, ng, nb, na = new[5:-1].split(",")
            a = float(na) * float(alpha.strip(" ,"))
            return f"rgba({nr},{ng},{nb},{a:.3g})"
        nr, ng, nb = _rgb(new)
        if alpha:
            return f"rgba({nr},{ng},{nb}{alpha.replace(' ', '')})"
        return f"rgb({nr},{ng},{nb})"

    def font_rep(m):
        new = _font_value(m.group(2))
        if new != m.group(2):
            stats["fonts"] = stats.get("fonts", 0) + 1
        return m.group(1) + new + m.group(3)

    def radius_rep(m):
        new = _snap_radius(m.group(2))
        if new != m.group(2):
            stats["radius"] = stats.get("radius", 0) + 1
        return m.group(1) + new

    def space_rep(m):
        new = _snap_space(m.group(2))
        if new != m.group(2):
            stats["spacing"] = stats.get("spacing", 0) + 1
        return m.group(1) + new

    def decls(text: str) -> str:
        text = HEX_RE.sub(hex_rep, text)
        text = RGBA_RE.sub(rgba_rep, text)
        text = FONT_RE.sub(font_rep, text)
        text = FONT_SHORTHAND_RE.sub(font_rep, text)
        text = RADIUS_RE.sub(radius_rep, text)
        text = SPACE_RE.sub(space_rep, text)
        return text

    if "{" not in css:  # a style="..." attribute: declarations only
        return decls(css)

    if "{{" in css:
        # CSS inside a Python f-string/str.format: braces are doubled and
        # single braces are placeholders. Work on a de-doubled view.
        masked = css.replace("{{", "\x01").replace("}}", "\x02")
        masked = re.sub(r"\{[^{}]*\}", lambda m: m.group(0).replace("{", "\x03").replace("}", "\x04"), masked)
        plain = masked.replace("\x01", "{").replace("\x02", "}")
        out = rewrite_css(plain, stats)
        out = out.replace("{", "{{").replace("}", "}}")
        return out.replace("\x03", "{").replace("\x04", "}")

    def rule(m):
        if PREVIEW_SELECTOR_RE.search(m.group(1)):
            return m.group(0)  # previews of rendered video keep the render colors
        return m.group(1) + "{" + decls(m.group(2)) + "}"

    return RULE_RE.sub(rule, css)


STYLE_BLOCK_RE = re.compile(r"(<style\b[^>]*>)(.*?)(</style>)", re.S | re.I)
STYLE_ATTR_RE = re.compile(r"(\bstyle\s*=\s*)(\"[^\"]*\"|'[^']*')", re.I)


def token_root_css() -> str:
    lines = ";".join(f"--gsf-{k}:{v}" for k, v in TOKENS.items())
    return (
        f"/* {MARKER} */:root{{{lines};--gsf-font:{FONT_STACK};"
        "--gsf-radius-sm:13px;--gsf-radius-md:18px;--gsf-radius-lg:28px;--gsf-radius-pill:999px;"
        "--gsf-space-1:4px;--gsf-space-2:8px;--gsf-space-3:12px;--gsf-space-4:16px;"
        "--gsf-space-5:24px;--gsf-space-6:32px;--gsf-space-7:48px}"
    )


def rewrite_document(text: str, stats: dict, inject: bool) -> str:
    """Rewrite CSS inside <style> blocks and style attributes."""
    def block(m):
        return m.group(1) + rewrite_css(m.group(2), stats) + m.group(3)

    def attr(m):
        q = m.group(2)
        return m.group(1) + q[0] + rewrite_css(q[1:-1], stats) + q[-1]

    out = STYLE_BLOCK_RE.sub(block, text)
    out = STYLE_ATTR_RE.sub(attr, out)
    if inject and MARKER not in out:
        tag = f"<style>{token_root_css()}</style>"
        if re.search(r"<head[^>]*>", out, re.I):
            out = re.sub(r"(<head[^>]*>)", lambda m: m.group(1) + tag, out, count=1, flags=re.I)
        else:
            out = tag + out
    return out


def targets(root: Path) -> tuple[list[Path], list[Path]]:
    """Return (html documents, python sources that emit HTML)."""
    web = root / "web"
    html = sorted(web.glob("*_component/**/*.html"))
    html += sorted((web / "legal").glob("*.html"))
    gate = web / "mobile_only_gate.html"
    if gate.exists():
        html.append(gate)
    py = sorted(root.glob("GamingShortsFactory_V*.py"))
    py += [p for p in (web / "contact_server.py", web / "direct_upload_server.py") if p.exists()]
    return html, py


def apply(root: Path) -> dict:
    html, py = targets(root)
    report: dict[str, dict] = {}
    for path in html + py:
        text = path.read_text(encoding="utf-8")
        stats: dict = {}
        new = rewrite_document(text, stats, inject=path.suffix == ".html")
        if new != text:
            path.write_text(new, encoding="utf-8")
        report[str(path.relative_to(root))] = stats
    # The Streamlit main page gets the token sheet and the global font once.
    for main in sorted(root.glob("GamingShortsFactory_V*.py")):
        text = main.read_text(encoding="utf-8")
        if MARKER in text:
            continue
        css = token_root_css() + (
            "html,body,.stApp,.stMarkdown,.stButton button,input,textarea,select,label,p,h1,h2,h3,h4,h5,h6"
            "{font-family:var(--gsf-font)}"
        )
        literal = repr(f"<style>{css}</style>")
        hook = f"\ntry:\n    st.markdown({literal}, unsafe_allow_html=True)\nexcept Exception:\n    pass\n"
        # Insert right after `st.set_page_config(...)` so it precedes all UI.
        m = re.search(r"^st\.set_page_config\(.*?\)\s*$", text, re.M | re.S)
        if m:
            text = text[: m.end()] + hook + text[m.end():]
            main.write_text(text, encoding="utf-8")
            report.setdefault(str(main.relative_to(root)), {})["token_sheet"] = 1
    # Native Streamlit widgets follow the theme in .streamlit/config.toml.
    cfg = root / ".streamlit" / "config.toml"
    if cfg.exists():
        theme = {
            "primaryColor": TOKENS["primary"],
            "backgroundColor": TOKENS["bg-soft"],
            "secondaryBackgroundColor": TOKENS["surface"],
            "textColor": TOKENS["ink"],
        }
        text = cfg.read_text(encoding="utf-8")
        new = text
        for key, value in theme.items():
            new, n = re.subn(rf'(?m)^{key}\s*=\s*"[^"]*"', f'{key} = "{value}"', new)
            if n == 0 and "[theme]" in new:
                new = new.replace("[theme]", f'[theme]\n{key} = "{value}"', 1)
        if new != text:
            cfg.write_text(new, encoding="utf-8")
            report.setdefault(".streamlit/config.toml", {})["theme"] = 1
    return report


def report_map(files: list[str]) -> None:
    seen: dict[str, int] = {}
    for f in files:
        text = Path(f).read_text(encoding="utf-8", errors="ignore")
        chunks = [m.group(2) for m in STYLE_BLOCK_RE.finditer(text)] + [m.group(2) for m in STYLE_ATTR_RE.finditer(text)]
        for c in chunks:
            for m in HEX_RE.finditer(c):
                k = m.group(0).upper()
                seen[k] = seen.get(k, 0) + 1
    rows = sorted(seen.items(), key=lambda kv: -kv[1])
    for hexv, n in rows:
        print(f"{n:5d}  {hexv:8s} -> {map_hex(hexv) or 'keep'}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--report":
        report_map(sys.argv[2:])
        sys.exit(0)
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "/app")
    result = apply(root)
    total = {}
    for stats in result.values():
        for k, v in stats.items():
            total[k] = total.get(k, 0) + v
    print("V412 brand tokens:", json.dumps(total))
    mains = sorted(root.glob("GamingShortsFactory_V*.py"))
    if not mains or not all(MARKER in m.read_text(encoding="utf-8") for m in mains):
        print("V412 fatal: Streamlit main page not found or set_page_config hook missing", file=sys.stderr)
        sys.exit(1)
