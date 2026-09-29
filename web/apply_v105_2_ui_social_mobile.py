from pathlib import Path

src=Path('/app/GamingShortsFactory_V105_1_NO_AUDIO_MASTER.py')
out=Path('/app/GamingShortsFactory_V105_2_UI_SOCIAL_MOBILE.py')
s=src.read_text(encoding='utf-8')

# Native mobile share helper.
if 'import streamlit.components.v1 as components' not in s:
    anchor='import streamlit as st\n'
    if anchor not in s:
        raise RuntimeError('Streamlit import anchor missing')
    s=s.replace(anchor,anchor+'import streamlit.components.v1 as components\n',1)

# 1) Empty speech transcription should be explicit instead of looking broken.
old='''                    st.session_state["editor_auto_sub_scene_token"]=_auto_sub_token
                    st.session_state["editor_auto_sub_error"]=str(_auto_err or "")

                    if _auto_err:
                        st.session_state["editor_sub_words"]=[]
                        st.session_state["editor_sub_live_words"]=[]
                        st.session_state["editor_sub_text"]=""
                    else:
                        _auto_words=list(_auto_words or [])
                        _auto_text=" ".join(
                            str(w.get("text","")).strip()
                            for w in _auto_words
                            if str(w.get("text","")).strip()
                        )
                        st.session_state["editor_sub_words"]=_auto_words
                        st.session_state["editor_sub_live_words"]=_auto_words
                        st.session_state["editor_sub_text"]=_auto_text
'''
new='''                    st.session_state["editor_auto_sub_scene_token"]=_auto_sub_token
                    st.session_state["editor_auto_sub_error"]=str(_auto_err or "")

                    if _auto_err:
                        st.session_state["editor_auto_sub_no_speech"]=False
                        st.session_state["editor_sub_words"]=[]
                        st.session_state["editor_sub_live_words"]=[]
                        st.session_state["editor_sub_text"]=""
                    else:
                        _auto_words=list(_auto_words or [])
                        _auto_text=" ".join(
                            str(w.get("text","")).strip()
                            for w in _auto_words
                            if str(w.get("text","")).strip()
                        )
                        st.session_state["editor_auto_sub_no_speech"]=not bool(_auto_text)
                        st.session_state["editor_sub_words"]=_auto_words
                        st.session_state["editor_sub_live_words"]=_auto_words
                        st.session_state["editor_sub_text"]=_auto_text
'''
if old not in s:
    raise RuntimeError('Auto subtitle result anchor missing')
s=s.replace(old,new,1)

old='''                elif st.session_state.get("editor_sub_live_words"):
                    st.caption(
                        "Trascrizione automatica pronta · "
                        f"{len(st.session_state.get('editor_sub_live_words',[]))} parole"
                    )
'''
new='''                elif st.session_state.get("editor_auto_sub_no_speech",False):
                    st.info("Nessuna traccia parlata")
                elif st.session_state.get("editor_sub_live_words"):
                    st.caption(
                        "Trascrizione automatica pronta · "
                        f"{len(st.session_state.get('editor_sub_live_words',[]))} parole"
                    )
'''
if old not in s:
    raise RuntimeError('Auto subtitle status anchor missing')
s=s.replace(old,new,1)

s=s.replace(
    'st.session_state.pop("editor_auto_sub_error",None)\n                        st.rerun()',
    'st.session_state.pop("editor_auto_sub_error",None)\n                        st.session_state.pop("editor_auto_sub_no_speech",None)\n                        st.rerun()',
    1,
)

# 2) Ad before Create Short + more breathing room before the action button.
old='''    if _show_final_flow:
        st.divider()
        st.markdown('<div class="gsf-icon-title">' + _gsf_v67_badge("play", "Crea lo Short finale", "peach") + '</div>', unsafe_allow_html=True)
'''
new='''    if _show_final_flow:
        st.markdown('<aside class="v67-ad" aria-label="Spazio pubblicitario">Pubblicità</aside>', unsafe_allow_html=True)
        st.divider()
        st.markdown('<div class="gsf-icon-title">' + _gsf_v67_badge("play", "Crea lo Short finale", "peach") + '</div>', unsafe_allow_html=True)
        st.markdown('<div style="height:22px" aria-hidden="true"></div>', unsafe_allow_html=True)
'''
if old not in s:
    raise RuntimeError('Create Short heading anchor missing')
s=s.replace(old,new,1)

# 3) Allow publishing with user-edited copy instead of always rebuilding it.
s=s.replace(
    'def _gsf_publish_social_upload(video, platform):',
    'def _gsf_publish_social_upload(video, platform, pack_override=None):',
    1,
)
old='''    recipe = st.session_state.get("gsf_final_recipe", {}) or {}
    start = float(recipe.get("start", 0.0) or 0.0)
    game = st.session_state.get("gioco", "Gaming")
    tone = st.session_state.get("tono_social", "Gaming forte")
    pack = _gsf_finalize_publish_pack(
        _gsf_build_publish_pack(start, platform=platform_name, game=game, tone=tone)
    )
'''
new='''    recipe = st.session_state.get("gsf_final_recipe", {}) or {}
    start = float(recipe.get("start", 0.0) or 0.0)
    game = st.session_state.get("gioco", "Gaming")
    tone = st.session_state.get("tono_social", "Gaming forte")
    if isinstance(pack_override,dict) and pack_override:
        pack=dict(pack_override)
    else:
        pack = _gsf_finalize_publish_pack(
            _gsf_build_publish_pack(start, platform=platform_name, game=game, tone=tone)
        )
'''
if old not in s:
    raise RuntimeError('Social pack override anchor missing')
s=s.replace(old,new,1)

start_marker='''            if st.session_state.get("show_social_publish_v54", False):
                st.markdown('<div class="gsf-icon-title">' + _gsf_v67_badge("publish", "Pubblicazione diretta", "indigo") + '</div>', unsafe_allow_html=True)
'''
end_marker='''                _auth_url = st.session_state.get("social_auth_url_v77", "")
'''
a=s.find(start_marker)
b=s.find(end_marker,a)
if a<0 or b<0:
    raise RuntimeError('Direct social UI block anchors missing')

new_block='''            if st.session_state.get("show_social_publish_v54", False):
                st.markdown('<div class="gsf-icon-title">' + _gsf_v67_badge("publish", "Pubblicazione diretta", "indigo") + '</div>', unsafe_allow_html=True)
                _selected_social = st.session_state.get("social_selected_v59")
                _social_columns = st.columns(3, gap="small")
                for _column, _platform in zip(
                    _social_columns, ("YouTube", "TikTok", "Instagram")
                ):
                    with _column, st.container(key="v69_social_" + _platform.lower()):
                        if st.button(
                            _platform,
                            type=("primary" if _selected_social == _platform else "secondary"),
                            use_container_width=True,
                            key="social_upload_v59_" + _platform.lower(),
                        ):
                            st.session_state["social_selected_v59"] = _platform
                            st.session_state["social_started_v59"] = False
                            st.session_state.pop("social_error_v59", None)
                            st.session_state.pop("social_auth_url_v77", None)
                            st.session_state.pop("social_auth_platform_v77", None)
                            st.rerun()

                _selected_social = st.session_state.get("social_selected_v59")
                if _selected_social in ("YouTube","TikTok","Instagram"):
                    _platform_name = {
                        "YouTube":"YouTube Shorts",
                        "TikTok":"TikTok",
                        "Instagram":"Instagram Reels",
                    }[_selected_social]
                    _recipe = st.session_state.get("gsf_final_recipe", {}) or {}
                    _start = float(_recipe.get("start",0.0) or 0.0)
                    _game = st.session_state.get("gioco","Gaming")
                    _tone = st.session_state.get("tono_social","Gaming forte")
                    _base_pack = _gsf_finalize_publish_pack(
                        _gsf_build_publish_pack(
                            _start,
                            platform=_platform_name,
                            game=_game,
                            tone=_tone,
                        )
                    )
                    _ctx = _gsf_publish_context_token(_base_pack)
                    _slug = _selected_social.lower()
                    _default_title = str(_base_pack.get("selected_title",_base_pack.get("title","")) or "")
                    _default_description = _gsf_social_clean_description(_base_pack)
                    _default_hashtags = " ".join(_base_pack.get("hashtags",[]) or [])

                    st.markdown(
                        '<div style="margin-top:14px;padding:14px 16px;border:1px solid rgba(112,142,168,.28);'
                        'border-radius:18px;background:rgba(255,255,255,.72)">'
                        '<strong>'+html.escape(_selected_social)+'</strong> · controlla i dati prima di pubblicare'
                        '</div>',
                        unsafe_allow_html=True,
                    )
                    _title = st.text_input(
                        "Titolo",
                        value=_default_title,
                        key=f"social_title_{_slug}_{_ctx}",
                    )
                    _description = st.text_area(
                        "Descrizione",
                        value=_default_description,
                        key=f"social_description_{_slug}_{_ctx}",
                        height=120,
                    )
                    _hashtags = st.text_input(
                        "Hashtag",
                        value=_default_hashtags,
                        key=f"social_hashtags_{_slug}_{_ctx}",
                    )

                    if st.button(
                        "PUBBLICA",
                        type="primary",
                        use_container_width=True,
                        key=f"social_publish_confirm_{_slug}_{_ctx}",
                    ):
                        _edited_pack = _gsf_social_pack_for_upload(
                            _base_pack,
                            _title,
                            _description,
                            _hashtags,
                        )
                        _connected, _connect_error = _gsf_social_connection_status(_selected_social)
                        if not _connected and GSF_WEB_MODE:
                            st.session_state["social_auth_url_v77"] = "/social-connect"
                            st.session_state["social_auth_platform_v77"] = _selected_social
                            st.session_state["social_error_v59"] = (
                                "Collega " + _selected_social + " nella nuova scheda, poi torna qui e premi PUBBLICA."
                            )
                        elif not _connected:
                            _connected, _connect_error = _gsf_connect_social_account(_selected_social)
                            if not _connected:
                                st.session_state["social_error_v59"] = _connect_error

                        if _connected:
                            st.session_state.pop("social_auth_url_v77",None)
                            st.session_state.pop("social_auth_platform_v77",None)
                            st.session_state["social_error_v59"] = ""
                            with st.spinner("Carico il video su " + _selected_social + "..."):
                                _ok, _message, _path = _gsf_publish_social_upload(
                                    _final_video,
                                    _selected_social,
                                    pack_override=_edited_pack,
                                )
                            st.session_state["social_started_v59"] = _ok
                            if _path:
                                st.session_state["social_export_v59"] = _path
                            if not _ok:
                                st.session_state["social_error_v59"] = _message

'''
s=s[:a]+new_block+s[b:]

# 4) Mobile native share/save. Keep Streamlit download as fallback.
download_anchor='''            with _download_col:
                st.download_button(
                    "SCARICA",
                    _final_video,
                    "gaming_short_finale.mp4",
                    "video/mp4",
                    use_container_width=True,
                    key="download_final_v54"
                )
'''
download_new='''            with _download_col:
                st.download_button(
                    "SCARICA",
                    _final_video,
                    "gaming_short_finale.mp4",
                    "video/mp4",
                    use_container_width=True,
                    key="download_final_v54"
                )

            # V105.2: expose the final MP4 through the authenticated /media route
            # and invoke the phone's native share sheet (iOS: includes Salva video
            # when Safari/OS supports file sharing). No base64 copy in Streamlit.
            try:
                _share_root=Path(os.environ.get("GSF_RUNTIME_ROOT","/tmp/gsf-runtime"))/"sessions"/str(GSF_SESSION_ID)/"media"
                _share_root.mkdir(parents=True,exist_ok=True)
                _share_path=_share_root/"gaming_short_finale_share.mp4"
                if (not _share_path.exists()) or _share_path.stat().st_size!=len(_final_video):
                    _share_path.write_bytes(bytes(_final_video))
                _share_url=f"/media/{quote(str(GSF_SESSION_ID),safe='')}/media/gaming_short_finale_share.mp4"
                components.html(
                    f"""<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<style>body{{margin:0;font-family:Arial,sans-serif}}button{{width:100%;border:1px solid #9fcdea;border-radius:12px;
padding:11px 12px;background:#fff;color:#17324a;font-weight:750;font-size:14px}}#msg{{font-size:12px;color:#667b8e;margin-top:6px;text-align:center}}</style></head>
<body><button id="share">SALVA / CONDIVIDI SU MOBILE</button><div id="msg"></div>
<script>
const btn=document.getElementById('share'), msg=document.getElementById('msg');
btn.onclick=async()=>{{
  try{{
    const r=await fetch('{_share_url}',{{credentials:'include'}});
    if(!r.ok) throw new Error('video non disponibile');
    const blob=await r.blob();
    const file=new File([blob],'gaming_short_finale.mp4',{{type:'video/mp4'}});
    if(navigator.share && (!navigator.canShare || navigator.canShare({{files:[file]}}))){{
      await navigator.share({{files:[file],title:'Gaming Short'}});
      msg.textContent='Condivisione aperta. Puoi tornare subito all’app.';
    }}else{{
      window.open('{_share_url}','_blank');
      msg.textContent='Il browser non supporta il salvataggio diretto: usa il menu del video.';
    }}
  }}catch(e){{msg.textContent='Usa SCARICA come alternativa.';}}
}};
</script></body></html>""",
                    height=76,
                )
            except Exception:
                pass
'''
if download_anchor not in s:
    raise RuntimeError('Final download anchor missing')
s=s.replace(download_anchor,download_new,1)

s=s.replace(
    'Gaming Shorts Factory · V105.1 No-Audio Master',
    'Gaming Shorts Factory · V105.2 UI Social Mobile',
    1,
)

compile(s,str(out),'exec')
out.write_text(s,encoding='utf-8')
print(f'V105.2 UI/social/mobile patch applied: {out}')
