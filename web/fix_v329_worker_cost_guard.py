#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
DIRECT=ROOT/'web/direct_upload_server.py'
BRIDGE=ROOT/'web/gsf_bucket_bridge.py'


def _ensure_import(text):
    if 'import urllib.error' in text:
        return text
    if 'import urllib.request\n' in text:
        return text.replace('import urllib.request\n','import urllib.request\nimport urllib.error\n',1)
    raise RuntimeError('V329 urllib.request import anchor missing')


def patch_direct(text):
    before=text
    text=_ensure_import(text)
    if 'def _worker_request_with_retry(' not in text:
        anchor='def _trigger_prescan(payload):\n'
        if anchor not in text:
            raise RuntimeError('V329 direct prescan anchor missing')
        helper='''def _worker_request_with_retry(req,timeout=12,attempts=3):
    last_exc=None
    total=max(1,int(attempts or 1))
    for attempt in range(total):
        try:
            return urllib.request.urlopen(req,timeout=timeout)
        except urllib.error.HTTPError as exc:
            last_exc=exc
            if int(getattr(exc,"code",0) or 0) not in (502,503,504) or attempt>=total-1:
                raise
        except (urllib.error.URLError,TimeoutError,ConnectionError,OSError) as exc:
            last_exc=exc
            if attempt>=total-1:
                raise
        time.sleep(0.45*(attempt+1))
    if last_exc is not None:
        raise last_exc
    raise RuntimeError("worker request retry exhausted")

'''
        text=text.replace(anchor,helper+anchor,1)
    marker='WORKER_URL+"/prescan"'
    pos=text.find(marker)
    if pos<0:
        raise RuntimeError('V329 direct worker URL anchor missing')
    old='with urllib.request.urlopen(req,timeout=12) as resp:'
    idx=text.find(old,pos)
    if idx>=0:
        text=text[:idx]+'with _worker_request_with_retry(req,timeout=12,attempts=3) as resp:'+text[idx+len(old):]
    elif '_worker_request_with_retry(req,timeout=12' not in text[pos:pos+1200]:
        raise RuntimeError('V329 direct urlopen anchor missing')
    compile(text,str(DIRECT),'exec')
    return text,before!=text


def patch_bridge(text):
    before=text
    text=_ensure_import(text)
    if 'def _worker_status_request(' not in text:
        anchor='def _worker_status(analysis_key):\n'
        if anchor not in text:
            raise RuntimeError('V329 bridge worker status anchor missing')
        helper='''def _worker_status_request(req,timeout=3.0):
    last_exc=None
    for attempt in range(3):
        try:
            return urllib.request.urlopen(req,timeout=timeout)
        except urllib.error.HTTPError as exc:
            last_exc=exc
            if int(getattr(exc,"code",0) or 0) not in (502,503,504) or attempt>=2:
                raise
        except (urllib.error.URLError,TimeoutError,ConnectionError,OSError) as exc:
            last_exc=exc
            if attempt>=2:
                raise
        time.sleep(0.45*(attempt+1))
    if last_exc is not None:
        raise last_exc
    raise RuntimeError("worker status retry exhausted")

'''
        text=text.replace(anchor,helper+anchor,1)
    marker='worker_url+"/status?"+query'
    pos=text.find(marker)
    if pos<0:
        raise RuntimeError('V329 bridge status URL anchor missing')
    old='with urllib.request.urlopen(req,timeout=3.0) as resp:'
    idx=text.find(old,pos)
    if idx>=0:
        text=text[:idx]+'with _worker_status_request(req,timeout=3.0) as resp:'+text[idx+len(old):]
    elif '_worker_status_request(req,timeout=3.0)' not in text[pos:pos+1000]:
        raise RuntimeError('V329 bridge urlopen anchor missing')
    compile(text,str(BRIDGE),'exec')
    return text,before!=text


def main():
    direct=DIRECT.read_text(encoding='utf-8')
    bridge=BRIDGE.read_text(encoding='utf-8')
    direct,d_changed=patch_direct(direct)
    bridge,b_changed=patch_bridge(bridge)
    DIRECT.write_text(direct,encoding='utf-8')
    BRIDGE.write_text(bridge,encoding='utf-8')
    print('V329 worker cold-start cost guard applied direct_changed=',d_changed,'bridge_changed=',b_changed,flush=True)


if __name__=='__main__':
    main()
