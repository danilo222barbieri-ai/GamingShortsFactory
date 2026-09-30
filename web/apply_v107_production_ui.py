from pathlib import Path
import ast as _gsf_patch_ast

src=Path('/app/GamingShortsFactory_V106_BETA_RC1.py')
out=Path('/app/GamingShortsFactory_V107_PRODUCTION_UI.py')
s=src.read_text(encoding='utf-8')

# Approved UX: hide only the uploaded-source preview before motor selection.
# AI candidate players, Editor 2027 and final-result players stay untouched.
_source_preview_start='''    # PLAYER HTML5 ADATTIVO DEFINITIVO
'''
_source_preview_end='''    st.divider()
    st.markdown('<div class="gsf-icon-title">Come vuoi creare?</div>', unsafe_allow_html=True)
'''
if _source_preview_start not in s or _source_preview_end not in s:
    raise RuntimeError('Uploaded source preview block not found')
_gsf_pre,_gsf_tail=s.split(_source_preview_start,1)
_gsf_hidden,_gsf_post=_gsf_tail.split(_source_preview_end,1)
s=(
    _gsf_pre
    + '    # Anteprima sorgente caricata nascosta per UX; il file resta disponibile internamente.\n'
    + "    st.markdown('<div style=\"height:6px\" aria-hidden=\"true\"></div>', unsafe_allow_html=True)\n"
    + _source_preview_end
    + _gsf_post
)

s=s.replace(
    'Come vuoi creare?',
    'Scegli il tuo motore IA o crea il tuo gameplay'
)

# DEMO UX: i pulsanti delle tre clip AI devono essere visivamente distinti
# dallo stato verde "Video caricato".
_choice_css=r'''
<style id="gsf-demo-choice-color">
[class*="st-key-v71_choose_short_"] button{
    min-height:38px !important;
    border-radius:12px !important;
    background:linear-gradient(135deg,#EDF8FE 0%,#F1EEFF 100%) !important;
    color:#446986 !important;
    border:1px solid #D2E5F1 !important;
    box-shadow:0 5px 14px rgba(79,125,157,.10) !important;
    font-weight:800 !important;
}
[class*="st-key-v71_choose_short_"] button:hover{
    background:linear-gradient(135deg,#E4F5FD 0%,#EAE5FF 100%) !important;
    border-color:#BFDDED !important;
    transform:translateY(-1px) !important;
}
[class*="st-key-v71_short_card_"]{
    padding:8px 8px 10px !important;
    border-radius:18px !important;
}
.v71-card-meta{
    position:relative !important;
    display:flex !important;
    flex-direction:column !important;
    gap:3px !important;
    min-height:70px !important;
    padding:8px 5px 7px !important;
    margin:0 !important;
    overflow:visible !important;
}
.v71-card-meta .v70-short-card-label,
.v71-card-meta .v70-short-card-time,
.v71-card-meta .v70-short-card-score{
    position:static !important;
    inset:auto !important;
    transform:none !important;
    float:none !important;
    display:block !important;
    width:auto !important;
    max-width:100% !important;
    margin:0 !important;
    line-height:1.25 !important;
}
.v71-card-meta .v70-short-card-label{
    min-height:18px !important;
}
.v71-card-meta .v70-short-card-time{
    min-height:17px !important;
    white-space:nowrap !important;
}
.v71-card-meta .v70-short-card-score{
    margin-top:2px !important;
}
[class*="st-key-v71_auto_sub_"]{
    clear:both !important;
    position:relative !important;
    z-index:2 !important;
    margin:6px 4px 7px !important;
    padding:7px 7px 5px !important;
    border-top:1px solid rgba(184,211,227,.55) !important;
}
[class*="st-key-v71_auto_sub_"] [data-testid="stToggle"]{
    padding:0 !important;
    min-height:28px !important;
    align-items:center !important;
}
[class*="st-key-v71_auto_sub_"] label{
    font-size:10.5px !important;
    line-height:1.15 !important;
    color:#667F92 !important;
    font-weight:750 !important;
    white-space:nowrap !important;
}
[class*="st-key-v71_choose_short_"]{
    margin-top:2px !important;
}
.v71-selected-pill{
    box-sizing:border-box !important;
    min-height:38px !important;
    height:38px !important;
    display:flex !important;
    align-items:center !important;
    justify-content:center !important;
    width:100% !important;
    margin:2px 0 0 !important;
    padding:0 10px !important;
    border-radius:12px !important;
    background:linear-gradient(135deg,#EDF8FE 0%,#F1EEFF 100%) !important;
    border:1px solid #D2E5F1 !important;
    box-shadow:0 5px 14px rgba(79,125,157,.10) !important;
    color:#66869E !important;
    font-size:10.5px !important;
    line-height:1 !important;
    font-weight:850 !important;
    letter-spacing:.035em !important;
}
[class*="st-key-edit_ai_"] button{
    min-height:42px !important;
    border-radius:14px !important;
    background:linear-gradient(135deg,#DDF4FE 0%,#EAE5FF 100%) !important;
    color:#315E7A !important;
    border:1px solid #C7E2EF !important;
    box-shadow:0 7px 18px rgba(79,125,157,.12) !important;
    font-weight:850 !important;
}
[class*="st-key-edit_ai_"] button:hover{
    filter:brightness(1.015) !important;
    transform:translateY(-1px) !important;
}
</style>
'''
# Center the moment-selection heading/subtitle in the demo.
s=s.replace("Scegli il tuo momento","")
s=s.replace("Riproduci le tre anteprime direttamente qui e scegli il momento migliore.","")
_moment_heading = '''                st.markdown(
                    '<div class="gsf-moment-head">'
                    '<div class="gsf-moment-title">Scegli il tuo momento</div>'
                    '<div class="gsf-moment-subtitle">Riproduci le tre anteprime direttamente qui e scegli il momento migliore.</div>'
                    '</div>',
                    unsafe_allow_html=True,
                )
'''
_choice_anchor='''                with st.container(key="v71-short-grid"):
'''
if _choice_anchor not in s:
    raise RuntimeError('Demo three-short grid anchor not found')
s=s.replace(
    _choice_anchor,
    '                st.markdown(' + repr(_choice_css) + ', unsafe_allow_html=True)\n'
    + _moment_heading
    + _choice_anchor,
    1,
)

_card_meta_old="""                            st.markdown(
                                f'''<div class="v70-short-card-label">{html.escape(_card["label"])}</div>
                                <div class="v70-short-card-time">{_card["start"]:.0f}s → {_card["end"]:.0f}s · {_card["preview_duration"]:.0f}s</div>
                                {f'<span class="v70-short-card-score">{_quality}</span>' if _quality else ''}''',
                                unsafe_allow_html=True,
                            )
"""
_card_meta_new="""                            st.markdown(
                                f'''<div class="v71-card-meta">
                                <div class="v70-short-card-label">{html.escape(_card["label"])}</div>
                                <div class="v70-short-card-time">{_card["start"]:.0f}s → {_card["end"]:.0f}s · {_card["preview_duration"]:.0f}s</div>
                                {f'<span class="v70-short-card-score">{_quality}</span>' if _quality else ''}
                                </div>''',
                                unsafe_allow_html=True,
                            )
"""
if _card_meta_old not in s:
    raise RuntimeError("Demo card metadata block not found")
s=s.replace(_card_meta_old,_card_meta_new,1)

_card_choose_old='''                            if st.button(
                                "✓ SELEZIONATA" if _is_selected else "SCEGLI QUESTO",
                                key=f"v71_choose_short_{_card['index']}",
                                type="primary" if _is_selected else "secondary",
                                use_container_width=True,
                            ):
                                st.session_state.auto_clip_scelta = float(_card["start"])
                                st.session_state["auto_clip_duration"] = float(_card["preview_duration"])
                                st.session_state["preview_key"] = None
                                st.session_state.pop("preview_bytes", None)
                                st.rerun()
'''
_card_choose_new='''                            _sub_key=f"v71_auto_sub_{_card['index']}"
                            if _sub_key not in st.session_state:
                                st.session_state[_sub_key]=bool(
                                    st.session_state.get("project_subtitles_enabled",True)
                                )
                            _sub_enabled=st.toggle(
                                "Sottotitoli automatici",
                                key=_sub_key,
                            )

                            if _is_selected:
                                st.session_state["project_subtitles_enabled"]=bool(_sub_enabled)
                                st.markdown(
                                    '<div class="v71-selected-pill">✓ CLIP SCELTA</div>',
                                    unsafe_allow_html=True,
                                )
                                _auto_recipe=_gsf_recipe_selected(
                                    "auto",
                                    float(_card["start"]),
                                    float(_card["preview_duration"]),
                                    str(_source_path),
                                    master_token=_gsf_upload_master_token(video),
                                    subtitles_enabled=bool(_sub_enabled),
                                    manual_hook=(
                                        st.session_state.get("hook_testo","")
                                        if st.session_state.get("hook_enabled_v102",True)
                                        else _GSF_HOOK_OFF_V102
                                    )
                                )
                                _gsf_set_final_recipe(_auto_recipe,source_label="AI")
                                st.session_state["publication_preview_bytes"]=_card_bytes
                            else:
                                if st.button(
                                    "SCEGLI QUESTO",
                                    key=f"v71_choose_short_{_card['index']}",
                                    type="secondary",
                                    use_container_width=True,
                                ):
                                    st.session_state.auto_clip_scelta=float(_card["start"])
                                    st.session_state["auto_clip_duration"]=float(_card["preview_duration"])
                                    st.session_state["project_subtitles_enabled"]=bool(_sub_enabled)
                                    _auto_recipe=_gsf_recipe_selected(
                                        "auto",
                                        float(_card["start"]),
                                        float(_card["preview_duration"]),
                                        str(_source_path),
                                        master_token=_gsf_upload_master_token(video),
                                        subtitles_enabled=bool(_sub_enabled),
                                        manual_hook=(
                                            st.session_state.get("hook_testo","")
                                            if st.session_state.get("hook_enabled_v102",True)
                                            else _GSF_HOOK_OFF_V102
                                        )
                                    )
                                    _gsf_set_final_recipe(_auto_recipe,source_label="AI")
                                    st.session_state["publication_preview_bytes"]=_card_bytes
                                    st.session_state["preview_key"]=None
                                    st.session_state.pop("preview_bytes",None)
                                    st.session_state["gsf_editor_2027_inline_open"]=False
                                    st.rerun()
'''
if _card_choose_old not in s:
    raise RuntimeError("Demo card chooser block not found")
s=s.replace(_card_choose_old,_card_choose_new,1)


# DEMO UX: Editor 2027 is the only editor shown, and only after a clip is chosen.
_old_editor_open='''                    if st.button(
                        "MODIFICA NELL’EDITOR",
                        use_container_width=True,
                        key=f"edit_ai_{start:.2f}_{durata_effettiva:.2f}"
                    ):
                        # Apre UNA copia dell'Editor direttamente sotto questa clip.
                        _inline_id=f"{start:.2f}_{durata_effettiva:.2f}"
                        _edit_dir=_gsf_session_mkdtemp("gsf_inline_ai_")
                        _edit_input=os.path.join(_edit_dir,"ai_clip_inline_preview.mp4")
                        _edit_original=str(_source_path)
                        with open(_edit_input,"wb") as _ef:
                            _ef.write(st.session_state.preview_bytes)
                        st.session_state["inline_editor_id"]=_inline_id
                        st.session_state["inline_editor_dir"]=_edit_dir
                        st.session_state["inline_editor_input"]=_edit_input
                        st.session_state["inline_editor_original_input"]=_edit_original
                        st.session_state["inline_editor_source_start"]=float(start)
                        st.session_state["inline_editor_duration"]=float(
                            durata_video(_edit_input) or durata_effettiva
                        )
                        st.session_state.pop("inline_final_bytes",None)
                        # Un solo editor AI aperto alla volta.
                        st.rerun()
'''
_new_editor_open='''                    with st.container(key=f"gsf-major-game-editor_{start:.2f}_{durata_effettiva:.2f}"):
                        _gsf_open_game_editor=st.button(
                            "APRI GAME EDITOR",
                            use_container_width=True,
                            key=f"edit_ai_{start:.2f}_{durata_effettiva:.2f}"
                        )
                        st.markdown(
                            '<div class="gsf-major-note">Ritocca il gameplay nel Game Editor oppure, se ti piace già così, prosegui verso lo Short finale.</div>',
                            unsafe_allow_html=True,
                        )
                    if _gsf_open_game_editor:
                        _selected_sub_key=f"v71_auto_sub_{int(_selected_card['index'])}"
                        _selected_sub_enabled=bool(
                            st.session_state.get(
                                _selected_sub_key,
                                st.session_state.get("project_subtitles_enabled",True)
                            )
                        )
                        st.session_state["project_subtitles_enabled"]=_selected_sub_enabled
                        _auto_recipe=_gsf_recipe_selected(
                            "auto",
                            float(start),
                            float(durata_effettiva),
                            str(_source_path),
                            master_token=_gsf_upload_master_token(video),
                            subtitles_enabled=_selected_sub_enabled,
                            manual_hook=(
                                st.session_state.get("hook_testo","")
                                if st.session_state.get("hook_enabled_v102",True)
                                else _GSF_HOOK_OFF_V102
                            )
                        )
                        _gsf_set_final_recipe(_auto_recipe,source_label="AI")
                        st.session_state["publication_preview_bytes"]=st.session_state.get("preview_bytes")
                        st.session_state["gsf_editor_2027_inline_open"]=True
                        st.session_state["gsf_editor_2027_start"]=float(start)
                        st.session_state.pop("inline_editor_id",None)
                        st.rerun()
'''
if _old_editor_open not in s:
    raise RuntimeError("Demo old inline editor opener not found")
s=s.replace(_old_editor_open,_new_editor_open,1)

_editor_cols_old='''                edit_col, keep_col = st.columns(2)
'''
_editor_cols_new='''                edit_col = st.container()
'''
if _editor_cols_old not in s:
    raise RuntimeError("Demo editor action columns not found")
s=s.replace(_editor_cols_old,_editor_cols_new,1)

_keep_start='''                with keep_col:
'''
_keep_marker='''                # ===== EDITOR INLINE DELLA CLIP AI =====
'''
if _keep_start not in s or _keep_marker not in s:
    raise RuntimeError("Demo old selected/keep bar not found")
_keep_pre,_keep_tail=s.split(_keep_start,1)
_keep_hidden,_keep_post=_keep_tail.split(_keep_marker,1)
s=_keep_pre+_keep_marker+_keep_post

_old_inline_marker='''                # ===== EDITOR INLINE DELLA CLIP AI =====
                _this_inline_id=f"{start:.2f}_{durata_effettiva:.2f}"
                if st.session_state.get("inline_editor_id")==_this_inline_id:
'''
_new_inline_marker='''                # ===== GAME EDITOR INLINE DELLA CLIP AI =====
                _this_inline_id=f"{start:.2f}_{durata_effettiva:.2f}"
                if (
                    st.session_state.get("gsf_editor_2027_inline_open",False)
                    and abs(float(st.session_state.get("gsf_editor_2027_start",start))-float(start))<0.05
                ):
                    try:
                        import sys as _gsf_ed27_sys
                        if "/app/web" not in _gsf_ed27_sys.path:
                            _gsf_ed27_sys.path.insert(0,"/app/web")
                        from editor_2027_embed import (
                            render_editor_2027_embed as _gsf_render_editor_2027_embed,
                            editor_2027_state_key as _gsf_inline_state_key,
                            editor_2027_initial_state as _gsf_inline_initial_state,
                            editor_2027_clip_bounds as _gsf_inline_clip_bounds,
                            editor_2027_render_kwargs as _gsf_inline_render_kwargs,
                        )
                        _gsf_ed27_path=_gsf_bytes_to_preview(
                            st.session_state.get("preview_bytes") or b"",
                            f"editor2027_{start:.2f}"
                        )
                        if _gsf_ed27_path:
                            _gsf_inline_slot=_gsf_inline_state_key(_gsf_ed27_path)
                            _gsf_inline_component_key=_gsf_inline_slot+"_component"
                            _gsf_inline_saved=st.session_state.get(_gsf_inline_slot)
                            if not isinstance(_gsf_inline_saved,dict):
                                _gsf_inline_saved=_gsf_inline_initial_state(float(durata_effettiva))
                            _gsf_inline_state=_gsf_render_editor_2027_embed(
                                _gsf_ed27_path,
                                height=660,
                                key=_gsf_inline_component_key,
                                initial_state=_gsf_inline_saved,
                            )
                            if isinstance(_gsf_inline_state,dict):
                                st.session_state[_gsf_inline_slot]=dict(_gsf_inline_state)
                            else:
                                _gsf_inline_state=dict(_gsf_inline_saved)
                            _gsf_inline_rel_start,_gsf_inline_duration=_gsf_inline_clip_bounds(
                                _gsf_inline_state,float(durata_effettiva)
                            )
                            _gsf_inline_kwargs=_gsf_inline_render_kwargs(
                                _gsf_inline_state,st.session_state
                            )
                            _gsf_inline_recipe=_gsf_recipe_selected(
                                "inline_editor",
                                float(start)+float(_gsf_inline_rel_start),
                                float(_gsf_inline_duration),
                                str(_source_path),
                                master_token=_gsf_upload_master_token(video),
                                subtitles_enabled=bool(_gsf_inline_kwargs.get("subtitles_enabled",True)),
                                render_kwargs=_gsf_inline_kwargs,
                                editor_2027_state=dict(_gsf_inline_state),
                                manual_hook=_GSF_HOOK_OFF_V102,
                            )
                            if st.session_state.get("gsf_final_recipe")!=_gsf_inline_recipe:
                                _gsf_set_final_recipe(
                                    _gsf_inline_recipe,source_label="Editor 2027"
                                )
                    except Exception as _gsf_ed27_exc:
                        st.error("Game Editor non disponibile: "+str(_gsf_ed27_exc))

                # Vecchio Editor disattivato: il Game Editor 2027 è l'unico editor inline.
                if False and st.session_state.get("inline_editor_id")==_this_inline_id:
'''
if _old_inline_marker not in s:
    raise RuntimeError("Demo old inline editor marker not found")
s=s.replace(_old_inline_marker,_new_inline_marker,1)

# Switching among the three AI clips closes any currently open Game Editor.
_old_choice='''                                st.session_state["preview_key"] = None
                                st.session_state.pop("preview_bytes", None)
                                st.rerun()
'''
_new_choice='''                                st.session_state["preview_key"] = None
                                st.session_state.pop("preview_bytes", None)
                                st.session_state["gsf_editor_2027_inline_open"]=False
                                st.rerun()
'''
if _old_choice in s:
    s=s.replace(_old_choice,_new_choice,1)


# DEMO UX: i tre passaggi principali devono leggere come veri spartiacque.
_major_action_css=r'''
<style id="gsf-major-actions">
.gsf-major-note{
    position:relative;
    max-width:620px;
    margin:9px auto 18px;
    padding:10px 14px;
    border-radius:16px;
    border:1px solid #D6E7F2;
    background:linear-gradient(135deg,rgba(239,250,255,.97),rgba(244,241,255,.96));
    box-shadow:0 7px 18px rgba(91,126,170,.08);
    color:#60798E;
    text-align:center;
    font-size:12px;
    font-weight:700;
    line-height:1.35;
}
.gsf-major-note:before{
    content:"";
    position:absolute;
    left:50%;
    top:-6px;
    width:11px;
    height:11px;
    transform:translateX(-50%) rotate(45deg);
    background:#F1F8FE;
    border-left:1px solid #D6E7F2;
    border-top:1px solid #D6E7F2;
}
.st-key-gsf-major-personalize button,
[class*="st-key-gsf-major-personalize"] button,
[class*="st-key-gsf-major-create-ai"] button,
[class*="st-key-gsf-major-game-editor_"] button,
[class*="st-key-gsf-major-create-short"] button{
    min-height:56px !important;
    border-radius:17px !important;
    border:1px solid rgba(255,255,255,.34) !important;
    color:#FFFFFF !important;
    font-size:15px !important;
    font-weight:900 !important;
    letter-spacing:.045em !important;
    transition:transform .16s ease,box-shadow .16s ease,filter .16s ease !important;
}
.st-key-gsf-major-personalize button,
[class*="st-key-gsf-major-personalize"] button,
[class*="st-key-gsf-major-create-ai"] button,
[class*="st-key-gsf-major-game-editor_"] button,
[class*="st-key-gsf-major-create-short"] button{
    background:linear-gradient(135deg,#8B67E8 0%,#6557D9 100%) !important;
    box-shadow:0 12px 28px rgba(104,84,205,.28) !important;
}
[class*="st-key-gsf-major-create-ai"] button:hover,
[class*="st-key-gsf-major-game-editor_"] button:hover,
[class*="st-key-gsf-major-create-short"] button:hover{
    transform:translateY(-2px) !important;
    filter:brightness(1.035) !important;
    box-shadow:0 15px 34px rgba(104,84,205,.36) !important;
}
@media(max-width:750px){
    .gsf-major-note{font-size:11px;padding:9px 12px;margin-bottom:15px}
    .st-key-gsf-major-personalize button,
    [class*="st-key-gsf-major-personalize"] button,
    [class*="st-key-gsf-major-create-ai"] button,
    [class*="st-key-gsf-major-game-editor_"] button,
    [class*="st-key-gsf-major-create-short"] button{
        min-height:52px !important;
        font-size:13px !important;
    }
}
</style>
'''
_major_heading='''    st.markdown('<div class="gsf-icon-title">Scegli il tuo motore IA o crea il tuo gameplay</div>', unsafe_allow_html=True)
'''
_major_heading_centered='''    st.markdown('<div class="gsf-icon-title" style="display:flex;justify-content:center;text-align:center;width:100%;">Scegli il tuo motore IA o crea il tuo gameplay</div>', unsafe_allow_html=True)
'''
if _major_heading not in s:
    raise RuntimeError("Demo major-action heading anchor not found")
s=s.replace(
    _major_heading,
    _major_heading_centered + '    st.markdown(' + repr(_major_action_css) + ', unsafe_allow_html=True)\n',
    1,
)

_engine_note_old='''    st.caption(_engine_help.get(modalita, ""))
'''
_engine_note_new='''    st.markdown(
        '<div class="gsf-major-note">'+html.escape(str(_engine_help.get(modalita,"") or ""))+'</div>',
        unsafe_allow_html=True,
    )
'''
if _engine_note_old not in s:
    raise RuntimeError("Demo engine help note anchor not found")
s=s.replace(_engine_note_old,_engine_note_new,1)

_create_ai_old='''        if st.button("CREA CON AI", use_container_width=True):
'''
_create_ai_new='''        with st.container(key="gsf-major-create-ai"):
            _gsf_create_ai_clicked=st.button("CREA CON IA",use_container_width=True)
            st.markdown(
                '<div class="gsf-major-note">L’IA analizza il gameplay e ti propone i momenti migliori già pronti da scegliere.</div>',
                unsafe_allow_html=True,
            )
        if _gsf_create_ai_clicked:
'''
if _create_ai_old not in s:
    raise RuntimeError("Demo CREA CON IA anchor not found")
s=s.replace(_create_ai_old,_create_ai_new,1)

_create_short_old='''            _v1054_create_final_clicked=st.button(
                "CREA SHORT FINALE",
                type="primary",
                use_container_width=True,
                key="create_final_short_v54"
            )
'''
_create_short_new='''            def _gsf_v107_queue_final_render():
                if st.session_state.get("gsf_v107_final_render_pending") or st.session_state.get("gsf_v107_final_render_running"):
                    return
                _recipe=st.session_state.get("gsf_final_recipe")
                if isinstance(_recipe,dict) and _recipe:
                    st.session_state["gsf_v107_render_recipe_snapshot"]=dict(_recipe)
                _src=""
                if isinstance(_recipe,dict):
                    _src=str(_recipe.get("source_path") or "")
                if not _src:
                    _src=str(st.session_state.get("gsf_source_path") or "")
                if _src:
                    st.session_state["gsf_v107_render_source_snapshot"]=_src
                st.session_state["gsf_v107_final_render_pending"]=True
                st.session_state["gsf_v107_final_render_running"]=True
                st.session_state["gsf_v107_render_started_at"]=__import__("time").time()
                st.session_state["gsf_v107_render_toast_shown"]=False
                st.session_state["gsf_v107_render_complete_notified"]=True

            try:
                _gsf_restore_src=str(
                    st.session_state.get("gsf_v107_render_source_snapshot")
                    or st.session_state.get("gsf_source_path")
                    or ""
                )
                _gsf_restore_root=(__import__("pathlib").Path(
                    __import__("os").environ.get("GSF_RUNTIME_ROOT","/tmp/gsf-runtime")
                )/"sessions").resolve()
                _gsf_restore_rel=__import__("pathlib").Path(_gsf_restore_src).resolve().relative_to(_gsf_restore_root)
                _gsf_restore_sid=str(_gsf_restore_rel.parts[0]) if _gsf_restore_rel.parts else ""
                _gsf_restore_final=_gsf_restore_root/_gsf_restore_sid/"media"/"gaming_short_finale_share.mp4"
                _gsf_restore_started=float(st.session_state.get("gsf_v107_render_started_at",0.0) or 0.0)
                if (
                    _gsf_restore_sid
                    and _gsf_restore_final.is_file()
                    and _gsf_restore_final.stat().st_size>1024
                    and (_gsf_restore_started<=0.0 or _gsf_restore_final.stat().st_mtime>=_gsf_restore_started-1.0)
                ):
                    _gsf_restored_bytes=_gsf_restore_final.read_bytes()
                    st.session_state["publication_final_bytes"]=_gsf_restored_bytes
                    st.session_state["publication_ready"]=True
                    if st.session_state.get("gsf_v107_final_render_running",False):
                        st.session_state["gsf_v107_render_done_toast"]=True
                    st.session_state["gsf_v107_final_render_running"]=False
                    st.session_state["gsf_v107_final_render_pending"]=False
            except Exception:
                pass

            with st.container(key="gsf-major-create-short"):
                _v1054_create_final_clicked=st.button(
                    "CREA SHORT FINALE",
                    use_container_width=True,
                    key="create_final_short_v54",
                    on_click=_gsf_v107_queue_final_render,
                    disabled=bool(st.session_state.get("gsf_v107_final_render_running",False)),
                )

            _gsf_v107_pending=bool(
                st.session_state.pop("gsf_v107_final_render_pending",False)
            )
            if st.session_state.pop("gsf_v107_render_done_toast",False):
                st.toast("✅ Short pronto · apri lo Share Hub per condividerlo.")
            if _gsf_v107_pending and not st.session_state.get("gsf_v107_render_toast_shown",False):
                st.toast("🎬 Short in lavorazione · puoi continuare a usare l’app.")
                st.session_state["gsf_v107_render_toast_shown"]=True
            if _gsf_v107_pending:
                _snap=st.session_state.get("gsf_v107_render_recipe_snapshot")
                if isinstance(_snap,dict) and _snap:
                    st.session_state["gsf_final_recipe"]=dict(_snap)
                _src_snap=str(st.session_state.get("gsf_v107_render_source_snapshot") or "")
                if _src_snap:
                    st.session_state["gsf_source_path"]=_src_snap
                    st.session_state["gsf_editor_source_path"]=_src_snap

            _v1054_create_final_clicked=bool(
                _v1054_create_final_clicked or _gsf_v107_pending
            )
            if _v1054_create_final_clicked:
                try:
                    print(
                        "GSF_FINAL_CREATE_CLICK",
                        "recipe="+str(bool(st.session_state.get("gsf_final_recipe"))),
                        "source="+str(bool(st.session_state.get("gsf_source_path"))),
                        flush=True,
                    )
                except Exception:
                    pass
            st.markdown(
                '<div class="gsf-major-note">Genera la versione finale pronta per il download e la pubblicazione sui tuoi social collegati.</div>',
                unsafe_allow_html=True,
            )
'''
if _create_short_old not in s:
    raise RuntimeError("Demo CREA SHORT anchor not found")
s=s.replace(_create_short_old,_create_short_new,1)

# A Streamlit rerun can obsolete the script while FFmpeg keeps running. Persist
# a successful final MP4 inside the locked renderer itself, before returning to
# Streamlit, so changing UI cannot lose the result or start duplicate renders.
_gsf_locked_render_old='''        return subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
        )
'''
_gsf_locked_render_new='''        _gsf_locked_result=subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
        )
        if _gsf_locked_result.returncode==0:
            try:
                _gsf_out=__import__("pathlib").Path(str(cmd[-1])).resolve()
                if "gsf_final_v54_" in str(_gsf_out.parent):
                    _gsf_os=__import__("os")
                    _gsf_root=(__import__("pathlib").Path(
                        _gsf_os.environ.get("GSF_RUNTIME_ROOT","/tmp/gsf-runtime")
                    )/"sessions").resolve()
                    _gsf_rel=_gsf_out.relative_to(_gsf_root)
                    _gsf_sid=str(_gsf_rel.parts[0]) if _gsf_rel.parts else ""
                    if _gsf_sid and _gsf_out.is_file() and _gsf_out.stat().st_size>1024:
                        _gsf_media=_gsf_root/_gsf_sid/"media"
                        _gsf_media.mkdir(parents=True,exist_ok=True)
                        _gsf_stable=_gsf_media/"gaming_short_finale_share.mp4"
                        _gsf_tmp=_gsf_media/"gaming_short_finale_share.mp4.tmp"
                        __import__("shutil").copyfile(_gsf_out,_gsf_tmp)
                        _gsf_os.replace(_gsf_tmp,_gsf_stable)
                        print(
                            "GSF_FINAL_STABLE_READY",
                            "sid="+_gsf_sid,
                            "bytes="+str(_gsf_stable.stat().st_size),
                            flush=True,
                        )
                        try:
                            _gsf_u=__import__("urllib.request",fromlist=["Request","urlopen"])
                            _gsf_j=__import__("json")
                            _gsf_payload=_gsf_j.dumps({
                                "title":"Short pronto",
                                "body":"Il tuo Short è pronto. Tocca per aprire lo Share Hub.",
                                "url":"/#share-hub",
                                "tag":"gsf-short-ready",
                            }).encode("utf-8")
                            _gsf_req=_gsf_u.Request(
                                "http://127.0.0.1:8502/push/notify",
                                data=_gsf_payload,
                                headers={
                                    "Content-Type":"application/json",
                                    "X-GSF-Session-ID":_gsf_sid,
                                },
                                method="POST",
                            )
                            _gsf_u.urlopen(_gsf_req,timeout=4).read()
                        except Exception as _gsf_push_exc:
                            print("GSF_FINAL_PUSH_WARN",repr(str(_gsf_push_exc)),flush=True)
            except Exception as _gsf_stable_exc:
                print("GSF_FINAL_STABLE_WARN",repr(str(_gsf_stable_exc)),flush=True)
        return _gsf_locked_result
'''
if _gsf_locked_render_old not in s:
    raise RuntimeError("V107 locked renderer persistence anchor missing")
s=s.replace(_gsf_locked_render_old,_gsf_locked_render_new,1)

# Instrument the real V105.4 render gate so a click cannot disappear silently.
_gsf_final_gate='''            if _v1054_create_final_clicked:
                _final_dir=_gsf_session_mkdtemp("gsf_final_v54_")
'''
_gsf_final_gate_new='''            if _v1054_create_final_clicked:
                try:
                    print(
                        "GSF_FINAL_RENDER_ENTER",
                        "recipe="+str(bool(st.session_state.get("gsf_final_recipe"))),
                        "source="+str(bool(st.session_state.get("gsf_source_path"))),
                        flush=True,
                    )
                except Exception:
                    pass
                _final_dir=_gsf_session_mkdtemp("gsf_final_v54_")
'''
if _gsf_final_gate not in s:
    raise RuntimeError("V107 final render gate anchor missing")
s=s.replace(_gsf_final_gate,_gsf_final_gate_new,1)

# DEMO mobile cleanup: keep only the blue primary CTA for the final Short.
# Remove the older peach/orange heading so the action is not duplicated.
s=s.replace(
    '''        st.markdown('<div class="gsf-icon-title">' + _gsf_v67_badge("play", "Crea lo Short finale", "peach") + '</div>', unsafe_allow_html=True)
''',
    '',
    1,
)

# Remove an internal technical caption accidentally exposed in the preview card.
s=s.replace(
    "Stable identity shared by AI, single render and batch render.",
    "",
)


# Production keeps the real connected-account publication flow from V106.\n\n# Production footer: supported social channels.
_social_footer = r'''
st.markdown("""
<style>
.gsf-social-footer{
  margin:16px auto 4px;
  padding:14px 10px 8px;
  text-align:center;
  color:#60788d;
}
.gsf-social-footer-title{
  margin-bottom:9px;
  font-size:.80rem;
  font-weight:850;
  letter-spacing:.03em;
  color:#526f86;
}
.gsf-social-row{
  display:flex;
  justify-content:center;
  align-items:center;
  gap:8px;
  flex-wrap:nowrap;
}
.gsf-social-icon{
  width:38px;
  height:38px;
  flex:0 0 38px;
  border-radius:12px;
  display:grid;
  place-items:center;
  border:1px solid #D8E8F3;
  background:linear-gradient(145deg,#F8FCFF,#EEF6FC);
  box-shadow:0 5px 13px rgba(74,110,142,.08);
  color:#547790;
}
.gsf-social-icon svg{
  width:18px;
  height:18px;
  display:block;
  fill:none;
  stroke:currentColor;
  stroke-width:1.8;
  stroke-linecap:round;
  stroke-linejoin:round;
}
.gsf-social-icon.youtube svg .yt-fill{
  fill:currentColor;
  stroke:none;
}
.gsf-social-icon.facebook{
  font-size:19px;
  font-weight:900;
  font-family:Arial,sans-serif;
  line-height:1;
}
@media(max-width:600px){
  .gsf-social-footer{margin-top:12px;padding-top:12px}
  .gsf-social-row{gap:7px}
  .gsf-social-icon{
    width:36px;
    height:36px;
    flex-basis:36px;
    border-radius:11px;
  }
  .gsf-social-icon svg{width:17px;height:17px}
}
</style>
<div class="gsf-social-footer">
  <div class="gsf-social-footer-title">Social supportati</div>
  <div class="gsf-social-row">
    <span class="gsf-social-icon facebook" aria-label="Facebook" title="Facebook">f</span>
    <span class="gsf-social-icon instagram" aria-label="Instagram" title="Instagram">
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <rect x="3.5" y="3.5" width="17" height="17" rx="5"></rect>
        <circle cx="12" cy="12" r="4"></circle>
        <circle cx="17.5" cy="6.8" r="1"></circle>
      </svg>
    </span>
    <span class="gsf-social-icon youtube" aria-label="YouTube" title="YouTube">
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path d="M21 7.2c-.2-1.4-1.3-2.5-2.7-2.7C16.6 4.2 14.3 4 12 4s-4.6.2-6.3.5C4.3 4.7 3.2 5.8 3 7.2A30 30 0 0 0 2.8 12c0 1.6.1 3.2.2 4.8.2 1.4 1.3 2.5 2.7 2.7 1.7.3 4 .5 6.3.5s4.6-.2 6.3-.5c1.4-.2 2.5-1.3 2.7-2.7.1-1.6.2-3.2.2-4.8s-.1-3.2-.2-4.8z"></path>
        <path class="yt-fill" d="M10 8.7v6.6l5.5-3.3z"></path>
      </svg>
    </span>
    <span class="gsf-social-icon tiktok" aria-label="TikTok" title="TikTok">
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path d="M14.2 4v9.1a4.2 4.2 0 1 1-3.5-4.1"></path>
        <path d="M14.2 4c.5 2.5 2.1 4.1 4.7 4.5"></path>
      </svg>
    </span>
  </div>
</div>
""", unsafe_allow_html=True)
'''
s = s.rstrip() + "\n\n" + _social_footer.lstrip()

# Match the approved demo social area on phones: keep the three real publish
# actions compact and side-by-side instead of Streamlit stacking them as huge cards.
_social_mobile_demo_layout = r'''
st.markdown("""
<style id="gsf-v107-social-mobile-demo-layout">
@media(max-width:600px){
  div[data-testid="stHorizontalBlock"]:has(.st-key-v69_social_youtube),
  div[data-testid="stHorizontalBlock"]:has(.st-key-v69_social_tiktok),
  div[data-testid="stHorizontalBlock"]:has(.st-key-v69_social_instagram){
    display:grid !important;
    grid-template-columns:repeat(3,minmax(0,1fr)) !important;
    gap:7px !important;
    align-items:stretch !important;
  }
  div[data-testid="stHorizontalBlock"]:has(.st-key-v69_social_youtube) > div,
  div[data-testid="stHorizontalBlock"]:has(.st-key-v69_social_tiktok) > div,
  div[data-testid="stHorizontalBlock"]:has(.st-key-v69_social_instagram) > div{
    width:100% !important;
    min-width:0 !important;
    flex:initial !important;
  }
  .st-key-v69_social_youtube,
  .st-key-v69_social_tiktok,
  .st-key-v69_social_instagram{
    min-height:0 !important;
    padding:0 !important;
    margin:0 !important;
  }
  .st-key-v69_social_youtube button,
  .st-key-v69_social_tiktok button,
  .st-key-v69_social_instagram button{
    min-height:54px !important;
    height:54px !important;
    padding:0 6px !important;
    border-radius:14px !important;
    font-size:11px !important;
    line-height:1 !important;
    box-shadow:0 6px 16px rgba(65,96,121,.09) !important;
  }
  .st-key-v69_social_youtube button p,
  .st-key-v69_social_tiktok button p,
  .st-key-v69_social_instagram button p{
    font-size:11px !important;
    white-space:nowrap !important;
  }
  .gsf-icon-title:has(.v67-badge-indigo){
    margin-bottom:10px !important;
  }
}
</style>
""", unsafe_allow_html=True)
'''
s = s.rstrip() + "\n\n" + _social_mobile_demo_layout.lstrip()

# Creator Hub entry point: always reachable without disturbing the current video/session.
_creator_hub_entry = r'''
st.markdown("""
<style>
.gsf-account-fab{
  position:fixed;
  top:14px;
  right:18px;
  z-index:999990;
  display:flex;
  align-items:center;
  gap:7px;
  height:38px;
  padding:0 13px;
  border-radius:14px;
  border:1px solid #D8E8F3;
  background:rgba(255,255,255,.90);
  -webkit-backdrop-filter:blur(14px);
  backdrop-filter:blur(14px);
  box-shadow:0 7px 20px rgba(52,91,122,.12);
  color:#476E8A !important;
  text-decoration:none !important;
  font-size:11px;
  font-weight:900;
  letter-spacing:.025em;
}
.gsf-account-fab svg{
  width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:1.8;
  stroke-linecap:round;stroke-linejoin:round;
}
@media(max-width:600px){
  .gsf-account-fab{
    top:auto;
    bottom:calc(18px + env(safe-area-inset-bottom, 0px));
    right:12px;
    width:auto;
    min-width:82px;
    height:46px;
    padding:0 14px;
    justify-content:center;
    border-radius:15px;
    z-index:2147483000;
    background:rgba(255,255,255,.96);
    box-shadow:0 10px 26px rgba(52,91,122,.22);
  }
  .gsf-account-fab svg{width:19px;height:19px}
  .gsf-account-fab span{
    display:inline;
    font-size:10px;
    letter-spacing:.035em;
  }
}
</style>
<a class="gsf-account-fab" href="/account" target="_self" aria-label="Apri Creator Hub">
  <svg viewBox="0 0 24 24" aria-hidden="true">
    <circle cx="12" cy="8" r="4"></circle>
    <path d="M4.5 20c.9-4 3.4-6 7.5-6s6.6 2 7.5 6"></path>
  </svg>
  <span>CREATOR HUB</span>
</a>
""", unsafe_allow_html=True)
'''
s = s.rstrip() + "\n\n" + _creator_hub_entry.lstrip()


# Compact production footer on mobile/desktop and remove the redundant "Collega social" link.
_footer_compact = r'''
st.markdown("""
<style id="gsf-v107-footer-compact">
/* Remove the redundant first footer link while preserving Privacy, Termini and Contatti. */
a[href*="social"]:not(.gsf-account-fab),
a[href*="connect"]:not(.gsf-account-fab){
  display:none !important;
}
/* Pull the legal/version/social footer into a single compact visual block. */
.v67-footer{
  margin:4px auto 2px !important;
  padding:2px 0 !important;
  text-align:center !important;
  font-size:.70rem !important;
  line-height:1.2 !important;
  color:#74899A !important;
}
.gsf-legal-footer{
  margin:2px auto 1px !important;
  padding:1px 0 !important;
  font-size:.70rem !important;
  line-height:1.15 !important;
}
.gsf-legal-footer a{font-weight:700 !important}
.gsf-social-footer{
  margin:1px auto 0 !important;
  padding:1px 6px 0 !important;
}
.gsf-social-footer-title{display:none !important}
.gsf-social-row{gap:6px !important}
.gsf-social-icon{
  width:26px !important;height:26px !important;flex-basis:26px !important;
  border-radius:8px !important;box-shadow:0 3px 8px rgba(74,110,142,.06) !important;
}
.gsf-social-icon svg{width:13px !important;height:13px !important}
@media(max-width:600px){
  .v67-footer{margin:3px auto 1px !important;font-size:.66rem !important}
  .gsf-legal-footer{margin:1px auto !important;font-size:.67rem !important}
  .gsf-social-footer{margin:0 auto !important;padding:0 4px !important}
  .gsf-social-row{gap:5px !important}
  .gsf-social-icon{width:24px !important;height:24px !important;flex-basis:24px !important;border-radius:7px !important}
  .gsf-social-icon svg{width:12px !important;height:12px !important}
  [data-testid="stAppViewContainer"] hr{
    margin-top:.24rem !important;
    margin-bottom:.24rem !important;
  }
  [data-testid="stAppViewContainer"] footer,
  [data-testid="stAppViewContainer"] footer > div{
    margin-top:0 !important;
    padding-top:0 !important;
    padding-bottom:0 !important;
  }
}
</style>
<script>
(()=>{
  const clean=()=>{
    document.querySelectorAll('a').forEach(a=>{
      const txt=(a.textContent||'').trim().toLowerCase();
      if(txt==='collega social') a.style.display='none';
      if(txt==='privacy'){
        /* Privacy is the first legal item: remove every leftover separator before it. */
        let n=a.previousSibling;
        while(n){
          const prev=n.previousSibling;
          const t=(n.textContent||'').trim();
          if(t==='' || t==='·' || t==='•' || t==='|' || t==='.' || t==='-') n.remove();
          else break;
          n=prev;
        }
        const parent=a.parentElement;
        if(parent){
          parent.childNodes.forEach(node=>{
            if(node===a)return;
            if(node.compareDocumentPosition && (node.compareDocumentPosition(a)&Node.DOCUMENT_POSITION_FOLLOWING)){
              const t=(node.textContent||'').trim();
              if(t==='·' || t==='•' || t==='|' || t==='.') node.remove();
            }
          });
        }
      }
    });
    /* Keep the version line compact: one line instead of two. */
    document.querySelectorAll('.v67-footer br').forEach(br=>{
      br.replaceWith(document.createTextNode(' · '));
    });
  };
  clean();
  new MutationObserver(clean).observe(document.body,{childList:true,subtree:true});
})();
</script>
""", unsafe_allow_html=True)
'''
s = s.rstrip() + "\n\n" + _footer_compact.lstrip()

# Mobile footer/social polish: compact vertical rhythm and high-contrast publication icons.
_footer_mobile_v2 = r'''
st.markdown("""
<style id="gsf-v107-footer-mobile-v2">
/* Footer: remove the large dead zones visible on phones. */
.gsf-social-footer{
  margin:2px auto 0 !important;
  padding:2px 8px 0 !important;
}
.gsf-social-footer-title{margin:4px 0 6px !important}
@media(max-width:600px){
  [data-testid="stAppViewContainer"] hr{margin:.28rem 0 !important}
  [data-testid="stAppViewContainer"] footer,
  [data-testid="stAppViewContainer"] footer > div{
    margin:0 !important;padding:0 !important;
  }
  .gsf-social-footer{margin:0 auto !important;padding:0 6px !important}
  .gsf-social-footer-title{margin:2px 0 4px !important}
  .gsf-social-footer-icons{gap:7px !important;margin:0 !important}
  .gsf-social-footer-icons a{width:46px !important;height:46px !important}
  /* Publication buttons: icons were washed out on the light mobile background. */
  [class*="st-key-"] button svg{opacity:1 !important}
  .gsf-publish-grid button,.gsf-social-publish button{
    color:#355a73 !important;
    font-weight:800 !important;
  }
  .gsf-publish-grid button svg,.gsf-social-publish button svg{
    stroke:#355a73 !important;fill:none !important;opacity:1 !important;
  }
}
</style>
<script>
(()=>{
 const enhance=()=>{
   const heading=[...document.querySelectorAll('div,p,h1,h2,h3,h4')].find(x=>(x.textContent||'').trim()==='Pubblicazione diretta');
   if(!heading)return;
   const root=heading.parentElement?.parentElement?.parentElement || heading.parentElement;
   if(root) root.classList.add('gsf-publish-grid');
   const buttons=root?[...root.querySelectorAll('button')]:[];
   const names=['YouTube','TikTok','Instagram'];
   buttons.forEach((b,i)=>{ if(i<3 && !(b.textContent||'').trim()) b.setAttribute('aria-label',names[i]); });
   /* Facebook is a visual destination placeholder until its publishing connector is implemented. */
   if(root && !root.querySelector('[data-gsf-facebook]')){
     const row=buttons[0]?.parentElement?.parentElement;
     if(row){
       const fb=document.createElement('div');
       fb.dataset.gsfFacebook='1';
       fb.title='Facebook';
       fb.setAttribute('aria-label','Facebook');
       fb.innerHTML='<div style="width:100%;height:100%;min-height:58px;border:1px solid #c9dbe8;border-radius:16px;display:flex;align-items:center;justify-content:center;font:900 26px Arial;color:#355a73;background:rgba(255,255,255,.58)">f</div>';
       row.insertBefore(fb,row.firstChild);
     }
   }
 };
 enhance(); new MutationObserver(enhance).observe(document.body,{childList:true,subtree:true});
})();
</script>
""", unsafe_allow_html=True)
'''
s = s.rstrip() + "\n\n" + _footer_mobile_v2.lstrip()

# Hide the redundant publication heading; the social buttons are self-explanatory.
_publish_heading_cleanup = r'''
st.markdown("""
<script>
(()=>{
 const clean=()=>{
   document.querySelectorAll('div,p,h1,h2,h3,h4').forEach(el=>{
     if((el.textContent||'').trim()==='Pubblicazione diretta'){
       const block=el.closest('[data-testid="stMarkdownContainer"]') || el;
       block.style.display='none';
       block.style.margin='0';
       block.style.padding='0';
     }
   });
 };
 clean(); new MutationObserver(clean).observe(document.body,{childList:true,subtree:true});
})();
</script>
""", unsafe_allow_html=True)
'''
s = s.rstrip() + "\n\n" + _publish_heading_cleanup.lstrip()

# Final result UX — final-only, always-open publish flow; download stays last.
# These source rewrites must happen here in the patcher, never inside the generated app.
s=s.replace(
    'if st.session_state.get("show_social_publish_v54", False):',
    'if _has_final:'
)

# Final UX owns this area: remove the legacy publication title and the ad above it.
s=s.replace(
    'st.markdown(\'<div class="gsf-icon-title">\' + _gsf_v67_badge("publish", "Pubblicazione diretta", "indigo") + \'</div>\', unsafe_allow_html=True)',
    'st.empty()'
)
_gsf_final_ad_old='''            with st.container(key="v1054_ad_after_final_result"):
                st.markdown(
                    '<aside class="v67-ad" aria-label="Spazio pubblicitario">Pubblicità</aside>',
                    unsafe_allow_html=True,
                )

'''
s=s.replace(_gsf_final_ad_old,'',1)

# The obsolete large PUBBLICA launcher is hidden by the scoped browser cleanup below.
# Do not rewrite the source block here: preserving the original code avoids brittle
# multiline regex changes while the composer is already forced open by _has_final.

# Final publication must stay Streamlit-native. Do not inject executable JS in
# st.markdown: on mobile Markdown can render the script source as page text.
_gsf_social_row_old='''                _social_columns = st.columns(3, gap="small")
                for _column, _platform in zip(
                    _social_columns, ("YouTube", "TikTok", "Instagram")
                ):
'''
_gsf_social_row_new='''                _social_columns = st.columns(4, gap="small")
                for _column, _platform in zip(
                    _social_columns, ("Facebook", "Instagram", "YouTube", "TikTok")
                ):
'''
if _gsf_social_row_old not in s:
    raise RuntimeError("V107 native social selector anchor missing")
s=s.replace(_gsf_social_row_old,_gsf_social_row_new,1)

# Replace the obsolete title with the approved milestone CTA, rendered by the
# same native Streamlit button system used by CREA CON IA / CREA SHORT.
_gsf_social_selected_anchor='''                _selected_social = st.session_state.get("social_selected_v59")
                _social_columns = st.columns(4, gap="small")
'''
_gsf_social_selected_new='''                _selected_social = st.session_state.get("social_selected_v59")
                _social_columns = st.columns(4, gap="small")
'''
if _gsf_social_selected_anchor not in s:
    raise RuntimeError("V107 native publish heading anchor missing")
s=s.replace(_gsf_social_selected_anchor,_gsf_social_selected_new,1)

# Facebook gets its own native composer. Direct Facebook video publishing is
# intentionally not faked: connection is available now; direct publish remains
# dependent on Meta Page publishing permissions.
_gsf_auth_anchor='''                _auth_url = st.session_state.get("social_auth_url_v77", "")
'''
_gsf_facebook_panel='''                if _selected_social == "Facebook":
                    with st.container(key="v1055_social_composer_facebook"):
                        st.markdown(
                            '<div class="v1055-social-head"><strong>Dettagli Facebook</strong><span>Compila i dati da pubblicare</span></div>',
                            unsafe_allow_html=True,
                        )
                        st.text_input("Titolo",key="social_title_facebook_v107")
                        st.text_area("Descrizione",key="social_description_facebook_v107",height=120)
                        st.text_input("Hashtag",key="social_hashtags_facebook_v107")
                        st.link_button(
                            "COLLEGA FACEBOOK",
                            "/account/facebook/start",
                            use_container_width=True,
                        )
                        st.caption("La pubblicazione video diretta su Facebook richiede i permessi Meta della Pagina.")

'''
if _gsf_auth_anchor not in s:
    raise RuntimeError("V107 Facebook composer insertion anchor missing")
s=s.replace(_gsf_auth_anchor,_gsf_facebook_panel+_gsf_auth_anchor,1)

# Rename the existing upper PUBBLICA launcher without restructuring the
# surrounding Streamlit columns. The old sibling download stays in source but
# is hidden by CSS below; this avoids brittle source surgery.
_gsf_action_tree=_gsf_patch_ast.parse(s)
_gsf_social_if=None
for _node in _gsf_patch_ast.walk(_gsf_action_tree):
    if isinstance(_node,_gsf_patch_ast.If):
        _body=_gsf_patch_ast.get_source_segment(s,_node) or ""
        _test=(_gsf_patch_ast.get_source_segment(s,_node.test) or "").strip()
        if _test=="_has_final" and "social_selected_v59" in _body and "_social_columns" in _body:
            _gsf_social_if=_node
            break
if _gsf_social_if is None:
    raise RuntimeError("V107 native final social block missing before action cleanup")

_gsf_publish_calls=[]
for _node in _gsf_patch_ast.walk(_gsf_action_tree):
    if not isinstance(_node,_gsf_patch_ast.Call) or _node.lineno>=_gsf_social_if.lineno:
        continue
    _fn=_node.func
    if not (isinstance(_fn,_gsf_patch_ast.Attribute) and _fn.attr=="button"):
        continue
    if not _node.args or not isinstance(_node.args[0],_gsf_patch_ast.Constant):
        continue
    _label=str(_node.args[0].value or "")
    if "PUBBLICA" not in _label.upper() or "CREA" in _label.upper():
        continue
    _seg=_gsf_patch_ast.get_source_segment(s,_node) or ""
    if "social_publish_confirm" in _seg:
        continue
    _gsf_publish_calls.append(_node)
if len(_gsf_publish_calls)!=1:
    raise RuntimeError("V107 expected one legacy pre-social PUBBLICA launcher, found "+str(len(_gsf_publish_calls)))

_gsf_pub_call=_gsf_publish_calls[0]
_gsf_old_pub_call=_gsf_patch_ast.get_source_segment(s,_gsf_pub_call) or ""
_gsf_pub_call.args[0]=_gsf_patch_ast.Constant(value="CONDIVIDI O SCARICA")
_gsf_pub_call.keywords=[_kw for _kw in _gsf_pub_call.keywords if _kw.arg!="key"]
_gsf_pub_call.keywords.append(_gsf_patch_ast.keyword(arg="key",value=_gsf_patch_ast.Constant(value="gsf_share_download_top")))
_gsf_patch_ast.fix_missing_locations(_gsf_pub_call)
_gsf_new_pub_call=_gsf_patch_ast.unparse(_gsf_pub_call)
if not _gsf_old_pub_call:
    raise RuntimeError("V107 could not read legacy PUBBLICA launcher")
s=s.replace(_gsf_old_pub_call,_gsf_new_pub_call,1)

_gsf_top_download='''            with _download_col:
'''
_gsf_top_download_i=s.find(_gsf_top_download)
if _gsf_top_download_i<0:
    raise RuntimeError("V107 top download block missing")
_gsf_top_download_end=s.find('''            if _has_final:
''',_gsf_top_download_i)
if _gsf_top_download_end<0:
    raise RuntimeError("V107 top download block end missing")
_gsf_top_download_block=s[_gsf_top_download_i:_gsf_top_download_end]
s=s[:_gsf_top_download_i]+s[_gsf_top_download_end:]

# Add one final download button at the end of the always-open social block.
_gsf_pub_tree=_gsf_patch_ast.parse(s)
_gsf_pub_lines=s.splitlines(keepends=True)
_gsf_pub_nodes=[]
for _node in _gsf_patch_ast.walk(_gsf_pub_tree):
    if not isinstance(_node,_gsf_patch_ast.If):
        continue
    _body=_gsf_patch_ast.get_source_segment(s,_node) or ""
    _test=(_gsf_patch_ast.get_source_segment(s,_node.test) or "").strip()
    if _test=="_has_final" and "social_selected_v59" in _body and "_social_columns" in _body:
        _gsf_pub_nodes.append(_node)
if len(_gsf_pub_nodes)!=1:
    raise RuntimeError("V107 expected one exact _has_final social block, found "+str(len(_gsf_pub_nodes)))
_gsf_pub_node=_gsf_pub_nodes[0]
_gsf_pub_line=_gsf_pub_lines[_gsf_pub_node.lineno-1]
_gsf_pub_indent=_gsf_pub_line[:len(_gsf_pub_line)-len(_gsf_pub_line.lstrip())]+'    '
_gsf_download_tail=[
    _gsf_pub_indent+'with st.container(key="gsf-final-download-after-social"):\n',
    _gsf_pub_indent+'    st.download_button("SCARICA",_final_video,"gaming_short_finale.mp4","video/mp4",use_container_width=True,key="gsf_final_download_after_social")\n',
]
_gsf_pub_lines[_gsf_pub_node.end_lineno:_gsf_pub_node.end_lineno]=_gsf_download_tail
s="".join(_gsf_pub_lines)

# Compact the already-existing final success state instead of rendering a
# second "Short finale pronto" card below the action bar.
for _old_success in (
    'st.success("✅ Short finale pronto")',
    "st.success('✅ Short finale pronto')",
    'st.success("Short finale pronto")',
    "st.success('Short finale pronto')",
):
    if _old_success in s:
        s=s.replace(
            _old_success,
            'st.markdown(\'<div class="gsf-final-status"><span class="gsf-hub-state"><i></i>SHORT PRONTO</span><span class="gsf-hub-kicker">SHARE HUB</span></div>\',unsafe_allow_html=True)',
            1,
        )
        break

_final_publish_v4 = r'''
st.markdown("""
<style id="gsf-v107-final-publish-v4">
.gsf-final-status{
  margin:0 auto 10px;
  padding:6px 2px;
  color:#4f7b64;
  font-size:12px;
  font-weight:800;
  line-height:1.2;
}
.st-key-gsf-final-top-action-row{
  width:100% !important;
}
div[data-testid="stHorizontalBlock"]:has(.st-key-gsf_share_download_top) > div[data-testid="column"]:has(.st-key-gsf_share_download_top){
  flex:1 1 100% !important;
  width:100% !important;
  max-width:100% !important;
}
div[data-testid="stHorizontalBlock"]:has(.st-key-gsf_share_download_top) > div[data-testid="column"]:not(:has(.st-key-gsf_share_download_top)){
  display:none !important;
}
.st-key-gsf-final-top-action-row [data-testid="stHorizontalBlock"],
.st-key-gsf-final-top-action-row [data-testid="column"]{
  width:100% !important;
  flex:1 1 100% !important;
}
div[data-testid="stHorizontalBlock"]:has(.st-key-download_final_v54) > div[data-testid="column"]:not(:has(.st-key-download_final_v54)),
div[data-testid="stHorizontalBlock"]:has(.st-key-download_final_v54_fallback) > div[data-testid="column"]:not(:has(.st-key-download_final_v54_fallback)){
  flex:1 1 100% !important;
  width:100% !important;
}
.st-key-v69_social_facebook button,
.st-key-v69_social_instagram button,
.st-key-v69_social_youtube button,
.st-key-v69_social_tiktok button{
  min-height:76px !important;
  border-radius:16px !important;
  border:1px solid #d1e1eb !important;
  background:linear-gradient(145deg,#ffffff,#edf5fa) !important;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.98),0 7px 17px rgba(65,96,121,.09) !important;
  font-size:11px !important;
  font-weight:850 !important;
  display:flex !important;
  flex-direction:column !important;
  align-items:center !important;
  justify-content:center !important;
  gap:6px !important;
  padding:8px 7px !important;
  overflow:hidden !important;
}
.st-key-v69_social_facebook [data-testid="stBaseButton-primary"],
.st-key-v69_social_instagram [data-testid="stBaseButton-primary"],
.st-key-v69_social_youtube [data-testid="stBaseButton-primary"],
.st-key-v69_social_tiktok [data-testid="stBaseButton-primary"],
.st-key-v69_social_facebook button[kind="primary"],
.st-key-v69_social_instagram button[kind="primary"],
.st-key-v69_social_youtube button[kind="primary"],
.st-key-v69_social_tiktok button[kind="primary"]{
  border-color:#9c88ea !important;
  background:linear-gradient(145deg,#f5f0ff,#ece7ff) !important;
  color:#29465b !important;
  box-shadow:0 7px 18px rgba(104,84,205,.16) !important;
}
.st-key-v69_social_facebook button:before,
.st-key-v69_social_instagram button:before,
.st-key-v69_social_youtube button:before,
.st-key-v69_social_tiktok button:before{
  width:38px !important;
  height:38px !important;
  min-width:38px !important;
  min-height:38px !important;
  flex:0 0 38px !important;
  display:grid !important;
  place-items:center !important;
  border-radius:50% !important;
  box-sizing:border-box !important;
  opacity:1 !important;
  filter:none !important;
  background-image:none !important;
  box-shadow:0 5px 12px rgba(42,69,88,.16),inset 0 1px 0 rgba(255,255,255,.24) !important;
  font-family:Arial,sans-serif !important;
  text-align:center !important;
}
.st-key-v69_social_facebook button:before{
  content:"f" !important;
  background:#1877F2 !important;
  color:#fff !important;
  font-size:31px !important;
  font-weight:900 !important;
  line-height:38px !important;
}
.st-key-v69_social_instagram button:before{
  content:"◎" !important;
  background:linear-gradient(145deg,#833AB4 0%,#C13584 32%,#E1306C 55%,#F77737 78%,#FCAF45 100%) !important;
  color:#fff !important;
  font-size:31px !important;
  font-weight:900 !important;
  line-height:35px !important;
}
.st-key-v69_social_youtube button:before{
  content:"▶" !important;
  background:#FF0000 !important;
  color:#fff !important;
  font-size:21px !important;
  font-weight:900 !important;
  line-height:38px !important;
  padding-left:2px !important;
}
.st-key-v69_social_tiktok button:before{
  content:"♪" !important;
  background:#111 !important;
  color:#fff !important;
  font-size:29px !important;
  font-weight:900 !important;
  line-height:38px !important;
  text-shadow:-1.5px 0 #25F4EE,1.5px 0 #FE2C55 !important;
}
.st-key-v69_social_facebook button p,
.st-key-v69_social_instagram button p,
.st-key-v69_social_youtube button p,
.st-key-v69_social_tiktok button p,
.st-key-v69_social_facebook button span,
.st-key-v69_social_instagram button span,
.st-key-v69_social_youtube button span,
.st-key-v69_social_tiktok button span{
  color:#29465b !important;
  opacity:1 !important;
  font-weight:850 !important;
}
[class*="st-key-v1055_social_composer_"]{
  box-sizing:border-box !important;
  width:100% !important;
  margin:9px auto 12px !important;
  padding:14px !important;
  border:1px solid rgba(116,154,184,.24) !important;
  border-radius:20px !important;
  background:linear-gradient(180deg,rgba(247,252,255,.97),rgba(255,255,255,.99)) !important;
  box-shadow:0 10px 28px rgba(36,85,125,.07) !important;
}
[class*="st-key-social_publish_confirm_"] button,
.st-key-gsf-final-download-after-social button,
[class*="st-key-gsf-final-download-after-social"] button{
  min-height:48px !important;
  border-radius:14px !important;
  font-weight:900 !important;
}
.st-key-gsf-final-download-after-social,
[class*="st-key-gsf-final-download-after-social"]{
  margin-top:12px !important;
}
.st-key-gsf-final-download-after-social button,
[class*="st-key-gsf-final-download-after-social"] button{
  min-height:48px !important;
  border:1px solid rgba(69,165,214,.42) !important;
  background:linear-gradient(135deg,#78D7F3 0%,#50B9E9 100%) !important;
  color:#173B53 !important;
  box-shadow:0 9px 21px rgba(70,164,211,.20),inset 0 1px 0 rgba(255,255,255,.45) !important;
  font-size:13px !important;
  font-weight:900 !important;
}
.st-key-download_final_v54,
.st-key-download_final_v54_fallback,
div[data-testid="column"]:has(.st-key-download_final_v54),
div[data-testid="column"]:has(.st-key-download_final_v54_fallback),
.st-key-v1053_ad_before_final,
.st-key-v1054_ad_after_ai,
.st-key-v1055_ad_after_ai,
.st-key-v1054_ad_after_final_action,
.st-key-v1054_ad_after_final_result{
  display:none !important;
}
@media(max-width:600px){
  div[data-testid="stHorizontalBlock"]:has(.st-key-v69_social_facebook){
    display:grid !important;
    grid-template-columns:repeat(2,minmax(0,1fr)) !important;
    gap:8px !important;
  }
  div[data-testid="stHorizontalBlock"]:has(.st-key-v69_social_facebook) > div{
    width:100% !important;
  }
  .st-key-v69_social_facebook button,
  .st-key-v69_social_instagram button,
  .st-key-v69_social_youtube button,
  .st-key-v69_social_tiktok button{
    min-height:72px !important;
    border-radius:15px !important;
  }
}
</style>
""", unsafe_allow_html=True)
'''
s = s.rstrip() + "\n\n" + _final_publish_v4.lstrip()

_share_hub_glass = r'''
st.markdown("""
<style id="gsf-share-hub-glass">
@keyframes gsfHubIn{
  from{opacity:0;transform:translateY(8px) scale(.988)}
  to{opacity:1;transform:translateY(0) scale(1)}
}
.gsf-final-status{
  width:max-content !important;
  max-width:100% !important;
  display:flex !important;
  align-items:center !important;
  justify-content:space-between !important;
  gap:16px !important;
  margin:4px 0 10px !important;
  padding:8px 12px !important;
  border:1px solid rgba(181,216,235,.28) !important;
  border-radius:999px !important;
  background:linear-gradient(145deg,rgba(29,44,58,.70),rgba(52,66,83,.50)) !important;
  -webkit-backdrop-filter:blur(18px) saturate(1.2) !important;
  backdrop-filter:blur(18px) saturate(1.2) !important;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.12),0 10px 24px rgba(30,54,72,.12) !important;
  color:#E9F6FC !important;
  animation:gsfHubIn .28s ease-out both;
}
.gsf-hub-state{
  display:flex;
  align-items:center;
  gap:7px;
  font-size:10px;
  font-weight:900;
  letter-spacing:.11em;
  color:#EAF9F3 !important;
}
.gsf-hub-state i{
  width:7px;
  height:7px;
  display:block;
  border-radius:50%;
  background:#62D6B2;
  box-shadow:0 0 12px rgba(98,214,178,.85);
}
.gsf-hub-kicker{
  font-size:8px;
  font-weight:900;
  letter-spacing:.16em;
  color:#8FDDF0 !important;
  opacity:.94;
}
div[data-testid="stHorizontalBlock"]:has(.st-key-v69_social_facebook){
  position:relative !important;
  margin:2px 0 10px !important;
  padding:12px !important;
  border:1px solid rgba(181,216,235,.22) !important;
  border-radius:26px !important;
  background:
    radial-gradient(circle at 18% 0%,rgba(89,207,238,.14),transparent 34%),
    radial-gradient(circle at 84% 100%,rgba(138,127,232,.15),transparent 38%),
    linear-gradient(145deg,rgba(25,39,53,.78),rgba(48,61,79,.60)) !important;
  -webkit-backdrop-filter:blur(24px) saturate(1.25) !important;
  backdrop-filter:blur(24px) saturate(1.25) !important;
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,.11),
    0 18px 42px rgba(20,45,64,.16) !important;
  overflow:hidden !important;
  animation:gsfHubIn .30s ease-out both;
}
.st-key-v69_social_facebook button,
.st-key-v69_social_instagram button,
.st-key-v69_social_youtube button,
.st-key-v69_social_tiktok button{
  min-height:74px !important;
  border-radius:18px !important;
  border:1px solid rgba(219,238,248,.14) !important;
  background:linear-gradient(145deg,rgba(255,255,255,.105),rgba(255,255,255,.045)) !important;
  color:#EDF7FC !important;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.08),0 8px 20px rgba(6,20,30,.12) !important;
  -webkit-backdrop-filter:blur(12px) !important;
  backdrop-filter:blur(12px) !important;
  transition:transform .16s ease,border-color .16s ease,background .16s ease,box-shadow .16s ease !important;
}
.st-key-v69_social_facebook button:hover,
.st-key-v69_social_instagram button:hover,
.st-key-v69_social_youtube button:hover,
.st-key-v69_social_tiktok button:hover{
  transform:translateY(-2px) !important;
  border-color:rgba(120,219,244,.36) !important;
  background:linear-gradient(145deg,rgba(255,255,255,.15),rgba(255,255,255,.07)) !important;
}
.st-key-v69_social_facebook [data-testid="stBaseButton-primary"],
.st-key-v69_social_instagram [data-testid="stBaseButton-primary"],
.st-key-v69_social_youtube [data-testid="stBaseButton-primary"],
.st-key-v69_social_tiktok [data-testid="stBaseButton-primary"],
.st-key-v69_social_facebook button[kind="primary"],
.st-key-v69_social_instagram button[kind="primary"],
.st-key-v69_social_youtube button[kind="primary"],
.st-key-v69_social_tiktok button[kind="primary"]{
  border-color:rgba(105,223,255,.66) !important;
  background:
    linear-gradient(145deg,rgba(89,207,238,.24),rgba(138,127,232,.22)) !important;
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,.13),
    0 0 0 1px rgba(105,223,255,.10),
    0 12px 28px rgba(89,207,238,.13) !important;
}
.st-key-v69_social_facebook button p,
.st-key-v69_social_instagram button p,
.st-key-v69_social_youtube button p,
.st-key-v69_social_tiktok button p,
.st-key-v69_social_facebook button span,
.st-key-v69_social_instagram button span,
.st-key-v69_social_youtube button span,
.st-key-v69_social_tiktok button span{
  color:#EEF8FC !important;
  opacity:1 !important;
  font-size:10px !important;
  font-weight:850 !important;
  letter-spacing:.025em !important;
}
.st-key-v69_social_facebook button:before,
.st-key-v69_social_instagram button:before,
.st-key-v69_social_youtube button:before,
.st-key-v69_social_tiktok button:before{
  width:42px !important;
  height:42px !important;
  min-width:42px !important;
  min-height:42px !important;
  flex:0 0 42px !important;
  border:1px solid rgba(255,255,255,.18) !important;
  box-shadow:0 8px 18px rgba(4,16,25,.26),inset 0 1px 0 rgba(255,255,255,.26) !important;
}
[class*="st-key-v1055_social_composer_"]{
  margin:8px 0 12px !important;
  padding:16px !important;
  border:1px solid rgba(181,216,235,.20) !important;
  border-radius:24px !important;
  background:
    radial-gradient(circle at 100% 0%,rgba(138,127,232,.12),transparent 34%),
    linear-gradient(145deg,rgba(25,39,53,.82),rgba(47,61,78,.66)) !important;
  -webkit-backdrop-filter:blur(24px) saturate(1.20) !important;
  backdrop-filter:blur(24px) saturate(1.20) !important;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.10),0 18px 38px rgba(20,45,64,.14) !important;
  animation:gsfHubIn .24s ease-out both;
}
[class*="st-key-v1055_social_composer_"] label,
[class*="st-key-v1055_social_composer_"] p,
[class*="st-key-v1055_social_composer_"] span,
[class*="st-key-v1055_social_composer_"] .v1055-social-head{
  color:#EAF5FA !important;
}
[class*="st-key-v1055_social_composer_"] input,
[class*="st-key-v1055_social_composer_"] textarea{
  border:1px solid rgba(203,229,242,.16) !important;
  background:rgba(6,16,25,.32) !important;
  color:#F2FAFD !important;
  -webkit-backdrop-filter:blur(10px) !important;
  backdrop-filter:blur(10px) !important;
}
[class*="st-key-v1055_social_composer_"] input::placeholder,
[class*="st-key-v1055_social_composer_"] textarea::placeholder{
  color:#95A9B7 !important;
  opacity:.95 !important;
}
.st-key-gsf-final-download-after-social,
[class*="st-key-gsf-final-download-after-social"]{
  margin-top:10px !important;
  animation:gsfHubIn .30s ease-out both;
}
.st-key-gsf-final-download-after-social button,
[class*="st-key-gsf-final-download-after-social"] button{
  min-height:46px !important;
  border-radius:16px !important;
  border:1px solid rgba(105,223,255,.34) !important;
  background:linear-gradient(135deg,rgba(89,207,238,.94),rgba(76,161,222,.94)) !important;
  color:#102E42 !important;
  box-shadow:0 10px 24px rgba(66,166,215,.20),inset 0 1px 0 rgba(255,255,255,.42) !important;
}
@media(max-width:600px){
  .gsf-final-status{padding:7px 10px !important;gap:12px !important}
  .gsf-hub-state{font-size:9px}
  .gsf-hub-kicker{font-size:7px}
  div[data-testid="stHorizontalBlock"]:has(.st-key-v69_social_facebook){
    padding:9px !important;
    gap:8px !important;
    border-radius:22px !important;
  }
  .st-key-v69_social_facebook button,
  .st-key-v69_social_instagram button,
  .st-key-v69_social_youtube button,
  .st-key-v69_social_tiktok button{
    min-height:68px !important;
    border-radius:16px !important;
  }
  .st-key-v69_social_facebook button:before,
  .st-key-v69_social_instagram button:before,
  .st-key-v69_social_youtube button:before,
  .st-key-v69_social_tiktok button:before{
    width:38px !important;
    height:38px !important;
    min-width:38px !important;
    min-height:38px !important;
    flex-basis:38px !important;
  }
  [class*="st-key-v1055_social_composer_"]{
    padding:13px !important;
    border-radius:20px !important;
  }
}
</style>
""", unsafe_allow_html=True)
'''
s = s.rstrip() + "\n\n" + _share_hub_glass.lstrip()

# Web/mobile spacing hygiene and removal of leaked literal newline markers.
_layout_hygiene = r'''
st.markdown("""
<style id="gsf-layout-hygiene">
.st-key-gsf-major-create-ai,
.st-key-gsf-major-create-short,
[class*="st-key-gsf-major-game-editor_"],
.st-key-gsf-major-personalize{
  margin-top:10px !important;
  margin-bottom:10px !important;
}
[class*="st-key-gsf-major-game-editor_"]{
  margin-top:18px !important;
}
.gsf-major-note{
  margin:7px auto 13px !important;
}
.gsf-moment-head{
  margin:8px auto 13px !important;
}
.v67-ad{
  margin-top:12px !important;
  margin-bottom:12px !important;
}
.st-key-v1055_ad_manual_after_editor{
  margin-top:-24px !important;
}
[data-testid="stAppViewContainer"] hr{
  margin-top:.55rem !important;
  margin-bottom:.55rem !important;
}
@media(max-width:600px){
  .st-key-gsf-major-create-ai,
  .st-key-gsf-major-create-short,
  [class*="st-key-gsf-major-game-editor_"],
  .st-key-gsf-major-personalize{
    margin-top:8px !important;
    margin-bottom:8px !important;
  }
  [class*="st-key-gsf-major-game-editor_"]{margin-top:14px !important}
  .gsf-major-note{margin:6px auto 10px !important}
  .gsf-moment-head{margin:6px auto 10px !important}
  .v67-ad{margin-top:9px !important;margin-bottom:9px !important}
  .st-key-v1055_ad_manual_after_editor{margin-top:-52px !important}
  [data-testid="stAppViewContainer"] hr{margin:.38rem 0 !important}
}
</style>
<script>
(()=>{
 const slashN=String.fromCharCode(92)+'n';
 const isOnlyNewlineMarker=(value)=>{
   let t=String(value||'').replace(/\s/g,'');
   if(!t || !t.includes(slashN)) return false;
   while(t.includes(slashN)) t=t.split(slashN).join('');
   return t==='';
 };
 const cleanArtifacts=()=>{
   /* Some legacy markers are not inside stMarkdownContainer.
      Remove the exact visible backslash-n text wherever Streamlit mounts it. */
   const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
   const doomed=[];
   let node;
   while((node=walker.nextNode())){
     const parent=node.parentElement;
     if(!parent || ['SCRIPT','STYLE','TEXTAREA','INPUT'].includes(parent.tagName)) continue;
     if(isOnlyNewlineMarker(node.nodeValue)) doomed.push(node);
   }
   doomed.forEach(node=>{
     const parent=node.parentElement;
     node.nodeValue='';
     const host=parent?.closest('[data-testid="stElementContainer"]')
       || parent?.closest('[data-testid="stMarkdownContainer"]')
       || parent;
     if(host && !(host.textContent||'').trim()){
       host.style.display='none';
       host.style.height='0';
       host.style.minHeight='0';
       host.style.margin='0';
       host.style.padding='0';
       host.style.overflow='hidden';
     }
   });
 };
 cleanArtifacts();
 new MutationObserver(cleanArtifacts).observe(document.body,{childList:true,subtree:true,characterData:true});
})();
</script>
""", unsafe_allow_html=True)
'''
s = s.rstrip() + "\n\n" + _layout_hygiene.lstrip()

# DEMO typography: one coherent UI font across the whole product.
_demo_typography = r'''
st.markdown("""
<style id="gsf-demo-global-typography">
:root{
  --gsf-ui-font: ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
}
html,body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] p,
[data-testid="stAppViewContainer"] span,
[data-testid="stAppViewContainer"] div,
[data-testid="stAppViewContainer"] label,
[data-testid="stAppViewContainer"] button,
[data-testid="stAppViewContainer"] input,
[data-testid="stAppViewContainer"] textarea,
[data-testid="stAppViewContainer"] select,
[data-testid="stAppViewContainer"] h1,
[data-testid="stAppViewContainer"] h2,
[data-testid="stAppViewContainer"] h3,
[data-testid="stAppViewContainer"] h4,
[data-testid="stAppViewContainer"] h5,
[data-testid="stAppViewContainer"] h6,
.gsf-major-note,
.gsf-demo-publish,
.gsf-social-footer,
.gsf-account-fab{
  font-family:var(--gsf-ui-font) !important;
}
code,pre,kbd,samp{
  font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,"Liberation Mono",monospace !important;
}
</style>
""", unsafe_allow_html=True)
'''
s = s.rstrip() + "\n\n" + _demo_typography.lstrip()


# Final footer override: compact three-row footer (version / legal / social).
_footer_override_v4 = r'''
st.markdown("""
<style id="gsf-footer-override-v4">
.v67-footer,.gsf-legal-footer,.gsf-social-footer{
  display:none !important;
  height:0 !important;
  min-height:0 !important;
  margin:0 !important;
  padding:0 !important;
  overflow:hidden !important;
}
.gsf-footer-v4{
  width:min(720px,calc(100% - 20px));
  margin:4px auto 7px;
  padding:7px 8px 6px;
  border-top:1px solid rgba(195,214,227,.65);
  display:flex;
  flex-direction:column;
  justify-content:center;
  align-items:center;
  gap:9px;
  color:#6d8496;
  text-align:center;
}
.gsf-footer-v4 .version{
  font-size:10px;
  line-height:1.1;
  font-weight:750;
}
.gsf-footer-v4 .legal{
  display:flex;
  align-items:center;
  justify-content:center;
  gap:6px;
  font-size:10px;
  line-height:1.1;
}
.gsf-footer-v4 a{
  color:#647f92 !important;
  text-decoration:none !important;
  font-weight:750;
}
.gsf-footer-v4 .socials{
  display:flex;
  align-items:center;
  justify-content:center;
  gap:8px;
}
.gsf-footer-v4 .social{
  width:30px;
  height:30px;
  border-radius:10px;
  border:1px solid rgba(192,213,227,.92);
  background:
    linear-gradient(145deg,rgba(255,255,255,.98),rgba(235,244,250,.94));
  display:grid;
  place-items:center;
  color:#5d778b !important;
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,.96),
    0 4px 10px rgba(65,96,121,.08);
  transition:transform .16s ease,box-shadow .16s ease,border-color .16s ease,background .16s ease;
}
.gsf-footer-v4 .social:hover{
  transform:translateY(-2px);
  border-color:#b8d5e7;
  background:linear-gradient(145deg,#f9fdff,#e8f3fa);
  box-shadow:
    inset 0 1px 0 #fff,
    0 7px 14px rgba(65,96,121,.13);
}
.gsf-footer-v4 .social svg{
  width:15px;
  height:15px;
  display:block;
  fill:currentColor;
}
.gsf-footer-v4 .social.ig svg{width:16px;height:16px}
.gsf-footer-v4 .social.tw svg{width:16px;height:16px}
[data-testid="stAppViewContainer"] .block-container{padding-bottom:.55rem !important}
@media(max-width:600px){
  .gsf-footer-v4{
    margin:3px auto 5px;
    padding:6px 6px 5px;
    gap:7px;
  }
  .gsf-footer-v4 .version,
  .gsf-footer-v4 .legal{font-size:9px}
  .gsf-footer-v4 .socials{gap:7px}
  .gsf-footer-v4 .social{
    width:28px;
    height:28px;
    border-radius:9px;
  }
  .gsf-footer-v4 .social svg{width:14px;height:14px}
  .gsf-footer-v4 .social.ig svg,
  .gsf-footer-v4 .social.tw svg{width:15px;height:15px}
  [data-testid="stAppViewContainer"] .block-container{padding-bottom:.35rem !important}
}
</style>
<div class="gsf-footer-v4">
  <div class="version">Gaming Shorts Factory · Beta</div>
  <div class="legal">
    <a href="/privacy" target="_blank">Privacy</a>
    <span>·</span>
    <a href="/terms" target="_blank">Termini</a>
    <span>·</span>
    <a href="/contact" target="_blank">Contatti</a>
  </div>
  <div class="socials" aria-label="Social">
    <a class="social fb" href="https://www.facebook.com/profile.php?id=61595124112318&amp;locale=it_IT" target="_blank" rel="noopener noreferrer" aria-label="Facebook" title="Facebook">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M13.7 22v-9h3l.5-3.5h-3.5V7.3c0-1 .3-1.7 1.8-1.7h1.9V2.5c-.3 0-1.5-.1-2.8-.1-2.8 0-4.7 1.7-4.7 4.8v2.7H7v3.5h2.9v9h3.8z"/></svg>
    </a>
    <a class="social ig" href="https://www.instagram.com/gamingshortsfactory/" target="_blank" rel="noopener noreferrer" aria-label="Instagram" title="Instagram">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7.4 2h9.2A5.4 5.4 0 0 1 22 7.4v9.2a5.4 5.4 0 0 1-5.4 5.4H7.4A5.4 5.4 0 0 1 2 16.6V7.4A5.4 5.4 0 0 1 7.4 2Zm0 2A3.4 3.4 0 0 0 4 7.4v9.2A3.4 3.4 0 0 0 7.4 20h9.2a3.4 3.4 0 0 0 3.4-3.4V7.4A3.4 3.4 0 0 0 16.6 4H7.4Zm9.6 1.5a1.25 1.25 0 1 1 0 2.5 1.25 1.25 0 0 1 0-2.5ZM12 7a5 5 0 1 1 0 10 5 5 0 0 1 0-10Zm0 2a3 3 0 1 0 0 6 3 3 0 0 0 0-6Z"/></svg>
    </a>
    <a class="social yt" href="https://www.youtube.com/@Dans222nrg" target="_blank" rel="noopener noreferrer" aria-label="YouTube" title="YouTube">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M23 12s0-3.7-.5-5.4a3 3 0 0 0-2.1-2.1C18.7 4 12 4 12 4s-6.7 0-8.4.5a3 3 0 0 0-2.1 2.1C1 8.3 1 12 1 12s0 3.7.5 5.4a3 3 0 0 0 2.1 2.1C5.3 20 12 20 12 20s6.7 0 8.4-.5a3 3 0 0 0 2.1-2.1C23 15.7 23 12 23 12Zm-13.2 3.4V8.6l6 3.4-6 3.4Z"/></svg>
    </a>
    <a class="social tt" href="https://www.tiktok.com/@gamingshortsfactory" target="_blank" rel="noopener noreferrer" aria-label="TikTok" title="TikTok">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15.6 2c.4 2.3 1.8 3.7 4.1 3.9v3.3a9.1 9.1 0 0 1-4.1-1v6.4a6.6 6.6 0 1 1-5.7-6.5v3.4a3.2 3.2 0 1 0 2.4 3.1V2h3.3Z"/></svg>
    </a>
    <a class="social tw" href="https://www.twitch.tv/dan222s86" target="_blank" rel="noopener noreferrer" aria-label="Twitch" title="Twitch">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4.3 2 2 6.1v14h5.1V24l3.8-3.9h3.1L20 14V2H4.3Zm13.6 11-3.4 3.4H11l-2.9 2.9v-2.9H4V4.1h13.9V13ZM15.2 6.5h-2v5.2h2V6.5Zm-4.7 0h-2v5.2h2V6.5Z"/></svg>
    </a>
  </div>
</div>
<script>
(()=>{
  const clean=()=>{
    const slashN=String.fromCharCode(92)+'n';
    document.querySelectorAll('[data-testid="stMarkdownContainer"]').forEach(el=>{
      const t=(el.textContent||'').replace(/\\s/g,'');
      if(t && t.split(slashN).join('')===''){
        const host=el.parentElement||el;
        host.style.display='none';
        host.style.height='0';
        host.style.minHeight='0';
        host.style.margin='0';
        host.style.padding='0';
        host.style.overflow='hidden';
      }
    });
  };
  clean();
  new MutationObserver(clean).observe(document.body,{childList:true,subtree:true});
})();
</script>
""", unsafe_allow_html=True)
'''
s = s.rstrip() + "\n\n" + _footer_override_v4.lstrip()

# DEMO global metallic visual language: same cold blue-grey treatment used in the lower site.
_demo_metallic_look = r'''
st.markdown("""
<style id="gsf-demo-metallic-look">
:root{
  --gsf-metal-0:#FBFDFF;
  --gsf-metal-1:#F6FAFD;
  --gsf-metal-2:#EEF5FA;
  --gsf-metal-3:#E7F0F6;
  --gsf-metal-border:#D3E3ED;
  --gsf-metal-border-strong:#C3D8E5;
  --gsf-metal-text:#536F84;
  --gsf-metal-title:#2F526A;
  --gsf-metal-shadow:0 8px 22px rgba(65,96,121,.10);
  --gsf-metal-shadow-hover:0 11px 27px rgba(65,96,121,.15);
}
[data-testid="stAppViewContainer"]{
  background:
    radial-gradient(circle at 50% 0%,rgba(239,247,252,.72),transparent 38%),
    linear-gradient(180deg,#FFFFFF 0%,#FAFCFE 45%,#F5F9FC 100%) !important;
}
.gsf-major-note,
.gsf-demo-publish,
.gsf-social-icon,
.gsf-account-fab,
.v71-selected-pill,
[class*="st-key-v71_short_card_"]{
  border-color:var(--gsf-metal-border) !important;
  background:linear-gradient(145deg,var(--gsf-metal-0) 0%,var(--gsf-metal-2) 58%,#F3F1FA 100%) !important;
  box-shadow:var(--gsf-metal-shadow) !important;
  color:var(--gsf-metal-text) !important;
}
.gsf-major-note:before{
  background:var(--gsf-metal-1) !important;
  border-color:var(--gsf-metal-border) !important;
}
.gsf-demo-publish-btn,
[data-testid="stButton"] button,
[data-testid="stDownloadButton"] button{
  border:1px solid var(--gsf-metal-border) !important;
  background:linear-gradient(145deg,#FFFFFF 0%,var(--gsf-metal-2) 100%) !important;
  color:var(--gsf-metal-title) !important;
  box-shadow:0 6px 16px rgba(65,96,121,.09) !important;
}
.gsf-demo-publish-btn:hover,
[data-testid="stButton"] button:hover,
[data-testid="stDownloadButton"] button:hover{
  border-color:var(--gsf-metal-border-strong) !important;
  box-shadow:var(--gsf-metal-shadow-hover) !important;
}
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input,
[data-testid="stSelectbox"] > div > div,
[data-baseweb="select"] > div{
  border-color:var(--gsf-metal-border) !important;
  background:linear-gradient(180deg,#FFFFFF 0%,#F7FAFC 100%) !important;
  color:var(--gsf-metal-title) !important;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.88),0 4px 13px rgba(65,96,121,.055) !important;
}
[data-testid="stExpander"],
[data-testid="stMetric"],
[data-testid="stVerticalBlockBorderWrapper"]{
  border-color:var(--gsf-metal-border) !important;
}
.gsf-icon-title,
.gsf-demo-publish-title,
.gsf-social-footer-title,
.gsf-moment-title{
  color:var(--gsf-metal-title) !important;
}
.gsf-moment-head{
  width:100%;
  margin:8px auto 15px;
  text-align:center;
}
.gsf-moment-title{
  font-size:17px;
  font-weight:900;
  letter-spacing:.018em;
  line-height:1.2;
}
.gsf-moment-subtitle{
  max-width:680px;
  margin:5px auto 0;
  color:#718A9D;
  font-size:12px;
  font-weight:700;
  line-height:1.4;
}
@media(max-width:600px){
  .gsf-moment-title{font-size:15px}
  .gsf-moment-subtitle{font-size:11px;padding:0 8px}
}
</style>
""", unsafe_allow_html=True)
'''
s = s.rstrip() + "\n\n" + _demo_metallic_look.lstrip()


# DEMO upload visual: lock circle and its icon/text group to the exact center.
_demo_upload_centering = r'''
st.markdown("""
<style id="gsf-demo-upload-centering">
.st-key-v73-upload-shell{
  width:100% !important;
  margin-left:auto !important;
  margin-right:auto !important;
  text-align:center !important;
}
.gsf-v89-upload-visual{
  left:auto !important;
  right:auto !important;
  margin-left:auto !important;
  margin-right:auto !important;
  padding:0 !important;
  align-items:center !important;
  justify-content:center !important;
  gap:14px !important;
  text-align:center !important;
}
.gsf-v89-upload-icon{
  display:block !important;
  width:100% !important;
  margin:0 !important;
  text-align:center !important;
  line-height:1 !important;
}
.gsf-v89-upload-label{
  display:flex !important;
  align-items:center !important;
  justify-content:center !important;
  width:150px !important;
  max-width:150px !important;
  min-height:40px !important;
  margin:0 auto !important;
  padding:0 !important;
  text-align:center !important;
  line-height:1.18 !important;
}
@media(max-width:600px){
  .gsf-v89-upload-visual{gap:12px !important}
  .gsf-v89-upload-label{
    width:144px !important;
    max-width:144px !important;
    min-height:38px !important;
  }
}
</style>
""", unsafe_allow_html=True)
'''
s = s.rstrip() + "\n\n" + _demo_upload_centering.lstrip()


# DEMO dialogs: match the site's typography and metallic language.
_demo_dialog_style = r'''
st.markdown("""
<style id="gsf-demo-dialog-style">
[data-testid="stDialog"],
[data-testid="stDialog"] *,
[role="dialog"],
[role="dialog"] *{
  font-family:var(--gsf-ui-font,ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif) !important;
}
[data-testid="stDialog"] p,
[data-testid="stDialog"] span,
[role="dialog"] p,
[role="dialog"] span{
  color:#536F84 !important;
  font-weight:700 !important;
  letter-spacing:.005em !important;
}
[data-testid="stDialog"] h1,
[data-testid="stDialog"] h2,
[data-testid="stDialog"] h3,
[role="dialog"] h1,
[role="dialog"] h2,
[role="dialog"] h3{
  color:#2F526A !important;
  font-weight:900 !important;
  letter-spacing:.015em !important;
}
</style>
""", unsafe_allow_html=True)
'''
s = s.rstrip() + "\n\n" + _demo_dialog_style.lstrip()


# Final visual override: the four milestone CTAs must be exactly the same.
_major_cta_final_override = r'''
st.markdown("""
<style id="gsf-major-actions-final-override">
.st-key-gsf_share_download_top button,
[class*="st-key-gsf_share_download_top"] button,
.st-key-gsf-final-top-action-row button,
[class*="st-key-gsf-final-top-action-row"] button,
.st-key-gsf-major-create-ai button,
.st-key-gsf-major-personalize button,
[class*="st-key-gsf-major-personalize"] button,
[class*="st-key-gsf-major-create-ai"] button,
.st-key-gsf-major-personalize button,
[class*="st-key-gsf-major-personalize"] button,
[class*="st-key-gsf-major-game-editor_"] button,
.st-key-gsf-major-create-short button,
[class*="st-key-gsf-major-create-short"] button,
[class*="st-key-edit_ai_"] button,
.st-key-create_final_short_v54 button,
[class*="st-key-create_final_short_v54"] button,
.st-key-gsf_demo_social_publish_preview button,
[class*="st-key-gsf_demo_social_publish_preview"] button,
[class*="st-key-social_publish_confirm_"] button{
    width:100% !important;
    height:56px !important;
    min-height:56px !important;
    max-height:56px !important;
    padding:0 18px !important;
    border-radius:17px !important;
    border:1px solid rgba(255,255,255,.34) !important;
    background:linear-gradient(135deg,#8B67E8 0%,#6557D9 100%) !important;
    color:#FFFFFF !important;
    font-size:15px !important;
    font-weight:900 !important;
    line-height:1 !important;
    letter-spacing:.045em !important;
    box-shadow:0 12px 28px rgba(104,84,205,.28) !important;
}
.st-key-gsf_share_download_top button:hover,
[class*="st-key-gsf_share_download_top"] button:hover,
.st-key-gsf-final-top-action-row button:hover,
[class*="st-key-gsf-final-top-action-row"] button:hover,
.st-key-gsf-major-create-ai button:hover,
[class*="st-key-gsf-major-create-ai"] button:hover,
.st-key-gsf-major-personalize button:hover,
[class*="st-key-gsf-major-personalize"] button:hover,
[class*="st-key-gsf-major-game-editor_"] button:hover,
.st-key-gsf-major-create-short button:hover,
[class*="st-key-gsf-major-create-short"] button:hover,
[class*="st-key-edit_ai_"] button:hover,
.st-key-create_final_short_v54 button:hover,
[class*="st-key-create_final_short_v54"] button:hover,
.st-key-gsf_demo_social_publish_preview button:hover,
[class*="st-key-gsf_demo_social_publish_preview"] button:hover,
[class*="st-key-social_publish_confirm_"] button:hover{
    transform:translateY(-2px) !important;
    filter:brightness(1.035) !important;
    box-shadow:0 15px 34px rgba(104,84,205,.36) !important;
}
@media(max-width:750px){
    .st-key-gsf_share_download_top button,
    [class*="st-key-gsf_share_download_top"] button,
    .st-key-gsf-final-top-action-row button,
    [class*="st-key-gsf-final-top-action-row"] button,
    .st-key-gsf-major-create-ai button,
    .st-key-gsf-major-personalize button,
    [class*="st-key-gsf-major-personalize"] button,
    [class*="st-key-gsf-major-create-ai"] button,
    [class*="st-key-gsf-major-game-editor_"] button,
    .st-key-gsf-major-create-short button,
    [class*="st-key-gsf-major-create-short"] button,
    [class*="st-key-edit_ai_"] button,
    .st-key-create_final_short_v54 button,
    [class*="st-key-create_final_short_v54"] button,
    .st-key-gsf_demo_social_publish_preview button,
    [class*="st-key-gsf_demo_social_publish_preview"] button,
    [class*="st-key-social_publish_confirm_"] button{
        height:52px !important;
        min-height:52px !important;
        max-height:52px !important;
        font-size:13px !important;
    }
}

</style>
""", unsafe_allow_html=True)
'''
s = s.rstrip() + "\n\n" + _major_cta_final_override.lstrip()

_share_cta_exact_override = r'''
st.markdown("""
<style id="gsf-share-cta-exact-create-short">
.st-key-gsf_share_download_top button,
[class*="st-key-gsf_share_download_top"] button,
.st-key-gsf_share_download_top button[kind="primary"],
[class*="st-key-gsf_share_download_top"] button[kind="primary"]{
  width:100% !important;
  height:56px !important;
  min-height:56px !important;
  max-height:56px !important;
  padding:0 18px !important;
  border-radius:17px !important;
  border:1px solid rgba(255,255,255,.34) !important;
  background:linear-gradient(135deg,#8B67E8 0%,#6557D9 100%) !important;
  color:#FFFFFF !important;
  font-family:var(--gsf-ui-font,ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif) !important;
  font-size:15px !important;
  font-weight:900 !important;
  line-height:1 !important;
  letter-spacing:.045em !important;
  box-shadow:0 12px 28px rgba(104,84,205,.28) !important;
}
.st-key-gsf_share_download_top button *,
[class*="st-key-gsf_share_download_top"] button *{
  color:#FFFFFF !important;
  font-family:var(--gsf-ui-font,ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif) !important;
  font-size:15px !important;
  font-weight:900 !important;
  letter-spacing:.045em !important;
}
@media(max-width:750px){
  .st-key-gsf_share_download_top button,
  [class*="st-key-gsf_share_download_top"] button{
    height:52px !important;
    min-height:52px !important;
    max-height:52px !important;
    font-size:13px !important;
  }
  .st-key-gsf_share_download_top button *,
  [class*="st-key-gsf_share_download_top"] button *{
    font-size:13px !important;
  }
}
</style>
""", unsafe_allow_html=True)
'''
s = s.rstrip() + "\n\n" + _share_cta_exact_override.lstrip()

_irreversible_share_ux = r'''
st.markdown("""
<style id="gsf-irreversible-share-ux">
[data-testid="stToast"]{
  border:1px solid rgba(181,216,235,.26) !important;
  border-radius:18px !important;
  background:linear-gradient(145deg,rgba(29,44,58,.88),rgba(50,64,81,.78)) !important;
  -webkit-backdrop-filter:blur(22px) saturate(1.22) !important;
  backdrop-filter:blur(22px) saturate(1.22) !important;
  box-shadow:0 18px 40px rgba(20,45,64,.22),inset 0 1px 0 rgba(255,255,255,.10) !important;
}
[data-testid="stToast"] *{color:#F0F8FC !important;font-weight:750 !important}
.st-key-v69_social_facebook button,
.st-key-v69_social_instagram button,
.st-key-v69_social_youtube button,
.st-key-v69_social_tiktok button,
.st-key-v69_social_facebook button[kind="secondary"],
.st-key-v69_social_instagram button[kind="secondary"],
.st-key-v69_social_youtube button[kind="secondary"],
.st-key-v69_social_tiktok button[kind="secondary"]{
  min-height:72px !important;
  display:flex !important;
  flex-direction:column !important;
  align-items:center !important;
  justify-content:center !important;
  gap:6px !important;
  padding:8px !important;
  border:1px solid rgba(218,237,247,.15) !important;
  border-radius:17px !important;
  background:linear-gradient(145deg,rgba(255,255,255,.10),rgba(255,255,255,.045)) !important;
  color:#EEF8FC !important;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.08),0 8px 20px rgba(6,20,30,.10) !important;
}
.st-key-v69_social_facebook button[kind="primary"],
.st-key-v69_social_instagram button[kind="primary"],
.st-key-v69_social_youtube button[kind="primary"],
.st-key-v69_social_tiktok button[kind="primary"],
.st-key-v69_social_facebook [data-testid="stBaseButton-primary"],
.st-key-v69_social_instagram [data-testid="stBaseButton-primary"],
.st-key-v69_social_youtube [data-testid="stBaseButton-primary"],
.st-key-v69_social_tiktok [data-testid="stBaseButton-primary"]{
  border-color:rgba(105,223,255,.74) !important;
  background:linear-gradient(145deg,rgba(89,207,238,.20),rgba(138,127,232,.22)) !important;
  box-shadow:0 0 0 1px rgba(105,223,255,.12),0 0 24px rgba(105,223,255,.18),inset 0 1px 0 rgba(255,255,255,.13) !important;
  transform:translateY(-1px) !important;
}
.st-key-v69_social_facebook button p,
.st-key-v69_social_instagram button p,
.st-key-v69_social_youtube button p,
.st-key-v69_social_tiktok button p{
  width:100% !important;
  margin:0 !important;
  text-align:center !important;
  color:#EEF8FC !important;
  opacity:1 !important;
}
</style>
""", unsafe_allow_html=True)
'''
s = s.rstrip() + "\n\n" + _irreversible_share_ux.lstrip()


# Manual editor heading: same visual weight as the main CREA CON IA milestone.
_manual_editor_heading_css = r'''
st.markdown("""
<style id="gsf-manual-editor-heading-style">
.st-key-gsf-major-personalize button,
[class*="st-key-gsf-major-personalize"] button{
    pointer-events:none !important;
    cursor:default !important;
}
</style>
""", unsafe_allow_html=True)
'''
s = s.rstrip() + "\n\n" + _manual_editor_heading_css.lstrip()


# Runtime safety: suppress legacy literal newline markdown around Editor 2027.
s=s.replace("st.markdown('\\\\n')", "st.empty()")
s=s.replace('st.markdown("\\\\n")', "st.empty()")
s=s.replace("st.markdown('\\\\n\\\\n')", "st.empty()")
s=s.replace('st.markdown("\\\\n\\\\n")', "st.empty()")

# DEMO EDITOR ROUTING: "Scegli scena" / Manuale must use Editor 2027, never the legacy editor.
_gsf_manual_tree = _gsf_patch_ast.parse(s)
_gsf_manual_lines = s.splitlines(keepends=True)
_gsf_manual_candidates = []

for _gsf_node in _gsf_patch_ast.walk(_gsf_manual_tree):
    if not isinstance(_gsf_node, _gsf_patch_ast.If):
        continue
    _gsf_test = _gsf_patch_ast.get_source_segment(s, _gsf_node.test) or ""
    if "Manuale" not in _gsf_test or "modalita" not in _gsf_test:
        continue
    if not _gsf_node.body:
        continue
    _gsf_body_start = _gsf_node.body[0].lineno - 1
    _gsf_body_end = _gsf_node.body[-1].end_lineno
    _gsf_body_text = "".join(_gsf_manual_lines[_gsf_body_start:_gsf_body_end])
    _gsf_score = (
        _gsf_body_text.count("editor_") * 5
        + _gsf_body_text.count("st.") * 2
        + _gsf_body_text.count("Scena") * 3
        + len(_gsf_body_text) / 1000.0
    )
    _gsf_manual_candidates.append((_gsf_score, _gsf_node, _gsf_body_start, _gsf_body_end, _gsf_body_text))

if not _gsf_manual_candidates:
    raise RuntimeError('Demo Manual/Scegli scena editor branch not found')

_gsf_manual_candidates.sort(key=lambda _x: _x[0], reverse=True)
_gsf_score, _gsf_node, _gsf_body_start, _gsf_body_end, _gsf_old_body = _gsf_manual_candidates[0]

_gsf_first_body_line = _gsf_manual_lines[_gsf_body_start]
_gsf_indent = _gsf_first_body_line[:len(_gsf_first_body_line)-len(_gsf_first_body_line.lstrip())]

_gsf_new_manual_body = [
    _gsf_indent + 'try:\n',
    _gsf_indent + '    with st.container(key="v1055_ad_manual_before_editor"):\n',
    _gsf_indent + '        st.markdown(_gsf_v1057_ad_markup(2),unsafe_allow_html=True)\n',
    _gsf_indent + 'except Exception as _gsf_manual_ad_exc:\n',
    _gsf_indent + '    print("GSF_MANUAL_AD_SKIP",repr(str(_gsf_manual_ad_exc)),flush=True)\n',
    _gsf_indent + 'st.markdown(\'<div style="height:26px" aria-hidden="true"></div>\',unsafe_allow_html=True)\n',
    _gsf_indent + 'with st.container(key="gsf-major-personalize"):\n',
    _gsf_indent + '    st.button("PERSONALIZZA IL TUO GAMEPLAY",use_container_width=True)\n',
    _gsf_indent + 'st.markdown(\'<div class="gsf-major-note">Modifica scena, look, sottotitoli e audio prima di continuare.</div>\',unsafe_allow_html=True)\n',
    _gsf_indent + 'try:\n',
    _gsf_indent + '    import os as _gsf_manual_os\n',
    _gsf_indent + '    import sys as _gsf_manual_sys\n',
    _gsf_indent + '    if "/app/web" not in _gsf_manual_sys.path:\n',
    _gsf_indent + '        _gsf_manual_sys.path.insert(0,"/app/web")\n',
    _gsf_indent + '    from editor_2027_embed import (\n',
    _gsf_indent + '        render_editor_2027_embed as _gsf_render_manual_editor_2027,\n',
    _gsf_indent + '        editor_2027_state_key as _gsf_editor_2027_state_key,\n',
    _gsf_indent + '        editor_2027_initial_state as _gsf_editor_2027_initial_state,\n',
    _gsf_indent + '        editor_2027_clip_bounds as _gsf_editor_2027_clip_bounds,\n',
    _gsf_indent + '        editor_2027_render_kwargs as _gsf_editor_2027_render_kwargs,\n',
    _gsf_indent + '    )\n',
    _gsf_indent + '    _gsf_manual_path=str(st.session_state.get("gsf_editor_source_path") or st.session_state.get("gsf_source_path") or "")\n',
    _gsf_indent + '    if (not _gsf_manual_path or not _gsf_manual_os.path.isfile(_gsf_manual_path)) and not GSF_WEB_MODE:\n',
    _gsf_indent + '        try:\n',
    _gsf_indent + '            _gsf_manual_bytes=video.getvalue() if hasattr(video,"getvalue") else b""\n',
    _gsf_indent + '            _gsf_manual_path=_gsf_bytes_to_preview(_gsf_manual_bytes,"manual_scene_source") if _gsf_manual_bytes else ""\n',
    _gsf_indent + '        except Exception:\n',
    _gsf_indent + '            _gsf_manual_path=""\n',
    _gsf_indent + '    if _gsf_manual_path:\n',
    _gsf_indent + '        print("GSF_MANUAL_EDITOR_OPEN",_gsf_manual_path,"exists="+str(_gsf_manual_os.path.isfile(_gsf_manual_path)),flush=True)\n',
    _gsf_indent + '        st.session_state["gsf_manual_editor_open"]=True\n',
    _gsf_indent + '        # Persist the exact Editor source across component/button reruns.\n',
    _gsf_indent + '        st.session_state["gsf_source_path"]=str(_gsf_manual_path)\n',
    _gsf_indent + '        st.session_state["gsf_editor_source_path"]=str(_gsf_manual_path)\n',
    _gsf_indent + '        try:\n',
    _gsf_indent + '            _gsf_manual_source_duration=float(durata_video(_gsf_manual_path) or 15.0)\n',
    _gsf_indent + '        except Exception:\n',
    _gsf_indent + '            _gsf_manual_source_duration=15.0\n',
    _gsf_indent + '        _gsf_manual_duration=max(0.5,min(60.0,_gsf_manual_source_duration))\n',
    _gsf_indent + '        _gsf_proxy_sig=__import__("hashlib").sha1((str(_gsf_manual_path)+"|"+str(_gsf_manual_os.path.getsize(_gsf_manual_path))+"|"+str(int(_gsf_manual_os.path.getmtime(_gsf_manual_path)))+"|editor2027-h264-v1").encode("utf-8")).hexdigest()[:16]\n',
    _gsf_indent + '        _gsf_manual_proxy=_gsf_manual_os.path.join(str(GSF_PREVIEW_DIR),"editor2027_manual_"+_gsf_proxy_sig+".mp4")\n',
    _gsf_indent + '        _gsf_proxy_ok=_gsf_manual_os.path.isfile(_gsf_manual_proxy) and _gsf_manual_os.path.getsize(_gsf_manual_proxy)>4096\n',
    _gsf_indent + '        if not _gsf_proxy_ok:\n',
    _gsf_indent + '            with st.spinner("Preparazione Game Editor..."):\n',
    _gsf_indent + '                _gsf_proxy_ok=bool(crea_anteprima(_gsf_manual_path,_gsf_manual_proxy,0.0,_gsf_manual_duration))\n',
    _gsf_indent + '        _gsf_manual_editor_media=_gsf_manual_proxy if _gsf_proxy_ok else _gsf_manual_path\n',
    _gsf_indent + '        print("GSF_MANUAL_EDITOR_PROXY","source="+str(_gsf_manual_path),"editor="+str(_gsf_manual_editor_media),"proxy_ok="+str(bool(_gsf_proxy_ok)),"duration="+str(round(_gsf_manual_duration,3)),flush=True)\n',
    _gsf_indent + '        _gsf_manual_state_slot=_gsf_editor_2027_state_key(_gsf_manual_path)\n',
    _gsf_indent + '        _gsf_manual_component_key=_gsf_manual_state_slot+"_component"\n',
    _gsf_indent + '        _gsf_manual_saved_state=st.session_state.get(_gsf_manual_state_slot)\n',
    _gsf_indent + '        if not isinstance(_gsf_manual_saved_state,dict):\n',
    _gsf_indent + '            _gsf_manual_saved_state=_gsf_editor_2027_initial_state(_gsf_manual_duration)\n',
    _gsf_indent + '        _gsf_manual_editor_state=_gsf_render_manual_editor_2027(\n',
    _gsf_indent + '            _gsf_manual_editor_media,height=720,key=_gsf_manual_component_key,initial_state=_gsf_manual_saved_state\n',
    _gsf_indent + '        )\n',
    _gsf_indent + '        if isinstance(_gsf_manual_editor_state,dict):\n',
    _gsf_indent + '            st.session_state[_gsf_manual_state_slot]=dict(_gsf_manual_editor_state)\n',
    _gsf_indent + '        else:\n',
    _gsf_indent + '            _gsf_manual_editor_state=dict(_gsf_manual_saved_state)\n',
    _gsf_indent + '        try:\n',
    _gsf_indent + '            _gsf_manual_start,_gsf_manual_render_duration=_gsf_editor_2027_clip_bounds(\n',
    _gsf_indent + '                _gsf_manual_editor_state,_gsf_manual_duration\n',
    _gsf_indent + '            )\n',
    _gsf_indent + '            _gsf_manual_render_kwargs=_gsf_editor_2027_render_kwargs(\n',
    _gsf_indent + '                _gsf_manual_editor_state,st.session_state\n',
    _gsf_indent + '            )\n',
    _gsf_indent + '            _gsf_manual_recipe=_gsf_recipe_selected(\n',
    _gsf_indent + '                "main_editor",_gsf_manual_start,_gsf_manual_render_duration,str(_gsf_manual_path),\n',
    _gsf_indent + '                master_token=(str(_gsf_manual_os.path.getsize(_gsf_manual_path))+":"+str(int(_gsf_manual_os.path.getmtime(_gsf_manual_path)))) if _gsf_manual_os.path.isfile(_gsf_manual_path) else "",\n',
    _gsf_indent + '                subtitles_enabled=bool(_gsf_manual_render_kwargs.get("subtitles_enabled",True)),\n',
    _gsf_indent + '                render_kwargs=_gsf_manual_render_kwargs,\n',
    _gsf_indent + '                editor_2027_state=dict(_gsf_manual_editor_state),\n',
    _gsf_indent + '                manual_hook=_GSF_HOOK_OFF_V102,\n',
    _gsf_indent + '            )\n',
    _gsf_indent + '            if st.session_state.get("gsf_final_recipe")!=_gsf_manual_recipe:\n',
    _gsf_indent + '                _gsf_set_final_recipe(_gsf_manual_recipe,source_label="Editor 2027")\n',
    _gsf_indent + '            try:\n',
    _gsf_indent + '                _gsf_manual_preview_bytes=video.getvalue() if hasattr(video,"getvalue") else None\n',
    _gsf_indent + '                if _gsf_manual_preview_bytes:\n',
    _gsf_indent + '                    st.session_state["publication_preview_bytes"]=_gsf_manual_preview_bytes\n',
    _gsf_indent + '            except Exception:\n',
    _gsf_indent + '                pass\n',
    _gsf_indent + '        except Exception as _gsf_manual_recipe_exc:\n',
    _gsf_indent + '            _gsf_manual_fallback_state=_gsf_editor_2027_initial_state(_gsf_manual_duration)\n',
    _gsf_indent + '            st.session_state["gsf_final_recipe"]={\n',
    _gsf_indent + '                "kind":"main_editor","start":0.0,"duration":_gsf_manual_duration,\n',
    _gsf_indent + '                "source_path":str(_gsf_manual_path),\n',
    _gsf_indent + '                "render_kwargs":_gsf_editor_2027_render_kwargs(_gsf_manual_fallback_state,st.session_state),\n',
    _gsf_indent + '            }\n',
    _gsf_indent + '    else:\n',
    _gsf_indent + '        st.warning("Video non disponibile nel Game Editor.")\n',
    _gsf_indent + 'except Exception as _gsf_manual_editor_exc:\n',
    _gsf_indent + '    print("GSF_MANUAL_EDITOR_ERROR",repr(str(_gsf_manual_editor_exc)),flush=True)\n',
    _gsf_indent + '    st.warning("Game Editor da ricaricare. Riprova Scegli scena.")\n',
    _gsf_indent + 'try:\n',
    _gsf_indent + '    with st.container(key="v1055_ad_manual_after_editor"):\n',
    _gsf_indent + '        st.markdown(_gsf_v1057_ad_markup(3),unsafe_allow_html=True)\n',
    _gsf_indent + 'except Exception as _gsf_manual_ad2_exc:\n',
    _gsf_indent + '    print("GSF_MANUAL_AD2_SKIP",repr(str(_gsf_manual_ad2_exc)),flush=True)\n',
]

_gsf_manual_lines[_gsf_body_start:_gsf_body_end] = _gsf_new_manual_body
s = "".join(_gsf_manual_lines)
print("GSF Manual/Scegli scena routed to Editor 2027")

# Final render completion: refresh exactly once after a successful final MP4 is stored.
_gsf_final_tree=_gsf_patch_ast.parse(s)
_gsf_final_lines=s.splitlines(keepends=True)
_gsf_final_targets=[]
for _gsf_node in _gsf_patch_ast.walk(_gsf_final_tree):
    if not isinstance(_gsf_node,_gsf_patch_ast.If):
        continue
    _test=_gsf_patch_ast.get_source_segment(s,_gsf_node.test) or ""
    _body=_gsf_patch_ast.get_source_segment(s,_gsf_node) or ""
    if "_v1054_create_final_clicked" in _test and "_final_dir" in _body and "gsf_final_v54_" in _body:
        _gsf_final_targets.append(_gsf_node)
if len(_gsf_final_targets)!=1:
    raise RuntimeError("V107 expected one final render gate, found "+str(len(_gsf_final_targets)))
_gsf_final_node=_gsf_final_targets[0]
_gsf_final_line=_gsf_final_lines[_gsf_final_node.lineno-1]
_gsf_final_indent=_gsf_final_line[:len(_gsf_final_line)-len(_gsf_final_line.lstrip())]
_gsf_final_refresh=[
    _gsf_final_indent+'if _v1054_create_final_clicked:\n',
    _gsf_final_indent+'    _gsf_completed_final=locals().get("_final_video")\n',
    _gsf_final_indent+'    if isinstance(_gsf_completed_final,(bytes,bytearray)) and len(_gsf_completed_final)>1024:\n',
    _gsf_final_indent+'        st.session_state["publication_final_bytes"]=bytes(_gsf_completed_final)\n',
    _gsf_final_indent+'        st.session_state["publication_ready"]=True\n',
    _gsf_final_indent+'        st.session_state["gsf_v107_final_render_running"]=False\n',
    _gsf_final_indent+'        st.session_state["gsf_v107_render_done_toast"]=True\n',
    _gsf_final_indent+'        print("GSF_FINAL_RENDER_READY",len(_gsf_completed_final),flush=True)\n',
    _gsf_final_indent+'        st.rerun()\n',
_gsf_final_lines[_gsf_final_node.end_lineno:_gsf_final_node.end_lineno]=_gsf_final_refresh
s="".join(_gsf_final_lines)

# Remove markdown calls that render only blank/literal newline markers.
_gsf_nl_tree=_gsf_patch_ast.parse(s)
_gsf_nl_lines=s.splitlines(keepends=True)
_gsf_nl_replacements=[]
for _node in _gsf_patch_ast.walk(_gsf_nl_tree):
    if not isinstance(_node,_gsf_patch_ast.Expr):
        continue
    _call=_node.value
    if not isinstance(_call,_gsf_patch_ast.Call):
        continue
    _func=_call.func
    if not (
        isinstance(_func,_gsf_patch_ast.Attribute)
        and _func.attr=="markdown"
        and isinstance(_func.value,_gsf_patch_ast.Name)
        and _func.value.id=="st"
        and _call.args
        and isinstance(_call.args[0],_gsf_patch_ast.Constant)
        and isinstance(_call.args[0].value,str)
    ):
        continue
    _value=_call.args[0].value
    _compact=_value.strip().replace("\\n","")
    if _compact=="":
        _start=_node.lineno-1
        _end=getattr(_node,"end_lineno",_node.lineno)
        _line=_gsf_nl_lines[_start]
        _indent=_line[:len(_line)-len(_line.lstrip())]
        _gsf_nl_replacements.append((_start,_end,_indent+"st.empty()\n"))

for _start,_end,_replacement in sorted(_gsf_nl_replacements,reverse=True):
    _gsf_nl_lines[_start:_end]=[_replacement]
s="".join(_gsf_nl_lines)
if _gsf_nl_replacements:
    print("V107 removed newline-only markdown blocks:",len(_gsf_nl_replacements))

compile(s,str(out),'exec')
out.write_text(s,encoding='utf-8')
print('V107 production UI applied:',out)
# V107 production UI: Editor 2027 + approved milestone guides
