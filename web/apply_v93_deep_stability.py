from pathlib import Path

src=Path('/app/GamingShortsFactory_V92_AI_REACTION_QUALITY.py')
out=Path('/app/GamingShortsFactory_V93_DEEP_STABILITY.py')
s=src.read_text(encoding='utf-8')

def replace_once(old,new,label):
    global s
    if old not in s:
        raise RuntimeError(f'V93 patch target not found: {label}')
    s=s.replace(old,new,1)

# 1) Session recovery: duration buttons use a runtime-built key
# ("v70_duration_" + label), so V80.1 AST discovery cannot see the prefix.
replace_once(
'''_gsf_restore_persistent_state()
''',
'''try:
    if "v70_duration_" not in _GSF_TRANSIENT_WIDGET_PREFIXES:
        _GSF_TRANSIENT_WIDGET_PREFIXES=tuple(_GSF_TRANSIENT_WIDGET_PREFIXES)+("v70_duration_",)
except Exception:
    pass

_gsf_restore_persistent_state()
''',
'duration widget recovery guard')

# 2) Real Streamlit upload progress uses a file-chip spinner in current builds,
# not role=progressbar. Keep the existing selectors and add the real one.
replace_once(
'''.st-key-v73-upload-shell:has([data-testid*="Progress"]) .gsf-v91-upload-status{{
    display:flex;
}}
''',
'''.st-key-v73-upload-shell:has([data-testid*="Progress"]) .gsf-v91-upload-status,
.st-key-v73-upload-shell:has([data-testid="stFileChipIconSpinner"]) .gsf-v91-upload-status{{
    display:flex;
}}
''',
'real upload spinner selector')

# 3) The UI contract says 15s/30s applies to all three AI proposals.
# AI Director boundary refinement may shift the start, but must not lengthen it.
replace_once(
'''                                candidati_rifiniti.append(nuovo_start)
                                clip_rifinite[round(nuovo_start, 3)] = nuova_durata
''',
'''                                nuova_durata=float(duration)
                                candidati_rifiniti.append(nuovo_start)
                                clip_rifinite[round(nuovo_start, 3)] = nuova_durata
''',
'AI refined duration contract')

# 4) Reazioni may load Whisper Tiny. A long session can then hit the Railway
# memory ceiling during final FFmpeg rendering. Release analysis-only RAM first.
anchor='''def _gsf_render_final_recipe(recipe,output_path,video_obj=None):
'''
helper='''def _gsf_v93_release_analysis_memory():
    if not GSF_LOW_MEMORY_WEB:
        return
    for _key in (
        "gsf_ai_scan_cache_v40",
        "gsf_ai_scan_cache_v50",
        "gsf_ai_voice_cache_v40",
        "gsf_ai_refine_motion_cache_v50",
        "gsf_fast_ai_cache",
    ):
        try:
            st.session_state.pop(_key,None)
        except Exception:
            pass
    for _cached in (
        globals().get("_gsf_ai_whisper_tiny"),
        globals().get("_gsf_subtitle_whisper_model"),
    ):
        try:
            if _cached is not None:
                _cached.clear()
        except Exception:
            pass
    try:
        import gc
        gc.collect()
    except Exception:
        pass
    try:
        import ctypes
        ctypes.CDLL("libc.so.6").malloc_trim(0)
    except Exception:
        pass


def _gsf_render_final_recipe(recipe,output_path,video_obj=None):
'''
replace_once(anchor,helper,'analysis memory release helper')

replace_once(
'''                with st.spinner("🎬 Creo lo Short finale..."):
                    _final_result=_gsf_render_final_recipe(
''',
'''                with st.spinner("🎬 Creo lo Short finale..."):
                    _gsf_v93_release_analysis_memory()
                    _final_result=_gsf_render_final_recipe(
''',
'pre-render memory release')

s=s.replace(
    'Gaming Shorts Factory · V92 AI Reaction Quality',
    'Gaming Shorts Factory · V93 Deep Stability'
)

out.write_text(s,encoding='utf-8')
print(f'V93 patch applied: {out}')
