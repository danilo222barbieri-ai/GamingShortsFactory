#!/usr/bin/env python3
from pathlib import Path
import sys

MARK='V332_GLOBAL_FRAME_LOCK'
ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
HOME=ROOT/'web/home_v154_component/index.html'
APP=ROOT/'GamingShortsFactory_V154_STRUCTURAL_HOME.py'

HOME_STYLE=r'''
<style id="v332HomeFrameLock">
@media(max-width:760px){
  #home154{height:100dvh!important;min-height:100dvh!important;max-height:100dvh!important;overflow:hidden!important;padding-bottom:7px!important}
  #home154 .ui{height:100%!important;min-height:0!important;display:flex!important;flex-direction:column!important;overflow:hidden!important}
  #home154 .topbar{display:flex!important;flex:0 0 34px!important;min-height:34px!important;visibility:visible!important;opacity:1!important}
  #home154 #view{flex:1 1 auto!important;min-height:0!important;overflow:hidden!important}
  #home154 .bottomNav{display:grid!important;flex:0 0 62px!important;height:62px!important;min-height:62px!important;max-height:62px!important;margin:0 0 4px!important;visibility:visible!important;opacity:1!important}
  #home154 .siteFooter{display:grid!important;flex:0 0 30px!important;height:30px!important;min-height:30px!important;max-height:30px!important;margin:0!important;padding:1px 8px!important;visibility:visible!important;opacity:1!important;overflow:hidden!important}
  #home154 .footerBrand{display:none!important}
  #home154 .footerSocial{display:flex!important;align-items:center!important;justify-content:center!important;gap:7px!important}
  #home154 .footerSocialLink{width:16px!important;height:16px!important;min-width:16px!important;min-height:16px!important;padding:2px!important;visibility:visible!important;opacity:1!important}
  #home154 .footLinks{display:flex!important;align-items:center!important;justify-content:flex-end!important;gap:6px!important;white-space:nowrap!important}
}
</style>
'''

SHELL_BLOCK=r'''
# V332_GLOBAL_FRAME_LOCK — fixed header + Game Bar + footer on every internal page.
if GSF_WEB_MODE:
    st.html(r"""
    <div style="display:none!important"><script>
    ((P)=>{
      if(P.__GSF_V332_GLOBAL_FRAME_LOCK)return;
      P.__GSF_V332_GLOBAL_FRAME_LOCK=true;
      const D=P.document;
      const style=D.createElement('style');
      style.id='gsf-v332-global-frame-lock';
      style.textContent=`
        @media(max-width:760px){
          #gsf-v330-global-brand{top:8px!important;z-index:2147483662!important}
          #gsf-v330-global-footer{height:30px!important;min-height:30px!important;max-height:30px!important;z-index:2147483660!important}
          #gsf-page-nav-v249,[id^="gsf-page-nav"]{
            position:fixed!important;
            left:max(18px,env(safe-area-inset-left))!important;
            right:max(18px,env(safe-area-inset-right))!important;
            bottom:calc(var(--gsf-v330-footer-h,30px) + env(safe-area-inset-bottom))!important;
            height:62px!important;min-height:62px!important;max-height:62px!important;
            margin:0!important;z-index:2147483661!important;
          }
        }
      `;
      if(!D.getElementById(style.id))D.head.appendChild(style);

      const ids=[
        'gsf-social-overlay-v159',
        'gsf-creator-hub-live-v160',
        'gsf-editor-overlay-v220',
        'gsf-ai-overlay-v221',
        'gsf-account-overlay-v223',
        'gsf-short-overlay-v331'
      ];
      const isOpen=(el)=>{
        if(!el)return false;
        if(el.classList.contains('is-open'))return true;
        if(el.getAttribute('aria-hidden')==='false')return true;
        const s=P.getComputedStyle(el);
        return s.visibility!=='hidden'&&s.display!=='none'&&s.pointerEvents!=='none'&&Number(s.opacity||1)>.02;
      };
      const sync=()=>{
        const internal=ids.some(id=>isOpen(D.getElementById(id)));
        const brand=D.getElementById('gsf-v330-global-brand');
        const footer=D.getElementById('gsf-v330-global-footer');
        const nav=D.querySelector('#gsf-page-nav-v249,[id^="gsf-page-nav"]');
        if(brand)brand.classList.toggle('show',internal);
        if(footer)footer.classList.toggle('show',internal);
        if(nav){
          nav.style.display=internal?'grid':'none';
          nav.style.visibility=internal?'visible':'hidden';
          nav.style.opacity=internal?'1':'0';
          nav.style.pointerEvents=internal?'auto':'none';
        }
      };
      let raf=0;const schedule=()=>{if(raf)return;raf=P.requestAnimationFrame(()=>{raf=0;sync()})};
      new P.MutationObserver(schedule).observe(D.documentElement,{subtree:true,childList:true,attributes:true,attributeFilter:['class','style','aria-hidden']});
      P.addEventListener('resize',schedule,{passive:true});
      P.addEventListener('message',schedule,true);
      schedule();
    })(window.parent);
    </script></div>
    """, height=0)
'''


def main():
    if not HOME.is_file(): raise SystemExit('V332 Home missing')
    if not APP.is_file(): raise SystemExit('V332 shell missing')

    home=HOME.read_text(encoding='utf-8')
    if 'v332HomeFrameLock' not in home:
        if '</head>' not in home: raise RuntimeError('V332 Home head anchor missing')
        home=home.replace('</head>',HOME_STYLE+'\n</head>',1)
        HOME.write_text(home,encoding='utf-8')

    shell=APP.read_text(encoding='utf-8')
    if MARK not in shell:
        shell=shell.rstrip()+"\n\n"+SHELL_BLOCK+"\n"
        compile(shell,str(APP),'exec')
        APP.write_text(shell,encoding='utf-8')
    print('V332 global frame lock applied',flush=True)

if __name__=='__main__': main()
