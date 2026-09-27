FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    GSF_WEB_MODE=1 \
    GSF_MEDIA_BIND=0.0.0.0 \
    GSF_MEDIA_PORT=8765 \
    GSF_MEDIA_BASE_URL=/media \
    GSF_RUNTIME_ROOT=/tmp/gsf-runtime \
    GSF_SESSION_TTL_SECONDS=7200

RUN apt-get update && apt-get install -y --no-install-recommends \
      ffmpeg nginx gettext-base ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements-web.txt /app/requirements-web.txt
RUN python -m pip install --upgrade pip && \
    python -m pip install -r /app/requirements-web.txt

# The application source is stored as a compressed text payload so the
# repository can be maintained through browser/connector uploads.
COPY src_payload /app/src_payload
RUN python -c "import base64,gzip,pathlib; p=pathlib.Path('/app/src_payload'); s=''.join(x.read_text() for x in sorted(p.glob('gsf_v77.py.gz.b64.part*'))); pathlib.Path('/app/GamingShortsFactory_V77_WEB_READY.py').write_bytes(gzip.decompress(base64.b64decode(s)))"

COPY .streamlit /app/.streamlit
COPY web /app/web

RUN chmod +x /app/web/start_web.sh && mkdir -p /tmp/gsf-runtime

EXPOSE 8080
CMD ["/app/web/start_web.sh"]
