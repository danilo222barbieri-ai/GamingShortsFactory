#!/usr/bin/env python3
from pathlib import Path
import sys

MARKER = "GSF_SECURITY_V410"


def _replace_once(text, old, new, label):
    if new in text:
        return text
    if old not in text:
        raise RuntimeError(f"V410 anchor missing: {label}")
    return text.replace(old, new, 1)


def _function_block(text, name, next_name):
    start = text.index(f"def {name}(")
    end = text.index(f"def {next_name}(", start)
    return start, end, text[start:end]


def _replace_in_function(text, name, next_name, old, new, label):
    start, end, block = _function_block(text, name, next_name)
    patched = _replace_once(block, old, new, label)
    return text[:start] + patched + text[end:]


def patch_nginx(path):
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        return False

    edge = '''# GSF_SECURITY_V410 — edge hardening, abuse control and browser policy
limit_req_zone $binary_remote_addr zone=gsf_api_v410:10m rate=20r/s;
limit_req_zone $binary_remote_addr zone=gsf_upload_v410:10m rate=5r/s;
limit_conn_zone $binary_remote_addr zone=gsf_conn_v410:10m;

'''
    text = edge + text

    server_anchor = "    server_name _;\n"
    server_hardening = '''    server_name _;

    # V410 browser hardening. CSP remains compatible with Streamlit/components and social embeds.
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Permissions-Policy "camera=(), microphone=(), geolocation=(), payment=()" always;
    add_header Strict-Transport-Security "max-age=15552000" always;
    add_header Content-Security-Policy "default-src 'self' data: blob: https:; script-src 'self' 'unsafe-inline' 'unsafe-eval' https:; style-src 'self' 'unsafe-inline' https:; img-src 'self' data: blob: https:; media-src 'self' blob: https:; connect-src 'self' https: wss:; frame-src 'self' https:; object-src 'none'; base-uri 'self'; form-action 'self' https:; frame-ancestors 'self';" always;
    limit_conn gsf_conn_v410 40;
'''
    text = _replace_once(text, server_anchor, server_hardening, "nginx server hardening")

    text = _replace_once(
        text,
        "    location /direct-upload/ {\n",
        "    location /direct-upload/ {\n        limit_req zone=gsf_upload_v410 burst=24 nodelay;\n        limit_conn gsf_conn_v410 16;\n",
        "direct upload rate limit",
    )
    text = _replace_once(
        text,
        "    location = /drafts/delete {\n",
        "    location = /drafts/delete {\n        limit_req zone=gsf_api_v410 burst=10 nodelay;\n        limit_except POST { deny all; }\n",
        "draft delete method guard",
    )
    text = _replace_once(
        text,
        "    location = /contact {\n",
        "    location = /contact {\n        limit_req zone=gsf_api_v410 burst=8 nodelay;\n",
        "contact rate limit",
    )

    path.write_text(text, encoding="utf-8")
    return True


def patch_server(path):
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        return False

    text = _replace_once(
        text,
        "import html\n",
        "import html\nimport hashlib\nimport hmac\nimport subprocess\n",
        "security imports",
    )
    text = _replace_once(
        text,
        "from pathlib import Path\n",
        "from pathlib import Path\nfrom cryptography.fernet import Fernet, InvalidToken\n",
        "Fernet import",
    )

    social_anchor = '''def _social_sid(handler):
    return _safe_id(handler.headers.get("X-GSF-Session-ID"))

'''
    helpers = r'''def _social_sid(handler):
    return _safe_id(handler.headers.get("X-GSF-Session-ID"))


# GSF_SECURITY_V410 — application-layer hardening.
def _security_fernet():
    raw=str(os.environ.get("GSF_DATA_ENCRYPTION_KEY","") or "").strip()
    if not raw:
        raise RuntimeError("GSF_DATA_ENCRYPTION_KEY is required")
    try:
        return Fernet(raw.encode("ascii"))
    except Exception:
        derived=base64.urlsafe_b64encode(hashlib.sha256(raw.encode("utf-8")).digest())
        return Fernet(derived)


def _security_encrypt_json(payload):
    raw=json.dumps(dict(payload or {}),ensure_ascii=False,separators=(",",":")).encode("utf-8")
    return _security_fernet().encrypt(raw)


def _security_decrypt_json(raw):
    data=raw.encode("utf-8") if isinstance(raw,str) else bytes(raw or b"")
    if not data:
        return {}
    # Backward-compatible migration: legacy objects were plaintext JSON.
    if data.lstrip().startswith((b"{",b"[")):
        payload=json.loads(data.decode("utf-8"))
    else:
        try:
            payload=json.loads(_security_fernet().decrypt(data).decode("utf-8"))
        except InvalidToken as exc:
            raise RuntimeError("encrypted social token cannot be decrypted") from exc
    return payload if isinstance(payload,dict) else {}


def _security_write_json(path,payload):
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=Path(str(path)+".tmp")
    tmp.write_bytes(_security_encrypt_json(payload))
    try:
        os.chmod(tmp,0o600)
    except Exception:
        pass
    os.replace(tmp,path)


def _security_read_json(path):
    path=Path(path)
    return _security_decrypt_json(path.read_bytes())


def _security_csrf_token(sid):
    sid=_safe_id(sid)
    secret=str(
        os.environ.get("GSF_CSRF_SECRET","")
        or os.environ.get("GSF_DATA_ENCRYPTION_KEY","")
        or os.environ.get("GSF_SOCIAL_CONNECT_KEY","")
        or ""
    ).encode("utf-8")
    if not sid or not secret:
        return ""
    return hmac.new(secret,sid.encode("utf-8"),hashlib.sha256).hexdigest()


def _security_csrf_valid(handler,sid):
    expected=_security_csrf_token(sid)
    provided=str(handler.headers.get("X-GSF-CSRF","") or "")
    fetch_site=str(handler.headers.get("Sec-Fetch-Site","") or "").strip().lower()
    if fetch_site and fetch_site not in ("same-origin","same-site","none"):
        return False
    return bool(expected and provided and hmac.compare_digest(expected,provided))


def _security_validate_media(path,expected_ext=""):
    path=Path(path)
    if not path.is_file() or path.stat().st_size<=1024:
        raise ValueError("media validation failed: empty or missing file")
    ext=str(expected_ext or path.suffix or "").lower()
    if ext not in ALLOWED_EXT:
        raise ValueError("media validation failed: unsupported container")
    probe=subprocess.run(
        [
            "ffprobe","-v","error","-show_entries",
            "format=format_name,duration:stream=codec_type,width,height",
            "-of","json",str(path),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=30,
    )
    if probe.returncode!=0:
        raise ValueError("media validation failed: decoder rejected file")
    try:
        payload=json.loads(probe.stdout or "{}")
    except Exception as exc:
        raise ValueError("media validation failed: invalid probe output") from exc
    fmt=str((payload.get("format") or {}).get("format_name") or "").lower()
    if not any(name in fmt for name in ("mov","mp4","matroska","webm")):
        raise ValueError("media validation failed: unexpected format")
    try:
        duration=float((payload.get("format") or {}).get("duration") or 0.0)
    except Exception:
        duration=0.0
    if duration<=0.0 or duration>43200.0:
        raise ValueError("media validation failed: invalid duration")
    streams=list(payload.get("streams") or [])
    if not streams or len(streams)>32:
        raise ValueError("media validation failed: invalid stream count")
    videos=[s for s in streams if str((s or {}).get("codec_type") or "")=="video"]
    if not videos:
        raise ValueError("media validation failed: no video stream")
    for stream in videos:
        width=int((stream or {}).get("width") or 0)
        height=int((stream or {}).get("height") or 0)
        if width<=0 or height<=0 or width>8192 or height>8192 or width*height>40000000:
            raise ValueError("media validation failed: unsafe dimensions")
    return {"format":fmt,"duration":duration,"streams":len(streams)}

'''
    text = _replace_once(text, social_anchor, helpers, "security helper insertion")

    # Seal social tokens both on the ephemeral filesystem and in the private bucket.
    for name, next_name, local_check in (
        ("_tiktok_user_load","_tiktok_user_write_local","payload.get(\"access_token\")"),
        ("_youtube_user_load","_youtube_user_write_local","payload.get(\"token\")"),
        ("_instagram_user_load","_instagram_user_write_local","payload.get(\"ig_user_id\")"),
    ):
        text = _replace_in_function(
            text,name,next_name,
            'payload=json.loads(local.read_text(encoding="utf-8"))',
            'payload=_security_read_json(local)',
            name+" local decrypt",
        )
        text = _replace_in_function(
            text,name,next_name,
            'payload=json.loads(obj["Body"].read().decode("utf-8"))',
            'payload=_security_decrypt_json(obj["Body"].read())',
            name+" bucket decrypt",
        )

    text = _replace_in_function(
        text,"_tiktok_user_write_local","_tiktok_user_save",
        '_write_json_atomic(social/"tiktok_token.json",token)',
        '_security_write_json(social/"tiktok_token.json",token)',
        "TikTok token local seal",
    )
    text = _replace_in_function(
        text,"_tiktok_user_write_local","_tiktok_user_save",
        '_write_json_atomic(social/"tiktok_config.json",{\n        "client_key":TIKTOK_CLIENT_KEY,\n        "client_secret":TIKTOK_CLIENT_SECRET,\n    })',
        '_security_write_json(social/"tiktok_config.json",{\n        "client_key":TIKTOK_CLIENT_KEY,\n        "client_secret":TIKTOK_CLIENT_SECRET,\n    })',
        "TikTok config local seal",
    )
    text = _replace_in_function(
        text,"_youtube_user_write_local","_youtube_user_save",
        '_write_json_atomic(social/"youtube_token.json",token)',
        '_security_write_json(social/"youtube_token.json",token)',
        "YouTube token local seal",
    )
    text = _replace_in_function(
        text,"_instagram_user_write_local","_instagram_user_save",
        '_write_json_atomic(social/"instagram_config.json",dict(payload or {}))',
        '_security_write_json(social/"instagram_config.json",dict(payload or {}))',
        "Instagram token local seal",
    )

    for name, next_name in (
        ("_tiktok_user_save","_youtube_user_key"),
        ("_youtube_user_save","_instagram_user_key"),
        ("_instagram_user_save","_creator_session_key"),
    ):
        text = _replace_in_function(
            text,name,next_name,
            'Body=json.dumps(payload,ensure_ascii=False).encode("utf-8"),',
            'Body=_security_encrypt_json(payload),',
            name+" bucket seal",
        )
        text = _replace_in_function(
            text,name,next_name,
            'ContentType="application/json",',
            'ContentType="application/octet-stream",',
            name+" encrypted content type",
        )

    # Validate the real media container/streams before a source becomes browser-visible or reaches FFmpeg analysis.
    text = _replace_once(
        text,
        '        if tmp.stat().st_size!=total:\n            raise IOError(f"bucket materialization size mismatch {tmp.stat().st_size} != {total}")\n        os.replace(tmp,final)',
        '        if tmp.stat().st_size!=total:\n            raise IOError(f"bucket materialization size mismatch {tmp.stat().st_size} != {total}")\n        _security_validate_media(tmp,ext)\n        os.replace(tmp,final)',
        "bucket media validation",
    )
    text = _replace_once(
        text,
        '                    final=media/f"source_direct_{safe_stem}_{upload_id}{ext}"\n                    os.replace(data_path,final)',
        '                    final=media/f"source_direct_{safe_stem}_{upload_id}{ext}"\n                    _security_validate_media(data_path,ext)\n                    os.replace(data_path,final)',
        "direct media validation",
    )

    # GET is now read-only; draft deletion is POST + same-session CSRF.
    old_get_delete = '''        if clean=="/drafts/delete":
            sid=_social_sid(self)
            draft_id=_safe_id((parse_qs(path.query).get("id") or [""])[0])
            if sid and draft_id:
                _draft_delete(sid,draft_id)
            _redirect(self,"/account")
            return
'''
    new_get_delete = '''        if clean=="/drafts/delete":
            _json(self,405,{"ok":False,"error":"method not allowed"})
            return
'''
    text = _replace_once(text, old_get_delete, new_get_delete, "GET draft delete removal")

    post_anchor = '''        if not sid:
            _json(self,400,{"ok":False,"error":"invalid session"})
            return

        if path=="/editor/state/save":
'''
    post_delete = '''        if not sid:
            _json(self,400,{"ok":False,"error":"invalid session"})
            return

        if path=="/drafts/delete":
            if not _security_csrf_valid(self,sid):
                _json(self,403,{"ok":False,"error":"csrf validation failed"})
                return
            draft_id=_safe_id((parse_qs(urlparse(self.path).query).get("id") or [""])[0])
            if not draft_id:
                _json(self,400,{"ok":False,"error":"invalid draft id"})
                return
            ok=bool(_draft_delete(sid,draft_id))
            _json(self,200 if ok else 404,{"ok":ok,"id":draft_id})
            return

        if path=="/editor/state/save":
'''
    text = _replace_once(text, post_anchor, post_delete, "POST draft delete CSRF handler")

    # Rewrite only the small server-rendered draft card fragment to use the protected POST route.
    start, end, _ = _function_block(text,"_draft_cards_html","_creator_login")
    draft_function = r'''def _draft_cards_html(sid):
    sid=_safe_id(sid)
    drafts=_draft_list(sid)
    if not drafts:
        return '<div class="draftEmpty">Nessuna bozza salvata.</div>'
    rows=[]
    csrf=_security_csrf_token(sid)
    for draft in drafts:
        did=_safe_id(draft.get("id",""))
        title=html.escape(str(draft.get("title") or "Bozza"))
        source=html.escape(str(draft.get("source_name") or "Gameplay"))
        persistent=bool(draft.get("source_persistent"))
        try:
            updated=time.strftime("%d/%m · %H:%M",time.localtime(float(draft.get("updated_at") or 0)))
        except Exception:
            updated=""
        href="/drafts/resume?id="+urllib.parse.quote(did,safe="")
        safety='<span class="draftSafe">salvata</span>' if persistent else '<span class="draftSafe draftSafeSync">sincronizzazione</span>'
        rows.append(
            '<div class="draftCard"><div class="draftInfo"><strong>'+title+'</strong><span>'+source+' · '+html.escape(updated)+' · '+safety+
            '</span></div><div class="draftActions"><a class="draftOpen" href="'+href+'" onclick="return gsfResumeDraft(event,this.href)">RIPRENDI</a>'+
            '<a class="draftDelete" href="#" onclick="return gsfDeleteDraft(event,\''+did+'\',\''+csrf+'\')">ELIMINA</a></div></div>'
        )
    return (
        '<div id="draftInlineMessage" class="draftInlineMessage" aria-live="polite"></div>'
        '<div class="draftGrid">'+"".join(rows)+'</div>'
        '<script>'
        'async function gsfResumeDraft(ev,url){ev.preventDefault();'
        'const m=document.getElementById("draftInlineMessage");if(m){m.textContent="Recupero bozza…";m.className="draftInlineMessage show";}'
        'try{const sep=url.includes("?")?"&":"?";const r=await fetch(url+sep+"json=1",{cache:"no-store",credentials:"same-origin"});const j=await r.json();'
        'if(!r.ok||!j.ok)throw new Error(j.error||"Bozza non disponibile");'
        'window.top.location.href=j.url||"/";}'
        'catch(e){if(m){m.textContent=e.message||"Bozza non disponibile. Riprova.";m.className="draftInlineMessage show error";}}'
        'return false;}'
        'async function gsfDeleteDraft(ev,id,csrf){ev.preventDefault();if(!confirm("Eliminare questa bozza?"))return false;'
        'const m=document.getElementById("draftInlineMessage");try{const r=await fetch("/drafts/delete?id="+encodeURIComponent(id),{method:"POST",cache:"no-store",credentials:"same-origin",headers:{"X-GSF-CSRF":csrf,"Accept":"application/json"}});const j=await r.json();'
        'if(!r.ok||!j.ok)throw new Error(j.error||"Eliminazione non riuscita");window.location.reload();}'
        'catch(e){if(m){m.textContent=e.message||"Eliminazione non riuscita.";m.className="draftInlineMessage show error";}}return false;}'
        '</script>'
    )

'''
    text = text[:start] + draft_function + text[end:]

    path.write_text(text, encoding="utf-8")
    return True


def main():
    root=Path(sys.argv[1] if len(sys.argv)>1 else "/app").resolve()
    web=root/"web"
    nginx=web/"nginx.conf.template"
    server=web/"direct_upload_server.py"
    if not nginx.is_file() or not server.is_file():
        raise SystemExit(f"V410 invalid app root: {root}")
    n=patch_nginx(nginx)
    s=patch_server(server)
    print(f"V410 security hardening applied nginx={int(n)} server={int(s)}")


if __name__=="__main__":
    main()
