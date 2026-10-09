#!/usr/bin/env python3
from pathlib import Path
import ast
import base64
import gzip
import re
import sys

ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
APP=ROOT/'GamingShortsFactory_V154_STRUCTURAL_HOME.py'
HOME=ROOT/'web/home_v154_component/index.html'
MARK='GSF_GLOBAL_SHELL_V343'
IMPORT='import streamlit.components.v1 as _gsf_components_v343'

LEGACY_PARENT_MARKERS=(
    'V327_EDITOR_OPEN_BRIDGE',
    'V328_GLOBAL_BALANCE',
    'V330_GLOBAL_CHROME',
    'V331_PRIMARY_ACTIONS_ROUTING',
    'V332_GLOBAL_FRAME_LOCK',
    'V334_GLOBAL_CHROME_HARD_LOCK',
)

HOME_RESERVE=r'''
<!-- V343_HOME_SHELL_RESERVE -->
<style id="v343HomeShellReserve">
:root{--gsf-v343-home-head:calc(44px + env(safe-area-inset-top));--gsf-v343-home-bottom:calc(62px + 30px + max(8px,env(safe-area-inset-bottom)) + 12px)}
html.gsf-v343-parent-ready #home154 .topbar,
html.gsf-v343-parent-ready #home154 .bottomNav,
html.gsf-v343-parent-ready #home154 .siteFooter{visibility:hidden!important;opacity:0!important;pointer-events:none!important}
@media(max-width:760px){
  html,body{height:100%!important;min-height:100%!important;overflow:hidden!important}
  #home154{height:100dvh!important;min-height:100dvh!important;max-height:100dvh!important;overflow:hidden!important}
  #home154 .topbar{display:flex!important;min-height:var(--gsf-v343-home-head)!important;height:var(--gsf-v343-home-head)!important;flex:0 0 var(--gsf-v343-home-head)!important}
  #home154 .bottomNav{display:grid!important;min-height:68px!important;height:68px!important;max-height:68px!important;flex:0 0 68px!important;margin:0!important}
  #home154 .siteFooter{display:grid!important;min-height:calc(36px + max(8px,env(safe-area-inset-bottom)))!important;height:calc(36px + max(8px,env(safe-area-inset-bottom)))!important;max-height:calc(36px + max(8px,env(safe-area-inset-bottom)))!important;flex:0 0 calc(36px + max(8px,env(safe-area-inset-bottom)))!important;margin:0!important}
}
</style>
'''

EDITOR_OLD=r'''  function GSF_V333_OPEN_EDITOR(){
    try{
      const o=D.getElementById('gsf-editor-overlay-v220');
      if(!o)return false;
      const f=o.querySelector('iframe.gsf-editor-frame,iframe[title="Game Editor"]');
      if(f&&f.dataset.loaded!=='1'){
        f.src='/editor-live/?v=333';
        f.dataset.src='/editor-live/';
        f.dataset.loaded='1';
      }
      ['gsf-social-overlay-v159','gsf-creator-hub-live-v160','gsf-ai-overlay-v221','gsf-account-overlay-v223','gsf-short-overlay-v331'].forEach(id=>{
        const x=D.getElementById(id);if(!x)return;
        x.classList.remove('is-open');x.style.opacity='0';x.style.visibility='hidden';x.style.pointerEvents='none';x.setAttribute('aria-hidden','true');
      });
      o.classList.add('is-open');o.style.opacity='1';o.style.visibility='visible';o.style.pointerEvents='auto';o.setAttribute('aria-hidden','false');
      try{P.sessionStorage.setItem('gsf_editor_overlay_open_v223','1')}catch(_e){}
      try{P.postMessage({type:'GSF_SHELL_NAV',target:'editor'},P.location.origin)}catch(_e){}
      return true;
    }catch(_e){return false}
  }'''

EDITOR_NEW=r'''  function GSF_V333_OPEN_EDITOR(){
    try{
      P.postMessage({type:'GSF_SHELL_NAV',target:'editor'},P.location.origin);
      return true;
    }catch(_e){return false}
  }'''

JS_GZIP_B64='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'


def build_shell_block()->str:
    bridge=gzip.decompress(base64.b64decode(JS_GZIP_B64)).decode('utf-8')
    return "\n# GSF_GLOBAL_SHELL_V343 — the only parent-owned header, Game Bar, footer and shell router.\nif GSF_WEB_MODE:\n    _gsf_components_v343.html("+repr(bridge)+", height=0)\n"


def strip_legacy_parent_blocks(text:str)->str:
    lines=text.splitlines(keepends=True)
    tree=ast.parse(text)
    removals=[]
    for marker in LEGACY_PARENT_MARKERS:
        comment_idx=next((i for i,line in enumerate(lines) if line.startswith(f'# {marker}')),None)
        if comment_idx is None:
            continue
        if_line=comment_idx+2  # AST line numbers are 1-based; comment is immediately before the if.
        node=next((n for n in tree.body if isinstance(n,ast.If) and n.lineno==if_line),None)
        if node is None or not getattr(node,'end_lineno',None):
            raise RuntimeError(f'V343 cannot retire legacy parent block: {marker}')
        removals.append((comment_idx,node.end_lineno))
    for begin,end_line in sorted(removals,reverse=True):
        del lines[begin:end_line]
    return ''.join(lines)


def patch_home(text:str)->str:
    if 'V343_HOME_SHELL_RESERVE' not in text:
        if '</head>' not in text: raise RuntimeError('V343 Home head anchor missing')
        text=text.replace('</head>',HOME_RESERVE+'\n</head>',1)
    if EDITOR_OLD in text:
        text=text.replace(EDITOR_OLD,EDITOR_NEW,1)
    elif 'function GSF_V333_OPEN_EDITOR()' in text and "target:'editor'" not in text:
        raise RuntimeError('V343 V333 Editor route could not be canonicalized')
    return text


def patch_app(text:str)->str:
    text=strip_legacy_parent_blocks(text)
    text=re.sub(r'(?m)^# V34[012]_[^\n]*\n?','',text)
    if IMPORT not in text:
        anchor='import streamlit as st\n'
        if anchor not in text: raise RuntimeError('V343 Streamlit import anchor missing')
        text=text.replace(anchor,anchor+IMPORT+'\n',1)
    if MARK not in text:
        text=text.rstrip()+'\n\n'+build_shell_block()+'\n'
    compile(text,str(APP),'exec')
    return text


def main()->None:
    if not APP.is_file() or not HOME.is_file(): raise SystemExit('V343 runtime files missing')
    app_before=APP.read_text(encoding='utf-8');home_before=HOME.read_text(encoding='utf-8')
    app_after=patch_app(app_before);home_after=patch_home(home_before)
    APP.write_text(app_after,encoding='utf-8');HOME.write_text(home_after,encoding='utf-8')
    print('V343 single global shell applied app_changed=',app_before!=app_after,'home_changed=',home_before!=home_after,flush=True)

if __name__=='__main__': main()
