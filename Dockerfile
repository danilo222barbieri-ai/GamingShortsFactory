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
      ffmpeg nginx gettext-base ca-certificates tesseract-ocr tesseract-ocr-eng tesseract-ocr-ita zbar-tools \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements-web.txt /app/requirements-web.txt
COPY constraints-web.txt /app/constraints-web.txt
RUN python -m pip install --upgrade pip && python -m pip install -r /app/requirements-web.txt -c /app/constraints-web.txt
RUN mkdir -p /app/.cache/huggingface && python -c "from faster_whisper import WhisperModel; WhisperModel('tiny', device='cpu', compute_type='int8')"
COPY src_payload /app/src_payload
COPY web /app/web
COPY web/gsf_perf.py /app/gsf_perf.py
COPY web/ffmpeg_lowmem.py /usr/local/bin/ffmpeg
RUN python -c "import base64,pathlib,struct; p=pathlib.Path('/app/web/app_icons'); s=''.join((p/f'official_logo_180.b64.part{i}').read_text().strip() for i in range(1,5)); raw=base64.b64decode(s); (p/'app-icon.png').write_bytes(raw); (p/'apple-touch-icon.png').write_bytes(raw); (p/'official_logo_180.valid.b64').write_text(s); assert raw[:8]==b'\\x89PNG\\r\\n\\x1a\\n'; assert struct.unpack('>II',raw[16:24])==(180,180); print('GSF production app icon 180: PASS')" && \
    /usr/bin/ffmpeg -hide_banner -loglevel error -y -i /app/web/app_icons/app-icon.png -vf scale=192:192 /app/web/app_icons/app-icon-192.png && \
    /usr/bin/ffmpeg -hide_banner -loglevel error -y -i /app/web/app_icons/app-icon.png -vf scale=512:512 /app/web/app_icons/app-icon-512.png && \
    python -c "import pathlib,struct; p=pathlib.Path('/app/web/app_icons'); dims={n:struct.unpack('>II',(p/n).read_bytes()[16:24]) for n in ('app-icon-192.png','app-icon-512.png')}; assert dims['app-icon-192.png']==(192,192); assert dims['app-icon-512.png']==(512,512); print('GSF PWA icons 192/512: PASS')"
RUN chmod +x /usr/local/bin/ffmpeg && python -c "import base64,gzip,pathlib; p=pathlib.Path('/app/src_payload'); s=''.join(x.read_text() for x in sorted(p.glob('gsf_v77.py.gz.b64.part*'))); pathlib.Path('/app/GamingShortsFactory_V77_WEB_READY.py').write_bytes(gzip.decompress(base64.b64decode(s)))" && \
    python /app/web/apply_v78_mobile_patch.py && python /app/web/apply_v79_session_social_patch.py && python /app/web/apply_v80_ui_auto_sub_patch.py && python /app/web/apply_v80_1_hotfix.py && python /app/web/apply_v80_2_render_hotfix.py && python /app/web/apply_v81_mobile_tablet_patch.py && python /app/web/apply_v82_fixpack.py && python /app/web/apply_v83_upload_fix.py && python /app/web/apply_v84_mobile_media_upload_fix.py && python /app/web/apply_v85_upload_cleanup.py && python /app/web/apply_v86_single_upload_circle.py && python /app/web/apply_v87_upload_persist.py && python /app/web/apply_v88_persistent_loaded_circle.py && python /app/web/apply_v89_decoupled_upload_visual.py && python /app/web/apply_v90_upload_visual_fix.py && python /app/web/apply_v91_roadmap_polish.py && python /app/web/apply_v92_ai_reaction_quality.py && python /app/web/apply_v93_deep_stability.py && python /app/web/apply_v94_short_quality.py && python /app/web/apply_v95_render_text_polish.py && python /app/web/apply_v98_editor_polish.py && python /app/web/apply_v98_1_editor_hotfix.py && python /app/web/apply_v98_2_upload_recovery.py && python /app/web/apply_v98_3_home_compact.py && python /app/web/apply_v98_4_editor_cleanup.py && python /app/web/apply_v98_5_style_only.py && python /app/web/apply_v98_6_player_sizes.py && python /app/web/apply_v98_7_new_video_fix.py && python /app/web/apply_v98_8_upload_memory_fix.py && python /app/web/apply_v98_9_direct_upload.py && python /app/web/apply_v98_10_speed_pass1.py && python /app/web/apply_v98_11_speed_all.py && python /app/web/apply_v98_12_upload_64mb.py && python /app/web/apply_v98_final.py && python /app/web/apply_v98_final_6lanes.py && python /app/web/apply_v99_ai_turbo.py && python /app/web/apply_v99_final_arch.py && python /app/web/apply_v100_smart_reframe.py && python /app/web/apply_v100_1_quality_mobile.py && python /app/web/apply_v100_2_master_quality.py && python /app/web/apply_v100_3_native_crop_hq.py && python /app/web/apply_v100_4_render_stable.py && python /app/web/apply_v100_5_max_upload.py && python /app/web/apply_v100_6_fps_guard.py && python /app/web/apply_v100_7_memory_safe_render.py && python /app/web/apply_v100_8_fast_render.py && python /app/web/apply_v101_subtitle_refinement.py && python /app/web/apply_v102_smart_hook.py && python /app/web/apply_v103_final_quality.py && python /app/web/apply_v103_1_clean_hook_pixfmt.py && python /app/web/apply_v103_2_canonical_format.py && python /app/web/apply_v104_direct_social.py && \
    python /app/web/apply_v104_2_legal_footer.py && python /app/web/apply_v104_3_memory_safe_render.py && python /app/web/apply_v104_4_shared_social_token.py && python /app/web/apply_v104_5_youtube_social_connect.py && python /app/web/apply_v104_6_stable_social_flow.py && python /app/web/apply_v104_7_instagram_login.py && python /app/web/apply_v105_perf_telemetry.py && python /app/web/apply_v105_no_audio_master.py && python /app/web/apply_v105_2_ui_social_mobile.py && python /app/web/test_v105_2_ui_social_mobile.py /app/GamingShortsFactory_V105_2_UI_SOCIAL_MOBILE.py && python /app/web/apply_v105_3_polish.py && python /app/web/test_v105_3_polish.py /app/GamingShortsFactory_V105_3_POLISH.py && python /app/web/apply_v105_4_social_stability.py && python /app/web/test_v105_4_social_stability.py /app/GamingShortsFactory_V105_4_SOCIAL_STABILITY.py && python /app/web/apply_v105_5_refinements.py && python /app/web/test_v105_5_refinements.py /app/GamingShortsFactory_V105_5_REFINEMENTS.py && python /app/web/apply_v105_6_ads_preview.py && python /app/web/test_v105_6_ads_preview.py /app/GamingShortsFactory_V105_6_ADS_PREVIEW.py && python /app/web/apply_v105_7_adsense_live.py && python /app/web/test_v105_7_adsense_live.py /app/GamingShortsFactory_V105_7_ADSENSE_READY.py /app/web/install_adsense_bridge.py && python /app/web/install_adsense_bridge.py && python /app/web/apply_v106_editor_perf_filters.py && python /app/web/test_v106_editor_perf_filters.py /app/GamingShortsFactory_V106_BETA_RC1.py && python /app/web/test_v104_3_memory_safe_render.py /app/GamingShortsFactory_V106_BETA_RC1.py && python /app/web/test_v104_4_social_connect.py /app/GamingShortsFactory_V106_BETA_RC1.py /app/web/nginx.conf.template /app/web/direct_upload_server.py && python /app/web/test_v104_5_youtube_connect.py /app/GamingShortsFactory_V106_BETA_RC1.py /app/web/nginx.conf.template /app/web/direct_upload_server.py && python /app/web/test_v104_6_stable_social_flow.py /app/GamingShortsFactory_V106_BETA_RC1.py /app/web/nginx.conf.template /app/web/direct_upload_server.py && python /app/web/test_v104_7_instagram_login.py /app/GamingShortsFactory_V106_BETA_RC1.py /app/web/direct_upload_server.py && python -c "import gsf_perf; print('V105 runtime telemetry import: PASS')" && python /app/web/test_v105_perf_telemetry.py && python /app/web/test_v105_pipeline_telemetry.py && python /app/web/test_v105_no_audio_master.py /app/GamingShortsFactory_V106_BETA_RC1.py && python /app/web/test_v105_prescan_bridge.py && python /app/web/test_v105_upload_policy.py && python /app/web/test_v105_worker_image.py && python /app/web/test_v105_render_contract.py && python /app/web/test_v105_benchmark_diagnostics.py && python /app/web/test_v105_benchmark_no_audio.py && python /app/web/test_v105_dependency_lock.py && python /app/web/test_v105_stress_matrix_contract.py && python /app/web/test_v104_2_legal_pages.py /app/web/nginx.conf.template && python /app/web/test_v105_4_contact_form.py && python /app/web/test_v105_5_contact_form.py /app/web/contact_server.py && python /app/web/test_tiktok_site_verification.py /app/web/nginx.conf.template && python -m py_compile /app/GamingShortsFactory_V106_BETA_RC1.py && python -m py_compile /app/web/contact_server.py && python /app/web/apply_v107_production_ui.py && python /app/web/apply_v107_1_stability.py && python /app/web/apply_v108_game_vision.py && python /app/web/apply_v109_zoomout_shortfix.py && python /app/web/test_v109_zoomout.py /app/GamingShortsFactory_V109_ZOOMOUT.py && python /app/web/test_v108_game_vision.py /app/GamingShortsFactory_V109_ZOOMOUT.py && python /app/web/test_v107_production_ui.py /app/GamingShortsFactory_V109_ZOOMOUT.py && python /app/web/test_v107_production_assets.py && python /app/web/test_editor_2027_component.py /app/GamingShortsFactory_V109_ZOOMOUT.py && python /app/web/test_v107_1_stability.py /app/GamingShortsFactory_V109_ZOOMOUT.py && python /app/web/test_v107_ffmpeg_smoke.py && python -m py_compile /app/GamingShortsFactory_V109_ZOOMOUT.py && python /app/web/apply_v110_creator_hub_solid.py && python /app/web/test_v110_creator_hub_solid.py /app/GamingShortsFactory_V110_HUB_SOLID.py && python -m py_compile /app/GamingShortsFactory_V110_HUB_SOLID.py && python /app/web/apply_v111_final_visibility.py && python /app/web/test_v111_final_visibility.py /app/GamingShortsFactory_V111_FINAL_VISIBLE.py /app/web/direct_upload_server.py && python -m py_compile /app/GamingShortsFactory_V111_FINAL_VISIBLE.py && python -m py_compile /app/web/direct_upload_server.py && python /app/web/apply_v112_game_brain.py && python /app/web/test_v112_game_brain.py /app/GamingShortsFactory_V112_GAME_BRAIN.py && python -m py_compile /app/GamingShortsFactory_V112_GAME_BRAIN.py && python /app/web/apply_v113_guardian.py && python /app/web/test_v113_guardian.py /app/GamingShortsFactory_V113_GUARDIAN.py && python -m py_compile /app/GamingShortsFactory_V113_GUARDIAN.py && python -m py_compile /app/web/direct_upload_server.py && python /app/web/test_v124_ai_core.py && python /app/web/apply_v124_ai_os.py && python /app/web/test_v124_ai_os.py /app/GamingShortsFactory_V124_AI_OS.py && python /app/web/test_editor_2027_component.py /app/GamingShortsFactory_V124_AI_OS.py && python -m py_compile /app/GamingShortsFactory_V124_AI_OS.py && python -m py_compile /app/web/ai_director_v124.py && python -m py_compile /app/web/quality_control_v124.py && python -m py_compile /app/web/guardian_intelligence_v124.py && python -m py_compile /app/web/direct_upload_server.py && python /app/web/apply_v125_cinematic_ai.py && python /app/web/test_v125_cinematic_ai.py /app/GamingShortsFactory_V125_CINEMATIC_AI.py && python /app/web/test_v124_ai_os.py /app/GamingShortsFactory_V125_CINEMATIC_AI.py && python /app/web/test_editor_2027_component.py /app/GamingShortsFactory_V125_CINEMATIC_AI.py && python -m py_compile /app/GamingShortsFactory_V125_CINEMATIC_AI.py && python -m py_compile /app/web/cinematic_render_v125.py && python /app/web/apply_v126_creative_director.py && python /app/web/test_v126_creative_director.py /app/GamingShortsFactory_V126_CREATIVE_DIRECTOR.py && python /app/web/test_v124_ai_os.py /app/GamingShortsFactory_V126_CREATIVE_DIRECTOR.py && python /app/web/test_editor_2027_component.py /app/GamingShortsFactory_V126_CREATIVE_DIRECTOR.py && python -m py_compile /app/GamingShortsFactory_V126_CREATIVE_DIRECTOR.py && python -m py_compile /app/web/creative_render_v126.py && python /app/web/test_v127_learning_ranker.py && python /app/web/apply_v127_learning_ranker.py && python /app/web/test_v124_ai_os.py /app/GamingShortsFactory_V127_LEARNING_RANKER.py && python /app/web/test_editor_2027_component.py /app/GamingShortsFactory_V127_LEARNING_RANKER.py && python -m py_compile /app/GamingShortsFactory_V127_LEARNING_RANKER.py && python -m py_compile /app/web/feedback_learning_v127.py && python -m py_compile /app/web/direct_upload_server.py && python /app/web/test_v128_proactive_guardian.py && python /app/web/apply_v128_proactive_guardian.py && python /app/web/test_v124_ai_os.py /app/GamingShortsFactory_V128_PROACTIVE_GUARDIAN.py && python /app/web/test_editor_2027_component.py /app/GamingShortsFactory_V128_PROACTIVE_GUARDIAN.py && python -m py_compile /app/GamingShortsFactory_V128_PROACTIVE_GUARDIAN.py && python -m py_compile /app/web/guardian_watchdog_v128.py && python -m py_compile /app/web/direct_upload_server.py && python /app/web/test_v129_auto_highlights.py && python /app/web/apply_v129_auto_highlights.py && python /app/web/test_v124_ai_os.py /app/GamingShortsFactory_V129_AUTO_HIGHLIGHTS.py && python /app/web/test_editor_2027_component.py /app/GamingShortsFactory_V129_AUTO_HIGHLIGHTS.py && python -m py_compile /app/GamingShortsFactory_V129_AUTO_HIGHLIGHTS.py && python -m py_compile /app/web/auto_highlights/engine_v129.py && python -m py_compile /app/web/ai_worker_server.py && \
    python /app/web/test_v129_creator_hub.py && \
    python /app/web/apply_v130_one_click_ai.py && \
    python /app/web/test_v130_one_click_ai.py /app/GamingShortsFactory_V130_ONE_CLICK_AI.py && \
    python /app/web/test_v124_ai_os.py /app/GamingShortsFactory_V130_ONE_CLICK_AI.py && \
    python /app/web/test_editor_2027_component.py /app/GamingShortsFactory_V130_ONE_CLICK_AI.py && \
    python -m py_compile /app/GamingShortsFactory_V130_ONE_CLICK_AI.py && \
    python -m py_compile /app/web/one_click_v130.py && \
    python /app/web/apply_v130_1_hotfix.py && \
    python /app/web/test_v130_1_hotfix.py /app/GamingShortsFactory_V130_1_HOTFIX.py && \
    python /app/web/test_v124_ai_os.py /app/GamingShortsFactory_V130_1_HOTFIX.py && \
    python /app/web/test_editor_2027_component.py /app/GamingShortsFactory_V130_1_HOTFIX.py && \
    python -m py_compile /app/GamingShortsFactory_V130_1_HOTFIX.py && \
    python /app/web/apply_v130_2_stability_ux.py && \
    python /app/web/test_v130_2_stability_ux.py /app/GamingShortsFactory_V130_2_STABILITY_UX.py && \
    python /app/web/test_v124_ai_os.py /app/GamingShortsFactory_V130_2_STABILITY_UX.py && \
    python /app/web/test_editor_2027_component.py /app/GamingShortsFactory_V130_2_STABILITY_UX.py && \
    python -m py_compile /app/GamingShortsFactory_V130_2_STABILITY_UX.py && \
    python /app/web/test_v135_frame_vision.py && \
    python /app/web/test_v136_director_orchestrator.py && \
    python /app/web/test_v137_vision_consumers.py && \
    python /app/web/test_v138_creator_learning.py && \
    python /app/web/test_v139_render_director.py && \
    python /app/web/test_v140_performance_learning.py && \
    python /app/web/test_v141_long_form_director.py && \
    python /app/web/apply_v142_director_runtime.py && \
    python /app/web/test_v142_director_runtime.py /app/GamingShortsFactory_V142_DIRECTOR_RUNTIME.py && \
    python -m py_compile /app/GamingShortsFactory_V142_DIRECTOR_RUNTIME.py && \
    python /app/web/apply_v143_render_execution.py && \
    python /app/web/test_v143_render_execution.py /app/GamingShortsFactory_V143_RENDER_EXECUTION.py && \
    python -m py_compile /app/GamingShortsFactory_V143_RENDER_EXECUTION.py && \
    python /app/web/test_v144_visual_scoring.py && \
    python /app/web/apply_v144_visual_scoring.py && \
    python -m py_compile /app/GamingShortsFactory_V144_VISUAL_SCORING.py && \
    python /app/web/apply_v145_content_memory.py && \
    python /app/web/test_v145_content_memory.py /app/web/direct_upload_server.py /app/GamingShortsFactory_V145_CONTENT_MEMORY.py && \
    python -m py_compile /app/GamingShortsFactory_V145_CONTENT_MEMORY.py && \
    python -m py_compile /app/web/direct_upload_server.py && \
    python /app/web/test_v146_ocr_privacy.py && \
    python /app/web/test_v147_cover_longform.py && \
    python /app/web/test_v149_privacy_cleanup.py /app/GamingShortsFactory_V143_RENDER_EXECUTION.py && \
    python /app/web/apply_v148_social_analytics.py && \
    python /app/web/test_v148_social_analytics.py /app/web/direct_upload_server.py /app/GamingShortsFactory_V148_ANALYTICS_LEARNING.py && \
    python /app/web/test_editor_2027_component.py /app/GamingShortsFactory_V148_ANALYTICS_LEARNING.py && \
    python -m py_compile /app/GamingShortsFactory_V148_ANALYTICS_LEARNING.py && \
    python -m py_compile /app/web/direct_upload_server.py && \
    python /app/web/test_v150_end_to_end_stability.py /app/GamingShortsFactory_V148_ANALYTICS_LEARNING.py /app/web/direct_upload_server.py /app/web/ai_worker_server.py && \
    python /app/web/apply_v151_living_home.py && python -m py_compile /app/GamingShortsFactory_V151_LIVING_HOME.py && \
    python /app/web/apply_v152_ui_reset.py && python -m py_compile /app/GamingShortsFactory_V152_UI_RESET.py && \
    python /app/web/apply_v154_structural_home.py && python -m py_compile /app/GamingShortsFactory_V154_STRUCTURAL_HOME.py
RUN python /app/web/test_v153_living_tail.py
RUN python /app/web/test_v154_structural_home.py
RUN python /app/web/test_v158_persistent_shell.py
RUN python /app/web/test_v159_surface_shell.py
RUN python /app/web/test_v160_hub_shell.py
RUN python /app/web/test_v161_viewport_fit.py
RUN python /app/web/test_v161_1_zero_scroll.py
RUN python /app/web/test_v162_1_short_desktop_fit.py
RUN python /app/web/test_v163_adaptive_artboard.py
RUN python /app/web/test_v164_home_reference.py
RUN python /app/web/test_v165_fluid_responsive_home.py
RUN python /app/web/test_v166_mega_responsive_home.py
RUN python /app/web/test_v167_home_visual_final.py
RUN python /app/web/test_v168_home_nav_ads.py
RUN python /app/web/test_v169_reference_fidelity.py
RUN python /app/web/test_v170_geometry_color_repair.py
RUN python /app/web/test_v162_1_home_lift.py
RUN python -m compileall -q /app/web
COPY .streamlit /app/.streamlit
RUN PORT=8080 envsubst '${PORT}' < /app/web/nginx.conf.template > /tmp/gsf-nginx-test.conf && cp /tmp/gsf-nginx-test.conf /etc/nginx/conf.d/default.conf && nginx -t
RUN chmod +x /app/web/start_web.sh && mkdir -p /tmp/gsf-runtime
EXPOSE 8080
CMD ["/app/web/start_web.sh"]
