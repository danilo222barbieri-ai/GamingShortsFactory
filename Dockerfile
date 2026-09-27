FROM python:3.12-slim

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
      ffmpeg nginx gettext-base ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements-web.txt /app/requirements-web.txt
RUN python -m pip install --upgrade pip && \
    python -m pip install -r /app/requirements-web.txt

RUN mkdir -p /app/.cache/huggingface && \
    python -c "from faster_whisper import WhisperModel; WhisperModel('tiny', device='cpu', compute_type='int8'); print('GSF V84 Whisper Tiny ready')"

COPY src_payload /app/src_payload
COPY web /app/web
COPY web/ffmpeg_lowmem.py /usr/local/bin/ffmpeg
RUN chmod +x /usr/local/bin/ffmpeg && \
    python -c "import base64,gzip,pathlib; p=pathlib.Path('/app/src_payload'); s=''.join(x.read_text() for x in sorted(p.glob('gsf_v77.py.gz.b64.part*'))); pathlib.Path('/app/GamingShortsFactory_V77_WEB_READY.py').write_bytes(gzip.decompress(base64.b64decode(s)))" && \
    python /app/web/apply_v78_mobile_patch.py && \
    python /app/web/apply_v79_session_social_patch.py && \
    python /app/web/apply_v80_ui_auto_sub_patch.py && \
    python /app/web/apply_v80_1_hotfix.py && \
    python /app/web/apply_v80_2_render_hotfix.py && \
    python /app/web/apply_v81_mobile_tablet_patch.py && \
    python /app/web/apply_v82_fixpack.py && \
    python /app/web/apply_v83_upload_fix.py && \
    python /app/web/apply_v84_mobile_media_upload_fix.py && \
    python -m py_compile /app/GamingShortsFactory_V84_MOBILE_MEDIA_FIX.py

COPY .streamlit /app/.streamlit

RUN PORT=8080 envsubst '${PORT}' < /app/web/nginx.conf.template > /tmp/gsf-nginx-test.conf && \
    cp /tmp/gsf-nginx-test.conf /etc/nginx/conf.d/default.conf && \
    nginx -t

RUN chmod +x /app/web/start_web.sh && mkdir -p /tmp/gsf-runtime

EXPOSE 8080
CMD ["/app/web/start_web.sh"]
