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
                        ["Volume","Velocità","Luminosità","Contrasto"],
                        key="editor_extra_tool"
                    )
''',
'main filter tool option')

# V106.1 — Filters are a first-class video control, not hidden in "Parametro".
replace_once(
'''                        editor_contrast=st.slider("Contrasto",.70,1.50,float(st.session_state.get("editor_contrast",1.0)),.05,key="editor_contrast")

            st.markdown('<div class="gsf-icon-title gsf-subtitles-title">' + _gsf_v67_badge("text", "Sottotitoli", "lilac") + '</div>', unsafe_allow_html=True)
''',
'''                        editor_contrast=st.slider("Contrasto",.70,1.50,float(st.session_state.get("editor_contrast",1.0)),.05,key="editor_contrast")

            st.markdown(
                '<div class="gsf-icon-title gsf-v1061-filters-title">' +
                _gsf_v67_badge("edit", "Filtri video", "indigo") +
                '</div>',
                unsafe_allow_html=True,
                help="Modifica importante dell'immagine: il filtro resta nella preview e nel render finale."
            )
            editor_filter_preset=st.segmented_control(
                "Filtro video",
                list(_GSF_V106_FILTER_PRESETS),
                key="editor_filter_preset",
                label_visibility="collapsed"
            )
            if editor_filter_preset is None:
                editor_filter_preset=st.session_state.get("editor_filter_preset","Originale")
            editor_filter_intensity=st.slider(
                "Intensità filtro",0,100,
                int(st.session_state.get("editor_filter_intensity",70)),
                5,key="editor_filter_intensity",
                disabled=(str(editor_filter_preset)=="Originale")
            )

            st.markdown('<div class="gsf-icon-title gsf-subtitles-title">' + _gsf_v67_badge("text", "Sottotitoli", "lilac") + '</div>', unsafe_allow_html=True)
''',
'main prominent filters')

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
                                        ["Volume","Luminosità","Contrasto","Velocità"],
                                        key=f"inline_reg_v18_{_this_inline_id}"
                                    )
''',
'inline filter tool option')

# V106.1 — Subtitle colors are draft -> explicit Apply, so the action is obvious.
replace_once(
'''                        c1,c2,c3=st.columns(3,gap="small")
                        with c1:
                            st.color_picker("Testo",st.session_state.get("subtitle_text_color_v18",st.session_state.get("subtitle_text_color","#FFFFFF")),key="subtitle_text_color_v18")
                        with c2:
                            st.color_picker("Attiva",st.session_state.get("subtitle_active_color_v18",st.session_state.get("subtitle_active_color","#FFD400")),key="subtitle_active_color_v18")
                        with c3:
                            st.color_picker("Bordo",st.session_state.get("subtitle_outline_color_v18",st.session_state.get("subtitle_outline_color","#000000")),key="subtitle_outline_color_v18")
''',
'''                        _v1061_main_colors=(
                            ("subtitle_text_color_draft_v1061","subtitle_text_color_v18","subtitle_text_color","#FFFFFF"),
                            ("subtitle_active_color_draft_v1061","subtitle_active_color_v18","subtitle_active_color","#FFD400"),
                            ("subtitle_outline_color_draft_v1061","subtitle_outline_color_v18","subtitle_outline_color","#000000"),
                        )
                        for _draft,_actual,_base,_fallback in _v1061_main_colors:
                            _actual_value=st.session_state.get(_actual,st.session_state.get(_base,_fallback))
                            _snap=_draft+"_applied"
                            if _draft not in st.session_state or st.session_state.get(_snap)!=_actual_value:
                                st.session_state[_draft]=_actual_value
                                st.session_state[_snap]=_actual_value
                        c1,c2,c3=st.columns(3,gap="small")
                        with c1:
                            st.color_picker("Testo",key="subtitle_text_color_draft_v1061")
                            if st.button("Applica",key="apply_sub_text_color_v1061",use_container_width=True):
                                _c=st.session_state["subtitle_text_color_draft_v1061"]
                                st.session_state["subtitle_text_color_v18"]=_c
                                st.session_state["subtitle_text_color"]=_c
                                st.session_state["subtitle_text_color_draft_v1061_applied"]=_c
                                st.rerun()
                        with c2:
                            st.color_picker("Attiva",key="subtitle_active_color_draft_v1061")
                            if st.button("Applica",key="apply_sub_active_color_v1061",use_container_width=True):
                                _c=st.session_state["subtitle_active_color_draft_v1061"]
                                st.session_state["subtitle_active_color_v18"]=_c
                                st.session_state["subtitle_active_color"]=_c
                                st.session_state["subtitle_active_color_draft_v1061_applied"]=_c
                                st.rerun()
                        with c3:
                            st.color_picker("Bordo",key="subtitle_outline_color_draft_v1061")
                            if st.button("Applica",key="apply_sub_outline_color_v1061",use_container_width=True):
                                _c=st.session_state["subtitle_outline_color_draft_v1061"]
                                st.session_state["subtitle_outline_color_v18"]=_c
                                st.session_state["subtitle_outline_color"]=_c
                                st.session_state["subtitle_outline_color_draft_v1061_applied"]=_c
                                st.rerun()
''',
'main subtitle explicit color apply')

replace_once(
'''                                        c1,c2,c3=st.columns(3,gap="small")
                                        with c1:
                                            st.session_state["subtitle_text_color"]=st.color_picker("Testo",st.session_state.get("subtitle_text_color","#FFFFFF"),key=f"inline_txtcol_v18_{_this_inline_id}")
                                        with c2:
                                            st.session_state["subtitle_active_color"]=st.color_picker("Attiva",st.session_state.get("subtitle_active_color","#FFD400"),key=f"inline_actcol_v18_{_this_inline_id}")
                                        with c3:
                                            st.session_state["subtitle_outline_color"]=st.color_picker("Bordo",st.session_state.get("subtitle_outline_color","#000000"),key=f"inline_outcol_v18_{_this_inline_id}")
''',
'''                                        _txt_actual=f"inline_txtcol_v18_{_this_inline_id}"
                                        _act_actual=f"inline_actcol_v18_{_this_inline_id}"
                                        _out_actual=f"inline_outcol_v18_{_this_inline_id}"
                                        _txt_draft=f"inline_txtcol_draft_v1061_{_this_inline_id}"
                                        _act_draft=f"inline_actcol_draft_v1061_{_this_inline_id}"
                                        _out_draft=f"inline_outcol_draft_v1061_{_this_inline_id}"
                                        for _draft,_actual,_base,_fallback in (
                                            (_txt_draft,_txt_actual,"subtitle_text_color","#FFFFFF"),
                                            (_act_draft,_act_actual,"subtitle_active_color","#FFD400"),
                                            (_out_draft,_out_actual,"subtitle_outline_color","#000000"),
                                        ):
                                            _actual_value=st.session_state.get(_actual,st.session_state.get(_base,_fallback))
                                            _snap=_draft+"_applied"
                                            if _draft not in st.session_state or st.session_state.get(_snap)!=_actual_value:
                                                st.session_state[_draft]=_actual_value
                                                st.session_state[_snap]=_actual_value
                                        c1,c2,c3=st.columns(3,gap="small")
                                        with c1:
                                            st.color_picker("Testo",key=_txt_draft)
                                            if st.button("Applica",key=f"inline_apply_txt_v1061_{_this_inline_id}",use_container_width=True):
                                                _c=st.session_state[_txt_draft]
                                                st.session_state[_txt_actual]=_c
                                                st.session_state["subtitle_text_color"]=_c
                                                st.session_state[_txt_draft+"_applied"]=_c
                                                st.rerun()
                                        with c2:
                                            st.color_picker("Attiva",key=_act_draft)
                                            if st.button("Applica",key=f"inline_apply_act_v1061_{_this_inline_id}",use_container_width=True):
                                                _c=st.session_state[_act_draft]
                                                st.session_state[_act_actual]=_c
                                                st.session_state["subtitle_active_color"]=_c
                                                st.session_state[_act_draft+"_applied"]=_c
                                                st.rerun()
                                        with c3:
                                            st.color_picker("Bordo",key=_out_draft)
                                            if st.button("Applica",key=f"inline_apply_out_v1061_{_this_inline_id}",use_container_width=True):
                                                _c=st.session_state[_out_draft]
                                                st.session_state[_out_actual]=_c
                                                st.session_state["subtitle_outline_color"]=_c
                                                st.session_state[_out_draft+"_applied"]=_c
                                                st.rerun()
''',
'inline subtitle explicit color apply')

# V106.1 — same first-class filter treatment in the inline editor.
replace_once(
'''                                        st.session_state[_spd_key]=st.select_slider("Velocità",options=[.5,.75,1.0,1.25,1.5,2.0],value=float(st.session_state[_spd_key]),key=f"inline_spd_widget_v18_{_this_inline_id}")

                            st.markdown('<div class="gsf-icon-title gsf-subtitles-title">' + _gsf_v67_badge("text", "Sottotitoli", "lilac") + '</div>', unsafe_allow_html=True, help="Automatici: fa tutto l'AI. Manuali: trascrive la clip e permette di correggere testo e aspetto. Nessuno: video pulito.")
''',
'''                                        st.session_state[_spd_key]=st.select_slider("Velocità",options=[.5,.75,1.0,1.25,1.5,2.0],value=float(st.session_state[_spd_key]),key=f"inline_spd_widget_v18_{_this_inline_id}")

                            st.markdown(
                                '<div class="gsf-icon-title gsf-v1061-filters-title">' +
                                _gsf_v67_badge("edit", "Filtri video", "indigo") +
                                '</div>',
                                unsafe_allow_html=True,
                                help="Modifica importante dell'immagine: visibile subito e inclusa nello Short finale."
                            )
                            st.segmented_control(
                                "Filtro video",
                                list(_GSF_V106_FILTER_PRESETS),
                                key=_filter_key,
                                label_visibility="collapsed"
                            )
                            st.slider(
                                "Intensità filtro",0,100,
                                int(st.session_state.get(_filter_strength_key,70)),
                                5,key=_filter_strength_key,
                                disabled=(st.session_state.get(_filter_key,"Originale")=="Originale")
                            )
                            st.session_state["v106_last_inline_filter_preset"]=st.session_state.get(_filter_key,"Originale")
                            st.session_state["v106_last_inline_filter_intensity"]=st.session_state.get(_filter_strength_key,70)

                            st.markdown('<div class="gsf-icon-title gsf-subtitles-title">' + _gsf_v67_badge("text", "Sottotitoli", "lilac") + '</div>', unsafe_allow_html=True, help="Automatici: fa tutto l'AI. Manuali: trascrive la clip e permette di correggere testo e aspetto. Nessuno: video pulito.")
''',
'inline prominent filters')

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
    'Gaming Shorts Factory · V106.1 BETA RC1',
    1,
)

compile(s,str(out),'exec')
out.write_text(s,encoding='utf-8')
print(f'V106 BETA RC1 editor performance + filters applied: {out}')
