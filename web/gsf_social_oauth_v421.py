"""Small validation helpers for the existing companion OAuth routes. No storage or sessions."""
import base64
import hashlib
import hmac
import json
import re


def verify_meta_signed_request(value, secret):
    """Verify Meta's exact encoded payload before reading identity. Never echo input."""
    if not secret:
        raise RuntimeError('Meta application secret is not configured')
    try:
        if not isinstance(value,str) or len(value)>16384:
            raise ValueError()
        signature,payload=value.split('.')
        def decode(part):
            if not re.fullmatch(r'[A-Za-z0-9_-]+={0,2}',part):raise ValueError()
            return base64.b64decode(part+'='*((-len(part))%4),altchars=b'-_',validate=True)
        expected=hmac.new(secret.encode(),payload.encode('ascii'),hashlib.sha256).digest()
        if not hmac.compare_digest(decode(signature),expected):raise ValueError()
        data=json.loads(decode(payload).decode('utf-8'))
        if not isinstance(data,dict) or data.get('algorithm')!='HMAC-SHA256':raise ValueError()
        uid=data.get('user_id')
        if not isinstance(uid,str) or not re.fullmatch(r'[0-9]{1,128}',uid):raise ValueError()
        return uid
    except (ValueError,TypeError,UnicodeError,KeyError):
        raise ValueError('Invalid Meta signed request') from None


class TwitchError(RuntimeError):
    def __init__(self,message,status=503):
        self.status=status
        super().__init__(message)


def validate_twitch_media_url(url):
    from urllib.parse import urlsplit
    try:
        parsed=urlsplit(url)
        host=(parsed.hostname or '').lower()
        if parsed.scheme!='https' or parsed.username is not None or parsed.password is not None or parsed.port not in (None,443):raise ValueError()
        if not (host.endswith('.twitchcdn.net') or host.endswith('.ttvnw.net')):raise ValueError()
        return url
    except ValueError:raise TwitchError('URL media Twitch non consentito.',400) from None


def download_twitch_clip(url,destination,max_bytes,opener=None):
    """Download only the official API's CDN URL, with redirect, size and time bounds."""
    import time
    import urllib.request
    from pathlib import Path
    class Redirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self,req,fp,code,msg,headers,newurl):
            validate_twitch_media_url(newurl)
            return super().redirect_request(req,fp,code,msg,headers,newurl)
    path=Path(destination);created=False
    try:
        validate_twitch_media_url(url)
        open_url=opener or urllib.request.build_opener(Redirect()).open
        started=time.monotonic();size=0
        with open_url(urllib.request.Request(url),timeout=15) as response:
            length=int(response.headers.get('Content-Length') or 0)
            if length>max_bytes:raise ValueError()
            with path.open('xb') as output:
                created=True
                while True:
                    if time.monotonic()-started>120:raise TimeoutError()
                    chunk=response.read(1024*1024)
                    if not chunk:break
                    size+=len(chunk)
                    if size>max_bytes:raise ValueError()
                    output.write(chunk)
            if not size or (length and size!=length):raise ValueError()
        return size
    except Exception:
        if created:path.unlink(missing_ok=True)
        raise TwitchError('Download clip non riuscito o file non importabile. Il progetto precedente è conservato.') from None
