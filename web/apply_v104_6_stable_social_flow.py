from pathlib import Path

src=Path('/app/GamingShortsFactory_V104_5_YOUTUBE_SOCIAL.py')
out=Path('/app/GamingShortsFactory_V104_6_STABLE_SOCIAL_FLOW.py')
s=src.read_text(encoding='utf-8')

# ------------------------------------------------------------------
# 1) Instagram connection is persisted per anonymous browser, same as
#    TikTok and YouTube.
# ------------------------------------------------------------------
anchor='def _gsf_instagram_config():\n'
pos=s.find(anchor)
if pos<0:
    raise RuntimeError('V104.6 Instagram config anchor missing')

helpers=r'''def _gsf_shared_instagram_load():
    try:
        client,bucket=_gsf_shared_tiktok_s3()
        if client is None:
            return {}
        obj=client.get_object(
            Bucket=bucket,
            Key=f"social-connections/{GSF_SESSION_ID}/instagram.json"
        )
        payload=json.loads(obj["Body"].read().decode("utf-8"))
        return payload if isinstance(payload,dict) else {}
    except Exception:
        return {}


def _gsf_shared_instagram_save(payload):
    try:
        client,bucket=_gsf_shared_tiktok_s3()
        if client is None:
            return False
        client.put_object(
            Bucket=bucket,
            Key=f"social-connections/{GSF_SESSION_ID}/instagram.json",
            Body=json.dumps(payload,ensure_ascii=False).encode("utf-8"),
            ContentType="application/json",
            CacheControl="no-store",
        )
        return True
    except Exception:
        return False


'''
s=s[:pos]+helpers+s[pos:]

old='''def _gsf_instagram_config():
    return _gsf_read_json_file(GSF_INSTAGRAM_CONFIG)
'''
new='''def _gsf_instagram_config():
    cfg=_gsf_read_json_file(GSF_INSTAGRAM_CONFIG)
    if cfg.get("ig_user_id") and cfg.get("access_token"):
        return cfg
    shared=_gsf_shared_instagram_load()
    if isinstance(shared,dict) and shared.get("ig_user_id") and shared.get("access_token"):
        try:
            _gsf_secure_write_json(GSF_INSTAGRAM_CONFIG,shared)
        except Exception:
            pass
        return shared
    return cfg
'''
if old not in s:
    raise RuntimeError('V104.6 Instagram config function mismatch')
s=s.replace(old,new,1)

old='''def _gsf_instagram_connect(ig_user_id,access_token):
    ok,username,error=_gsf_instagram_validate(
        ig_user_id,access_token
    )
    if not ok:
        return False,error

    _gsf_secure_write_json(
        GSF_INSTAGRAM_CONFIG,
        {
            "ig_user_id":str(ig_user_id).strip(),
            "access_token":str(access_token).strip(),
            "username":username,
        }
    )
    return True,username or "Instagram collegato"
'''
new='''def _gsf_instagram_connect(ig_user_id,access_token):
    ok,username,error=_gsf_instagram_validate(
        ig_user_id,access_token
    )
    if not ok:
        return False,error

    _payload={
        "ig_user_id":str(ig_user_id).strip(),
        "access_token":str(access_token).strip(),
        "username":username,
    }
    _gsf_secure_write_json(GSF_INSTAGRAM_CONFIG,_payload)
    _gsf_shared_instagram_save(_payload)
    return True,username or "Instagram collegato"
'''
if old not in s:
    raise RuntimeError('V104.6 Instagram connect function mismatch')
s=s.replace(old,new,1)

# ------------------------------------------------------------------
# 2) Web app no longer launches OAuth inside Streamlit.
#    It only checks connection and sends the user to standalone
#    /social-connect in a separate tab.
# ------------------------------------------------------------------
old='''                                if GSF_WEB_MODE:
                                    _auth_url, _auth_error = _gsf_social_web_auth_url(_platform)
                                    _connected, _connect_error = _gsf_social_connection_status(_platform)
                                    if _auth_url:
                                        st.session_state["social_auth_url_v77"] = _auth_url
                                        st.session_state["social_auth_platform_v77"] = _platform
                                        st.session_state["social_error_v59"] = (
                                            "Collega " + _platform + " per pubblicare tramite API ufficiale."
                                        )
                                    elif not _connected:
                                        st.session_state["social_error_v59"] = _auth_error or _connect_error
                                else:
'''
new='''                                if GSF_WEB_MODE:
                                    _connected, _connect_error = _gsf_social_connection_status(_platform)
                                    if not _connected:
                                        st.session_state["social_auth_url_v77"] = "/social-connect"
                                        st.session_state["social_auth_platform_v77"] = _platform
                                        st.session_state["social_error_v59"] = (
                                            "Collega " + _platform + " nella nuova scheda, poi torna qui e premi di nuovo."
                                        )
                                    else:
                                        st.session_state.pop("social_auth_url_v77",None)
                                        st.session_state.pop("social_auth_platform_v77",None)
                                        st.session_state["social_error_v59"] = ""
                                else:
'''
if old not in s:
    raise RuntimeError('V104.6 in-app social auth block mismatch')
s=s.replace(old,new,1)

# Clear any stale connection warning immediately before direct publication.
old='''                            if _connected:
                                with st.spinner("Carico il video su " + _platform + "..."):
'''
new='''                            if _connected:
                                st.session_state.pop("social_auth_url_v77",None)
                                st.session_state.pop("social_auth_platform_v77",None)
                                st.session_state["social_error_v59"] = ""
                                with st.spinner("Carico il video su " + _platform + "..."):
'''
if old not in s:
    raise RuntimeError('V104.6 connected publish block mismatch')
s=s.replace(old,new,1)

# Always open Social Connect in a new browser tab so the prepared Short and
# current Streamlit websocket/session stay untouched.
old='''                if _auth_url and _auth_platform:
                    st.link_button(
                        "COLLEGA " + str(_auth_platform).upper(),
                        _auth_url,
                        use_container_width=True,
                    )
                    st.caption("Collega TikTok una volta da Collega social in fondo alla pagina. Non serve caricare un video.")
'''
new='''                if _auth_url and _auth_platform:
                    _safe_platform=html.escape(str(_auth_platform).upper())
                    st.markdown(
                        '<a href="/social-connect" target="_blank" rel="noopener noreferrer" '
                        'style="display:block;width:100%;box-sizing:border-box;text-align:center;'
                        'text-decoration:none;padding:0.78rem 1rem;border-radius:0.6rem;'
                        'background:#1687ff;color:white;font-weight:800;margin:0.3rem 0 0.4rem 0">'
                        'COLLEGA '+_safe_platform+'</a>',
                        unsafe_allow_html=True,
                    )
                    st.caption(
                        "Si apre una nuova scheda: collega il social, chiudila e torna qui. "
                        "Il video pronto resta aperto e non viene azzerato."
                    )
'''
if old not in s:
    raise RuntimeError('V104.6 social link button block mismatch')
s=s.replace(old,new,1)

# ------------------------------------------------------------------
# 3) TikTok unaudited fallback: if public Direct Post is rejected solely
#    because the client is not audited, retry init as SELF_ONLY.
# ------------------------------------------------------------------
old='''    payload=init.get("data") or {}
    api_error=payload.get("error") or {}
    if not init.get("ok") or (
        isinstance(api_error,dict)
        and api_error.get("code") not in (None,"","ok")
    ):
        return {"ok":False,"error":str(payload or init.get("error"))}

    data=payload.get("data") or {}
'''
new='''    payload=init.get("data") or {}
    api_error=payload.get("error") or {}
    _api_code=str(api_error.get("code","") or "") if isinstance(api_error,dict) else ""
    if (
        _api_code=="unaudited_client_can_only_post_to_private_accounts"
        and privacy!="SELF_ONLY"
        and "SELF_ONLY" in options
    ):
        privacy="SELF_ONLY"
        init=_gsf_http_json(
            GSF_TIKTOK_DIRECT_INIT,
            method="POST",
            headers={
                "Authorization":f"Bearer {access_token}",
                "Content-Type":"application/json; charset=UTF-8",
            },
            json_body={
                "post_info":{
                    "title":caption,
                    "privacy_level":privacy,
                    "disable_comment":bool(creator.get("comment_disabled",False)),
                    "disable_duet":bool(creator.get("duet_disabled",False)),
                    "disable_stitch":bool(creator.get("stitch_disabled",False)),
                },
                "source_info":{
                    "source":"FILE_UPLOAD",
                    "video_size":size,
                    "chunk_size":chunk_size,
                    "total_chunk_count":total_count,
                }
            }
        )
        payload=init.get("data") or {}
        api_error=payload.get("error") or {}

    if not init.get("ok") or (
        isinstance(api_error,dict)
        and api_error.get("code") not in (None,"","ok")
    ):
        return {"ok":False,"error":str(payload or init.get("error"))}

    data=payload.get("data") or {}
'''
if old not in s:
    raise RuntimeError('V104.6 TikTok init result block mismatch')
s=s.replace(old,new,1)

marker='Gaming Shorts Factory · V104.5 YouTube Social Connect'
if marker in s:
    s=s.replace(marker,'Gaming Shorts Factory · V104.6 Stable Social Flow',1)

compile(s,str(out),'exec')
out.write_text(s,encoding='utf-8')
print(f'V104.6 stable social flow applied: {out}')
