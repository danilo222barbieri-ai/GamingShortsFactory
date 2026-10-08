#!/usr/bin/env python3
from pathlib import Path
import sys

MARK='V327_EDITOR_OPEN_BRIDGE'
BLOCK=r'''
# V327_EDITOR_OPEN_BRIDGE — keep Editor lazy, but guarantee shell-nav opens it.
if GSF_WEB_MODE:
    st.html(r"""
    <div style="display:none!important"><script>
    ((P)=>{
      if(P.__GSF_V327_EDITOR_BRIDGE)return;
      P.__GSF_V327_EDITOR_BRIDGE=true;
      const openEditor=()=>{
        const o=P.document.getElementById('gsf-editor-overlay-v220');
        if(!o)return;
        const f=o.querySelector('iframe.gsf-editor-frame,iframe[title="Game Editor"]');
        if(f && f.dataset.loaded!=='1'){
          f.src=(f.dataset.src||'/editor-live/')+'?v=327';
          f.dataset.loaded='1';
        }
        o.classList.add('is-open');
        o.style.opacity='1';
        o.style.visibility='visible';
        o.style.pointerEvents='auto';
        o.setAttribute('aria-hidden','false');
        try{P.sessionStorage.setItem('gsf_editor_overlay_open_v223','1')}catch(_e){}
      };
      P.addEventListener('message',(e)=>{
        if(e.origin!==P.location.origin||!e.data||e.data.type!=='GSF_SHELL_NAV')return;
        if(String(e.data.target||'')==='editor')openEditor();
      },true);
    })(window.parent);
    </script></div>
    """, height=0)
'''

def patch(text:str)->str:
    if MARK in text:return text
    return text.rstrip()+"\n\n"+BLOCK+"\n"

def main():
    root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
    shell=root/'GamingShortsFactory_V154_STRUCTURAL_HOME.py'
    if not shell.is_file(): raise SystemExit('V327 shell missing')
    before=shell.read_text(encoding='utf-8')
    after=patch(before)
    compile(after,str(shell),'exec')
    shell.write_text(after,encoding='utf-8')
    print('V327 editor open bridge applied changed=',before!=after,flush=True)

if __name__=='__main__': main()
