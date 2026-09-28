from pathlib import Path
import ast

src=Path('/app/GamingShortsFactory_V105_HARDENED.py')
out=Path('/app/GamingShortsFactory_V105_SOCIAL_STREAM.py')
s=src.read_text(encoding='utf-8')
tree=ast.parse(s)

publish=next(
    n for n in tree.body
    if isinstance(n,ast.FunctionDef) and n.name=='_gsf_publish_social_upload'
)

helpers=r'''
def _gsf_tiktok_direct_post_file(video_path,pack,progress_callback=None):
    """V105 TikTok Direct Post streamed from an existing MP4 path."""
    video_path=str(video_path or "")
    if not video_path or not os.path.isfile(video_path):
        return {"ok":False,"error":"Master video non disponibile"}
    size=int(os.path.getsize(video_path))
    if size<1024:
        return {"ok":False,"error":"Master video non disponibile"}

    token,config,error=_gsf_tiktok_credentials()
    if token is None:
        return {"ok":False,"error":error or "TikTok non collegato"}

    creator=_gsf_tiktok_creator_info()
    if not creator.get("ok"):
        return creator

    options=[
        str(x) for x in creator.get("privacy_level_options",[]) or []
        if str(x)
    ]
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
    chunk_size,total_count=_gsf_tiktok_chunk_plan(size)

    def _init(_privacy):
        return _gsf_http_json(
            GSF_TIKTOK_DIRECT_INIT,
            method="POST",
            headers={
                "Authorization":f"Bearer {access_token}",
                "Content-Type":"application/json; charset=UTF-8",
            },
            json_body={
                "post_info":{
                    "title":caption,
                    "privacy_level":_privacy,
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

    init=_init(privacy)
    payload=init.get("data") or {}
    api_error=payload.get("error") or {}
    _api_code=str(api_error.get("code","") or "") if isinstance(api_error,dict) else ""
    if (
        _api_code=="unaudited_client_can_only_post_to_private_accounts"
        and privacy!="SELF_ONLY"
        and "SELF_ONLY" in options
    ):
        privacy="SELF_ONLY"
        init=_init(privacy)
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
    with open(video_path,"rb") as source:
        while sent<size:
            remaining=size-sent
            if total_count<=1:
                this_size=remaining
            else:
                part_index=sent//chunk_size
                this_size=remaining if part_index>=total_count-1 else min(chunk_size,remaining)

            chunk=source.read(this_size)
            if len(chunk)!=this_size:
                return {
                    "ok":False,
                    "error":"Lettura master TikTok incompleta",
                    "publish_id":publish_id,
                }
            end=sent+this_size-1
            req=Request(
                upload_url,
                data=chunk,
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


def _gsf_youtube_upload_file(
    video_path,
    pack,
    privacy_status="private",
    made_for_kids=False,
    progress_callback=None
):
    """V105 resumable YouTube upload using the existing master path directly."""
    video_path=str(video_path or "")
    if not video_path or not os.path.isfile(video_path) or os.path.getsize(video_path)<1024:
        return {"ok":False,"error":"Master video finale non disponibile"}

    deps=_gsf_youtube_dependencies()
    if not deps.get("ok"):
        return {"ok":False,"error":deps.get("error","Dipendenze Google mancanti")}

    creds,error=_gsf_youtube_credentials()
    if creds is None:
        return {"ok":False,"error":error or "YouTube non collegato"}

    privacy_status=str(privacy_status or "private")
    if privacy_status not in ("private","unlisted","public"):
        privacy_status="private"

    try:
        youtube=deps["build"](
            "youtube","v3",
            credentials=creds,
            cache_discovery=False
        )
        title=str(
            pack.get("selected_title",pack.get("title","Gaming Short"))
            or "Gaming Short"
        ).strip()[:100]
        description=str(
            pack.get("selected_caption",pack.get("caption",""))
            or ""
        ).strip()[:5000]
        tags=[]
        for tag in pack.get("hashtags",[]) or []:
            clean=str(tag).strip().lstrip("#").strip()
            if clean and clean not in tags:
                tags.append(clean)

        body={
            "snippet":{
                "title":title,
                "description":description,
                "categoryId":"20",
                "tags":tags[:30],
            },
            "status":{
                "privacyStatus":privacy_status,
                "selfDeclaredMadeForKids":bool(made_for_kids),
            },
        }
        media=deps["MediaFileUpload"](
            video_path,
            chunksize=8*1024*1024,
            resumable=True,
            mimetype="video/mp4"
        )
        request=youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )

        response=None
        retries=0
        while response is None:
            try:
                status,response=request.next_chunk()
                if status is not None and progress_callback:
                    try:
                        progress_callback(max(0,min(100,int(status.progress()*100))))
                    except Exception:
                        pass
            except deps["HttpError"] as e:
                status_code=int(getattr(getattr(e,"resp",None),"status",0) or 0)
                if status_code in (500,502,503,504) and retries<4:
                    retries+=1
                    time.sleep(min(8,2**retries))
                    continue
                raise

        if progress_callback:
            try:
                progress_callback(100)
            except Exception:
                pass
        video_id=str((response or {}).get("id","") or "")
        if not video_id:
            return {
                "ok":False,
                "error":"YouTube non ha restituito l'ID del video",
                "response":response,
            }
        return {
            "ok":True,
            "video_id":video_id,
            "url":f"https://www.youtube.com/watch?v={video_id}",
            "privacy":privacy_status,
            "title":title,
            "response":response,
        }
    except Exception as e:
        return {"ok":False,"error":str(e)}


def _gsf_instagram_publish_reel_file(
    video_path,
    pack,
    share_to_feed=True,
    progress_callback=None
):
    """V105 Instagram Reel staging from file without a whole-master bytes copy."""
    video_path=str(video_path or "")
    if not video_path or not os.path.isfile(video_path) or os.path.getsize(video_path)<1024:
        return {"ok":False,"error":"Master video non disponibile"}

    if not GSF_WEB_MODE:
        with open(video_path,"rb") as source:
            return _gsf_instagram_publish_reel_auto(
                source.read(),
                pack,
                share_to_feed=share_to_feed,
                progress_callback=progress_callback,
            )

    client,bucket=_gsf_shared_tiktok_s3()
    if client is None or not bucket:
        return {
            "ok":False,
            "error":"Storage temporaneo Instagram non disponibile sul server"
        }

    try:
        stat=os.stat(video_path)
        fingerprint=hashlib.sha256(
            f"{video_path}|{stat.st_size}|{stat.st_mtime_ns}".encode("utf-8")
        ).hexdigest()[:20]
        key=f"social-stage/{GSF_SESSION_ID}/instagram-{fingerprint}.mp4"
        client.upload_file(
            video_path,
            bucket,
            key,
            ExtraArgs={"ContentType":"video/mp4","CacheControl":"no-store"},
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
            progress_callback=progress_callback,
        )
    except Exception as e:
        return {"ok":False,"error":"Staging Instagram: "+str(e)}
    finally:
        try:
            client.delete_object(Bucket=bucket,Key=key)
        except Exception:
            pass


'''

# Insert helpers immediately before the publish orchestrator.
lines=s.splitlines(keepends=True)
s=''.join(lines[:publish.lineno-1])+helpers+''.join(lines[publish.lineno-1:])

# Reparse after insertion and surgically rewrite only the three normal web
# publication calls. Legacy byte functions remain untouched as compatibility.
tree=ast.parse(s)
publish=next(
    n for n in tree.body
    if isinstance(n,ast.FunctionDef) and n.name=='_gsf_publish_social_upload'
)
changed={"youtube":0,"tiktok":0,"instagram":0}
for node in ast.walk(publish):
    if not isinstance(node,ast.Call) or not isinstance(node.func,ast.Name):
        continue
    target=None
    replacement=None
    if node.func.id=="_gsf_youtube_upload":
        target="youtube"; replacement="_gsf_youtube_upload_file"
    elif node.func.id=="_gsf_tiktok_direct_post":
        target="tiktok"; replacement="_gsf_tiktok_direct_post_file"
    elif node.func.id=="_gsf_instagram_publish_reel_auto":
        target="instagram"; replacement="_gsf_instagram_publish_reel_file"
    if not target:
        continue
    if not node.args:
        raise RuntimeError(f"V105 {target} publish call has no first argument")
    first=node.args[0]
    if not (
        isinstance(first,ast.Call)
        and isinstance(first.func,ast.Name)
        and first.func.id=="bytes"
        and first.args
        and isinstance(first.args[0],ast.Name)
        and first.args[0].id=="video"
    ):
        raise RuntimeError(f"V105 unexpected {target} publish first argument")
    node.func.id=replacement
    node.args[0]=ast.Name(id="exported",ctx=ast.Load())
    changed[target]+=1

if changed!={"youtube":1,"tiktok":1,"instagram":1}:
    raise RuntimeError(f"V105 expected one social call each, found {changed}")

ast.fix_missing_locations(publish)
new_publish=ast.unparse(publish)
lines=s.splitlines(keepends=True)
s=''.join(lines[:publish.lineno-1])+new_publish.rstrip()+"\n\n"+''.join(lines[publish.end_lineno:])

compile(s,str(out),"exec")
out.write_text(s,encoding="utf-8")
print(f"V105 social streaming applied: {out} | {changed}")
