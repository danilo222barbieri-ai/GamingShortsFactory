from pathlib import Path

src=Path('/app/GamingShortsFactory_V106_BETA_RC1.py')
out=Path('/app/GamingShortsFactory_V106_DEMO_REAL.py')
s=src.read_text(encoding='utf-8')

anchor='\nif video:\n'
if anchor not in s:
    raise RuntimeError('Demo real anchor not found: top-level if video')

inject=r'''
# ==========================================================
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

            # Do NOT pre-open publishing or editors: those must be exercised
            # through the real production buttons to expose real bugs.
            st.session_state.pop("show_social_publish_v53",None)
            st.session_state.pop("show_social_publish_v54",None)
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
_choice_anchor='''                with st.container(key="v71-short-grid"):
'''
if _choice_anchor not in s:
    raise RuntimeError('Demo three-short grid anchor not found')
s=s.replace(
    _choice_anchor,
    '                st.markdown(' + repr(_choice_css) + ', unsafe_allow_html=True)\n' + _choice_anchor,
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
_editor_cols_new='''                _edit_pad_l, edit_col, _edit_pad_r = st.columns([.80,3.40,.80])
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
    background:linear-gradient(135deg,#4FADE8 0%,#647FE5 100%) !important;
    color:#FFFFFF !important;
    font-size:15px !important;
    font-weight:900 !important;
    letter-spacing:.045em !important;
    box-shadow:0 12px 28px rgba(72,113,205,.30) !important;
    transition:transform .16s ease,box-shadow .16s ease,filter .16s ease !important;
}
[class*="st-key-gsf-major-create-ai"] button:hover,
[class*="st-key-gsf-major-game-editor_"] button:hover,
[class*="st-key-gsf-major-create-short"] button:hover{
    transform:translateY(-2px) !important;
    filter:brightness(1.025) !important;
    box-shadow:0 15px 34px rgba(72,113,205,.36) !important;
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
if _major_heading not in s:
    raise RuntimeError("Demo major-action heading anchor not found")
s=s.replace(
    _major_heading,
    _major_heading + '    st.markdown(' + repr(_major_action_css) + ', unsafe_allow_html=True)\n',
    1,
)

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
                    type="primary",
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


compile(s,str(out),'exec')
out.write_text(s,encoding='utf-8')
print('V106 functional demo applied:',out)
# ui-demo deploy trigger: Game Editor + milestone guides
