#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

MARK='V340_SHELL_RESILIENCE'
ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
HOME=ROOT/'web/home_v154_component/index.html'
APP=ROOT/'GamingShortsFactory_V154_STRUCTURAL_HOME.py'

HOME_OLD=r'''  #home154 .topbar,
  #home154 .bottomNav,
  #home154 .siteFooter{
    visibility:hidden!important;
    opacity:0!important;
    pointer-events:none!important;
  }'''
HOME_NEW=r'''  html.gsf-v334-parent-ready #home154 .topbar,
  html.gsf-v334-parent-ready #home154 .bottomNav,
  html.gsf-v334-parent-ready #home154 .siteFooter{
    visibility:hidden!important;
    opacity:0!important;
    pointer-events:none!important;
  }'''

HOME_WATCHER=r'''
<script id="V340_HOME_CHROME_FALLBACK">
(()=>{
  const root=document.documentElement;
  const complete=()=>{
    try{
      const d=window.parent.document;
      return !!(d.getElementById('gsf-v334-header')&&d.getElementById('gsf-v334-gamebar')&&d.getElementById('gsf-v334-footer'));
    }catch(_e){return false}
  };
  const sync=()=>root.classList.toggle('gsf-v334-parent-ready',complete());
  sync();
  window.addEventListener('message',e=>{
    if(!e.data)return;
    if(e.data.type==='GSF_V334_CHROME_READY'||e.data.type==='GSF_V334_CHROME_CHECK')sync();
  });
  window.setInterval(sync,900);
})();
</script>
'''

GUARD_OLD="""      if(P.__GSF_V334_GLOBAL_CHROME_HARD_LOCK)return;\n      P.__GSF_V334_GLOBAL_CHROME_HARD_LOCK=true;\n      const D=P.document;"""
GUARD_NEW="""      const D=P.document;\n      const v340ChromeComplete=()=>!!(D.getElementById('gsf-v334-header')&&D.getElementById('gsf-v334-gamebar')&&D.getElementById('gsf-v334-footer'));\n      if(P.__GSF_V334_GLOBAL_CHROME_HARD_LOCK&&v340ChromeComplete())return;\n      P.__GSF_V334_GLOBAL_CHROME_HARD_LOCK=true;"""

EDITOR_OLD=r'''      const v331OpenEditor=(attempt=0)=>{
        const o=D.getElementById('gsf-editor-overlay-v220');
        if(!o){if(attempt<20)P.setTimeout(()=>v331OpenEditor(attempt+1),45+attempt*18);return false}
        const f=o.querySelector('iframe.gsf-editor-frame,iframe[title="Game Editor"]');
        if(f&&f.dataset.loaded!=='1'){
          f.src='/editor-live/?v=331';
          f.dataset.src='/editor-live/';
          f.dataset.loaded='1';
        }
        closeCompeting('gsf-editor-overlay-v220');
        o.classList.add('is-open');
        o.style.opacity='1';o.style.visibility='visible';o.style.pointerEvents='auto';
        o.setAttribute('aria-hidden','false');
        try{P.sessionStorage.setItem(EDITOR_KEY,'1');P.sessionStorage.setItem(SHORT_KEY,'0')}catch(_e){}
        return true;
      };'''

EDITOR_NEW=r'''      const ensureEditorSurface=()=>{
        let o=D.getElementById('gsf-editor-overlay-v220');
        if(!o){
          o=D.createElement('section');
          o.id='gsf-editor-overlay-v220';
          o.setAttribute('aria-hidden','true');
          o.style.cssText='position:fixed;inset:0;z-index:2147483653;display:block;background:linear-gradient(180deg,#FEFFFF 0%,#F8FCFF 100%);opacity:0;visibility:hidden;pointer-events:none;transition:opacity .18s ease,visibility .18s ease;';
          o.innerHTML=`<div class="gsf-editor-shell" role="dialog" aria-modal="false" aria-label="Game Editor" style="position:absolute;left:0;right:0;top:44px;bottom:98px;min-height:0;background:#F8FCFF;overflow:hidden"><button class="v340EditorClose" type="button" aria-label="Chiudi Game Editor" style="position:absolute;right:8px;top:8px;z-index:20;width:34px;height:34px;border:1px solid rgba(150,184,214,.30);border-radius:12px;background:rgba(255,255,255,.94);color:#60789c;font:700 22px/1 sans-serif;box-shadow:0 8px 20px rgba(68,104,142,.10)">×</button><iframe class="gsf-editor-frame" title="Game Editor" data-src="/editor-live/" style="width:100%;height:100%;display:block;border:0;background:#F8FCFF" allow="autoplay; fullscreen; clipboard-read; clipboard-write" allowfullscreen></iframe></div>`;
          D.body.appendChild(o);
          const close=o.querySelector('.v340EditorClose');
          if(close)close.addEventListener('click',()=>{
            hideOverlay(o);
            try{P.sessionStorage.setItem(EDITOR_KEY,'0')}catch(_e){}
            P.postMessage({type:'GSF_SHELL_NAV',target:'home'},P.location.origin);
          });
        }
        let f=o.querySelector('iframe.gsf-editor-frame,iframe[title="Game Editor"]');
        if(!f){
          const host=o.querySelector('.gsf-editor-shell')||o;
          f=D.createElement('iframe');
          f.className='gsf-editor-frame';f.title='Game Editor';f.dataset.src='/editor-live/';
          f.style.cssText='width:100%;height:100%;display:block;border:0;background:#F8FCFF';
          f.setAttribute('allow','autoplay; fullscreen; clipboard-read; clipboard-write');
          f.setAttribute('allowfullscreen','');
          host.appendChild(f);
        }
        return o;
      };

      const v331OpenEditor=()=>{
        const o=ensureEditorSurface();
        const f=o.querySelector('iframe.gsf-editor-frame,iframe[title="Game Editor"]');
        if(f&&f.dataset.loaded!=='1'){
          f.dataset.src='/editor-live/';
          f.src='/editor-live/?v=340';
          f.dataset.loaded='1';
        }
        closeCompeting('gsf-editor-overlay-v220');
        o.classList.add('is-open');
        o.style.opacity='1';o.style.visibility='visible';o.style.pointerEvents='auto';
        o.setAttribute('aria-hidden','false');
        try{P.sessionStorage.setItem(EDITOR_KEY,'1');P.sessionStorage.setItem(SHORT_KEY,'0')}catch(_e){}
        return true;
      };'''


def patch_home(text:str)->str:
    if HOME_OLD in text:
        text=text.replace(HOME_OLD,HOME_NEW,1)
    elif 'html.gsf-v334-parent-ready #home154 .topbar' not in text:
        raise RuntimeError('V340 Home chrome visibility anchor missing')

    if 'V340_HOME_CHROME_FALLBACK' not in text:
        marker='<!-- V334_GLOBAL_CHROME_HOME_SLOT -->'
        pos=text.find(marker)
        if pos<0:
            raise RuntimeError('V340 V334 Home marker missing')
        end=text.find('</style>',pos)
        if end<0:
            raise RuntimeError('V340 V334 Home style end missing')
        end += len('</style>')
        text=text[:end]+'\n'+HOME_WATCHER+text[end:]
    return text


def patch_app(text:str)->str:
    if MARK in text:
        return text
    if GUARD_OLD not in text:
        if 'v340ChromeComplete' not in text:
            raise RuntimeError('V340 global chrome guard anchor missing')
    else:
        text=text.replace(GUARD_OLD,GUARD_NEW,1)

    if EDITOR_OLD not in text:
        if 'ensureEditorSurface' not in text:
            raise RuntimeError('V340 editor open anchor missing')
    else:
        text=text.replace(EDITOR_OLD,EDITOR_NEW,1)

    text=text.rstrip()+f'\n# {MARK}\n'
    compile(text,str(APP),'exec')
    return text


def main():
    if not HOME.is_file() or not APP.is_file():
        raise SystemExit('V340 runtime files missing')
    home_before=HOME.read_text(encoding='utf-8')
    app_before=APP.read_text(encoding='utf-8')
    home_after=patch_home(home_before)
    app_after=patch_app(app_before)
    HOME.write_text(home_after,encoding='utf-8')
    APP.write_text(app_after,encoding='utf-8')
    print('V340 shell resilience applied home_changed=',home_before!=home_after,'app_changed=',app_before!=app_after,flush=True)

    # V341 owns the rigid global shell contract. Keep it chained here so it is
    # always applied before V336 converts the V334 bridge into an executable
    # Streamlit component, including restart-safe boots where V340 is already present.
    v341=ROOT/'web/fix_v341_global_shell_contract.py'
    t341=ROOT/'web/test_v341_global_shell_contract.py'
    if not v341.is_file() or not t341.is_file():
        raise SystemExit('V341 shell contract files missing')
    subprocess.run([sys.executable,str(v341),str(ROOT)],check=True)
    subprocess.run([sys.executable,str(t341),str(ROOT)],check=True)

if __name__=='__main__':
    main()
