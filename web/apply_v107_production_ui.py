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
_create_short_new='''            with st.container(key="gsf-major-create-short"):
                _v1054_create_final_clicked=st.button(
                    "CREA SHORT FINALE",
                    use_container_width=True,
                    key="create_final_short_v54"
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

# The obsolete large PUBBLICA launcher is hidden by the scoped browser cleanup below.
# Do not rewrite the source block here: preserving the original code avoids brittle
# multiline regex changes while the composer is already forced open by _has_final.

_final_publish_v2 = r'''
st.markdown("""
<style id="gsf-v107-final-publish">
.gsf-final-ready{
  margin:16px auto 4px;text-align:center;color:#3f6f62;
  font-size:.96rem;font-weight:900;letter-spacing:.015em;
}
.gsf-final-publish-title{
  margin:4px 0 9px;text-align:center;color:#17324a;
  font-size:1.10rem;font-weight:950;letter-spacing:.08em;
}
.gsf-final-social-row{
  display:grid !important;
  grid-template-columns:repeat(4,minmax(0,1fr)) !important;
  gap:9px !important;
  align-items:stretch !important;
  margin:0 auto 8px !important;
}
.gsf-final-social-row > div,
.gsf-final-social-row > a{
  width:100% !important;min-width:0 !important;flex:initial !important;
}
.st-key-v69_social_youtube button,
.st-key-v69_social_tiktok button,
.st-key-v69_social_instagram button,
.gsf-facebook-publish-icon{
  min-height:58px !important;height:58px !important;
  border-radius:16px !important;
  display:flex !important;align-items:center !important;justify-content:center !important;
  border:1px solid #cbdde9 !important;
  background:linear-gradient(145deg,#fff,#eef5fa) !important;
  color:#355a73 !important;
  box-shadow:0 6px 16px rgba(65,96,121,.09) !important;
  text-decoration:none !important;
}
.st-key-v69_social_youtube button p,
.st-key-v69_social_tiktok button p,
.st-key-v69_social_instagram button p{display:none !important}
.st-key-v69_social_youtube button:before{content:"▶";font-size:21px;font-weight:950}
.st-key-v69_social_tiktok button:before{content:"♪";font-size:24px;font-weight:950}
.st-key-v69_social_instagram button:before{content:"◎";font-size:25px;font-weight:900}
.gsf-facebook-publish-icon{font:900 25px/1 Arial,sans-serif}
[class*="st-key-v1055_social_composer_"]{
  margin:8px auto 10px !important;
  padding:14px !important;
}
[data-testid="stDownloadButton"]{margin-top:8px !important;margin-bottom:8px !important}
@media(max-width:600px){
  .gsf-final-ready{margin:11px auto 3px;font-size:.90rem}
  .gsf-final-publish-title{margin:3px 0 7px;font-size:1rem}
  .gsf-final-social-row{gap:7px !important;margin-bottom:7px !important}
  .st-key-v69_social_youtube button,
  .st-key-v69_social_tiktok button,
  .st-key-v69_social_instagram button,
  .gsf-facebook-publish-icon{
    min-height:52px !important;height:52px !important;border-radius:14px !important;
  }
  [class*="st-key-v1055_social_composer_"]{padding:11px !important;margin:7px auto 8px !important}
}
</style>
<script>
(()=>{
 const tune=()=>{
   /* Hide legacy duplicate title and launcher. */
   document.querySelectorAll('div,p,h1,h2,h3,h4').forEach(el=>{
     if((el.textContent||'').trim()==='Pubblicazione diretta'){
       const block=el.closest('[data-testid="stMarkdownContainer"]')||el;
       block.style.display='none';
     }
   });
   document.querySelectorAll('button').forEach(b=>{
     const t=(b.textContent||'').trim().replace(/^➡️\\s*/,'');
     if(t==='PUBBLICA'){
       const key=b.closest('[class*="st-key-social_publish_confirm_"]');
       if(!key){
         const wrap=b.closest('[data-testid="stButton"]')||b.parentElement;
         if(wrap) wrap.style.display='none';
       }
     }
   });

   const y=document.querySelector('.st-key-v69_social_youtube');
   const row=y?.closest('div[data-testid="stHorizontalBlock"]');
   if(!row)return;
   row.classList.add('gsf-final-social-row');

   const labels=[
     ['.st-key-v69_social_youtube','YouTube'],
     ['.st-key-v69_social_tiktok','TikTok'],
     ['.st-key-v69_social_instagram','Instagram']
   ];
   labels.forEach(([sel,name])=>{
     const b=document.querySelector(sel+' button');
     if(b){b.title=name;b.setAttribute('aria-label',name);}
   });

   if(!row.querySelector('.gsf-facebook-publish-icon')){
     const fb=document.createElement('a');
     fb.className='gsf-facebook-publish-icon';
     fb.href='/account/facebook/start';
     fb.target='_blank';
     fb.rel='noopener';
     fb.title='Facebook · collega account';
     fb.setAttribute('aria-label','Facebook');
     fb.textContent='f';
     row.insertBefore(fb,row.firstChild);
   }

   if(!row.previousElementSibling?.classList.contains('gsf-final-publish-head')){
     const head=document.createElement('div');
     head.className='gsf-final-publish-head';
     head.innerHTML='<div class="gsf-final-ready">✅ Short finale pronto</div><div class="gsf-final-publish-title">PUBBLICA</div>';
     row.parentElement?.insertBefore(head,row);
   }

   /* SCARICA always follows the social row/composer and precedes ad/footer. */
   const dl=[...document.querySelectorAll('button,a')].find(x=>(x.textContent||'').trim()==='SCARICA');
   if(dl){
     const dlWrap=dl.closest('[data-testid="stDownloadButton"]')||dl.closest('[data-testid="stMarkdownContainer"]')||dl.parentElement;
     const composers=[...document.querySelectorAll('[class*="st-key-v1055_social_composer_"]')];
     const target=composers.length?composers[composers.length-1]:row;
     if(dlWrap && target && target.parentElement){
       try{target.insertAdjacentElement('afterend',dlWrap)}catch(e){}
     }
   }
 };
 tune();
 new MutationObserver(tune).observe(document.body,{childList:true,subtree:true});
})();
</script>
""", unsafe_allow_html=True)
'''
s = s.rstrip() + "\n\n" + _final_publish_v2.lstrip()

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
  .gsf-major-note{margin:6px auto 10px !important}
  .gsf-moment-head{margin:6px auto 10px !important}
  .v67-ad{margin-top:9px !important;margin-bottom:9px !important}
  [data-testid="stAppViewContainer"] hr{margin:.38rem 0 !important}
}
</style>
<script>
(()=>{
 const cleanArtifacts=()=>{
   document.querySelectorAll('[data-testid="stMarkdownContainer"]').forEach(el=>{
     const t=(el.textContent||'').trim();
     if(/^(?:\\n)+$/.test(t)){
       const host=el.parentElement||el;
       host.style.display='none';
       host.style.margin='0';
       host.style.padding='0';
       host.style.minHeight='0';
     }
   });
 };
 cleanArtifacts();
 new MutationObserver(cleanArtifacts).observe(document.body,{childList:true,subtree:true});
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


# Final footer override: replace the three old footer rows with one compact row.
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
  margin:2px auto 5px;
  padding:5px 8px;
  border-top:1px solid rgba(195,214,227,.65);
  display:flex;
  justify-content:center;
  align-items:center;
  gap:6px;
  flex-wrap:wrap;
  color:#6d8496;
  font-size:10px;
  line-height:1;
  text-align:center;
}
.gsf-footer-v4 a{color:#647f92 !important;text-decoration:none !important;font-weight:750}
.gsf-footer-v4 .soc{font-weight:800;opacity:.85;letter-spacing:.08em}
[data-testid="stAppViewContainer"] .block-container{padding-bottom:.45rem !important}
@media(max-width:600px){
  .gsf-footer-v4{margin:1px auto 3px;padding:4px 6px;font-size:9px;gap:5px}
  [data-testid="stAppViewContainer"] .block-container{padding-bottom:.25rem !important}
}
</style>
<div class="gsf-footer-v4">
  <span>Gaming Shorts Factory · Beta</span>
  <a href="/privacy" target="_blank">Privacy</a>
  <span>·</span>
  <a href="/terms" target="_blank">Termini</a>
  <span>·</span>
  <a href="/contact" target="_blank">Contatti</a>
  <span class="soc">f ◎ ▶ ♪</span>
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
.st-key-gsf-major-create-ai button,
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
    .st-key-gsf-major-create-ai button,
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

.st-key-gsf-major-personalize button,
[class*="st-key-gsf-major-personalize"] button{
    position:relative !important;
    pointer-events:none !important;
    cursor:default !important;
}
.st-key-gsf-major-personalize button::after,
[class*="st-key-gsf-major-personalize"] button::after{
    content:"→";
    position:absolute;
    right:20px;
    top:50%;
    transform:translateY(-52%);
    font-size:20px;
    font-weight:900;
    line-height:1;
    color:currentColor;
}
@media(max-width:750px){
    .st-key-gsf-major-personalize button::after,
    [class*="st-key-gsf-major-personalize"] button::after{
        right:15px;
        font-size:17px;
    }
}
</style>
""", unsafe_allow_html=True)
'''
s = s.rstrip() + "\n\n" + _major_cta_final_override.lstrip()


# Manual editor heading: same visual weight as the main CREA CON IA milestone.
_manual_editor_heading_css = r'''
st.markdown("""
<style id="gsf-manual-editor-heading-style">
.gsf-personalize-major{
    width:100%;
    min-height:56px;
    display:flex;
    align-items:center;
    justify-content:center;
    margin:8px auto 16px;
    padding:0 18px;
    border-radius:17px;
    border:1px solid rgba(255,255,255,.34);
    background:linear-gradient(135deg,#8B67E8 0%,#6557D9 100%);
    color:#FFFFFF !important;
    box-shadow:0 12px 28px rgba(104,84,205,.28);
    font-family:var(--gsf-ui-font,ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif);
    font-size:15px;
    font-weight:900;
    line-height:1;
    letter-spacing:.045em;
    text-align:center;
}
@media(max-width:750px){
    .gsf-personalize-major{
        min-height:52px;
        font-size:13px;
    }
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
    _gsf_indent + 'with st.container(key="v1055_ad_manual_before_editor"):\n',
    _gsf_indent + '    st.markdown(_gsf_v1057_ad_markup(2),unsafe_allow_html=True)\n',
    _gsf_indent + 'st.markdown(\'<div style="height:26px" aria-hidden="true"></div>\',unsafe_allow_html=True)\n',
    _gsf_indent + 'with st.container(key="gsf-major-personalize"):\n',
    _gsf_indent + '    st.markdown("<div class=\\\"gsf-personalize-title\\\">PERSONALIZZA IL TUO GAMEPLAY</div>",unsafe_allow_html=True)\n',
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
    _gsf_indent + '    _gsf_manual_path=str(st.session_state.get("gsf_source_path") or "")\n',
    _gsf_indent + '    if not _gsf_manual_path or not _gsf_manual_os.path.isfile(_gsf_manual_path):\n',
    _gsf_indent + '        try:\n',
    _gsf_indent + '            _gsf_manual_bytes=video.getvalue() if hasattr(video,"getvalue") else b""\n',
    _gsf_indent + '            _gsf_manual_path=_gsf_bytes_to_preview(_gsf_manual_bytes,"manual_scene_source") if _gsf_manual_bytes else ""\n',
    _gsf_indent + '        except Exception:\n',
    _gsf_indent + '            _gsf_manual_path=""\n',
    _gsf_indent + '    if _gsf_manual_path:\n',
    _gsf_indent + '        # Persist the exact Editor source across component/button reruns.\n',
    _gsf_indent + '        st.session_state["gsf_source_path"]=str(_gsf_manual_path)\n',
    _gsf_indent + '        st.session_state["gsf_editor_source_path"]=str(_gsf_manual_path)\n',
    _gsf_indent + '        _gsf_manual_duration=float(st.session_state.get("auto_clip_duration",15.0) or 15.0)\n',
    _gsf_indent + '        _gsf_manual_state_slot=_gsf_editor_2027_state_key(_gsf_manual_path)\n',
    _gsf_indent + '        _gsf_manual_component_key=_gsf_manual_state_slot+"_component"\n',
    _gsf_indent + '        _gsf_manual_saved_state=st.session_state.get(_gsf_manual_state_slot)\n',
    _gsf_indent + '        if not isinstance(_gsf_manual_saved_state,dict):\n',
    _gsf_indent + '            _gsf_manual_saved_state=_gsf_editor_2027_initial_state(_gsf_manual_duration)\n',
    _gsf_indent + '        _gsf_manual_editor_state=_gsf_render_manual_editor_2027(\n',
    _gsf_indent + '            _gsf_manual_path,height=720,key=_gsf_manual_component_key,initial_state=_gsf_manual_saved_state\n',
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
    _gsf_indent + '                master_token=_gsf_upload_master_token(video),\n',
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
    _gsf_indent + '    st.error("Game Editor non disponibile: "+str(_gsf_manual_editor_exc))\n',
    _gsf_indent + 'with st.container(key="v1055_ad_manual_after_editor"):\n',
    _gsf_indent + '    st.markdown(_gsf_v1057_ad_markup(3),unsafe_allow_html=True)\n',
]

_gsf_manual_lines[_gsf_body_start:_gsf_body_end] = _gsf_new_manual_body
s = "".join(_gsf_manual_lines)
print("GSF Manual/Scegli scena routed to Editor 2027")

compile(s,str(out),'exec')
out.write_text(s,encoding='utf-8')
print('V107 production UI applied:',out)
# V107 production UI: Editor 2027 + approved milestone guides
