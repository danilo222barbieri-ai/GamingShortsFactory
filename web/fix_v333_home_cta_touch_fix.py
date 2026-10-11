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

  function GSF_V333_OPEN_AI(){
    try{
      P.postMessage({type:'GSF_SHELL_NAV',target:'ai'},P.location.origin);
      return true;
    }catch(_e){return false}
  }

  function GSF_V333_OPEN_EDITOR(){
    try{
      P.postMessage({type:'GSF_SHELL_NAV',target:'editor'},P.location.origin);
      return true;
    }catch(_e){return false}
  }

  function GSF_V333_OPEN_SHORT(){
    try{
      P.postMessage({type:'GSF_SHELL_NAV',target:'short'},P.location.origin);
      return true;
    }catch(_e){return false}
  }

  function run(action){
    if(action==='ai')return GSF_V333_OPEN_AI();
    if(action==='editor')return GSF_V333_OPEN_EDITOR();
    if(action==='short')return GSF_V333_OPEN_SHORT();
    return false;
  }

  function bind(el,action){
    if(!el||el.dataset.v333Bound==='1')return;
    el.dataset.v333Bound='1';
    let lastTouch=0;
    el.addEventListener('touchend',e=>{
      lastTouch=Date.now();
      e.preventDefault();e.stopPropagation();e.stopImmediatePropagation();
      run(action);
    },{passive:false});
    el.addEventListener('click',e=>{
      if(Date.now()-lastTouch<700){e.preventDefault();e.stopPropagation();e.stopImmediatePropagation();return}
      e.preventDefault();e.stopPropagation();e.stopImmediatePropagation();
      run(action);
    },true);
  }

  const bindAll=()=>{
    bind(document.querySelector('.feature[data-action="ai"]'),'ai');
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
    print('V333/V372 Home CTA canonical routing applied changed=',changed,flush=True)

if __name__=='__main__': main()
