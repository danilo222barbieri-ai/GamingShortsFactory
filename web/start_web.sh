#!/bin/sh
set -eu
export PORT="${PORT:-8080}"

rm -f /etc/nginx/sites-enabled/default /etc/nginx/conf.d/default.conf
envsubst '${PORT}' < /app/web/nginx.conf.template > /etc/nginx/conf.d/default.conf
nginx

exec python -m streamlit run /app/web/demo_app.py \
  --server.address=127.0.0.1 --server.port=8501 \
  --server.maxUploadSize=4096 --server.maxMessageSize=4096 --server.headless=true
