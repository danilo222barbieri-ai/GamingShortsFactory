from pathlib import Path
import ast

src=Path('/app/GamingShortsFactory_V104_3_MEMORY_SAFE_RENDER.py')
out=Path('/app/GamingShortsFactory_V104_4_SHARED_SOCIAL.py')
s=src.read_text(encoding='utf-8')

tree=ast.parse(s)
node=next((n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_gsf_tiktok_credentials'),None)
if node is None:
    raise RuntimeError('V104.4 _gsf_tiktok_credentials not found')

original=ast.get_source_segment(s,node) or ''
if not original.startswith('def _gsf_tiktok_credentials'):
    raise RuntimeError('V104.4 TikTok credential function source invalid')
legacy=original.replace(
    'def _gsf_tiktok_credentials',
    'def _gsf_tiktok_credentials_legacy',
    1
)

bridge=r'''
def _gsf_shared_tiktok_s3():
    import boto3
    from botocore.config import Config
    bucket=os.environ.get("GSF_S3_BUCKET","")
    access=os.environ.get("GSF_S3_ACCESS_KEY_ID","")
    secret=os.environ.get("GSF_S3_SECRET_ACCESS_KEY","")
    endpoint=os.environ.get("GSF_S3_ENDPOINT","")
    region=os.environ.get("GSF_S3_REGION","auto") or "auto"
    if not (bucket and access and secret and endpoint):
        return None,bucket
    client=boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access,
        aws_secret_access_key=secret,
        region_name=region,
        config=Config(signature_version="s3v4",s3={"addressing_style":"virtual"}),
    )
    return client,bucket


def _gsf_shared_tiktok_load():
    try:
        client,bucket=_gsf_shared_tiktok_s3()
        if client is None:
            return {}
        obj=client.get_object(Bucket=bucket,Key=f"social-connections/{GSF_SESSION_ID}/tiktok.json")
        payload=json.loads(obj["Body"].read().decode("utf-8"))
        return payload if isinstance(payload,dict) else {}
    except Exception:
        return {}


def _gsf_shared_tiktok_save(payload):
    try:
        client,bucket=_gsf_shared_tiktok_s3()
        if client is None:
            return False
        client.put_object(
            Bucket=bucket,
            Key=f"social-connections/{GSF_SESSION_ID}/tiktok.json",
            Body=json.dumps(payload,ensure_ascii=False).encode("utf-8"),
            ContentType="application/json",
            CacheControl="no-store",
        )
        return True
    except Exception:
        return False


def _gsf_shared_tiktok_refresh(token):
    import urllib.parse as _up
    import urllib.request as _ur
    refresh=str((token or {}).get("refresh_token","") or "")
    cfg=_gsf_app_credentials()
    client_key=str(cfg.get("tiktok_client_key","") or "")
    client_secret=str(cfg.get("tiktok_client_secret","") or "")
    if not (refresh and client_key and client_secret):
        return token
    form=_up.urlencode({
        "client_key":client_key,
        "client_secret":client_secret,
        "grant_type":"refresh_token",
        "refresh_token":refresh,
    }).encode("utf-8")
    req=_ur.Request(
        "https://open.tiktokapis.com/v2/oauth/token/",
        data=form,
        headers={"Content-Type":"application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with _ur.urlopen(req,timeout=45) as resp:
            payload=json.loads(resp.read().decode("utf-8"))
        if not payload.get("access_token"):
            return token
        now=time.time()
        payload["saved_at"]=now
        payload["expires_at"]=now+int(payload.get("expires_in",0) or 0)
        payload["refresh_expires_at"]=now+int(payload.get("refresh_expires_in",0) or 0)
        _gsf_shared_tiktok_save(payload)
        return payload
    except Exception:
        return token


def _gsf_tiktok_credentials():
    token=_gsf_shared_tiktok_load()
    if token.get("access_token"):
        now=time.time()
        expires_at=float(token.get("expires_at",0) or 0)
        if expires_at and expires_at<=now+300 and token.get("refresh_token"):
            token=_gsf_shared_tiktok_refresh(token)
            expires_at=float(token.get("expires_at",0) or 0)
        if token.get("access_token") and (not expires_at or expires_at>now):
            return token,_gsf_app_credentials(),""
    return _gsf_tiktok_credentials_legacy()
'''

lines=s.splitlines(keepends=True)
replacement=legacy.rstrip()+"\n\n"+bridge.strip()+"\n\n"
s=''.join(lines[:node.lineno-1])+replacement+''.join(lines[node.end_lineno:])

marker='Gaming Shorts Factory · V104.3 Memory Safe Render'
if marker in s:
    s=s.replace(marker,'Gaming Shorts Factory · V104.4 Social Connect',1)

compile(s,str(out),'exec')
out.write_text(s,encoding='utf-8')
print(f'V104.4 shared TikTok token bridge applied: {out}')
