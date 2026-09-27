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
    python -c "from faster_whisper import WhisperModel; WhisperModel('tiny', device='cpu', compute_type='int8'); print('GSF V92 Whisper Tiny ready')"

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
    python /app/web/apply_v85_upload_cleanup.py && \
    python /app/web/apply_v86_single_upload_circle.py && \
    python /app/web/test_v86_uploader_patch.py /app/GamingShortsFactory_V86_SINGLE_UPLOAD_CIRCLE.py && \
    python /app/web/apply_v87_upload_persist.py && \
    python /app/web/test_v87_upload_persist.py /app/GamingShortsFactory_V87_UPLOAD_PERSISTS.py && \
    python /app/web/apply_v88_persistent_loaded_circle.py && \
    python /app/web/test_v88_persistent_loaded_circle.py /app/GamingShortsFactory_V88_PERSISTENT_LOADED_CIRCLE.py && \
    python /app/web/apply_v89_decoupled_upload_visual.py && \
    python /app/web/test_v89_decoupled_upload_visual.py /app/GamingShortsFactory_V89_DECOUPLED_UPLOAD_VISUAL.py && \
    python /app/web/apply_v90_upload_visual_fix.py && \
    python /app/web/test_v90_upload_visual_fix.py /app/GamingShortsFactory_V90_UPLOAD_VISUAL_FIX.py && \
    python /app/web/apply_v91_roadmap_polish.py && \
    python /app/web/test_v91_roadmap_polish.py /app/GamingShortsFactory_V91_ROADMAP_POLISH.py && \
    python /app/web/apply_v92_ai_reaction_quality.py && \
    python /app/web/test_v92_ai_reaction_quality.py /app/GamingShortsFactory_V92_AI_REACTION_QUALITY.py && \
    python -m py_compile /app/GamingShortsFactory_V92_AI_REACTION_QUALITY.py

COPY .streamlit /app/.streamlit

RUN PORT=8080 envsubst '${PORT}' < /app/web/nginx.conf.template > /tmp/gsf-nginx-test.conf && \
    cp /tmp/gsf-nginx-test.conf /etc/nginx/conf.d/default.conf && \
    nginx -t

RUN chmod +x /app/web/start_web.sh && mkdir -p /tmp/gsf-runtime

EXPOSE 8080
CMD ["/app/web/start_web.sh"]
