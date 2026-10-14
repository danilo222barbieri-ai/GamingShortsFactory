"""Materialize queue additions once during the V404 image build."""
from pathlib import Path
import ast
import re
import sys

MARKER = '# GSF QUEUE RUNTIME V411'


def patch_app_source(source):
    if MARKER in source:
        return source
    anchor = '    _gsf_v154_event=_gsf_render_home_v154('
    if anchor not in source:
        raise RuntimeError('Production Home/session restoration anchor missing')
    result = source.replace(anchor, '    ' + MARKER + '\n    from web.queue_runtime_v411 import render_queue_runtime\n    render_queue_runtime(st)\n\n' + anchor, 1)
    ast.parse(result)
    return result


def patch_csrf_server(source):
    if 'GSF_SECURITY_V410' not in source:
        raise RuntimeError('V410 must be applied before the Hub security bridge')
    start = source.index('if clean=="/creator-hub/state":')
    end = source.index('if clean=="/account":', start)
    block = source[start:end]
    if '"csrf_token":_security_csrf_token(sid)' in block:
        return source
    if '"ok":True,' not in block:
        raise RuntimeError('Creator Hub state response anchor missing')
    block = block.replace('"ok":True,', '"ok":True,\n                "csrf_token":_security_csrf_token(sid),', 1)
    return source[:start] + block + source[end:]


def patch_csrf_hub(source):
    if 'V411_HUB_CSRF_DELETE' in source:
        return source
    old = "await fetch('/drafts/delete?id='+encodeURIComponent(id),{credentials:'same-origin',redirect:'follow',cache:'no-store'});"
    new = """// V411_HUB_CSRF_DELETE
      const stateResponse=await fetch('/creator-hub/state',{credentials:'same-origin',cache:'no-store'});
      const identity=await stateResponse.json();
      if(!stateResponse.ok||!identity.csrf_token)throw new Error('Sessione non disponibile. Riprova.');
      const response=await fetch('/drafts/delete?id='+encodeURIComponent(id),{method:'POST',credentials:'same-origin',cache:'no-store',headers:{'X-GSF-CSRF':identity.csrf_token,'Accept':'application/json'}});
      const result=await response.json();
      if(!response.ok||!result.ok)throw new Error(result.error||'Bozza non eliminata');"""
    if old not in source:
        raise RuntimeError('V403 draft delete integration anchor missing')
    return source.replace(old, new, 1)


def patch_location_headers(source):
    if 'V411_LOCATION_SECURITY_HEADERS' in source:
        return source
    headers = re.findall(r'^    add_header (?:X-Content-Type-Options|X-Frame-Options|Referrer-Policy|Permissions-Policy|Strict-Transport-Security|Content-Security-Policy) .*;$', source, flags=re.M)
    if len(headers) != 6:
        raise RuntimeError('V410 security header definitions missing')
    # Nginx stops inheriting server headers when a location sets its own header.
    # Every real route must therefore carry the same policy explicitly.
    return re.sub(r'(?m)^([ \t]*)location ([^\n]+)\{\n', lambda m: m[0] + m[1] + '    # V411_LOCATION_SECURITY_HEADERS\n' + '\n'.join(m[1] + '    ' + line.strip() for line in headers) + '\n', source)


def patch_desktop_access(source):
    if '# V407_DESKTOP_ACCESS' in source:
        return source
    result, count = re.subn(r'\s*error_page 424 = /__gsf_mobile_gate;\s*if \(\$gsf_mobile_client = 0\) \{\s*return 424;\s*\}', '\n        # V407_DESKTOP_ACCESS\n', source)
    if not count:
        raise RuntimeError('Expected obsolete desktop device guards missing')
    return result


def patch_share_revision(source):
    if '# V411_SHARE_REVISION' in source:
        return source
    start=source.index('if clean=="/share/state":')
    end=source.index('if clean=="/share/final":', start)
    block=source[start:end]
    block=block.replace('final_bytes=int(stable.stat().st_size) if ready else 0', 'final_bytes=int(stable.stat().st_size) if ready else 0\n            # V411_SHARE_REVISION\n            revision=str(stable.stat().st_mtime_ns) if ready else ""',1)
    block=block.replace('final_bytes=int(head.get("ContentLength") or 0)', 'revision=str(head.get("ETag") or head.get("LastModified") or "")\n                        final_bytes=int(head.get("ContentLength") or 0)',1)
    # Both bucket lookup paths carry an immutable object revision.
    second='                        final_bytes=int(head.get("ContentLength") or 0)'
    pos=block.rfind(second)
    block=block[:pos]+block[pos:].replace(second,'                        revision=str(head.get("ETag") or head.get("LastModified") or "")\n'+second,1)
    block=block.replace('"final_bytes":final_bytes,','"final_bytes":final_bytes,\n                "revision":revision,',1)
    return source[:start]+block+source[end:]


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else '/app')
    target = root / 'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py'
    source = patch_app_source(target.read_text(encoding='utf-8'))
    compile(source, str(target), 'exec')
    target.write_text(source, encoding='utf-8')
    server = root / 'web/direct_upload_server.py'
    source = patch_share_revision(patch_csrf_server(server.read_text(encoding='utf-8')))
    compile(source, str(server), 'exec')
    server.write_text(source, encoding='utf-8')
    nginx = root / 'web/nginx.conf.template'
    nginx.write_text(patch_location_headers(patch_desktop_access(nginx.read_text(encoding='utf-8'))), encoding='utf-8')
    hub = root / 'web/creator_hub_v156_component/index.html'
    hub.write_text(patch_csrf_hub(hub.read_text(encoding='utf-8')), encoding='utf-8')
    print('V411 consolidated image integration: PASS', flush=True)


if __name__ == '__main__':
    main()

