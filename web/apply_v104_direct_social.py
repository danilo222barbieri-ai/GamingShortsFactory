from pathlib import Path
import ast,re

src=Path('/app/GamingShortsFactory_V103_2_CANONICAL_FORMAT.py')
out=Path('/app/GamingShortsFactory_V104_DIRECT_SOCIAL.py')
s=src.read_text(encoding='utf-8')

# ------------------------------------------------------------
# V104 — DIRECT SOCIAL ONLY
# YouTube Shorts / TikTok / Instagram Reels
# ------------------------------------------------------------

# TikTok Direct Post endpoints/scopes.
if re.search(r'^GSF_TIKTOK_SCOPES\s*=.*$',s,flags=re.M):
    s=re.sub(
        r'^GSF_TIKTOK_SCOPES\s*=.*$',
        'GSF_TIKTOK_SCOPES = "user.info.basic,video.publish"',
        s,count=1,flags=re.M
    )
else:
    anchor='GSF_TIKTOK_UPLOAD_INIT = "https://open.tiktokapis.com/v2/post/publish/inbox/video/init/"\n'
    if anchor not in s:
        raise RuntimeError('V104 TikTok constant anchor missing')
    s=s.replace(
        anchor,
        anchor+
        'GSF_TIKTOK_SCOPES = "user.info.basic,video.publish"\n',
        1
    )

const_anchor='GSF_TIKTOK_UPLOAD_INIT = "https://open.tiktokapis.com/v2/post/publish/inbox/video/init/"\n'
if const_anchor not in s:
    raise RuntimeError('V104 TikTok upload constant missing')
s=s.replace(
    const_anchor,
    const_anchor+
    'GSF_TIKTOK_DIRECT_INIT = "https://open.tiktokapis.com/v2/post/publish/video/init/"\n'
    'GSF_TIKTOK_CREATOR_INFO = "https://open.tiktokapis.com/v2/post/publish/creator_info/query/"\n',
    1
)

# Direct posting means video.publish, not the draft-only video.upload scope.
s=s.replace('"video.upload"','"video.publish"')
s=s.replace('TikTok video.upload','TikTok video.publish')
s=s.replace('concesso video.upload','concesso video.publish')

# Meta OAuth app credentials stay developer-side, never in end-user UI.
env_anchor='"public_app_url":"GSF_PUBLIC_APP_URL",'
if env_anchor not in s:
    raise RuntimeError('V104 app credentials env anchor missing')
s=s.replace(
    env_anchor,
    '"meta_app_id":"GSF_META_APP_ID",\n'
    '        "meta_app_secret":"GSF_META_APP_SECRET",\n'
    '        '+env_anchor,
    1
)

# Public publishing is the product default; unverified Google projects can
# still be forced private by YouTube itself.
s=s.replace(
    'prefs.setdefault("youtube_privacy","private")',
    'prefs.setdefault("youtube_privacy","public")',
    1
)

# ---------- TikTok direct post helpers ----------
insert_anchor='def _gsf_tiktok_upload_draft(video_bytes,progress_callback=None):\n'
pos=s.find(insert_anchor)
if pos<0:
    raise RuntimeError('V104 TikTok upload function anchor missing')

helper=r'''def _gsf_tiktok_creator_info():
    token,config,error=_gsf_tiktok_credentials()
    if token is None:
        return {"ok":False,"error":error or "TikTok non collegato"}

    res=_gsf_http_json(
        GSF_TIKTOK_CREATOR_INFO,
        method="POST",
        headers={
            "Authorization":f"Bearer {token.get('access_token','')}",
            "Content-Type":"application/json; charset=UTF-8",
        },
        json_body={}
    )
    payload=res.get("data") or {}
    api_error=payload.get("error") or {}
    if not res.get("ok") or (
        isinstance(api_error,dict)
        and api_error.get("code") not in (None,"","ok")
    ):
        return {"ok":False,"error":str(payload or res.get("error"))}

    data=payload.get("data") or {}
    return {
        "ok":True,
        "username":str(data.get("creator_username","") or ""),
        "nickname":str(data.get("creator_nickname","") or ""),
        "privacy_level_options":list(data.get("privacy_level_options") or []),
        "comment_disabled":bool(data.get("comment_disabled",False)),
        "duet_disabled":bool(data.get("duet_disabled",False)),
        "stitch_disabled":bool(data.get("stitch_disabled",False)),
        "max_video_post_duration_sec":int(data.get("max_video_post_duration_sec",0) or 0),
        "error":"",
    }


def _gsf_tiktok_direct_post(video_bytes,pack,progress_callback=None):
    """V104 official TikTok Direct Post. No draft hand-off."""
    token,config,error=_gsf_tiktok_credentials()
    if token is None:
        return {"ok":False,"error":error or "TikTok non collegato"}
    if not isinstance(video_bytes,(bytes,bytearray)) or len(video_bytes)<1:
        return {"ok":False,"error":"Master video non disponibile"}

    creator=_gsf_tiktok_creator_info()
    if not creator.get("ok"):
        return creator

    options=[
        str(x) for x in creator.get("privacy_level_options",[]) or []
        if str(x)
    ]
    # One explicit click on TikTok is the publish consent. Prefer public when
    # TikTok offers it; unaudited clients naturally fall back to SELF_ONLY.
    if "PUBLIC_TO_EVERYONE" in options:
        privacy="PUBLIC_TO_EVERYONE"
    elif "SELF_ONLY" in options:
        privacy="SELF_ONLY"
    elif options:
        privacy=options[0]
    else:
        return {"ok":False,"error":"TikTok non ha restituito opzioni di privacy"}

    caption=str(
        (pack or {}).get("selected_caption",(pack or {}).get("caption",""))
        or ""
    ).strip()[:2200]

    access_token=str(token.get("access_token","") or "")
    size=len(video_bytes)
    chunk_size,total_count=_gsf_tiktok_chunk_plan(size)

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
    upload_url=str(data.get("upload_url","") or "")
    publish_id=str(data.get("publish_id","") or "")
    if not upload_url or not publish_id:
        return {"ok":False,"error":"TikTok non ha restituito upload_url/publish_id"}

    sent=0
    while sent<size:
        remaining=size-sent
        if total_count<=1:
            this_size=remaining
        else:
            part_index=sent//chunk_size
            this_size=remaining if part_index>=total_count-1 else min(chunk_size,remaining)

        end=sent+this_size-1
        req=Request(
            upload_url,
            data=bytes(video_bytes[sent:sent+this_size]),
            headers={
                "Content-Type":"video/mp4",
                "Content-Length":str(this_size),
                "Content-Range":f"bytes {sent}-{end}/{size}",
            },
            method="PUT"
        )
        try:
            with urlopen(req,timeout=120) as resp:
                status=int(getattr(resp,"status",0) or 0)
                if status not in (200,201,206):
                    return {
                        "ok":False,
                        "error":f"TikTok upload HTTP {status}",
                        "publish_id":publish_id,
                    }
        except HTTPError as e:
            body=e.read().decode("utf-8","replace") if hasattr(e,"read") else ""
            return {
                "ok":False,
                "error":f"TikTok upload HTTP {getattr(e,'code',0)}: {body}",
                "publish_id":publish_id,
            }
        except Exception as e:
            return {"ok":False,"error":str(e),"publish_id":publish_id}

        sent+=this_size
        if progress_callback:
            try:
                progress_callback(int(sent/size*100))
            except Exception:
                pass

    return {
        "ok":True,
        "publish_id":publish_id,
        "privacy":privacy,
        "creator":creator.get("username") or creator.get("nickname") or "",
        "error":"",
    }


'''
s=s[:pos]+helper+s[pos:]

# ---------- Instagram OAuth bridge ----------
social_auth_anchor='def _gsf_social_connection_status(platform):\n'
pos=s.find(social_auth_anchor)
if pos<0:
    raise RuntimeError('V104 social auth insertion anchor missing')

ig_oauth=r'''GSF_META_AUTH_URL = "https://www.facebook.com/dialog/oauth"
GSF_META_TOKEN_URL = "https://graph.facebook.com/oauth/access_token"
GSF_META_SCOPES = "pages_show_list,instagram_basic,instagram_content_publish,pages_read_engagement"


def _gsf_instagram_web_auth_url():
    cfg=_gsf_app_credentials()
    app_id=str(cfg.get("meta_app_id","") or "").strip()
    app_secret=str(cfg.get("meta_app_secret","") or "").strip()
    redirect_uri=_gsf_public_app_url()
    if not app_id or not app_secret:
        # Preserve the existing pre-provisioned server connection path.
        uid=str(cfg.get("instagram_user_id","") or "").strip()
        token=str(cfg.get("instagram_access_token","") or "").strip()
        if uid and token:
            ok,msg=_gsf_instagram_connect(uid,token)
            return "","" if ok else msg
        return "","Instagram non è configurato sul server."
    if not redirect_uri or not redirect_uri.lower().startswith("https://"):
        return "","Instagram Web richiede GSF_PUBLIC_APP_URL in HTTPS."

    state=secrets.token_urlsafe(32)
    _gsf_write_oauth_state(state,{
        "platform":"Instagram",
        "redirect_uri":redirect_uri,
    })
    params={
        "client_id":app_id,
        "redirect_uri":redirect_uri,
        "state":state,
        "response_type":"code",
        "scope":GSF_META_SCOPES,
    }
    return GSF_META_AUTH_URL+"?"+urlencode(params),""


def _gsf_instagram_web_complete(code,state,pending):
    cfg=_gsf_app_credentials()
    app_id=str(cfg.get("meta_app_id","") or "").strip()
    app_secret=str(cfg.get("meta_app_secret","") or "").strip()
    redirect_uri=str((pending or {}).get("redirect_uri","") or _gsf_public_app_url()).strip()
    if not app_id or not app_secret or not redirect_uri:
        return False,"Configurazione Instagram/Meta incompleta sul server."

    token_url=GSF_META_TOKEN_URL+"?"+urlencode({
        "client_id":app_id,
        "client_secret":app_secret,
        "redirect_uri":redirect_uri,
        "code":str(code),
    })
    token_res=_gsf_http_json(token_url,method="GET",timeout=45)
    token_data=token_res.get("data") or {}
    user_token=str(token_data.get("access_token","") or "")
    if not token_res.get("ok") or not user_token:
        return False,str(token_data or token_res.get("error"))

    # Exchange to long-lived user token when Meta allows it.
    long_url=GSF_META_TOKEN_URL+"?"+urlencode({
        "grant_type":"fb_exchange_token",
        "client_id":app_id,
        "client_secret":app_secret,
        "fb_exchange_token":user_token,
    })
    long_res=_gsf_http_json(long_url,method="GET",timeout=45)
    long_data=long_res.get("data") or {}
    if long_res.get("ok") and long_data.get("access_token"):
        user_token=str(long_data.get("access_token"))

    accounts_url="https://graph.facebook.com/me/accounts?"+urlencode({
        "fields":"name,access_token,tasks,instagram_business_account",
        "access_token":user_token,
    })
    accounts_res=_gsf_http_json(accounts_url,method="GET",timeout=45)
    accounts_data=accounts_res.get("data") or {}
    pages=accounts_data.get("data") if isinstance(accounts_data,dict) else None
    if not accounts_res.get("ok") or not isinstance(pages,list):
        return False,str(accounts_data or accounts_res.get("error"))

    for page in pages:
        if not isinstance(page,dict):
            continue
        ig=(page.get("instagram_business_account") or {})
        ig_id=str(ig.get("id","") or "")
        page_token=str(page.get("access_token","") or "")
        if ig_id and page_token:
            ok,msg=_gsf_instagram_connect(ig_id,page_token)
            if ok:
                return True,"Instagram collegato."
            return False,msg

    return False,"Nessun account Instagram professionale collegato a una Pagina Facebook."


'''
s=s[:pos]+ig_oauth+s[pos:]

# Replace Instagram auth branch with actual OAuth.
old='''    if platform == "Instagram":
        # Meta publishing is API-only here, but user OAuth requires a dedicated
        # Meta Login configuration. A server-owned connection can be provisioned
        # through GSF_INSTAGRAM_USER_ID / GSF_INSTAGRAM_ACCESS_TOKEN.
        cfg = _gsf_app_credentials()
        uid = str(cfg.get("instagram_user_id", "") or "").strip()
        token = str(cfg.get("instagram_access_token", "") or "").strip()
        if uid and token:
            ok, msg = _gsf_instagram_connect(uid, token)
            return "", "" if ok else msg
        return "", "Instagram richiede la configurazione Meta del sito."
'''
new='''    if platform == "Instagram":
        return _gsf_instagram_web_auth_url()
'''
if old not in s:
    raise RuntimeError('V104 Instagram social auth branch missing')
s=s.replace(old,new,1)

# Instagram OAuth callback.
old='''    elif platform == "TikTok":
        ok, message = _gsf_tiktok_web_complete(code, state, pending)
    else:
        ok, message = False, "Callback social non riconosciuto."
'''
new='''    elif platform == "TikTok":
        ok, message = _gsf_tiktok_web_complete(code, state, pending)
    elif platform == "Instagram":
        ok, message = _gsf_instagram_web_complete(code, state, pending)
    else:
        ok, message = False, "Callback social non riconosciuto."
'''
if old not in s:
    raise RuntimeError('V104 OAuth callback anchor missing')
s=s.replace(old,new,1)

# TikTok branch: Direct Post instead of inbox/draft.
old='''        if platform == "TikTok":
            result = _gsf_tiktok_upload_draft(bytes(video))
            if not result.get("ok"):
                message = str(result.get("error", "Upload TikTok non riuscito"))
                _gsf_write_social_status(platform, "error", message)
                return False, message, exported
            message = "Video inviato a TikTok. Completa il post dalla notifica/bozza TikTok."
            _gsf_write_social_status(platform, "ready", message, publish_id=result.get("publish_id", ""))
            return True, message, exported
'''
new='''        if platform == "TikTok":
            result = _gsf_tiktok_direct_post(bytes(video), pack)
            if not result.get("ok"):
                message = str(result.get("error", "Pubblicazione TikTok non riuscita"))
                _gsf_write_social_status(platform, "error", message)
                return False, message, exported
            _privacy=str(result.get("privacy","") or "")
            message = (
                "Video pubblicato su TikTok."
                if _privacy!="SELF_ONLY"
                else "Video pubblicato su TikTok in modalità privata (SELF_ONLY)."
            )
            _gsf_write_social_status(
                platform, "ready", message,
                publish_id=result.get("publish_id", ""),
                privacy=_privacy,
            )
            return True, message, exported
'''
if old not in s:
    raise RuntimeError('V104 TikTok publish branch missing')
s=s.replace(old,new,1)

# Direct publication progress wording.
old='''    if state == "ready":
        st.success("✅ Video pronto su " + platform + ". Completa la pubblicazione lì.")
'''
new='''    if state == "ready":
        st.success("✅ " + str(status.get("message") or ("Pubblicato su " + platform + ".")))
'''
if old not in s:
    raise RuntimeError('V104 social progress ready anchor missing')
s=s.replace(old,new,1)

# V104 is deliberately only three direct-publish destinations; remove old
# metadata editor UI if still rendered anywhere in the final social block.
s=s.replace(
    'st.markdown(\'<div class="gsf-icon-title">\' + _gsf_v67_badge("publish", "Pubblicazione", "indigo") + \'</div>\', unsafe_allow_html=True)',
    'st.markdown(\'<div class="gsf-icon-title">\' + _gsf_v67_badge("publish", "Pubblicazione diretta", "indigo") + \'</div>\', unsafe_allow_html=True)',
    1
)

marker='Gaming Shorts Factory · V103.2 Canonical Final Format'
if marker not in s:
    raise RuntimeError('V104 version marker missing')
s=s.replace(marker,'Gaming Shorts Factory · V104 Direct Social',1)

out.write_text(s,encoding='utf-8')
print(f'V104 Direct Social applied: {out}')
