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

# DEMO UX: i pulsanti delle tre clip AI devono essere visivamente distinti
# dallo stato verde "Video caricato".
_choice_css=r'''
<style id="gsf-demo-choice-color">
[class*="st-key-v71_choose_short_"] button{
    background:linear-gradient(135deg,#6E63FF 0%,#4B9CFF 100%) !important;
    color:#FFFFFF !important;
    border:1px solid rgba(95,111,255,.55) !important;
    box-shadow:0 8px 20px rgba(77,116,255,.18) !important;
}
[class*="st-key-v71_choose_short_"] button:hover{
    filter:brightness(1.06) !important;
    transform:translateY(-1px) !important;
}
[class*="st-key-v71_choose_short_"] button:disabled{
    opacity:.72 !important;
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
_new_editor_open='''                    if st.button(
                        "MODIFICA NELL’EDITOR 2027",
                        use_container_width=True,
                        key=f"edit_ai_{start:.2f}_{durata_effettiva:.2f}"
                    ):
                        st.session_state["gsf_editor_2027_inline_open"]=True
                        st.session_state["gsf_editor_2027_start"]=float(start)
                        st.session_state.pop("inline_editor_id",None)
                        st.rerun()
'''
if _old_editor_open not in s:
    raise RuntimeError("Demo old inline editor opener not found")
s=s.replace(_old_editor_open,_new_editor_open,1)

_old_inline_marker='''                # ===== EDITOR INLINE DELLA CLIP AI =====
                _this_inline_id=f"{start:.2f}_{durata_effettiva:.2f}"
                if st.session_state.get("inline_editor_id")==_this_inline_id:
'''
_new_inline_marker='''                # ===== EDITOR 2027 INLINE DELLA CLIP AI =====
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
                        _gsf_ed27_h,_gsf_ed27_c=st.columns([.84,.16],gap="small")
                        with _gsf_ed27_h:
                            st.markdown(
                                '<div style="padding:7px 10px;border-radius:12px;background:linear-gradient(90deg,#FFF1EF,#F5F1FF);'
                                'border:1px solid #F2D2CF;color:#7E3B49;font-size:11px;font-weight:850;letter-spacing:.03em">'
                                'EDITOR 2027 · GAME PREVIEW'
                                '</div>',
                                unsafe_allow_html=True,
                            )
                        with _gsf_ed27_c:
                            if st.button("CHIUDI",key=f"close_ed27_{_this_inline_id}",use_container_width=True):
                                st.session_state["gsf_editor_2027_inline_open"]=False
                                st.rerun()
                        if _gsf_ed27_path:
                            _gsf_render_editor_2027_embed(_gsf_ed27_path,height=720)
                    except Exception as _gsf_ed27_exc:
                        st.error("Editor 2027 demo non disponibile: "+str(_gsf_ed27_exc))

                # Vecchio Editor disattivato nella demo.
                if False and st.session_state.get("inline_editor_id")==_this_inline_id:
'''
if _old_inline_marker not in s:
    raise RuntimeError("Demo old inline editor marker not found")
s=s.replace(_old_inline_marker,_new_inline_marker,1)

# Switching among the three AI clips closes any currently open Editor 2027.
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

# DEMO UX: upload circle in the same coral/red family as "Scegli scena",
# with extra top breathing room so it sits centered between the four controls and the ad.
_upload_changes=[
    (
        '.wrap{height:234px;display:flex;align-items:flex-start;justify-content:center;padding-top:8px;box-sizing:border-box}',
        '.wrap{height:270px;display:flex;align-items:flex-start;justify-content:center;padding-top:26px;box-sizing:border-box}'
    ),
    (
        'align-items:center;justify-content:center;background:#DDF5E8;border:2px solid #69BE8E;\\nbox-shadow:0 10px 26px rgba(31,78,121,.10);color:#236B43}',
        'align-items:center;justify-content:center;background:#FFE8E5;border:2px solid #F28B82;\\nbox-shadow:0 10px 26px rgba(216,91,102,.12);color:#9F3844}'
    ),
    (
        '.icon{font-size:54px;font-weight:700;line-height:.82;color:#238A50;margin-bottom:13px}',
        '.icon{font-size:54px;font-weight:700;line-height:.82;color:#D85B66;margin-bottom:13px}'
    ),
    (
        '.wrap{height:254px;display:flex;flex-direction:column;align-items:center;justify-content:flex-start;padding-top:8px;box-sizing:border-box}',
        '.wrap{height:290px;display:flex;flex-direction:column;align-items:center;justify-content:flex-start;padding-top:30px;box-sizing:border-box}'
    ),
    (
        'align-items:center;justify-content:center;background:#DCEBFC;border:2px solid #8DB4E2;\\nbox-shadow:0 10px 26px rgba(31,78,121,.10);color:#214F82;cursor:pointer;user-select:none}',
        'align-items:center;justify-content:center;background:#FFE7E3;border:2px solid #F39A90;\\nbox-shadow:0 10px 26px rgba(216,91,102,.12);color:#A94750;cursor:pointer;user-select:none}'
    ),
    (
        '.circle:hover{border-color:#6F9FD5;box-shadow:0 12px 30px rgba(31,78,121,.14)}',
        '.circle:hover{border-color:#EA7E72;box-shadow:0 12px 30px rgba(216,91,102,.18)}'
    ),
    (
        '.icon{font-size:58px;font-weight:500;line-height:.82;color:#24558B;margin-bottom:13px}',
        '.icon{font-size:58px;font-weight:500;line-height:.82;color:#D45A64;margin-bottom:13px}'
    ),
    (
        '.status{display:none;margin-top:7px;width:174px;text-align:center;color:#238A50;font-size:12px;font-weight:800}',
        '.status{display:none;margin-top:7px;width:174px;text-align:center;color:#B54A55;font-size:12px;font-weight:800}'
    ),
    (
        '.track{display:block;height:5px;margin-top:5px;border-radius:999px;background:rgba(34,197,94,.18);overflow:hidden}',
        '.track{display:block;height:5px;margin-top:5px;border-radius:999px;background:rgba(216,91,102,.18);overflow:hidden}'
    ),
    (
        '.bar{display:block;height:100%;width:0;background:#22C55E;border-radius:999px;transition:width .12s linear}',
        '.bar{display:block;height:100%;width:0;background:#D85B66;border-radius:999px;transition:width .12s linear}'
    ),
    (
        '.circle.busy{pointer-events:none;background:#E8F2FD}',
        '.circle.busy{pointer-events:none;background:#FFF0EE}'
    ),
    (
        '.circle.done{background:#DDF5E8;border-color:#69BE8E;color:#236B43}',
        '.circle.done{background:#FFE8E5;border-color:#F28B82;color:#9F3844}'
    ),
    (
        '.circle.done .icon{color:#238A50}',
        '.circle.done .icon{color:#D85B66}'
    ),
    (
        'height=244 if video is not None else 264,',
        'height=280 if video is not None else 300,'
    ),
]
for _old,_new in _upload_changes:
    if _old not in s:
        raise RuntimeError("Demo upload style anchor not found: "+_old[:70])
    s=s.replace(_old,_new,1)

s=s.replace(
    '@media(max-width:600px){.wrap{height:224px}.circle{width:208px;height:208px}',
    '@media(max-width:600px){.wrap{height:252px}.circle{width:208px;height:208px}',
    1
)
s=s.replace(
    '@media(max-width:600px){.wrap{height:244px}.circle{width:208px;height:208px}',
    '@media(max-width:600px){.wrap{height:278px}.circle{width:208px;height:208px}',
    1
)

compile(s,str(out),'exec')
out.write_text(s,encoding='utf-8')
print('V106 functional demo applied:',out)
