from pathlib import Path
import ast

src=Path('/app/GamingShortsFactory_V104_4_SHARED_SOCIAL.py')
out=Path('/app/GamingShortsFactory_V104_5_YOUTUBE_SOCIAL.py')
s=src.read_text(encoding='utf-8')

# ---------- shared YouTube token helpers ----------
anchor='def _gsf_youtube_save_credentials(creds):\n'
pos=s.find(anchor)
if pos<0:
    raise RuntimeError('V104.5 YouTube save anchor missing')

helpers=r'''def _gsf_shared_youtube_load():
    try:
        client,bucket=_gsf_shared_tiktok_s3()
        if client is None:
            return {}
        obj=client.get_object(
            Bucket=bucket,
            Key=f"social-connections/{GSF_SESSION_ID}/youtube.json"
        )
        payload=json.loads(obj["Body"].read().decode("utf-8"))
        return payload if isinstance(payload,dict) else {}
    except Exception:
        return {}


def _gsf_shared_youtube_save(payload):
    try:
        client,bucket=_gsf_shared_tiktok_s3()
        if client is None:
            return False
        client.put_object(
            Bucket=bucket,
            Key=f"social-connections/{GSF_SESSION_ID}/youtube.json",
            Body=json.dumps(payload,ensure_ascii=False).encode("utf-8"),
            ContentType="application/json",
            CacheControl="no-store",
        )
        return True
    except Exception:
        return False


'''
s=s[:pos]+helpers+s[pos:]

# ---------- persist every normal Google credential save to the bucket ----------
old='''def _gsf_youtube_save_credentials(creds):
    GSF_YOUTUBE_DIR.mkdir(parents=True,exist_ok=True)
    GSF_YOUTUBE_TOKEN.write_text(
        creds.to_json(),
        encoding="utf-8"
    )
    try:
        os.chmod(GSF_YOUTUBE_TOKEN,0o600)
    except Exception:
        pass
'''
new='''def _gsf_youtube_save_credentials(creds):
    GSF_YOUTUBE_DIR.mkdir(parents=True,exist_ok=True)
    _raw=creds.to_json()
    GSF_YOUTUBE_TOKEN.write_text(
        _raw,
        encoding="utf-8"
    )
    try:
        os.chmod(GSF_YOUTUBE_TOKEN,0o600)
    except Exception:
        pass
    try:
        _payload=json.loads(_raw)
        if isinstance(_payload,dict):
            _gsf_shared_youtube_save(_payload)
    except Exception:
        pass
'''
if old not in s:
    raise RuntimeError('V104.5 exact YouTube save function missing')
s=s.replace(old,new,1)

# ---------- recover the per-browser token before existing credential loader ----------
old='''    if not GSF_YOUTUBE_TOKEN.exists():
        return None,"Account YouTube non collegato"
'''
new='''    if not GSF_YOUTUBE_TOKEN.exists():
        _shared=_gsf_shared_youtube_load()
        if isinstance(_shared,dict) and _shared.get("token"):
            try:
                GSF_YOUTUBE_DIR.mkdir(parents=True,exist_ok=True)
                GSF_YOUTUBE_TOKEN.write_text(
                    json.dumps(_shared,ensure_ascii=False),
                    encoding="utf-8"
                )
                try:
                    os.chmod(GSF_YOUTUBE_TOKEN,0o600)
                except Exception:
                    pass
            except Exception:
                pass

    if not GSF_YOUTUBE_TOKEN.exists():
        return None,"Account YouTube non collegato"
'''
if old not in s:
    raise RuntimeError('V104.5 YouTube credential load anchor missing')
s=s.replace(old,new,1)

# ---------- allow existing Railway Web OAuth client ID/secret ----------
old='''    secret_path = os.path.expanduser(str(cfg.get("youtube_client_secret_file", "") or "").strip())
    if not secret_path or not os.path.exists(secret_path):
        return {}, "YouTube non è configurato sul server."
'''
new='''    secret_path = os.path.expanduser(str(cfg.get("youtube_client_secret_file", "") or "").strip())
    if not secret_path or not os.path.exists(secret_path):
        _client_id=str(os.environ.get("GSF_YOUTUBE_CLIENT_ID","") or "").strip()
        _client_secret=str(os.environ.get("GSF_YOUTUBE_CLIENT_SECRET","") or "").strip()
        _redirect=_gsf_public_app_url()
        if _client_id and _client_secret:
            return {
                "web":{
                    "client_id":_client_id,
                    "client_secret":_client_secret,
                    "auth_uri":"https://accounts.google.com/o/oauth2/auth",
                    "token_uri":"https://oauth2.googleapis.com/token",
                    "redirect_uris":[_redirect] if _redirect else [],
                }
            },""
        return {}, "YouTube non è configurato sul server."
'''
if old not in s:
    raise RuntimeError('V104.5 YouTube client-config anchor missing')
s=s.replace(old,new,1)

marker='Gaming Shorts Factory · V104.4 Social Connect'
if marker in s:
    s=s.replace(marker,'Gaming Shorts Factory · V104.5 YouTube Social Connect',1)

compile(s,str(out),'exec')
out.write_text(s,encoding='utf-8')
print(f'V104.5 YouTube Social Connect applied: {out}')
