#!/usr/bin/env python3
from pathlib import Path
import sys

MARK='V341_GLOBAL_SHELL_CONTRACT'
SAFE_MARK='V342_GLOBAL_CHROME_SAFEAREA'
ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
APP=ROOT/'GamingShortsFactory_V154_STRUCTURAL_HOME.py'
HOME=ROOT/'web/home_v154_component/index.html'

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
ACCOUNT_V341="const a=(j&&j.account)||{};const name=String(a.nickname||a.name||a.username||'Accedi');"
ACCOUNT_V342="const a=(j&&j.account)||{};const name=String(a.display_name||a.nickname||a.name||a.username||String(a.email||'').split('@')[0]||'Accedi');"

ROOT_OLD=':root{--gsf-v334-head:44px;--gsf-v334-foot:30px;--gsf-v334-bar:62px}'
ROOT_NEW=':root{--gsf-v334-head:44px;--gsf-v334-foot:30px;--gsf-v334-bar:62px;--gsf-v334-safe-bottom:max(8px,env(safe-area-inset-bottom))}'
GAMEBAR_BOTTOM_OLD='bottom:calc(var(--gsf-v334-foot) + env(safe-area-inset-bottom));height:var(--gsf-v334-bar)'
GAMEBAR_BOTTOM_NEW='bottom:calc(var(--gsf-v334-foot) + var(--gsf-v334-safe-bottom) + 6px);height:var(--gsf-v334-bar)'
FOOTER_HEIGHT_OLD='#gsf-v334-footer{position:fixed;left:0;right:0;bottom:0;height:var(--gsf-v334-foot);'
FOOTER_HEIGHT_NEW='#gsf-v334-footer{position:fixed;left:0;right:0;bottom:0;height:calc(var(--gsf-v334-foot) + var(--gsf-v334-safe-bottom));'
FOOTER_PADDING_OLD='padding:0 max(12px,env(safe-area-inset-right)) 0 max(12px,env(safe-area-inset-left));'
FOOTER_PADDING_NEW='padding:0 max(12px,env(safe-area-inset-right)) var(--gsf-v334-safe-bottom) max(12px,env(safe-area-inset-left));'
LOGO_OLD='#gsf-v334-header .v334Mark{display:block;width:13px;height:19px;flex:0 0 13px;background:#6c81a1;-webkit-mask-image:url("${LOGO}");mask-image:url("${LOGO}");-webkit-mask-size:contain;mask-size:contain;-webkit-mask-position:center;mask-position:center;-webkit-mask-repeat:no-repeat;mask-repeat:no-repeat}'
LOGO_NEW='#gsf-v334-header .v334Mark{display:block;width:18px;height:22px;flex:0 0 18px;background-color:transparent;background-image:url("${LOGO}");background-size:contain;background-position:center;background-repeat:no-repeat;-webkit-mask-image:none;mask-image:none}'

BOOT_ANCHOR="""      let tries=0;const boot=()=>{syncSocials();if(tries++<25&&!footer.querySelector('.v334Socials').children.length)P.setTimeout(boot,120)};boot();syncAccount();"""

LOCK_BLOCK=r'''      const suppressLocalChrome=(doc)=>{
        try{
          if(!doc||!doc.documentElement)return;
          /* Home keeps invisible header/nav/footer placeholders so the fixed
             parent shell never covers its CTA cards. V340 owns that handoff. */
          if(doc.getElementById('home154'))return;
          doc.documentElement.classList.add('gsf-global-shell-active');
          let lock=doc.getElementById('gsf-v341-local-chrome-lock');
          if(!lock){
            lock=doc.createElement('style');
            lock.id='gsf-v341-local-chrome-lock';
            lock.textContent=`
              html.gsf-global-shell-active .bottomNav,
              html.gsf-global-shell-active .siteFooter,
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
      /* V342_EDITOR_CANONICAL_ROUTE — Editor uses the same parent router as Crea Short. */
      P.postMessage({type:'GSF_SHELL_NAV',target:'editor'},P.location.origin);
      return true;
    }catch(_e){return false}
  }'''


def patch_home(home:str)->str:
    if 'V342_EDITOR_CANONICAL_ROUTE' in home:
        return home
    if EDITOR_OLD not in home:
        raise RuntimeError('V342 legacy Editor touch route anchor missing')
    return home.replace(EDITOR_OLD,EDITOR_NEW,1)


def patch_app(text:str)->str:
    # V341 base contract.
    if MARK not in text:
        if DESKTOP_OLD in text:
            text=text.replace(DESKTOP_OLD,DESKTOP_NEW,1)
        elif 'V341_DESKTOP_GLOBAL_CHROME' not in text:
            raise RuntimeError('V341 desktop chrome anchor missing')

        if HEADER_OLD in text:
            text=text.replace(HEADER_OLD,HEADER_NEW,1)
        elif HEADER_NEW not in text:
            raise RuntimeError('V341 account label anchor missing')

        if ACCOUNT_OLD in text:
            text=text.replace(ACCOUNT_OLD,ACCOUNT_V341,1)
        elif ACCOUNT_V341 not in text and ACCOUNT_V342 not in text:
            raise RuntimeError('V341 account sync anchor missing')

        if 'const suppressLocalChrome=' not in text:
            if BOOT_ANCHOR not in text:
                raise RuntimeError('V341 chrome boot anchor missing')
            text=text.replace(BOOT_ANCHOR,LOCK_BLOCK+'\n'+BOOT_ANCHOR,1)

        text=text.rstrip()+f'\n# {MARK}\n'

    # V342 hardens the global shell and removes the last legacy Editor dead-end.
    if ACCOUNT_V341 in text:
        text=text.replace(ACCOUNT_V341,ACCOUNT_V342,1)
    elif ACCOUNT_V342 not in text:
        raise RuntimeError('V342 account display-name anchor missing')

    if ROOT_OLD in text:
        text=text.replace(ROOT_OLD,ROOT_NEW,1)
    elif ROOT_NEW not in text:
        raise RuntimeError('V342 root safe-area anchor missing')

    if GAMEBAR_BOTTOM_OLD in text:
        text=text.replace(GAMEBAR_BOTTOM_OLD,GAMEBAR_BOTTOM_NEW,1)
    elif GAMEBAR_BOTTOM_NEW not in text:
        raise RuntimeError('V342 Game Bar bottom anchor missing')

    if FOOTER_HEIGHT_OLD in text:
        text=text.replace(FOOTER_HEIGHT_OLD,FOOTER_HEIGHT_NEW,1)
    elif FOOTER_HEIGHT_NEW not in text:
        raise RuntimeError('V342 footer height anchor missing')

    if FOOTER_PADDING_OLD in text:
        text=text.replace(FOOTER_PADDING_OLD,FOOTER_PADDING_NEW,1)
    elif FOOTER_PADDING_NEW not in text:
        raise RuntimeError('V342 footer safe padding anchor missing')

    if LOGO_OLD in text:
        text=text.replace(LOGO_OLD,LOGO_NEW,1)
    elif LOGO_NEW not in text:
        raise RuntimeError('V342 visible logo anchor missing')

    if SAFE_MARK not in text:
        text=text.rstrip()+f'\n# {SAFE_MARK} — visible logo, safe footer/Game Bar, canonical Editor route.\n'

    compile(text,str(APP),'exec')
    return text


def main():
    if not APP.is_file() or not HOME.is_file():
        raise SystemExit('V341/V342 runtime files missing')
    app_before=APP.read_text(encoding='utf-8')
    home_before=HOME.read_text(encoding='utf-8')
    app_after=patch_app(app_before)
    home_after=patch_home(home_before)
    APP.write_text(app_after,encoding='utf-8')
    HOME.write_text(home_after,encoding='utf-8')
    print('V341/V342 global shell + canonical Editor route applied app_changed=',app_before!=app_after,'home_changed=',home_before!=home_after,flush=True)

if __name__=='__main__':
    main()
