FROM public.ecr.aws/docker/library/python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    GSF_WEB_MODE=1 \
    GSF_LOW_MEMORY_WEB=1 \
    GSF_AI_VOICE_TRANSCRIPTION=0 \
    GSF_MEDIA_BIND=0.0.0.0 \
    GSF_MEDIA_PORT=8765 \
    GSF_MEDIA_BASE_URL=/media \
    GSF_RUNTIME_ROOT=/tmp/gsf-runtime \
    GSF_SESSION_TTL_SECONDS=21600 \
    HF_HOME=/app/.cache/huggingface \
    OMP_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    MKL_NUM_THREADS=1

RUN apt-get update && apt-get install -y --no-install-recommends \
      ffmpeg nginx gettext-base ca-certificates tesseract-ocr tesseract-ocr-eng tesseract-ocr-ita zbar-tools \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements-web.txt /app/requirements-web.txt
COPY constraints-web.txt /app/constraints-web.txt
RUN python -m pip install --upgrade pip && python -m pip install -r /app/requirements-web.txt -c /app/constraints-web.txt
RUN mkdir -p /app/.cache/huggingface && python -c "from faster_whisper import WhisperModel; WhisperModel('tiny', device='cpu', compute_type='int8')"

# ---------------------------------------------------------------------------
# GSF CANONICAL UI PIPELINE
# The repository files ARE the runtime UI. Everything below copies them 1:1.
# No legacy payload, no fix_/apply_ migration chain, no materialization and no
# startup transform may modify a canonical file (enforced by
# tools/gsf_ui_manifest.py and tests/test_canonical_ui_pipeline.py).
# Historical patch scripts stay in web/ for the record but are never executed.
# ---------------------------------------------------------------------------
COPY gsf_alive.py gsf_alive_notifications.py gsf_editor_v403.py gsf_project_state.py /app/
COPY gsf_core /app/gsf_core
COPY web /app/web
COPY web/gsf_perf.py /app/gsf_perf.py
COPY app.py /app/app.py
COPY .streamlit /app/.streamlit
COPY tools/gsf_ui_manifest.py /app/gsf_ui_manifest.py
COPY web/ffmpeg_lowmem.py /usr/local/bin/ffmpeg
RUN python -c "import base64,pathlib,struct; from PIL import Image; p=pathlib.Path('/app/web/app_icons'); src=p/'app-icon.png'; raw=src.read_bytes(); assert raw[:8]==b'\\x89PNG\\r\\n\\x1a\\n'; assert struct.unpack('>II',raw[16:24])==(180,180); (p/'apple-touch-icon.png').write_bytes(raw); (p/'official_logo_180.valid.b64').write_text(base64.b64encode(raw).decode('ascii')); im=Image.open(src); im.load(); im.resize((192,192), Image.Resampling.LANCZOS).save(p/'app-icon-192.png', format='PNG'); im.resize((512,512), Image.Resampling.LANCZOS).save(p/'app-icon-512.png', format='PNG'); assert Image.open(p/'app-icon-192.png').size==(192,192); assert Image.open(p/'app-icon-512.png').size==(512,512); print('GSF production/PWA icons: PASS')"

# Single explicit third-party bridge: Streamlit's own static index.html is not a
# repository file, so the top-level browser bridge (navigation lifecycle + AdSense)
# is installed into the Streamlit package here, exactly once and idempotently.
RUN python /app/web/install_adsense_bridge.py && \
    python -c "import pathlib,streamlit; s=(pathlib.Path(streamlit.__file__).parent/'static'/'index.html').read_text(); assert s.count('id=\"gsf-adsense-bridge\"')==1; print('GSF Streamlit bridge: PASS')"

# Compatibility alias for read-only contracts that still name the old entry file.
RUN ln -s /app/app.py /app/GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py && \
    chmod +x /usr/local/bin/ffmpeg /app/web/start_web.sh /app/web/start_web_fast.sh && \
    mkdir -p /tmp/gsf-runtime

# Byte-compile for fast cold starts (__pycache__ is outside the manifest).
RUN python -m compileall -q /app/app.py /app/web /app/gsf_core

# Record the manifest of what will be served, then prove the image equals it.
# The generated public icons must remain readable by nginx regardless of
# the permissions of the source image in the checkout.
RUN chmod 755 /app/web/app_icons && chmod 644 /app/web/app_icons/*.png && \
    python /app/gsf_ui_manifest.py write && python /app/gsf_ui_manifest.py verify

# Read-only contracts on the final canonical files (they must never write).
RUN python -m py_compile /app/app.py /app/web/direct_upload_server.py /app/web/contact_server.py && \
    python /app/web/test_v410_security_hardening.py /app && \
    python /app/gsf_ui_manifest.py verify

RUN PORT=8080 envsubst '${PORT}' < /app/web/nginx.conf.template > /tmp/gsf-nginx-test.conf && cp /tmp/gsf-nginx-test.conf /etc/nginx/conf.d/default.conf && nginx -t
EXPOSE 8080
CMD ["/app/web/start_web.sh"]
