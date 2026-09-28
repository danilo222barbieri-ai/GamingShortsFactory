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
RUN python -m pip install --upgrade pip && python -m pip install -r /app/requirements-web.txt
RUN mkdir -p /app/.cache/huggingface && python -c "from faster_whisper import WhisperModel; WhisperModel('tiny', device='cpu', compute_type='int8')"
COPY src_payload /app/src_payload
COPY web /app/web
COPY Dockerfile.worker /app/Dockerfile.worker
COPY requirements-worker.txt /app/requirements-worker.txt
RUN python /app/web/test_v105_upload_hardening.py /app/web/direct_upload_server.py
RUN python /app/web/test_v105_worker_core.py /app/web/ai_worker_server.py /app
RUN python /app/web/test_v105_render_bridge.py /app
COPY web/ffmpeg_lowmem.py /usr/local/bin/ffmpeg
RUN chmod +x /usr/local/bin/ffmpeg && python -c "import base64,gzip,pathlib; p=pathlib.Path('/app/src_payload'); s=''.join(x.read_text() for x in sorted(p.glob('gsf_v77.py.gz.b64.part*'))); pathlib.Path('/app/GamingShortsFactory_V77_WEB_READY.py').write_bytes(gzip.decompress(base64.b64decode(s)))" && \
    python /app/web/apply_v78_mobile_patch.py && python /app/web/apply_v79_session_social_patch.py && python /app/web/apply_v80_ui_auto_sub_patch.py && python /app/web/apply_v80_1_hotfix.py && python /app/web/apply_v80_2_render_hotfix.py && python /app/web/apply_v81_mobile_tablet_patch.py && python /app/web/apply_v82_fixpack.py && python /app/web/apply_v83_upload_fix.py && python /app/web/apply_v84_mobile_media_upload_fix.py && python /app/web/apply_v85_upload_cleanup.py && python /app/web/apply_v86_single_upload_circle.py && python /app/web/apply_v87_upload_persist.py && python /app/web/apply_v88_persistent_loaded_circle.py && python /app/web/apply_v89_decoupled_upload_visual.py && python /app/web/apply_v90_upload_visual_fix.py && python /app/web/apply_v91_roadmap_polish.py && python /app/web/apply_v92_ai_reaction_quality.py && python /app/web/apply_v93_deep_stability.py && python /app/web/apply_v94_short_quality.py && python /app/web/apply_v95_render_text_polish.py && python /app/web/apply_v98_editor_polish.py && python /app/web/apply_v98_1_editor_hotfix.py && python /app/web/apply_v98_2_upload_recovery.py && python /app/web/apply_v98_3_home_compact.py && python /app/web/apply_v98_4_editor_cleanup.py && python /app/web/apply_v98_5_style_only.py && python /app/web/apply_v98_6_player_sizes.py && python /app/web/apply_v98_7_new_video_fix.py && python /app/web/apply_v98_8_upload_memory_fix.py && python /app/web/apply_v98_9_direct_upload.py && python /app/web/apply_v98_10_speed_pass1.py && python /app/web/apply_v98_11_speed_all.py && python /app/web/apply_v98_12_upload_64mb.py && python /app/web/apply_v98_final.py && python /app/web/apply_v98_final_6lanes.py && python /app/web/apply_v99_ai_turbo.py && python /app/web/apply_v99_final_arch.py && python /app/web/extract_ai_scan_core.py /app/GamingShortsFactory_V99_FINAL_ARCH.py /app/web/generated_ai_scan_core.py && python /app/web/apply_v100_smart_reframe.py && python /app/web/apply_v100_1_quality_mobile.py && python /app/web/apply_v100_2_master_quality.py && python /app/web/apply_v100_3_native_crop_hq.py && python /app/web/apply_v100_4_render_stable.py && python /app/web/apply_v100_5_max_upload.py && python /app/web/apply_v100_6_fps_guard.py && python /app/web/apply_v100_7_memory_safe_render.py && python /app/web/apply_v100_8_fast_render.py && python /app/web/apply_v101_subtitle_refinement.py && python /app/web/apply_v102_smart_hook.py && python /app/web/apply_v103_final_quality.py && python /app/web/apply_v103_1_clean_hook_pixfmt.py && python /app/web/apply_v103_2_canonical_format.py && python /app/web/apply_v104_direct_social.py && \
    python /app/web/apply_v104_2_legal_footer.py && python /app/web/apply_v104_3_memory_safe_render.py && python /app/web/apply_v104_4_shared_social_token.py && python /app/web/apply_v104_5_youtube_social_connect.py && python /app/web/apply_v104_6_stable_social_flow.py && python /app/web/apply_v104_7_instagram_login.py && python /app/web/apply_v105_render_offload.py && python /app/web/inspect_v105_social_current.py /app/GamingShortsFactory_V105_HARDENED.py && python /app/web/test_v105_social_streaming.py /app/GamingShortsFactory_V105_HARDENED.py && python /app/web/test_v104_3_memory_safe_render.py /app/GamingShortsFactory_V105_HARDENED.py && python /app/web/test_v104_4_social_connect.py /app/GamingShortsFactory_V105_HARDENED.py /app/web/nginx.conf.template /app/web/direct_upload_server.py && python /app/web/test_v104_5_youtube_connect.py /app/GamingShortsFactory_V105_HARDENED.py /app/web/nginx.conf.template /app/web/direct_upload_server.py && python /app/web/test_v104_6_stable_social_flow.py /app/GamingShortsFactory_V105_HARDENED.py /app/web/nginx.conf.template /app/web/direct_upload_server.py && python /app/web/test_v104_7_instagram_login.py /app/GamingShortsFactory_V105_HARDENED.py /app/web/direct_upload_server.py && python /app/web/test_v105_render_offload.py /app/GamingShortsFactory_V105_HARDENED.py && python /app/web/test_v104_2_legal_pages.py /app/web/nginx.conf.template && python /app/web/test_tiktok_site_verification.py /app/web/nginx.conf.template && python -m py_compile /app/GamingShortsFactory_V105_HARDENED.py /app/web/generated_ai_scan_core.py /app/web/ai_worker_server.py
COPY .streamlit /app/.streamlit
RUN PORT=8080 envsubst '${PORT}' < /app/web/nginx.conf.template > /tmp/gsf-nginx-test.conf && cp /tmp/gsf-nginx-test.conf /etc/nginx/conf.d/default.conf && nginx -t
RUN chmod +x /app/web/start_web.sh && mkdir -p /tmp/gsf-runtime
EXPOSE 8080
CMD ["/app/web/start_web.sh"]
