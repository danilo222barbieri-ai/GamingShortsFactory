#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
APP=ROOT/'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py'
MARK='GSF_V348_TRANSPARENT_LOGO_FOOTER'

if not APP.is_file():
    raise SystemExit('V348 runtime app missing')

text=APP.read_text(encoding='utf-8')
if MARK in text:
    print('V348 transparent logo + footer already applied', flush=True)
    raise SystemExit(0)

block = r'''
# GSF_V348_TRANSPARENT_LOGO_FOOTER
import streamlit.components.v1 as _gsf_components_v348
_gsf_components_v348.html(r"""
<script id="gsf-v348-logo-footer">
(() => {
  const P=window.parent, D=P.document;
  const LOGO='data:image/png;base64,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';

  function ensureStyle(){
    let s=D.getElementById('gsf-v348-logo-footer-style');
    if(!s){
      s=D.createElement('style');
      s.id='gsf-v348-logo-footer-style';
      s.textContent=`
        #gsf-global-header img.gsf-v348-transparent-logo{
          background:transparent!important;
          border:0!important;
          box-shadow:none!important;
          object-fit:contain!important;
        }
        #gsf-global-header .gsf-v348-transparent-logo-wrap{
          background:transparent!important;
          border:0!important;
          box-shadow:none!important;
        }
        #gsf-global-footer{
          display:flex!important;
          visibility:visible!important;
          opacity:1!important;
          pointer-events:auto!important;
          position:fixed!important;
          left:0!important;
          right:0!important;
          bottom:max(4px,env(safe-area-inset-bottom))!important;
          min-height:30px!important;
          height:30px!important;
          max-height:30px!important;
          z-index:2147483600!important;
          transform:none!important;
        }
        #gsf-global-gamebar{
          bottom:calc(34px + max(8px,env(safe-area-inset-bottom)))!important;
        }
      `;
      D.head.appendChild(s);
    }
  }

  function apply(){
    ensureStyle();
    const h=D.getElementById('gsf-global-header');
    if(h){
      const imgs=[...h.querySelectorAll('img')];
      let logo=imgs.find(img=>{
        const r=img.getBoundingClientRect();
        return r.left < (P.innerWidth||1000)*0.5 && r.width<=90 && r.height<=90;
      }) || imgs[0];
      if(logo){
        if(logo.src!==LOGO) logo.src=LOGO;
        logo.classList.add('gsf-v348-transparent-logo');
        logo.style.background='transparent';
        logo.style.boxShadow='none';
        logo.style.objectFit='contain';
        const w=logo.parentElement;
        if(w){
          w.classList.add('gsf-v348-transparent-logo-wrap');
          w.style.background='transparent';
          w.style.boxShadow='none';
          w.style.border='0';
        }
      }
    }
    const f=D.getElementById('gsf-global-footer');
    if(f){
      f.style.display='flex';
      f.style.visibility='visible';
      f.style.opacity='1';
      f.style.pointerEvents='auto';
    }
  }

  apply();
  setTimeout(apply,80);
  setTimeout(apply,300);
  setTimeout(apply,900);
  try{
    new MutationObserver(apply).observe(D.documentElement,{childList:true,subtree:true});
  }catch(_e){}
})();
</script>
""", height=0)
'''
APP.write_text(text + '\n' + block + '\n', encoding='utf-8')
print('V348 transparent logo + footer applied', flush=True)
