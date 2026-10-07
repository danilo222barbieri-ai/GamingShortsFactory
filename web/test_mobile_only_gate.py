#!/usr/bin/env python3
from pathlib import Path
import re
import sys


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    raise SystemExit(1)


def ok(message: str) -> None:
    print(f"[ OK ] {message}")


def require(name: str, condition: bool) -> None:
    if not condition:
        fail(name)
    ok(name)


def block(text: str, marker: str) -> str:
    start = text.find(marker)
    if start < 0:
        fail(f"missing nginx block marker: {marker}")
    brace = text.find("{", start)
    if brace < 0:
        fail(f"missing opening brace after: {marker}")
    depth = 0
    for index in range(brace, len(text)):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    fail(f"unterminated nginx block: {marker}")
    return ""


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: test_mobile_only_gate.py NGINX_CONF GATE_HTML")

    nginx_path = Path(sys.argv[1])
    gate_path = Path(sys.argv[2])
    require("nginx template exists", nginx_path.exists())
    require("mobile-only gate page exists", gate_path.exists())

    nginx = nginx_path.read_text(encoding="utf-8")
    gate = gate_path.read_text(encoding="utf-8")
    gate_lower = gate.lower()

    require("desktop gate copy", "GSF è disponibile da smartphone" in gate)
    require("gate identifies GSF", "GSF" in gate)
    require("gate has no desktop-version escape", "versione desktop" not in gate_lower and "desktop-preview" not in gate_lower and "desktop-home" not in gate_lower)
    require("gate has no operational navigation", "href=\"/ai-v221" not in gate and "href=\"/editor-live" not in gate and "href=\"/creator-hub" not in gate and "href=\"/share-v156" not in gate)

    require("client hints mobile map", "$http_sec_ch_ua_mobile" in nginx and "$gsf_ch_mobile" in nginx)
    require("user-agent mobile map", "$http_user_agent" in nginx and "$gsf_ua_mobile" in nginx)
    require("combined mobile client map", "$gsf_mobile_client" in nginx)
    for token in ("iphone", "ipad", "android", "mobile", "tablet"):
        require(f"mobile classifier contains {token}", token in nginx.lower())

    require("internal gate location", "mobile_only_gate.html" in nginx and "internal;" in nginx)
    require("desktop gate status route", "@gsf_mobile_gate" in nginx or "/__gsf_mobile_gate" in nginx)

    desktop_preview = block(nginx, "location = /desktop-preview")
    desktop_home = block(nginx, "location = /desktop-home")
    require("desktop preview redirects to root", "return 302 /;" in desktop_preview or "return 301 /;" in desktop_preview)
    require("desktop home redirects to root", "return 302 /;" in desktop_home or "return 301 /;" in desktop_home)
    require("desktop preview alias removed", "alias" not in desktop_preview)
    require("desktop home alias removed", "alias" not in desktop_home)

    for marker in (
        "location = / {",
        "location /ai-v221/ {",
        "location /editor-live/ {",
        "location /creator-hub-v156/ {",
        "location /share-v156/ {",
    ):
        section = block(nginx, marker)
        require(f"desktop gate applied: {marker}", "$gsf_mobile_client" in section and ("return 424" in section or "return 425" in section))

    root = block(nginx, "location = / {")
    callback_positions = [
        root.find('if ($arg_state ~ "^gsfsc_")'),
        root.find('if ($arg_state ~ "^gsfyt_")'),
        root.find('if ($arg_state ~ "^gsfig_")'),
        root.find('if ($arg_state ~ "^gsfacg_")'),
        root.find('if ($arg_state ~ "^gsfacf_")'),
        root.find('if ($arg_state ~ "^gsfact_")'),
    ]
    gate_position = root.find("$gsf_mobile_client")
    require("all OAuth callbacks remain in root", all(position >= 0 for position in callback_positions))
    require("OAuth callbacks evaluated before desktop gate", gate_position >= 0 and max(callback_positions) < gate_position)

    require("gate disables caching", "no-store" in block(nginx, "location = /__gsf_mobile_gate") if "location = /__gsf_mobile_gate" in nginx else "no-store" in nginx)

    print("\nGSF MOBILE-ONLY GATE CONTRACT: PASS")


if __name__ == "__main__":
    main()
