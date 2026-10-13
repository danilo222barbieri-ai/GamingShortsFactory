#!/usr/bin/env python3
"""V403 final recovery refinements for Creator Hub and Editor handoff."""
from __future__ import annotations

from pathlib import Path
import re
import sys

MARK_PROFILE="V403_PROFILE_RESUME"
MARK_EDITOR="V403_EDITOR_HANDOFF"
ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
HUB=ROOT/'web'/'creator_hub_v156_component'/'index.html'
APP=ROOT/'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py'


def patch_hub_text(text:str)->str:
    if MARK_PROFILE in text:return text
    anchor=' openView("dashboard");loadState();'
    if anchor not in text:
        raise RuntimeError('V403 Creator Hub startup anchor missing')
    block=''' /* V403_PROFILE_RESUME — single-flight foreground refresh; last rendered identity stays visible on failure. */\n let v403StateLoadPromise=null;\n function v403ReloadState(){\n   if(v403StateLoadPromise)return v403StateLoadPromise;\n   v403StateLoadPromise=Promise.resolve(loadState()).finally(()=>{v403StateLoadPromise=null});\n   return v403StateLoadPromise;\n }\n document.addEventListener("visibilitychange",()=>{if(!document.hidden)v403ReloadState()});\n window.addEventListener("pageshow",()=>v403ReloadState());\n openView("dashboard");v403ReloadState();'''
    return text.replace(anchor,block,1)


def patch_app_text(text:str)->str:
    if MARK_EDITOR in text:return text
    if '# V403_APP_STABILITY_FLOW — final browser owner' not in text:
        raise RuntimeError('V403 runtime bridge must be applied before Editor handoff')
    pattern=re.compile(r"const openEditor=async\(\)=>\{.*?\};\n\s*const clickRender=",re.DOTALL)
    replacement=r'''/* V403_EDITOR_HANDOFF · component gsf_editor_2027_v1086 */
      const openEditor=async()=>{
        await flow('route',{route:'editor'});
        const snap=await broadcast();
        const rows=Array.isArray(snap?.candidates)?snap.candidates:[];
        const row=rows.find(x=>x&&String(x.id||'')===String(snap?.selected_candidate_id||''))||null;
        if(!row){await flow('route',{route:'moments'});openMoments();return}
        closeV403();
        P.postMessage({type:'GSF_SHELL_NAV',target:'editor',source:'v403',component_id:'gsf_editor_2027_v1086',candidate_id:String(row.id||''),video_url:String(row.preview_ref||snap?.source_video_ref||''),source_video_ref:String(snap?.source_video_ref||''),start_seconds:Number(row.start_seconds||0),end_seconds:Number(row.end_seconds||0),duration:Math.max(.5,Number(row.end_seconds||0)-Number(row.start_seconds||0)||Number(row.duration||15))},P.location.origin)
      };
      const clickRender='''
    out,n=pattern.subn(replacement,text,count=1)
    if n!=1:raise RuntimeError('V403 Editor handoff anchor missing')
    compile(out,str(APP),'exec')
    return out


def _patch(path:Path,fn,label:str)->None:
    if not path.is_file():raise RuntimeError(f'V403 missing {label}: {path}')
    before=path.read_text(encoding='utf-8');after=fn(before);path.write_text(after,encoding='utf-8');print(f'V403 {label} changed={before!=after}',flush=True)


def main()->None:
    _patch(HUB,patch_hub_text,'Creator Hub resume')
    _patch(APP,patch_app_text,'Editor selected-moment handoff')
    print('V403 PROFILE RESUME + EDITOR HANDOFF: PASS',flush=True)

if __name__=='__main__':main()
