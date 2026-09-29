from pathlib import Path
import ast as _gsf_patch_ast

src=Path('/app/GamingShortsFactory_V106_BETA_RC1.py')
out=Path('/app/GamingShortsFactory_V106_DEMO_REAL.py')
s=src.read_text(encoding='utf-8')

anchor='\nif video:\n'
if anchor not in s:
    raise RuntimeError('Demo real anchor not found: top-level if video')

inject=r'''
# ==========================================================
# deploy retrigger: ui-demo
# V106 REAL DEMO
# Production app/controls unchanged. Only the initial source,
# 3 AI candidates and already-rendered final Short are seeded.
# ==========================================================
import io as _gsf_demo_io

_GSF_REAL_DEMO = str(os.environ.get("GSF_REAL_DEMO","0") or "0").strip().lower() in {"1","true","yes","on"}

class _GSFRealDemoUpload(_gsf_demo_io.BytesIO):
    def __init__(self, data, name):
        super().__init__(data)
        self.name=str(name)
        self.size=len(data)

if _GSF_REAL_DEMO:
    _gsf_demo_source=Path("/app/demo_assets/demo_gameplay.mp4")
    _gsf_demo_clip=Path("/app/demo_assets/demo_clip.mp4")
    _gsf_demo_final=Path("/app/demo_assets/demo_final.mp4")

    if not (_gsf_demo_source.is_file() and _gsf_demo_clip.is_file() and _gsf_demo_final.is_file()):
        st.error("Demo media non disponibili.")
    else:
        # Feed the normal production flow with an UploadedFile-compatible
        # object only when no actual upload is present.
        if video is None:
            video=_GSFRealDemoUpload(
                _gsf_demo_source.read_bytes(),
                "demo_gameplay.mp4",
            )

        st.session_state.setdefault("gsf_source_path",str(_gsf_demo_source))
        st.session_state.setdefault("gsf_source_name","demo_gameplay.mp4")

        # Seed exactly once per Streamlit session. After this point engine
        # changes, Editor, subtitles, resets, candidate selection, final flow
        # and social buttons are the ordinary production code.
        if not st.session_state.get("_gsf_real_demo_seeded",False):
            _gsf_demo_clip_bytes=_gsf_demo_clip.read_bytes()
            _gsf_demo_final_bytes=_gsf_demo_final.read_bytes()

            # Default engine + already-computed AI result.
            st.session_state.setdefault("modalita_gsf","🚀 AUTO TOTALE")
            st.session_state["auto_clip_modalita"]="🚀 AUTO TOTALE"
            st.session_state["auto_clip_candidati"]=[8.0,28.0,48.0]
            st.session_state["auto_clip_scelta"]=8.0
            st.session_state["auto_clip_duration"]=15.0
            st.session_state["ai_director_scores"]=[
                (96.0,8.0),
                (91.0,28.0),
                (87.0,48.0),
            ]
            st.session_state["clip_rifinite"]={
                8.0:15.0,
                28.0:15.0,
                48.0:15.0,
            }

            # The selected first candidate is already materialized; choosing
            # another candidate follows the normal V106 path.
            st.session_state["preview_bytes"]=_gsf_demo_clip_bytes
            st.session_state["preview_key"]=None

            # Same state consumed by the ordinary final-result UI.
            st.session_state["gsf_final_recipe"]={
                "kind":"auto",
                "start":8.0,
                "duration":15.0,
                "source_path":str(_gsf_demo_source),
                "manual_hook":_GSF_HOOK_OFF_V102,
            }
            st.session_state["publication_ready"]=True
            st.session_state["publication_source"]="AI"
            st.session_state["publication_preview_bytes"]=_gsf_demo_clip_bytes
            st.session_state["publication_final_bytes"]=_gsf_demo_final_bytes

            # Keep the social publish area visible in the functional demo so
            # YouTube/TikTok/Instagram connection and publish controls can be tested directly.
            st.session_state["show_social_publish_v53"]=True
            st.session_state["show_social_publish_v54"]=True
            st.session_state.pop("current_view",None)
            st.session_state.pop("inline_editor_id",None)

            st.session_state["_gsf_real_demo_seeded"]=True

        st.markdown(
            '<div style="margin:8px 0 14px;padding:10px 13px;border:1px solid #B9DCEF;'
            'border-radius:16px;background:#F1F9FE;color:#376B8A;font-size:13px;font-weight:750">'
            '🧪 DEMO FUNZIONALE · video, 3 momenti AI e Short finale sono già pronti. '
            'Pulsanti, Editor, sottotitoli, cambio motore e social usano la V106 reale.'
            '</div>',
            unsafe_allow_html=True,
        )

'''

s=s.replace(anchor,'\n'+inject+'\nif video:\n',1)
s=s.replace(
    'Gaming Shorts Factory · V106 Functional Demo',
    'Gaming Shorts Factory · V105.6 Functional Demo'
)


# DEMO UX: dopo l'upload non mostrare il player dell'originale.
# Restano invariati motori, durata, tre anteprime AI ed Editor.
_source_preview_start='''    # PLAYER HTML5 ADATTIVO DEFINITIVO
'''
_source_preview_end='''    st.divider()
    st.markdown('<div class="gsf-icon-title">Come vuoi creare?</div>', unsafe_allow_html=True)
'''
if _source_preview_start not in s or _source_preview_end not in s:
    raise RuntimeError('Demo source preview block not found')
_pre,_tail=s.split(_source_preview_start,1)
_hidden,_post=_tail.split(_source_preview_end,1)
s=(
    _pre
    + '    # DEMO: anteprima del video caricato nascosta; il file resta disponibile internamente.\\n'
    + "    st.markdown('<div style=\"height:6px\" aria-hidden=\"true\"></div>', unsafe_allow_html=True)\\n"
    + _source_preview_end
    + _post
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
                        from editor_2027_embed import render_editor_2027_embed as _gsf_render_editor_2027_embed
                        _gsf_ed27_path=_gsf_bytes_to_preview(
                            st.session_state.get("preview_bytes") or b"",
                            f"editor2027_{start:.2f}"
                        )
                        if _gsf_ed27_path:
                            _gsf_render_editor_2027_embed(_gsf_ed27_path,height=660)
                    except Exception as _gsf_ed27_exc:
                        st.error("Game Editor demo non disponibile: "+str(_gsf_ed27_exc))

                # Vecchio Editor disattivato nella demo.
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


# DEMO: full publication area is always visible, even with no connected accounts.
_demo_social_publication = r'''
st.markdown("""
<style id="gsf-demo-social-publication-style">
.gsf-demo-publish{
  margin:26px auto 20px;
  padding:18px;
  border:1px solid #D9E8F3;
  border-radius:22px;
  background:linear-gradient(180deg,rgba(248,252,255,.98),rgba(255,255,255,.98));
  box-shadow:0 10px 28px rgba(49,87,118,.08);
}
.gsf-demo-publish-title{
  text-align:center;
  color:#17324A;
  font-size:15px;
  font-weight:900;
  letter-spacing:.025em;
  margin-bottom:13px;
}
.gsf-demo-publish-grid{
  display:grid;
  grid-template-columns:repeat(4,minmax(0,1fr));
  gap:10px;
}
.gsf-demo-publish-btn{
  min-height:50px;
  display:flex;
  align-items:center;
  justify-content:center;
  gap:8px;
  padding:0 12px;
  border:1px solid #D5E5F0;
  border-radius:15px;
  background:#FFFFFF;
  box-shadow:0 7px 18px rgba(56,92,122,.08);
  color:#315E7A !important;
  text-decoration:none !important;
  font-size:13px;
  font-weight:900;
}
.gsf-demo-publish-btn:hover{
  transform:translateY(-1px);
  border-color:#BFD9EA;
  box-shadow:0 10px 22px rgba(56,92,122,.12);
}
.gsf-demo-publish-dot{
  width:9px;height:9px;border-radius:50%;background:#AFC7D8;flex:0 0 9px;
}
.gsf-demo-publish-hint{
  margin-top:11px;
  text-align:center;
  color:#7890A2;
  font-size:11px;
  font-weight:700;
}
@media(max-width:600px){
  .gsf-demo-publish{padding:14px;margin-top:22px}
  .gsf-demo-publish-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:7px}
  .gsf-demo-publish-btn{min-height:46px;padding:0 8px;font-size:11px;border-radius:13px}
  .gsf-demo-publish-dot{width:8px;height:8px;flex-basis:8px}
}
</style>
<section class="gsf-demo-publish" aria-label="Pubblicazione social">
  <div class="gsf-demo-publish-title">PUBBLICA IL TUO SHORT</div>
  <div class="gsf-demo-publish-grid">
    <a class="gsf-demo-publish-btn" href="/account/facebook/start" target="_self">
      <span class="gsf-demo-publish-dot"></span>Facebook
    </a>
    <a class="gsf-demo-publish-btn" href="/social-connect/youtube/start" target="_self">
      <span class="gsf-demo-publish-dot"></span>YouTube
    </a>
    <a class="gsf-demo-publish-btn" href="/social-connect/tiktok/start" target="_self">
      <span class="gsf-demo-publish-dot"></span>TikTok
    </a>
    <a class="gsf-demo-publish-btn" href="/social-connect/instagram/start" target="_self">
      <span class="gsf-demo-publish-dot"></span>Instagram
    </a>
  </div>
  <div class="gsf-demo-publish-hint">Nella demo restano visibili anche senza account collegati.</div>
</section>
""", unsafe_allow_html=True)

with st.container(key="gsf-demo-social-form"):
    st.text_input(
        "Gioco",
        key="gsf_demo_social_game",
        placeholder="Es. ARC Raiders",
    )
    st.text_input(
        "Titolo",
        key="gsf_demo_social_title",
        placeholder="Es. La giocata migliore della partita",
    )
    st.text_area(
        "Descrizione",
        key="gsf_demo_social_description",
        placeholder="Es. Il momento decisivo del gameplay, pronto per lo Short.",
        height=120,
    )
    st.text_input(
        "Hashtag",
        key="gsf_demo_social_hashtags",
        placeholder="Es. #Gaming #Shorts #Gameplay",
    )
    if st.button(
        "PUBBLICA",
        use_container_width=True,
        key="gsf_demo_social_publish_preview",
    ):
        st.info("Collega un account social per pubblicare davvero.")
'''
_demo_footer_anchor='''with st.container(key="v1053_ad_footer"):
'''
if _demo_footer_anchor not in s:
    raise RuntimeError("Demo footer anchor not found for social publication")
s=s.replace(
    _demo_footer_anchor,
    _demo_social_publication.lstrip()+"\n\n"+_demo_footer_anchor,
    1,
)


# DEMO footer: social channels, visually ready while URLs are pending.
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
  <div class="gsf-social-footer-title">Seguici sui nostri canali</div>
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
    _gsf_indent + 'with st.container(key="gsf-major-personalize"):\n',
    _gsf_indent + '    st.button("PERSONALIZZA IL TUO GAMEPLAY",use_container_width=True,key="gsf_personalize_visual")\n',
    _gsf_indent + 'try:\n',
    _gsf_indent + '    import os as _gsf_manual_os\n',
    _gsf_indent + '    import sys as _gsf_manual_sys\n',
    _gsf_indent + '    if "/app/web" not in _gsf_manual_sys.path:\n',
    _gsf_indent + '        _gsf_manual_sys.path.insert(0,"/app/web")\n',
    _gsf_indent + '    from editor_2027_embed import render_editor_2027_embed as _gsf_render_manual_editor_2027\n',
    _gsf_indent + '    _gsf_manual_path=str(st.session_state.get("gsf_source_path") or "")\n',
    _gsf_indent + '    if not _gsf_manual_path or not _gsf_manual_os.path.isfile(_gsf_manual_path):\n',
    _gsf_indent + '        try:\n',
    _gsf_indent + '            _gsf_manual_bytes=video.getvalue() if hasattr(video,"getvalue") else b""\n',
    _gsf_indent + '            _gsf_manual_path=_gsf_bytes_to_preview(_gsf_manual_bytes,"manual_scene_source") if _gsf_manual_bytes else ""\n',
    _gsf_indent + '        except Exception:\n',
    _gsf_indent + '            _gsf_manual_path=""\n',
    _gsf_indent + '    if _gsf_manual_path:\n',
    _gsf_indent + '        _gsf_render_manual_editor_2027(_gsf_manual_path,height=720)\n',
    _gsf_indent + '        try:\n',
    _gsf_indent + '            _gsf_manual_duration=float(st.session_state.get("auto_clip_duration",15.0) or 15.0)\n',
    _gsf_indent + '            _gsf_manual_recipe=_gsf_recipe_selected(\n',
    _gsf_indent + '                "main_editor",0.0,_gsf_manual_duration,str(_gsf_manual_path),\n',
    _gsf_indent + '                master_token=_gsf_upload_master_token(video),\n',
    _gsf_indent + '                subtitles_enabled=bool(st.session_state.get("project_subtitles_enabled",True)),\n',
    _gsf_indent + '                manual_hook=_GSF_HOOK_OFF_V102,\n',
    _gsf_indent + '            )\n',
    _gsf_indent + '            _gsf_set_final_recipe(_gsf_manual_recipe,source_label="Editor")\n',
    _gsf_indent + '            try:\n',
    _gsf_indent + '                _gsf_manual_preview_bytes=video.getvalue() if hasattr(video,"getvalue") else None\n',
    _gsf_indent + '                if _gsf_manual_preview_bytes:\n',
    _gsf_indent + '                    st.session_state["publication_preview_bytes"]=_gsf_manual_preview_bytes\n',
    _gsf_indent + '            except Exception:\n',
    _gsf_indent + '                pass\n',
    _gsf_indent + '        except Exception as _gsf_manual_recipe_exc:\n',
    _gsf_indent + '            st.session_state["gsf_final_recipe"]={\n',
    _gsf_indent + '                "kind":"main_editor","start":0.0,"duration":15.0,"source_path":str(_gsf_manual_path)\n',
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
print('V106 functional demo applied:',out)
# ui-demo deploy trigger: Game Editor + milestone guides
