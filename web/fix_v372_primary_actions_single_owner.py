#!/usr/bin/env python3
from pathlib import Path
import sys

MARK='V372_PRIMARY_ACTIONS_SINGLE_OWNER'

FEATURE_OLD='''   if(action==="ai"){shellNav("ai");value({event:"open_ai",duration,engine});}
   if(action==="editor"){setEngine("manual");shellNav("editor");value({event:"open_editor",duration,engine:"manual"});}
   if(action==="short"){parentClick(["crea short","crea short finale","crea il tuo short"]);value({event:"create_short",duration,engine});}'''
FEATURE_NEW='''   // V372_PRIMARY_ACTIONS_SINGLE_OWNER: these tiles navigate only.
   // The opened page owns analysis/editor/render actions; never rerun Streamlit here.
   if(action==="ai"){shellNav("ai");}
   if(action==="editor"){shellNav("editor");}
   if(action==="short"){shellNav("short");}'''

EDITOR_OLD='''        if(e.origin!==location.origin||!e.data||e.data.type!=='GSF_SHELL_NAV')return;
        const t=String(e.data.target||'');
        if(t==='editor'){open();return}
        if(t==='close'||t==='home'||t==='social'||t==='hub'||t==='ai'||t==='account')close();'''
EDITOR_NEW='''        if(e.origin!==location.origin||!e.data||e.data.type!=='GSF_SHELL_NAV')return;
        const t=String(e.data.target||'');
        // V372: V343 chooses the page. V220 only bootstraps its own Editor surface.
        if(P.__GSF_GLOBAL_SHELL_V343){
          if(t==='editor'){open();return}
          return;
        }
        if(t==='editor'){open();return}
        if(t==='close'||t==='home'||t==='social'||t==='hub'||t==='ai'||t==='account')close();'''

AI_OLD='''        if(e.data.type!=='GSF_SHELL_NAV')return;
        const t=String(e.data.target||'');
        if(t==='ai'){open();return}
        if(t==='ai-state'){forwardState(e.data);return}
        if(t==='editor'||t==='social'||t==='hub'||t==='home'||t==='close'||t==='account')close();'''
AI_NEW='''        if(e.data.type!=='GSF_SHELL_NAV')return;
        const t=String(e.data.target||'');
        // V372: V343 owns navigation. V221 keeps only AI bootstrap/state forwarding.
        if(P.__GSF_GLOBAL_SHELL_V343){
          if(t==='ai'){open();return}
          if(t==='ai-state'){forwardState(e.data);return}
          return;
        }
        if(t==='ai'){open();return}
        if(t==='ai-state'){forwardState(e.data);return}
        if(t==='editor'||t==='social'||t==='hub'||t==='home'||t==='close'||t==='account')close();'''

V251_OLD='''        if(e.origin!==P.location.origin||!e.data||e.data.type!=='GSF_SHELL_NAV')return;
        const t=String(e.data.target||'');
        if(t==='ai-state')return;'''
V251_NEW='''        if(e.origin!==P.location.origin||!e.data||e.data.type!=='GSF_SHELL_NAV')return;
        // V372: V251 is legacy fallback only; V343 is the production router.
        if(P.__GSF_GLOBAL_SHELL_V343)return;
        const t=String(e.data.target||'');
        if(t==='ai-state')return;'''


def patch_home_text(text:str)->str:
    if FEATURE_NEW in text:
        return text
    if FEATURE_OLD not in text:
        raise RuntimeError('V372 Home primary action block missing')
    return text.replace(FEATURE_OLD,FEATURE_NEW,1)


def _replace_contract(text:str,old:str,new:str,label:str)->str:
    if new in text:
        return text
    if old not in text:
        raise RuntimeError(f'V372 {label} anchor missing')
    return text.replace(old,new,1)


def patch_shell_text(text:str)->str:
    # Only files that contain these production surfaces need the JS routing patch.
    has_surfaces=('gsf-editor-overlay-v220' in text and 'gsf-ai-overlay-v221' in text)
    if has_surfaces:
        text=_replace_contract(text,EDITOR_OLD,EDITOR_NEW,'Editor V220')
        text=_replace_contract(text,AI_OLD,AI_NEW,'AI V221')
        if '# V251 ROUTE GUARD' in text:
            text=_replace_contract(text,V251_OLD,V251_NEW,'V251 route guard')
    if MARK not in text:
        text=text.rstrip()+f'\n# {MARK}\n'
    return text


def _write(path:Path,patcher)->bool:
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
        raise SystemExit('V372 Home/generator files missing')

    home_changed=_write(home,patch_home_text)
    generator_changed=_write(generator,patch_shell_text)

    runtime_changed=[]
    for name in ('GamingShortsFactory_V154_STRUCTURAL_HOME.py','GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py'):
        path=root/name
        if not path.is_file():
            continue
        changed=_write(path,patch_shell_text)
        compile(path.read_text(encoding='utf-8'),str(path),'exec')
        runtime_changed.append((name,changed))

    print(
        'V372 primary actions single owner applied',
        'home_changed=',home_changed,
        'generator_changed=',generator_changed,
        'runtime_changed=',runtime_changed,
        flush=True,
    )


if __name__=='__main__':
    main()
