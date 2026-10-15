#!/bin/sh
# Kept for the Dockerfile CMD and older references: there is exactly one
# startup path, and it never transforms the UI.
exec /bin/sh /app/web/start_web.sh
