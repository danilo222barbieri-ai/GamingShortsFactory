#!/usr/bin/env python3
from pathlib import Path
import re
import sys

MARK = 'V366_CREATOR_HUB_STATE_STABILITY'
CACHE_TARGET = '/creator-hub-v156/?v=3662&ui=profile-ref-2'

CLIENT_RUNTIME = r'''
<!-- V366_CREATOR_HUB_STATE_STABILITY -->
<script id="v366CreatorHubDiagnostics">
(()=>{
  if(window.__gsfV366Diagnostics)return;
  window.__gsfV366Diagnostics=1;
  const send=(stage,err)=>{
    try{
      const payload=JSON.stringify({
        stage:String(stage||'unknown').slice(0,80),
        message:String(err&&err.message||err||'unknown').slice(0,300),
        stack:String(err&&err.stack||'').slice(0,1200),
        href:String(location.pathname||'').slice(0,160)
      });
      if(navigator.sendBeacon){
        navigator.sendBeacon('/creator-hub/client-error',new Blob([payload],{type:'application/json'}));
      }else{
        fetch('/creator-hub/client-error',{method:'POST',credentials:'same-origin',keepalive:true,headers:{'Content-Type':'application/json'},body:payload}).catch(()=>{});
      }
    }catch(_e){}
  };
  window.addEventListener('error',(e)=>send('window.error',e.error||e.message));
  window.addEventListener('unhandledrejection',(e)=>send('unhandledrejection',e.reason));
})();
</script>
'''


def _replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise RuntimeError(f'V366 missing client anchor: {label}')
    return text.replace(old, new, 1)


def patch_hub(text: str) -> str:
    # V366.1 restart safety: V359/V362 can delegate this repair more than once
    # during one container boot. Once the complete contract marker exists, do
    # not rewrite loadState again or duplicate the single-flight loader.
    if MARK in text:
        required = (
            'let stateLoadPromise=null;',
            'reportHubError("render",renderError)',
            '.socialCard[data-platform],.profileSocialRefRow[data-platform]',
            'if(!st||!btn)return',
            'id="v366CreatorHubDiagnostics"',
        )
        missing = [token for token in required if token not in text]
        if missing:
            raise RuntimeError('V366 marked Hub is incomplete: ' + ', '.join(missing))
        return text

    if 'V365_CREATOR_HUB_BOOTSTRAP_FIX' not in text:
        raise RuntimeError('V366 requires V365 Creator Hub bootstrap')

    text = _replace_once(
        text,
        '$$("[data-platform]").forEach(card=>{',
        '$$(".socialCard[data-platform],.profileSocialRefRow[data-platform]").forEach(card=>{',
        'social card selector',
    )
    text = _replace_once(
        text,
        'const st=card.querySelector(".socialState"),btn=card.querySelector("[data-connect]");\n     if(key==="twitch"&&!yes)',
        'const st=card.querySelector(".socialState"),btn=card.querySelector("[data-connect]");\n     if(!st||!btn)return;\n     if(key==="twitch"&&!yes)',
        'social child guard',
    )

    replacements = [
        ('$("#profileName").textContent=name;', 'const profileNameEl=$("#profileName");if(profileNameEl)profileNameEl.textContent=name;', 'profileName guard'),
        ('$("#planBadge").textContent=String(a.plan||"FREE").toUpperCase();', 'const planBadge=$("#planBadge");if(planBadge)planBadge.textContent=String(a.plan||"FREE").toUpperCase();', 'plan badge guard'),
        ('$("#profileMeta").textContent="Livello "+String(a.creator_level||1)+" · "+connectedCount+" account collegati";', 'const profileMeta=$("#profileMeta");if(profileMeta)profileMeta.textContent="Livello "+String(a.creator_level||1)+" · "+connectedCount+" account collegati";', 'profile meta guard'),
        ('$("#syncBadge").textContent=a.connected?"✓ Sincronizzato":"Sessione locale";$("#syncBadge").classList.toggle("ok",!!a.connected);', 'const syncBadge=$("#syncBadge");if(syncBadge){syncBadge.textContent=a.connected?"✓ Sincronizzato":"Sessione locale";syncBadge.classList.toggle("ok",!!a.connected)}', 'sync badge guard'),
    ]
    for old, new, label in replacements:
        text = _replace_once(text, old, new, label)

    anchor = 'const ppt=$("#profilePlanText");if(ppt)ppt.textContent=a.connected?"Piano collegato al tuo account":"Collega un account per gestire il piano";'
    render_slice = text[text.find('function render()'):text.find('async function loadState()')]
    if 'profileOverviewPlan' not in render_slice:
        if anchor not in text:
            raise RuntimeError('V366 profile overview anchor missing')
        extra = anchor + '\n   const pop=$("#profileOverviewPlan");if(pop)pop.textContent=String(a.plan||"FREE").toUpperCase();\n   const pos=$("#profileOverviewSocial");if(pos)pos.textContent=String(st.social||0)+"/5";'
        text = text.replace(anchor, extra, 1)

    load_re = re.compile(r' async function loadState\(\)\{.*?\n \}\n async function deleteShort', re.DOTALL)
    match = load_re.search(text)
    if not match:
        raise RuntimeError('V366 loadState block missing')
    new_loader = r''' let stateLoadPromise=null;
 function reportHubError(stage,err){
   try{
     const payload=JSON.stringify({stage:String(stage||"unknown").slice(0,80),message:String(err&&err.message||err||"unknown").slice(0,300),stack:String(err&&err.stack||"").slice(0,1200),view:String(current||"").slice(0,40)});
     if(navigator.sendBeacon)navigator.sendBeacon("/creator-hub/client-error",new Blob([payload],{type:"application/json"}));
     else fetch("/creator-hub/client-error",{method:"POST",cache:"no-store",credentials:"same-origin",keepalive:true,headers:{"Content-Type":"application/json"},body:payload}).catch(()=>{});
   }catch(_e){}
 }
 async function loadState(){
   if(stateLoadPromise)return stateLoadPromise;
   stateLoadPromise=(async()=>{
     try{
       const r=await fetch("/creator-hub/state",{cache:"no-store",credentials:"same-origin"}),j=await r.json();
       if(!r.ok||!j.ok)throw new Error(j.error||"Hub non disponibile");
       state=j;
       try{render()}catch(renderError){reportHubError("render",renderError);throw renderError}
       return state;
     }catch(e){
       reportHubError("loadState",e);
       const meta=$("#profileMeta");if(meta)meta.textContent="Profilo non disponibile · Riprova";
       const sr=$("#shortRows");if(sr)sr.innerHTML='<div class="empty">Creator Hub non disponibile. Riprova tra poco.</div>';
       const dr=$("#draftRows");if(dr)dr.innerHTML='<div class="empty">Creator Hub non disponibile. Riprova tra poco.</div>';
       return null;
     }
   })();
   try{return await stateLoadPromise}finally{stateLoadPromise=null}
 }
 async function deleteShort'''
    text = text[:match.start()] + new_loader + text[match.end():]

    if '</body>' not in text:
        raise RuntimeError('V366 Hub body anchor missing')
    text = text.replace('</body>', CLIENT_RUNTIME + '\n</body>', 1)
    return text


def patch_shell_cache(text: str) -> str:
    if CACHE_TARGET in text:
        return text
    text, count = re.subn(r'/creator-hub-v156/\?v=[^"\'\s]+', CACHE_TARGET, text)
    if count < 1:
        raise RuntimeError('V366 Creator Hub cache-key anchor missing')
    return text


def _find_route_block(text: str, exact: str) -> tuple[int, int, str]:
    lines = text.splitlines(keepends=True)
    start = -1
    indent = None
    for i, line in enumerate(lines):
        if line.strip() == exact:
            start = i
            indent = len(line) - len(line.lstrip(' '))
            break
    if start < 0 or indent is None:
        raise RuntimeError('V366 server route anchor missing: ' + exact)
    end = len(lines)
    for j in range(start + 1, len(lines)):
        stripped = lines[j].strip()
        if not stripped:
            continue
        level = len(lines[j]) - len(lines[j].lstrip(' '))
        if level == indent and (stripped.startswith('if ') or stripped.startswith('def ') or stripped.startswith('class ')):
            end = j
            break
    return start, end, ''.join(lines[start:end])


def patch_server(text: str) -> str:
    old_avatar = '"avatar":str(profile.get("avatar") or "")[:1800000] if isinstance(profile,dict) else "",'
    new_avatar = '"avatar":(("/creator-hub/avatar" if str(profile.get("avatar") or "").startswith("data:image/") else str(profile.get("avatar") or "")[:1800000]) if isinstance(profile,dict) else ""),'
    if new_avatar not in text:
        if old_avatar not in text:
            raise RuntimeError('V366 server avatar state anchor missing')
        text = text.replace(old_avatar, new_avatar, 1)

    start, end, block = _find_route_block(text, 'if clean=="/creator-hub/state":')
    if 'youtube_state=_youtube_user_load(sid)' not in block:
        social_anchor = '            all_shorts=_short_list(sid)\n'
        if social_anchor not in block:
            raise RuntimeError('V366 state social preload anchor missing')
        block = block.replace(
            social_anchor,
            social_anchor + '            youtube_state=_youtube_user_load(sid)\n            tiktok_state=_tiktok_user_load(sid)\n            instagram_state=_instagram_user_load(sid)\n',
            1,
        )
        block = block.replace('bool(_youtube_user_load(sid))', 'bool(youtube_state)')
        block = block.replace('bool(_tiktok_user_load(sid))', 'bool(tiktok_state)')
        block = block.replace('bool(_instagram_user_load(sid))', 'bool(instagram_state)')
        block = block.replace('(_youtube_user_load(sid),_tiktok_user_load(sid),_instagram_user_load(sid),providers.get("facebook"),providers.get("twitch"))', '(youtube_state,tiktok_state,instagram_state,providers.get("facebook"),providers.get("twitch"))')
        lines = text.splitlines(keepends=True)
        text = ''.join(lines[:start]) + block + ''.join(lines[end:])

    if 'if clean=="/creator-hub/avatar":' not in text:
        avatar_route = '''        if clean=="/creator-hub/avatar":\n            sid=_social_sid(self)\n            if not sid:\n                _json(self,400,{"ok":False,"error":"Sessione browser non valida."})\n                return\n            profile=_creator_account_load(sid) or {}\n            avatar=str(profile.get("avatar") or "") if isinstance(profile,dict) else ""\n            if avatar.startswith("data:image/") and ";base64," in avatar:\n                try:\n                    head,data=avatar.split(",",1)\n                    mime=head.split(";",1)[0].split(":",1)[1]\n                    raw=base64.b64decode(data,validate=True)\n                    _send_bytes(self,200,raw,mime,"private, max-age=60")\n                except Exception:\n                    _json(self,404,{"ok":False,"error":"Avatar non disponibile"})\n            else:\n                _json(self,404,{"ok":False,"error":"Avatar non disponibile"})\n            return\n'''
        anchor = '        if clean=="/creator-hub/state":\n'
        if anchor not in text:
            raise RuntimeError('V366 avatar route insertion anchor missing')
        text = text.replace(anchor, avatar_route + anchor, 1)

    if 'if path=="/creator-hub/client-error":' not in text:
        telemetry = '''        if path=="/creator-hub/client-error":\n            try:\n                data=_read_json(self,max_bytes=8*1024)\n                stage=str((data or {}).get("stage") or "unknown")[:80]\n                message=str((data or {}).get("message") or "")[:300]\n                stack=str((data or {}).get("stack") or "")[:1200].replace("\\n"," | ")\n                print("GSF_HUB_CLIENT_ERROR",sid,stage,repr(message),repr(stack),flush=True)\n                _json(self,200,{"ok":True})\n            except Exception as exc:\n                _json(self,400,{"ok":False,"error":str(exc)[:180]})\n            return\n\n'''
        anchor = '        if path=="/creator-hub/profile":\n'
        if anchor not in text:
            raise RuntimeError('V366 telemetry POST insertion anchor missing')
        text = text.replace(anchor, telemetry + anchor, 1)

    if '# V366_CREATOR_HUB_STATE_STABILITY' not in text:
        text = text.replace('FREE_DRAFT_LIMIT=5\n', 'FREE_DRAFT_LIMIT=5\n# V366_CREATOR_HUB_STATE_STABILITY\n', 1)
    return text


def main() -> None:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path('/app')
    if root.is_file():
        hub = root
        root = hub.parents[2]
    else:
        hub = root/'web'/'creator_hub_v156_component'/'index.html'
    server = root/'web'/'direct_upload_server.py'
    if not hub.is_file() or not server.is_file():
        raise SystemExit('V366 targets missing')
    hub_before = hub.read_text(encoding='utf-8')
    server_before = server.read_text(encoding='utf-8')
    hub_after = patch_hub(hub_before)
    server_after = patch_server(server_before)
    hub.write_text(hub_after, encoding='utf-8')
    server.write_text(server_after, encoding='utf-8')

    cache_changed = []
    for shell in (root/'GamingShortsFactory_V154_STRUCTURAL_HOME.py', root/'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py'):
        if not shell.is_file():
            continue
        before = shell.read_text(encoding='utf-8')
        after = patch_shell_cache(before)
        compile(after, str(shell), 'exec')
        shell.write_text(after, encoding='utf-8')
        cache_changed.append((shell.name, before != after))

    print('V366 Creator Hub state stability applied hub_changed=', hub_before != hub_after, 'server_changed=', server_before != server_after, 'cache=', cache_changed, flush=True)


if __name__ == '__main__':
    main()
