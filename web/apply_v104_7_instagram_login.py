from pathlib import Path
import ast

src=Path('/app/GamingShortsFactory_V104_6_STABLE_SOCIAL_FLOW.py')
out=Path('/app/GamingShortsFactory_V104_7_INSTAGRAM_LOGIN.py')
s=src.read_text(encoding='utf-8')

def replace_function(source,name,new_source):
    tree=ast.parse(source)
    node=next((n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name),None)
    if node is None:
        raise RuntimeError(f'Function {name} not found')
    lines=source.splitlines(keepends=True)
    start=node.lineno-1
    end=node.end_lineno
    replacement=new_source.rstrip()+"\n"
    return ''.join(lines[:start])+replacement+''.join(lines[end:])

# Expose the dedicated Instagram App credentials (different from the Meta App ID).
needle='''        "meta_app_id":"GSF_META_APP_ID",
        "meta_app_secret":"GSF_META_APP_SECRET",
'''
replacement='''        "instagram_app_id":"GSF_INSTAGRAM_APP_ID",
        "instagram_app_secret":"GSF_INSTAGRAM_APP_SECRET",
        "meta_app_id":"GSF_META_APP_ID",
        "meta_app_secret":"GSF_META_APP_SECRET",
'''
if needle not in s:
    raise RuntimeError('V104.7 app credentials anchor missing')
s=s.replace(needle,replacement,1)

s=replace_function(s,'_gsf_instagram_validate',r'''
def _gsf_instagram_validate(ig_user_id,access_token,api_host=None):
    ig_user_id=str(ig_user_id or "").strip()
    access_token=str(access_token or "").strip()
    if not ig_user_id or not access_token:
        return False,"","Inserisci IG User ID e access token"

    if not api_host:
        cfg=_gsf_instagram_config()
        api_host=str(cfg.get("api_host","") or "").strip()
    if not api_host:
        api_host=(
            "https://graph.instagram.com"
            if access_token.upper().startswith(("IGAA","IGQV","IG"))
            else "https://graph.facebook.com"
        )
    api_host=str(api_host).rstrip("/")

    url=(
        api_host+"/"
        +quote(ig_user_id,safe="")
        +"?"+urlencode({
            "fields":"id,username",
            "access_token":access_token,
        })
    )
    res=_gsf_http_json(url,method="GET")
    if not res.get("ok"):
        return False,"",str(res.get("data") or res.get("error"))

    data=res.get("data") or {}
    if data.get("error"):
        return False,"",str(data.get("error"))

    username=str(data.get("username","") or "")
    return True,username,""
''')

s=replace_function(s,'_gsf_instagram_connect',r'''
def _gsf_instagram_connect(ig_user_id,access_token,api_host=None,oauth_mode=None):
    if not api_host:
        api_host=(
            "https://graph.instagram.com"
            if str(access_token or "").upper().startswith(("IGAA","IGQV","IG"))
            else "https://graph.facebook.com"
        )
    ok,username,error=_gsf_instagram_validate(
        ig_user_id,access_token,api_host=api_host
    )
    if not ok:
        return False,error

    _payload={
        "ig_user_id":str(ig_user_id).strip(),
        "access_token":str(access_token).strip(),
        "username":username,
        "api_host":str(api_host).rstrip("/"),
        "oauth_mode":str(oauth_mode or ""),
    }
    _gsf_secure_write_json(GSF_INSTAGRAM_CONFIG,_payload)
    _gsf_shared_instagram_save(_payload)
    return True,username or "Instagram collegato"
''')

s=replace_function(s,'_gsf_instagram_publish_reel_auto',r'''
def _gsf_instagram_publish_reel_auto(
    video_bytes,
    pack,
    share_to_feed=True,
    progress_callback=None
):
    """
    In Railway web mode, stage the finished MP4 in the existing private S3
    bucket and give Meta a short-lived signed GET URL. This avoids the /media
    cookie protection that external Meta fetchers cannot satisfy.
    """
    if GSF_WEB_MODE:
        if not isinstance(video_bytes,(bytes,bytearray)) or len(video_bytes)<1024:
            return {"ok":False,"error":"Master video non disponibile"}

        client,bucket=_gsf_shared_tiktok_s3()
        if client is None or not bucket:
            return {
                "ok":False,
                "error":"Storage temporaneo Instagram non disponibile sul server"
            }

        digest=hashlib.sha256(bytes(video_bytes)).hexdigest()[:20]
        key=f"social-stage/{GSF_SESSION_ID}/instagram-{digest}.mp4"

        try:
            client.put_object(
                Bucket=bucket,
                Key=key,
                Body=bytes(video_bytes),
                ContentType="video/mp4",
                CacheControl="no-store",
            )
            media_url=client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket":bucket,
                    "Key":key,
                    "ResponseContentType":"video/mp4",
                },
                ExpiresIn=900,
            )
            return _gsf_instagram_publish_reel(
                media_url,
                pack,
                share_to_feed=share_to_feed,
                progress_callback=progress_callback
            )
        except Exception as e:
            return {"ok":False,"error":"Staging Instagram: "+str(e)}
        finally:
            try:
                client.delete_object(Bucket=bucket,Key=key)
            except Exception:
                pass

    stage,error=_gsf_start_instagram_staging(video_bytes)
    if stage is None:
        return {"ok":False,"error":error}

    try:
        return _gsf_instagram_publish_reel(
            stage["url"],
            pack,
            share_to_feed=share_to_feed,
            progress_callback=progress_callback
        )
    finally:
        _gsf_stop_instagram_staging(stage)
''')

s=replace_function(s,'_gsf_instagram_publish_reel',r'''
def _gsf_instagram_publish_reel(
    video_url,
    pack,
    share_to_feed=True,
    timeout_seconds=240,
    progress_callback=None
):
    cfg=_gsf_instagram_config()
    ig_user_id=str(cfg.get("ig_user_id","") or "")
    access_token=str(cfg.get("access_token","") or "")
    graph_base=str(cfg.get("api_host","") or "https://graph.facebook.com").rstrip("/")
    if not ig_user_id or not access_token:
        return {"ok":False,"error":"Instagram non collegato"}

    if not _gsf_instagram_public_video_url_ok(video_url):
        return {
            "ok":False,
            "error":"Instagram richiede un URL HTTPS pubblico del video",
        }

    caption=str(
        pack.get(
            "selected_caption",
            pack.get("caption","")
        ) or ""
    ).strip()

    create_url=graph_base+"/"+quote(ig_user_id,safe="")+"/media"
    create=_gsf_http_json(
        create_url,
        method="POST",
        form_body={
            "media_type":"REELS",
            "video_url":str(video_url).strip(),
            "caption":caption,
            "share_to_feed":"true" if share_to_feed else "false",
            "access_token":access_token,
        },
        timeout=60
    )
    create_data=create.get("data") or {}
    if not create.get("ok") or create_data.get("error"):
        return {
            "ok":False,
            "error":str(create_data or create.get("error")),
        }

    container_id=str(create_data.get("id","") or "")
    if not container_id:
        return {
            "ok":False,
            "error":"Meta non ha restituito il container Reel",
        }

    if progress_callback:
        try:
            progress_callback(20)
        except Exception:
            pass

    deadline=time.time()+max(60,int(timeout_seconds))
    last_status=""
    while time.time()<deadline:
        status_url=(
            graph_base+"/"
            +quote(container_id,safe="")
            +"?"+urlencode({
                "fields":"status_code,status",
                "access_token":access_token,
            })
        )
        status_res=_gsf_http_json(
            status_url,
            method="GET",
            timeout=45
        )
        status_data=status_res.get("data") or {}
        if not status_res.get("ok") or status_data.get("error"):
            return {
                "ok":False,
                "container_id":container_id,
                "error":str(status_data or status_res.get("error")),
            }

        last_status=str(
            status_data.get("status_code","") or ""
        ).upper()

        if last_status=="FINISHED":
            break
        if last_status in ("ERROR","EXPIRED"):
            return {
                "ok":False,
                "container_id":container_id,
                "error":str(status_data.get("status") or last_status),
            }

        if progress_callback:
            try:
                progress_callback(55)
            except Exception:
                pass
        time.sleep(3)

    if last_status!="FINISHED":
        return {
            "ok":False,
            "container_id":container_id,
            "error":"Timeout mentre Meta elaborava il Reel",
        }

    if progress_callback:
        try:
            progress_callback(80)
        except Exception:
            pass

    publish_url=graph_base+"/"+quote(ig_user_id,safe="")+"/media_publish"
    publish=_gsf_http_json(
        publish_url,
        method="POST",
        form_body={
            "creation_id":container_id,
            "access_token":access_token,
        },
        timeout=60
    )
    pub_data=publish.get("data") or {}
    if not publish.get("ok") or pub_data.get("error"):
        return {
            "ok":False,
            "container_id":container_id,
            "error":str(pub_data or publish.get("error")),
        }

    media_id=str(pub_data.get("id","") or "")
    if not media_id:
        return {
            "ok":False,
            "container_id":container_id,
            "error":"Meta non ha restituito l'ID del Reel pubblicato",
        }

    permalink=""
    info_url=(
        graph_base+"/"
        +quote(media_id,safe="")
        +"?"+urlencode({
            "fields":"permalink",
            "access_token":access_token,
        })
    )
    info=_gsf_http_json(info_url,method="GET",timeout=30)
    if info.get("ok"):
        permalink=str(
            (info.get("data") or {}).get("permalink","") or ""
        )

    if progress_callback:
        try:
            progress_callback(100)
        except Exception:
            pass

    return {
        "ok":True,
        "container_id":container_id,
        "media_id":media_id,
        "permalink":permalink,
        "error":"",
    }
''')

marker='Gaming Shorts Factory · V104.6 Stable Social Flow'
if marker in s:
    s=s.replace(marker,'Gaming Shorts Factory · V104.7 Instagram Login',1)

compile(s,str(out),'exec')
out.write_text(s,encoding='utf-8')
print(f'V104.7 Instagram Login applied: {out}')
