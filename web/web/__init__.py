"""Compatibility package for modules executed with /app/web as sys.path root.

The upload and contact servers run as scripts from /app/web, so ``import web``
resolves to this inner package there while Streamlit resolves the canonical
outer one. Both must expose every canonical helper: without the outer directory
on ``__path__`` a lazy ``from web.<helper> import ...`` raises ModuleNotFoundError
at request time only, even though the file is present in the image.
"""
from pathlib import Path

__path__.append(str(Path(__file__).resolve().parents[1]))
