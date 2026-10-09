#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
HOME=ROOT/'web/home_v154_component/index.html'
MARK='v333HomeCtaTouchFix'

STYLE=r'''
<style id="v333HomeCtaTouchFix">
#home154 .muralGuide,#home154 .muralGuide *,#home154 .muralAmbient,#home154 .muralAmbient *{pointer-events:none!important}
#home154 .features{position:relative!important;z-index:60!important;pointer-events:auto!important}
#home154 .feature{pointer-events:auto!important;touch-action:manipulation!important;-webkit-tap-highlight-color:transparent!important}
</style>
'''

SCRIPT=r'''
<script id="v333HomeCtaTouchScript">
(()=>{
  if(window.__GSF_V333_CTA_TOUCH)return;
  window.__GSF_V333_CTA_TOUCH=true;
  const P=window.parent;
  const D=P.document;

  function GSF_V333_OPEN_EDITOR(){
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
  }

  function GSF_V333_OPEN_SHORT(){
    try{
      P.postMessage({type:'GSF_SHELL_NAV',target:'short'},P.location.origin);
      return true;
    }catch(_e){return false}
  }

  function bind(el,action){
    if(!el||el.dataset.v333Bound==='1')return;
    el.dataset.v333Bound='1';
    let lastTouch=0;
    const run=()=>action==='editor'?GSF_V333_OPEN_EDITOR():GSF_V333_OPEN_SHORT();
    el.addEventListener('touchend',e=>{
      lastTouch=Date.now();
      e.preventDefault();e.stopPropagation();
      run();
    },{passive:false});
    el.addEventListener('click',e=>{
      if(Date.now()-lastTouch<700){e.preventDefault();e.stopPropagation();return}
      e.preventDefault();e.stopPropagation();
      run();
    },true);
  }

  const bindAll=()=>{
    bind(document.querySelector('.feature[data-action="editor"]'),'editor');
    bind(document.querySelector('.feature[data-action="short"]'),'short');
  };
  bindAll();
  new MutationObserver(bindAll).observe(document.documentElement,{subtree:true,childList:true});
})();
</script>
'''


def main():
    if not HOME.is_file(): raise SystemExit('V333 Home missing')
    text=HOME.read_text(encoding='utf-8')
    changed=False
    if MARK not in text:
      if '</head>' not in text: raise RuntimeError('V333 head anchor missing')
      text=text.replace('</head>',STYLE+'\n</head>',1);changed=True
    if 'v333HomeCtaTouchScript' not in text:
      if '</body>' not in text: raise RuntimeError('V333 body anchor missing')
      text=text.replace('</body>',SCRIPT+'\n</body>',1);changed=True
    HOME.write_text(text,encoding='utf-8')
    print('V333 Home CTA touch fix applied changed=',changed,flush=True)

if __name__=='__main__': main()
