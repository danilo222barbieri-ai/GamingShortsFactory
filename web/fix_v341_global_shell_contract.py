#!/usr/bin/env python3
from pathlib import Path
import sys

MARK='V341_GLOBAL_SHELL_CONTRACT'
ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
APP=ROOT/'GamingShortsFactory_V154_STRUCTURAL_HOME.py'

DESKTOP_OLD='@media(min-width:761px){#gsf-v334-header,#gsf-v334-gamebar,#gsf-v334-footer{display:none!important}}'
DESKTOP_NEW='''@media(min-width:761px){
          /* V341_DESKTOP_GLOBAL_CHROME */
          :root{--gsf-v334-head:52px;--gsf-v334-foot:34px;--gsf-v334-bar:66px}
          #gsf-v334-header{display:flex!important;height:var(--gsf-v334-head)!important;padding-left:clamp(24px,3vw,48px)!important;padding-right:clamp(24px,3vw,48px)!important}
          #gsf-v334-gamebar{display:grid!important;left:50%!important;right:auto!important;width:min(560px,52vw)!important;transform:translateX(-50%)!important}
          #gsf-v334-footer{display:grid!important}
        }'''

HEADER_OLD='<span class="v334AccountName">Profilo</span>'
HEADER_NEW='<span class="v334AccountName">Accedi</span>'
ACCOUNT_OLD="const a=(j&&j.account)||{};const name=String(a.nickname||a.name||a.username||'Profilo');"
ACCOUNT_NEW="const a=(j&&j.account)||{};const name=String(a.nickname||a.name||a.username||'Accedi');"

BOOT_ANCHOR="""      let tries=0;const boot=()=>{syncSocials();if(tries++<25&&!footer.querySelector('.v334Socials').children.length)P.setTimeout(boot,120)};boot();syncAccount();"""

LOCK_BLOCK=r'''      const suppressLocalChrome=(doc)=>{
        try{
          if(!doc||!doc.documentElement)return;
          doc.documentElement.classList.add('gsf-global-shell-active');
          let lock=doc.getElementById('gsf-v341-local-chrome-lock');
          if(!lock){
            lock=doc.createElement('style');
            lock.id='gsf-v341-local-chrome-lock';
            lock.textContent=`
              html.gsf-global-shell-active #home154 .topbar,
              html.gsf-global-shell-active #home154 .bottomNav,
              html.gsf-global-shell-active #home154 .siteFooter,
              html.gsf-global-shell-active .bottomNav,.siteFooter,
              html.gsf-global-shell-active .gameBar,
              html.gsf-global-shell-active .gamebar,
              html.gsf-global-shell-active .game-bar,
              html.gsf-global-shell-active [data-global-gamebar],
              html.gsf-global-shell-active [id^="gsf-page-nav"],
              html.gsf-global-shell-active [data-gsf-v341-duplicate-chrome="1"]{
                display:none!important;visibility:hidden!important;opacity:0!important;pointer-events:none!important
              }
            `;
            (doc.head||doc.documentElement).appendChild(lock);
          }
          [...doc.querySelectorAll('.brandOnly,.brandText,.brand,[class*="brand"],header,.topbar')].forEach(n=>{
            const txt=String(n.textContent||'').replace(/\s+/g,' ').trim().toUpperCase();
            if(!txt.includes('GAMING SHORTS FACTORY'))return;
            const host=n.closest('.topbar,.siteHeader,.globalHeader,header')||n;
            host.setAttribute('data-gsf-v341-duplicate-chrome','1');
          });
        }catch(_e){}
      };
      const syncChildChrome=()=>{
        D.querySelectorAll('iframe').forEach(frame=>{
          const apply=()=>{try{suppressLocalChrome(frame.contentDocument)}catch(_e){}};
          apply();
          if(frame.dataset.gsfV341Bound!=='1'){
            frame.dataset.gsfV341Bound='1';
            frame.addEventListener('load',apply,{passive:true});
          }
        });
      };
      const keepGlobalChromeMounted=()=>{
        if(!css.isConnected)(D.head||D.documentElement).appendChild(css);
        if(!header.isConnected)D.body.appendChild(header);
        if(!bar.isConnected)D.body.appendChild(bar);
        if(!footer.isConnected)D.body.appendChild(footer);
        syncChildChrome();
      };
      const v341Observer=new MutationObserver(()=>keepGlobalChromeMounted());
      v341Observer.observe(D.documentElement,{childList:true,subtree:true});
      P.setInterval(keepGlobalChromeMounted,700);
      keepGlobalChromeMounted();
'''


def main():
    if not APP.is_file():
        raise SystemExit('V341 shell app missing')
    text=APP.read_text(encoding='utf-8')
    if MARK in text:
        print('V341 global shell contract already applied',flush=True)
        return

    if DESKTOP_OLD not in text:
        if 'V341_DESKTOP_GLOBAL_CHROME' not in text:
            raise RuntimeError('V341 desktop chrome anchor missing')
    else:
        text=text.replace(DESKTOP_OLD,DESKTOP_NEW,1)

    if HEADER_OLD in text:
        text=text.replace(HEADER_OLD,HEADER_NEW,1)
    elif HEADER_NEW not in text:
        raise RuntimeError('V341 account label anchor missing')

    if ACCOUNT_OLD in text:
        text=text.replace(ACCOUNT_OLD,ACCOUNT_NEW,1)
    elif ACCOUNT_NEW not in text:
        raise RuntimeError('V341 account sync anchor missing')

    if 'const suppressLocalChrome=' not in text:
        if BOOT_ANCHOR not in text:
            raise RuntimeError('V341 chrome boot anchor missing')
        text=text.replace(BOOT_ANCHOR,LOCK_BLOCK+'\n'+BOOT_ANCHOR,1)

    text=text.rstrip()+f'\n# {MARK}\n'
    compile(text,str(APP),'exec')
    APP.write_text(text,encoding='utf-8')
    print('V341 rigid global shell applied',flush=True)

if __name__=='__main__':
    main()
