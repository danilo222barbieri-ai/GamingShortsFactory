from pathlib import Path

src=Path('/app/GamingShortsFactory_V105_7_ADSENSE_READY.py')
out=Path('/app/GamingShortsFactory_V106_BETA_RC1.py')
s=src.read_text(encoding='utf-8')

def replace_once(old,new,label):
    global s
    if old not in s:
        raise RuntimeError(f'V106 target not found: {label}')
    s=s.replace(old,new,1)

# ------------------------------------------------------------------
# V106 helpers: lightweight preview filters, cached probe, render lock.
# ------------------------------------------------------------------
anchor='''def _render_gsf_editor_live_player_legacy(
'''
helpers=r'''
import threading as _gsf_v106_threading

_GSF_V106_FILTER_PRESETS=(
    "Originale",
    "Gaming / Vibrante",
    "Cinematico",
    "Caldo",
    "Freddo",
    "Bianco e Nero",
)
_GSF_V106_RENDER_LOCK=_gsf_v106_threading.Lock()
_GSF_V106_PROBE_CACHE={}


def _gsf_v106_filter_strength(value):
    try:
        return max(0.0,min(1.0,float(value)/100.0))
    except Exception:
        return 0.0


def _gsf_v106_css_filter(preset,intensity):
    p=str(preset or "Originale")
    t=_gsf_v106_filter_strength(intensity)
    if p=="Gaming / Vibrante":
        return f"saturate({1.0+0.45*t:.4f}) contrast({1.0+0.08*t:.4f})"
    if p=="Cinematico":
        return f"saturate({1.0-0.18*t:.4f}) contrast({1.0+0.12*t:.4f}) sepia({0.08*t:.4f})"
    if p=="Caldo":
        return f"sepia({0.20*t:.4f}) saturate({1.0+0.08*t:.4f}) hue-rotate({-6.0*t:.3f}deg)"
    if p=="Freddo":
        return f"saturate({1.0+0.05*t:.4f}) hue-rotate({7.0*t:.3f}deg)"
    if p=="Bianco e Nero":
        return f"grayscale({t:.4f})"
    return ""


def _gsf_v106_ffmpeg_filter(preset,intensity):
    p=str(preset or "Originale")
    t=_gsf_v106_filter_strength(intensity)
    if t<=0.0001 or p=="Originale":
        return ""
    if p=="Gaming / Vibrante":
        return f"eq=saturation={1.0+0.45*t:.5f}:contrast={1.0+0.08*t:.5f}"
    if p=="Cinematico":
        return (
            f"eq=saturation={1.0-0.18*t:.5f}:contrast={1.0+0.12*t:.5f},"
            f"colorbalance=rs={0.025*t:.5f}:bs={-0.020*t:.5f}"
        )
    if p=="Caldo":
        return (
            f"eq=saturation={1.0+0.08*t:.5f},"
            f"colorbalance=rs={0.080*t:.5f}:bs={-0.060*t:.5f}"
        )
    if p=="Freddo":
        return (
            f"eq=saturation={1.0+0.05*t:.5f},"
            f"colorbalance=rs={-0.040*t:.5f}:bs={0.075*t:.5f}"
        )
    if p=="Bianco e Nero":
        return f"eq=saturation={1.0-t:.5f}"
    return ""


def _gsf_v106_probe_display_size_cached(source_path):
    p=Path(source_path)
    try:
        stt=p.stat()
        key=(str(p),int(stt.st_mtime_ns),int(stt.st_size))
    except Exception:
        return _gsf_probe_display_size(p)
    hit=_GSF_V106_PROBE_CACHE.get(key)
    if hit is not None:
        return hit
    result=_gsf_probe_display_size(p)
    if len(_GSF_V106_PROBE_CACHE)>=24:
        _GSF_V106_PROBE_CACHE.clear()
    _GSF_V106_PROBE_CACHE[key]=result
    return result


def _gsf_v106_run_render_locked(cmd,timeout,encoder="",fmt="",duration=0.0):
    wait_started=time.perf_counter()
    acquired=_GSF_V106_RENDER_LOCK.acquire(timeout=max(30.0,float(timeout or 600.0)))
    waited=time.perf_counter()-wait_started
    print(
        "GSF_EDITOR_RENDER_LOCK_WAIT",
        f"waited={waited:.3f}",
        f"encoder={encoder}",
        f"fmt={fmt}",
        flush=True,
    )
    if not acquired:
        raise subprocess.TimeoutExpired(cmd,float(timeout or 600.0))
    try:
        try:
            _gsf_v93_release_analysis_memory()
        except Exception:
            try:
                import gc
                gc.collect()
            except Exception:
                pass
        print(
            "GSF_EDITOR_RENDER_LOCK_START",
            f"encoder={encoder}",
            f"fmt={fmt}",
            f"duration={float(duration or 0.0):.3f}",
            flush=True,
        )
        return subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
        )
    finally:
        print(
            "GSF_EDITOR_RENDER_LOCK_END",
            f"encoder={encoder}",
            f"fmt={fmt}",
            flush=True,
        )
        _GSF_V106_RENDER_LOCK.release()


'''
replace_once(anchor,helpers+anchor,'helper insertion')

# ------------------------------------------------------------------
# Legacy/persistent live player: keep approved dimensions and player system,
# but avoid repeated ffprobe and apply filter in-browser.
# ------------------------------------------------------------------
replace_once(
'''    subtitle_words=None, subtitle_text="",
    subtitle_font="Arial", subtitle_x=50, subtitle_y=78
):''',
'''    subtitle_words=None, subtitle_text="",
    subtitle_font="Arial", subtitle_x=50, subtitle_y=78,
    filter_preset="Originale", filter_intensity=0
):''',
'legacy player signature')

replace_once(
'''    pw,ph,rotation,err=_gsf_probe_display_size(source_path)
''',
'''    _v106_probe_t0=time.perf_counter()
    pw,ph,rotation,err=_gsf_v106_probe_display_size_cached(source_path)
    print(
        "GSF_EDITOR_PROBE",
        f"fmt={fmt}",
        f"elapsed={time.perf_counter()-_v106_probe_t0:.4f}",
        flush=True,
    )
''',
'cached editor probe')

replace_once(
'''    con=max(0.0,float(contrast)); speed=float(speed)
    tx=_gsf_pan_translate(zoom,x_pos)
''',
'''    con=max(0.0,float(contrast)); speed=float(speed)
    _v106_fx=_gsf_v106_css_filter(filter_preset,filter_intensity)
    _v106_css_filter=(
        f"brightness({bri}) contrast({con})"
        + (f" {_v106_fx}" if _v106_fx else "")
    )
    tx=_gsf_pan_translate(zoom,x_pos)
''',
'legacy CSS filter setup')

replace_once(
'''      filter:brightness({bri}) contrast({con})}}
''',
'''      filter:{_v106_css_filter}}}
''',
'legacy CSS filter application')

# Persistent wrapper accepts filters. Current pinned Streamlit uses legacy
# fallback; extra data also future-proofs the V2 component contract.
replace_once(
'''    end_seconds=None, seek_target=None, seek_nonce=0, reset_id=0, clip_start_override=None,
    text_color=None, active_color=None, outline_color=None
):''',
'''    end_seconds=None, seek_target=None, seek_nonce=0, reset_id=0, clip_start_override=None,
    text_color=None, active_color=None, outline_color=None,
    filter_preset="Originale", filter_intensity=0
):''',
'persistent player signature')

replace_once(
'''            subtitle_font,subtitle_x,subtitle_y
        )
''',
'''            subtitle_font,subtitle_x,subtitle_y,
            filter_preset,filter_intensity
        )
''',
'legacy filter forwarding')

replace_once(
'''            "textColor":tc,"activeColor":ac,"outlineColor":oc,
''',
'''            "textColor":tc,"activeColor":ac,"outlineColor":oc,
            "filterPreset":str(filter_preset or "Originale"),
            "filterIntensity":float(filter_intensity or 0),
            "filterCss":_gsf_v106_css_filter(filter_preset,filter_intensity),
''',
'V2 filter data')

# ------------------------------------------------------------------
# Main editor filter state + preview + controls.
# ------------------------------------------------------------------
replace_once(
'''        if "editor_contrast" not in st.session_state: st.session_state["editor_contrast"]=1.0
''',
'''        if "editor_contrast" not in st.session_state: st.session_state["editor_contrast"]=1.0
        if "editor_filter_preset" not in st.session_state: st.session_state["editor_filter_preset"]="Originale"
        if "editor_filter_intensity" not in st.session_state: st.session_state["editor_filter_intensity"]=70
''',
'main filter defaults')

replace_once(
'''        editor_contrast=float(st.session_state.get("editor_contrast",1.0))

        # Conserva i limiti originali una sola volta per RESET TUTTO.
''',
'''        editor_contrast=float(st.session_state.get("editor_contrast",1.0))
        editor_filter_preset=str(st.session_state.get("editor_filter_preset","Originale") or "Originale")
        editor_filter_intensity=int(st.session_state.get("editor_filter_intensity",70) or 70)

        # Conserva i limiti originali una sola volta per RESET TUTTO.
''',
'main filter locals')

replace_once(
'''                outline_color=st.session_state.get("subtitle_outline_color_v18","#000000"),
''',
'''                outline_color=st.session_state.get("subtitle_outline_color_v18","#000000"),
                filter_preset=editor_filter_preset,
                filter_intensity=editor_filter_intensity,
''',
'main player filter args')

replace_once(
'''                    editor_extra_tool=st.selectbox("Parametro",["Volume","Velocità","Luminosità","Contrasto"],key="editor_extra_tool")
''',
'''                    editor_extra_tool=st.selectbox(
                        "Parametro",
                        ["Volume","Velocità","Luminosità","Contrasto","Filtro"],
                        key="editor_extra_tool"
                    )
''',
'main filter tool option')

replace_once(
'''                    elif editor_extra_tool=="Velocità":
''',
'''                    elif editor_extra_tool=="Filtro":
                        editor_filter_preset=st.selectbox(
                            "Filtro",
                            list(_GSF_V106_FILTER_PRESETS),
                            key="editor_filter_preset"
                        )
                        editor_filter_intensity=st.slider(
                            "Intensità filtro",0,100,
                            int(st.session_state.get("editor_filter_intensity",70)),
                            5,key="editor_filter_intensity",
                            disabled=(editor_filter_preset=="Originale")
                        )
                    elif editor_extra_tool=="Velocità":
''',
'main filter controls')

# Project-reset protection must understand untouched filter defaults.
replace_once(
'''        "editor_contrast": 1.0, "editor_speed": 1.0,
''',
'''        "editor_contrast": 1.0, "editor_speed": 1.0,
        "editor_filter_preset": "Originale", "editor_filter_intensity": 70,
''',
'main default protection')

# ------------------------------------------------------------------
# Inline editor filters.
# ------------------------------------------------------------------
replace_once(
'''                        _spd_key=f"inline_spd_{_this_inline_id}"
                        _submode_key=f"inline_submode_{_this_inline_id}"
''',
'''                        _spd_key=f"inline_spd_{_this_inline_id}"
                        _filter_key=f"inline_filter_{_this_inline_id}"
                        _filter_strength_key=f"inline_filter_strength_{_this_inline_id}"
                        _submode_key=f"inline_submode_{_this_inline_id}"
''',
'inline filter keys')

replace_once(
'''                        if _spd_key not in st.session_state: st.session_state[_spd_key]=1.0
                        if _submode_key not in st.session_state: st.session_state[_submode_key]="Automatici"
''',
'''                        if _spd_key not in st.session_state: st.session_state[_spd_key]=1.0
                        if _filter_key not in st.session_state: st.session_state[_filter_key]="Originale"
                        if _filter_strength_key not in st.session_state: st.session_state[_filter_strength_key]=70
                        if _submode_key not in st.session_state: st.session_state[_submode_key]="Automatici"
''',
'inline filter defaults')

replace_once(
'''                                outline_color=st.session_state.get(f"inline_outcol_v18_{_this_inline_id}","#000000"),
                                reset_id=st.session_state.get(f"inline_reset_id_{_this_inline_id}",0),
''',
'''                                outline_color=st.session_state.get(f"inline_outcol_v18_{_this_inline_id}","#000000"),
                                filter_preset=st.session_state.get(_filter_key,"Originale"),
                                filter_intensity=st.session_state.get(_filter_strength_key,70),
                                reset_id=st.session_state.get(f"inline_reset_id_{_this_inline_id}",0),
''',
'inline player filter args')

replace_once(
'''                                    _reg=st.selectbox("Parametro",["Volume","Luminosità","Contrasto","Velocità"],key=f"inline_reg_v18_{_this_inline_id}")
''',
'''                                    _reg=st.selectbox(
                                        "Parametro",
                                        ["Volume","Luminosità","Contrasto","Velocità","Filtro"],
                                        key=f"inline_reg_v18_{_this_inline_id}"
                                    )
''',
'inline filter tool option')

replace_once(
'''                                    if _reg=="Volume":
''',
'''                                    if _reg=="Filtro":
                                        st.session_state[_filter_key]=st.selectbox(
                                            "Filtro",
                                            list(_GSF_V106_FILTER_PRESETS),
                                            index=list(_GSF_V106_FILTER_PRESETS).index(
                                                st.session_state.get(_filter_key,"Originale")
                                                if st.session_state.get(_filter_key,"Originale") in _GSF_V106_FILTER_PRESETS
                                                else "Originale"
                                            ),
                                            key=f"inline_filter_widget_v106_{_this_inline_id}"
                                        )
                                        st.session_state[_filter_strength_key]=st.slider(
                                            "Intensità filtro",0,100,
                                            int(st.session_state.get(_filter_strength_key,70)),
                                            5,key=f"inline_filter_strength_widget_v106_{_this_inline_id}",
                                            disabled=(st.session_state[_filter_key]=="Originale")
                                        )
                                        st.session_state["v106_last_inline_filter_preset"]=st.session_state[_filter_key]
                                        st.session_state["v106_last_inline_filter_intensity"]=st.session_state[_filter_strength_key]
                                    elif _reg=="Volume":
''',
'inline filter controls')

# ------------------------------------------------------------------
# Final render filter: one-pass FFmpeg, no extra encode.
# ------------------------------------------------------------------
replace_once(
'''hook_duration=None, polish_audio=True):''',
'''hook_duration=None, polish_audio=True, filter_preset="Originale", filter_intensity=0):''',
'final core filter signature')

replace_once(
'''        vf = _gsf_render_video_filters(fmt, zoom, x_pos, y_pos, brightness, contrast, speed, ass_file=ass_file if os.path.exists(ass_file) else None, reframe_track=reframe_track)
        af = _gsf_render_audio_filter''',
'''        vf = _gsf_render_video_filters(fmt, zoom, x_pos, y_pos, brightness, contrast, speed, ass_file=ass_file if os.path.exists(ass_file) else None, reframe_track=reframe_track)
        _v106_final_fx=_gsf_v106_ffmpeg_filter(filter_preset,filter_intensity)
        if _v106_final_fx:
            vf=f"{vf},{_v106_final_fx}"
        af = _gsf_render_audio_filter''',
'one-pass final filter')

replace_once(
'''    if kind in ("main_editor","inline_editor"):
        kw=dict(recipe.get("render_kwargs") or {})
        return _gsf_render_core(
''',
'''    if kind in ("main_editor","inline_editor"):
        kw=dict(recipe.get("render_kwargs") or {})
        if kind=="main_editor":
            kw.setdefault(
                "filter_preset",
                st.session_state.get("editor_filter_preset","Originale")
            )
            kw.setdefault(
                "filter_intensity",
                st.session_state.get("editor_filter_intensity",70)
            )
        else:
            kw.setdefault(
                "filter_preset",
                st.session_state.get("v106_last_inline_filter_preset","Originale")
            )
            kw.setdefault(
                "filter_intensity",
                st.session_state.get("v106_last_inline_filter_intensity",70)
            )
        return _gsf_render_core(
''',
'editor recipe filter propagation')

# Serialize the actual FFmpeg encode to prevent duplicate jobs from exhausting
# the 1 GB web container. Existing timeout/error handling is preserved.
replace_once(
'''                r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=_diag_timeout)
''',
'''                r = _gsf_v106_run_render_locked(
                    cmd,_diag_timeout,
                    encoder=encoder,fmt=fmt,duration=duration
                )
''',
'render lock')

# Version marker.
s=s.replace(
    'Gaming Shorts Factory · V105.7 AdSense Ready',
    'Gaming Shorts Factory · V106 BETA RC1',
    1,
)

compile(s,str(out),'exec')
out.write_text(s,encoding='utf-8')
print(f'V106 BETA RC1 editor performance + filters applied: {out}')
