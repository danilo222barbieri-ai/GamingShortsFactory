#!/bin/sh
set -eu
# Compatibility alias. Security and UI are baked into the V404 image.
exec sh /app/web/start_web_fast.sh
