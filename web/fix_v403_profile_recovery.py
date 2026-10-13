#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

MARK = "V403_PROFILE_RECOVERY"
TARGET = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path("/app/web/creator_hub_v156_component/index.html")

OLD = r''' async function loadState(){
   try{
     const r=await fetch("/creator-hub/state",{cache:"no-store",credentials:"same-origin"}),j=await r.json();
     if(!r.ok||!j.ok)throw new Error(j.error||"Hub non disponibile");
     state=j;render();
   }catch(e){
     $("#shortRows").innerHTML='<div class="empty">Creator Hub non disponibile. Riprova tra poco.</div>';
     $("#draftRows").innerHTML='<div class="empty">Creator Hub non disponibile. Riprova tra poco.</div>';
   }
 }'''

NEW = r''' /* V403_PROFILE_RECOVERY */
 const V403_HUB_CACHE="gsf_creator_hub_last_valid_v403";
 function v403HubHasIdentity(value){return !!(value&&value.account&&typeof value.account==="object"&&(value.account.display_name||value.account.account_id||value.account.avatar));}
 function v403HubReadCache(){try{const raw=localStorage.getItem(V403_HUB_CACHE);if(!raw)return null;const value=JSON.parse(raw);return v403HubHasIdentity(value)?value:null}catch(_e){return null}}
 function v403HubWriteCache(value){try{if(!v403HubHasIdentity(value))return;const raw=JSON.stringify(value);if(raw.length<480000)localStorage.setItem(V403_HUB_CACHE,raw)}catch(_e){}}
 function v403HubMarkStale(){const meta=$("#profileMeta");if(meta&&state&&state.account&&state.account.display_name){const old=String(meta.textContent||"");if(!old.includes("ultimo stato valido"))meta.textContent=(old?old+" · ":"")+"ultimo stato valido"}}
 async function loadState(){
   const cached=v403HubReadCache();
   if(cached&&!v403HubHasIdentity(state)){state=cached;render();v403HubMarkStale()}
   try{
     const r=await fetch("/creator-hub/state",{cache:"no-store",credentials:"same-origin"}),j=await r.json();
     if(!r.ok||!j.ok)throw new Error(j.error||"Hub non disponibile");
     state=j;v403HubWriteCache(j);render();
   }catch(e){
     if(v403HubHasIdentity(state)){v403HubMarkStale();return}
     if(cached){state=cached;render();v403HubMarkStale();return}
     $("#shortRows").innerHTML='<div class="empty">Creator Hub non disponibile. Riprova tra poco.</div>';
     $("#draftRows").innerHTML='<div class="empty">Creator Hub non disponibile. Riprova tra poco.</div>';
   }
 }'''

RESUME = r'''
 /* V403 foreground reconciliation: refresh only when the Hub comes back. */
 document.addEventListener("visibilitychange",()=>{if(!document.hidden)loadState()});
 window.addEventListener("pageshow",()=>loadState(),{passive:true});
'''


def patch_text(text: str) -> str:
    if MARK in text:
        return text
    if OLD not in text:
        raise RuntimeError("V403 Creator Hub loadState anchor missing")
    out = text.replace(OLD, NEW, 1)
    anchor = ' $(".closeTop").onclick=()=>shell("home");'
    if anchor not in out:
        raise RuntimeError("V403 Creator Hub closeTop anchor missing")
    out = out.replace(anchor, RESUME + "\n" + anchor, 1)
    return out


def main() -> None:
    if not TARGET.is_file():
        raise SystemExit(f"V403 Creator Hub target missing: {TARGET}")
    before = TARGET.read_text(encoding="utf-8")
    after = patch_text(before)
    TARGET.write_text(after, encoding="utf-8")
    print("V403 profile recovery applied changed=", before != after, flush=True)


if __name__ == "__main__":
    main()
