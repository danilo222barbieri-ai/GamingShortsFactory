#!/usr/bin/env python3
from pathlib import Path
import re
import sys

MARK='V372_GLOBAL_SURFACE_OWNER'

HOME_OLD='''   if(action==="ai"){shellNav("ai");value({event:"open_ai",duration,engine});}
   if(action==="editor"){setEngine("manual");shellNav("editor");value({event:"open_editor",duration,engine:"manual"});}
   if(action==="short"){parentClick(["crea short","crea short finale","crea il tuo short"]);value({event:"create_short",duration,engine});}'''
HOME_NEW='''   // V372_GLOBAL_SURFACE_OWNER: primary cards only navigate. Real work stays inside each page.
   if(action==="ai"){shellNav("ai");}
   if(action==="editor"){setEngine("manual",false);shellNav("editor");}
   if(action==="short"){shellNav("short");}'''

LEGACY_WINDOW_OLD="""        if(e.origin!==location.origin||!e.data||e.data.type!=='GSF_SHELL_NAV')return;
        const t=String(e.data.target||'');
"""
LEGACY_WINDOW_NEW="""        if(e.origin!==location.origin||!e.data||e.data.type!=='GSF_SHELL_NAV')return;
        if(window.__GSF_GLOBAL_SHELL_V343)return;
        const t=String(e.data.target||'');
"""

AI_OLD="""        if(e.data.type!=='GSF_SHELL_NAV')return;
        const t=String(e.data.target||'');
"""
AI_NEW="""        if(e.data.type!=='GSF_SHELL_NAV')return;
        if(window.__GSF_GLOBAL_SHELL_V343)return;
        const t=String(e.data.target||'');
"""

V251_OLD="""      P.addEventListener('message',e=>{
        if(e.origin!==P.location.origin||!e.data||e.data.type!=='GSF_SHELL_NAV')return;
        const t=String(e.data.target||'');
        if(t==='ai-state')return;
"""
V251_NEW="""      P.addEventListener('message',e=>{
        if(e.origin!==P.location.origin||!e.data||e.data.type!=='GSF_SHELL_NAV')return;
        if(P.__GSF_GLOBAL_SHELL_V343)return;
        const t=String(e.data.target||'');
        if(t==='ai-state')return;
"""

AUTO_OLD="try{if(sessionStorage.getItem(KEY)==='1')setTimeout(()=>open(false),90)}catch(e){}"
AUTO_NEW="try{if(!window.__GSF_GLOBAL_SHELL_V343&&sessionStorage.getItem(KEY)==='1')setTimeout(()=>open(false),90)}catch(e){}"


def patch_home_text(text:str)->str:
    if HOME_NEW not in text:
        if HOME_OLD not in text:
            raise RuntimeError('V372 Home primary-action anchor missing')
        text=text.replace(HOME_OLD,HOME_NEW,1)
    return text


def patch_shell_text(text:str)->str:
    # V159/V160/V220/V223 legacy surface listeners use the window=P alias.
    # Stand every remaining one down once V343 is present. Internal component
    # messages are preserved; only GSF_SHELL_NAV ownership is retired.
    text=text.replace(LEGACY_WINDOW_OLD,LEGACY_WINDOW_NEW)

    # V221 handles GSF_AI_UI before the shell branch. Preserve that internal
    # bridge, but do not let V221 also open/close parent surfaces under V343.
    if AI_OLD in text:
        text=text.replace(AI_OLD,AI_NEW,1)

    # V251 is the old parent route guard. It must never show/hide overlays when
    # V343 is mounted; otherwise one tap has two competing surface owners.
    if V251_OLD in text:
        text=text.replace(V251_OLD,V251_NEW,1)

    # V220/V221 legacy session restore could reopen a surface after a Streamlit
    # remount independently of V343. Canonical V343 owns restore/navigation.
    text=text.replace(AUTO_OLD,AUTO_NEW)

    return text


def assert_contract(home:str,shell:str)->None:
    if HOME_NEW not in home:
        raise RuntimeError('V372 Home navigation-only contract missing')
    for token in (
        'if(window.__GSF_GLOBAL_SHELL_V343)return;',
        'if(P.__GSF_GLOBAL_SHELL_V343)return;',
        'if(!window.__GSF_GLOBAL_SHELL_V343&&sessionStorage.getItem(KEY)',
    ):
        if token not in shell:
            raise RuntimeError('V372 shell contract missing: '+token)


def write_if_changed(path:Path,patcher)->bool:
    before=path.read_text(encoding='utf-8')
    after=patcher(before)
    if after!=before:
        path.write_text(after,encoding='utf-8')
        return True
    return False


def main()->None:
    root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
    home=root/'web'/'home_v154_component'/'index.html'
    generator=root/'web'/'apply_v154_structural_home.py'
    if not home.is_file() or not generator.is_file():
        raise SystemExit('V372 required Home/generator files missing')

    home_changed=write_if_changed(home,patch_home_text)
    generator_changed=write_if_changed(generator,patch_shell_text)

    runtime_changed=[]
    for name in ('GamingShortsFactory_V154_STRUCTURAL_HOME.py','GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py'):
        path=root/name
        if not path.is_file():
            continue
        changed=write_if_changed(path,patch_shell_text)
        compile(path.read_text(encoding='utf-8'),str(path),'exec')
        runtime_changed.append((name,changed))

    assert_contract(home.read_text(encoding='utf-8'),generator.read_text(encoding='utf-8'))
    print('V372 global surface owner applied home_changed=',home_changed,'generator_changed=',generator_changed,'runtime_changed=',runtime_changed,flush=True)


if __name__=='__main__':
    main()
