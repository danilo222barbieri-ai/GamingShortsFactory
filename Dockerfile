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
    python -c "from faster_whisper import WhisperModel; WhisperModel('tiny', device='cpu', compute_type='int8'); print('GSF V95 Whisper Tiny ready')"

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
    python /app/web/apply_v93_deep_stability.py && \
    python /app/web/test_v93_deep_stability.py /app/GamingShortsFactory_V93_DEEP_STABILITY.py && \
    python /app/web/apply_v94_short_quality.py && \
    python /app/web/test_v94_short_quality.py /app/GamingShortsFactory_V94_SHORT_QUALITY.py && \
    python /app/web/apply_v95_render_text_polish.py && \
    python /app/web/test_v95_render_text_polish.py /app/GamingShortsFactory_V95_RENDER_TEXT_POLISH.py && \
    python /app/web/test_v96_streamlit_compat.py && \
    python -m py_compile /app/GamingShortsFactory_V95_RENDER_TEXT_POLISH.py && \
    python /app/web/apply_v98_editor_polish.py && \
    python /app/web/test_v98_editor_polish.py /app/GamingShortsFactory_V98_EDITOR_POLISH.py && \
    python -m py_compile /app/GamingShortsFactory_V98_EDITOR_POLISH.py && \
    python /app/web/apply_v98_1_editor_hotfix.py && \
    python /app/web/test_v98_1_editor_hotfix.py /app/GamingShortsFactory_V98_1_EDITOR_HOTFIX.py && \
    python -m py_compile /app/GamingShortsFactory_V98_1_EDITOR_HOTFIX.py && \
    python /app/web/apply_v98_2_upload_recovery.py && \
    python /app/web/test_v98_2_upload_recovery.py /app/GamingShortsFactory_V98_2_UPLOAD_RECOVERY.py && \
    python -m py_compile /app/GamingShortsFactory_V98_2_UPLOAD_RECOVERY.py && \
    python /app/web/apply_v98_3_home_compact.py && \
    python /app/web/test_v98_3_home_compact.py /app/GamingShortsFactory_V98_3_HOME_COMPACT.py && \
    python -m py_compile /app/GamingShortsFactory_V98_3_HOME_COMPACT.py && \
    python /app/web/apply_v98_4_editor_cleanup.py && \
    python /app/web/test_v98_4_editor_cleanup.py /app/GamingShortsFactory_V98_4_EDITOR_CLEANUP.py && \
    python -m py_compile /app/GamingShortsFactory_V98_4_EDITOR_CLEANUP.py && \
    python /app/web/apply_v98_5_style_only.py && \
    python /app/web/test_v98_5_style_only.py /app/GamingShortsFactory_V98_5_STYLE_ONLY.py && \
    python -m py_compile /app/GamingShortsFactory_V98_5_STYLE_ONLY.py && \
    python /app/web/apply_v98_6_player_sizes.py && \
    python /app/web/test_v98_6_player_sizes.py /app/GamingShortsFactory_V98_6_PLAYER_SIZES.py && \
    python -m py_compile /app/GamingShortsFactory_V98_6_PLAYER_SIZES.py && \
    python /app/web/apply_v98_7_new_video_fix.py && \
    python /app/web/test_v98_7_new_video_fix.py /app/GamingShortsFactory_V98_7_NEW_VIDEO_FIX.py && \
    python -m py_compile /app/GamingShortsFactory_V98_7_NEW_VIDEO_FIX.py && \
    python /app/web/apply_v98_8_upload_memory_fix.py && \
    python /app/web/test_v98_8_upload_memory_fix.py /app/GamingShortsFactory_V98_8_UPLOAD_MEMORY_FIX.py && \
    python -m py_compile /app/GamingShortsFactory_V98_8_UPLOAD_MEMORY_FIX.py && \
    python /app/web/apply_v98_9_direct_upload.py && \
    python /app/web/test_v98_9_direct_upload.py /app/GamingShortsFactory_V98_9_DIRECT_UPLOAD.py && \
    python -m py_compile /app/GamingShortsFactory_V98_9_DIRECT_UPLOAD.py && \
    python /app/web/apply_v98_10_speed_pass1.py && \
    python /app/web/test_v98_10_speed_pass1.py /app/GamingShortsFactory_V98_10_SPEED_PASS1.py && \
    python -m py_compile /app/GamingShortsFactory_V98_10_SPEED_PASS1.py && \
    python /app/web/apply_v98_11_speed_all.py && \
    python /app/web/test_v98_11_speed_all.py /app/GamingShortsFactory_V98_11_SPEED_ALL.py && \
    python -m py_compile /app/GamingShortsFactory_V98_11_SPEED_ALL.py && \
    python /app/web/apply_v98_12_upload_64mb.py && \
    python /app/web/test_v98_12_upload_64mb.py /app/GamingShortsFactory_V98_12_UPLOAD_64MB.py && \
    python -m py_compile /app/GamingShortsFactory_V98_12_UPLOAD_64MB.py && \
    python /app/web/apply_v98_final.py && \
    python /app/web/test_v98_final_acceptance.py /app/GamingShortsFactory_V98_FINAL.py && \
    python /app/web/test_v98_final_direct_upload.py && \
    python -m py_compile /app/GamingShortsFactory_V98_FINAL.py && \
    python /app/web/apply_v98_final_6lanes.py && \
    python /app/web/test_v98_final_6lanes.py /app/GamingShortsFactory_V98_FINAL_6LANES.py && \
    python -m py_compile /app/GamingShortsFactory_V98_FINAL_6LANES.py && \
    python /app/web/apply_v99_ai_turbo.py && \
    python /app/web/test_v99_ai_turbo.py /app/GamingShortsFactory_V99_AI_TURBO.py && \
    python /app/web/test_v99_ffmpeg_turbo.py && \
    python -m py_compile /app/GamingShortsFactory_V99_AI_TURBO.py && \
    python /app/web/apply_v99_final_arch.py && \
    python /app/web/test_v99_final_arch.py /app/GamingShortsFactory_V99_FINAL_ARCH.py && \
    python /app/web/test_v99_worker_engine.py && \
    python -m py_compile /app/GamingShortsFactory_V99_FINAL_ARCH.py && \
    python /app/web/apply_v100_smart_reframe.py && \
    python /app/web/test_v100_smart_reframe.py /app/GamingShortsFactory_V100_SMART_REFRAME.py && \
    python -m py_compile /app/GamingShortsFactory_V100_SMART_REFRAME.py && \
    python /app/web/apply_v100_1_quality_mobile.py && \
    python /app/web/test_v100_1_quality_mobile.py /app/GamingShortsFactory_V100_1_QUALITY_MOBILE.py && \
    python -m py_compile /app/GamingShortsFactory_V100_1_QUALITY_MOBILE.py && \
    python /app/web/apply_v100_2_master_quality.py && \
    python /app/web/test_v100_2_master_quality.py /app/GamingShortsFactory_V100_2_MASTER_QUALITY.py && \
    python -m py_compile /app/GamingShortsFactory_V100_2_MASTER_QUALITY.py && \
    python /app/web/apply_v100_3_native_crop_hq.py && \
    python /app/web/test_v100_3_native_crop_hq.py /app/GamingShortsFactory_V100_3_NATIVE_CROP_HQ.py && \
    python -m py_compile /app/GamingShortsFactory_V100_3_NATIVE_CROP_HQ.py && \
    python /app/web/apply_v100_4_render_stable.py && \
    python /app/web/test_v100_4_render_stable.py /app/GamingShortsFactory_V100_4_RENDER_STABLE.py && \
    python -m py_compile /app/GamingShortsFactory_V100_4_RENDER_STABLE.py && \
    python /app/web/apply_v100_5_max_upload.py && \
    python /app/web/test_v100_5_max_upload.py /app/GamingShortsFactory_V100_5_MAX_UPLOAD.py && \
    python -m py_compile /app/GamingShortsFactory_V100_5_MAX_UPLOAD.py && \
    python /app/web/apply_v100_6_fps_guard.py && \
    python /app/web/test_v100_6_fps_guard.py /app/GamingShortsFactory_V100_6_FPS_GUARD.py && \
    python -m py_compile /app/GamingShortsFactory_V100_6_FPS_GUARD.py && \
    python /app/web/apply_v100_7_memory_safe_render.py && \
    python /app/web/test_v100_7_memory_safe_render.py /app/GamingShortsFactory_V100_7_MEMORY_SAFE_RENDER.py && \
    python -m py_compile /app/GamingShortsFactory_V100_7_MEMORY_SAFE_RENDER.py && \
    python /app/web/apply_v100_8_fast_render.py && \
    python /app/web/test_v100_8_fast_render.py /app/GamingShortsFactory_V100_8_FAST_RENDER.py && \
    python -m py_compile /app/GamingShortsFactory_V100_8_FAST_RENDER.py && \
    python /app/web/apply_v101_subtitle_refinement.py && \
    python /app/web/test_v101_subtitle_refinement.py /app/GamingShortsFactory_V101_SUBTITLE_REFINEMENT.py && \
    python -m py_compile /app/GamingShortsFactory_V101_SUBTITLE_REFINEMENT.py && \
    python /app/web/apply_v102_smart_hook.py && \
    python /app/web/test_v102_smart_hook.py /app/GamingShortsFactory_V102_SMART_HOOK.py && \
    python -m py_compile /app/GamingShortsFactory_V102_SMART_HOOK.py && \
    python /app/web/inspect_v103_render.py && \
    python -m py_compile /app/web/direct_upload_server.py && \
    python -m py_compile /app/web/ai_worker_server.py && \
    python -m py_compile /app/web/gsf_bucket_bridge.py && \
    python -m py_compile /app/web/direct_upload_server.py

COPY .streamlit /app/.streamlit

RUN PORT=8080 envsubst '${PORT}' < /app/web/nginx.conf.template > /tmp/gsf-nginx-test.conf && \
    cp /tmp/gsf-nginx-test.conf /etc/nginx/conf.d/default.conf && \
    nginx -t

RUN chmod +x /app/web/start_web.sh && mkdir -p /tmp/gsf-runtime

EXPOSE 8080
CMD ["/app/web/start_web.sh"]
