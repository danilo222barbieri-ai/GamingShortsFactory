#!/usr/bin/env python3
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

GSF_UI_RELEASE = "308"


def versioned_path(path: str) -> str:
    """Return *path* with one authoritative UI release query parameter."""
    raw = str(path or "")
    parts = urlsplit(raw)
    query = [(key, value) for key, value in parse_qsl(parts.query, keep_blank_values=True) if key != "v"]
    query.append(("v", GSF_UI_RELEASE))
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))
