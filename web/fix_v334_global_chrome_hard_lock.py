#!/usr/bin/env python3
from pathlib import Path
import re
import sys

MARK='V334_GLOBAL_CHROME_HARD_LOCK'
ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
HOME=ROOT/'web/home_v154_component/index.html'
APP=ROOT/'GamingShortsFactory_V154_STRUCTURAL_HOME.py'
V330=ROOT/'web/fix_v330_global_chrome.py'


def logo_data():
    txt=V330.read_text(encoding='utf-8')
    m=re.search(r"LOGO_ALPHA='([^']+)'",txt)
    if not m:
        raise RuntimeError('V334 logo source missing')
    return m.group(1)


def home_block():
    return r'''
<!-- V334_GLOBAL_CHROME_HOME_SLOT -->
<style id="v334HomeChromeSlot">
@media(max-width:760px){
  /* Keep the approved Home geometry, but the visible chrome is parent-owned. */
  #home154 .topbar,
  #home154 .bottomNav,
  #home154 .siteFooter{
    visibility:hidden!important;
    opacity:0!important;
    pointer-events:none!important;
  }
  #home154 .topbar{display:flex!important;min-height:34px!important;height:34px!important;flex:0 0 34px!important}
  #home154 .bottomNav{display:grid!important;min-height:62px!important;height:62px!important;max-height:62px!important;flex:0 0 62px!important;margin:0 0 4px!important}
  #home154 .siteFooter{display:grid!important;min-height:30px!important;height:30px!important;max-height:30px!important;flex:0 0 30px!important;margin:0!important;padding:0!important}
}
</style>
'''


def shell_block(logo:str):
    return f'''
# {MARK} — one visible header, one Game Bar and one footer above every page.
if GSF_WEB_MODE:
    st.html(r"""
    <div style="display:none!important"><script>
    ((P)=>{{
      if(P.__GSF_V334_GLOBAL_CHROME_HARD_LOCK)return;
      P.__GSF_V334_GLOBAL_CHROME_HARD_LOCK=true;
      const D=P.document;
      const LOGO={logo!r};

      const css=D.createElement('style');
      css.id='gsf-v334-global-chrome-style';
      css.textContent=`
        :root{{--gsf-v334-head:44px;--gsf-v334-foot:30px;--gsf-v334-bar:62px}}
        #gsf-v330-global-brand,#gsf-v330-global-footer,#gsf-page-nav-v249,[id^="gsf-page-nav"]{{display:none!important}}
        #gsf-v334-header{{position:fixed;left:0;right:0;top:0;height:var(--gsf-v334-head);z-index:2147483647;display:flex;align-items:center;justify-content:space-between;padding:0 max(18px,env(safe-area-inset-left)) 0 max(18px,env(safe-area-inset-right));background:linear-gradient(180deg,rgba(250,253,255,.98),rgba(250,253,255,.88));-webkit-backdrop-filter:blur(16px);backdrop-filter:blur(16px);color:#6c81a1;box-sizing:border-box}}
        #gsf-v334-header .v334Brand{{display:flex;align-items:center;gap:7px;min-width:0;font:800 10px/1 "Avenir Next","SF Pro Display",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;letter-spacing:.25em;text-transform:uppercase;white-space:nowrap}}
        #gsf-v334-header .v334Mark{{display:block;width:13px;height:19px;flex:0 0 13px;background:#6c81a1;-webkit-mask-image:url("${{LOGO}}");mask-image:url("${{LOGO}}");-webkit-mask-size:contain;mask-size:contain;-webkit-mask-position:center;mask-position:center;-webkit-mask-repeat:no-repeat;mask-repeat:no-repeat}}
        #gsf-v334-header .v334Account{{height:30px;min-width:58px;display:flex;align-items:center;justify-content:center;gap:6px;padding:2px 9px 2px 4px;border:1px solid rgba(150,184,214,.28);border-radius:999px;background:rgba(255,255,255,.92);box-shadow:0 7px 19px rgba(68,104,142,.08);color:#60789c;font:800 9px/1 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}
        #gsf-v334-header .v334Avatar{{width:24px;height:24px;border-radius:50%;display:grid;place-items:center;overflow:hidden;background:linear-gradient(145deg,#e7f4ff,#e9f8f2);color:#6682a7;font-size:9px}}
        #gsf-v334-header .v334Avatar img{{width:100%;height:100%;object-fit:cover;display:block}}
        #gsf-v334-gamebar{{position:fixed;left:max(18px,env(safe-area-inset-left));right:max(18px,env(safe-area-inset-right));bottom:calc(var(--gsf-v334-foot) + env(safe-area-inset-bottom));height:var(--gsf-v334-bar);z-index:2147483647;display:grid;grid-template-columns:repeat(4,1fr);gap:3px;padding:6px 8px;border:1px solid rgba(145,181,213,.28);border-radius:999px;background:rgba(255,255,255,.95);-webkit-backdrop-filter:blur(22px);backdrop-filter:blur(22px);box-shadow:0 12px 34px rgba(59,104,148,.12),inset 0 1px 0 #fff;box-sizing:border-box}}
        #gsf-v334-gamebar button{{border:0;background:transparent;border-radius:999px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;color:#7f8fa8;font:800 7px/1 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;padding:2px;min-width:0}}
        #gsf-v334-gamebar button.active{{color:#4f93d7;background:rgba(219,241,255,.72)}}
        #gsf-v334-gamebar .v334Icon{{width:29px;height:29px;border-radius:50%;display:grid;place-items:center;background:linear-gradient(145deg,#F9FCFF,#EDF5FC);border:1px solid rgba(150,184,215,.24)}}
        #gsf-v334-gamebar button.active .v334Icon{{background:linear-gradient(145deg,#E8F5FF,#D8EBFF)}}
        #gsf-v334-gamebar svg{{width:17px;height:17px;fill:none;stroke:currentColor;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round}}
        #gsf-v334-footer{{position:fixed;left:0;right:0;bottom:0;height:var(--gsf-v334-foot);z-index:2147483647;display:grid;grid-template-columns:1fr auto 1fr;align-items:center;padding:0 max(12px,env(safe-area-inset-right)) 0 max(12px,env(safe-area-inset-left));border-top:1px solid rgba(150,184,214,.20);background:rgba(250,253,255,.96);-webkit-backdrop-filter:blur(18px);backdrop-filter:blur(18px);box-sizing:border-box;color:#6e88aa}}
        #gsf-v334-footer .v334Socials{{grid-column:2;display:flex;align-items:center;justify-content:center;gap:7px}}
        #gsf-v334-footer .v334Socials a{{width:17px;height:17px;display:grid;place-items:center;border-radius:50%;text-decoration:none;border:1px solid rgba(150,183,213,.22);background:#fff;color:#7388a7;font:900 7px/1 sans-serif;overflow:hidden}}
        #gsf-v334-footer .v334Socials svg{{width:100%;height:100%;display:block}}
        #gsf-v334-footer .v334Bug{{grid-column:3;justify-self:end;border:0;background:transparent;color:#6983a4;font:800 7px/1 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;padding:4px 0;white-space:nowrap}}
        #gsf-social-overlay-v159 .gsf-social-shell,
        #gsf-creator-hub-live-v160 .gsf-hub-shell-v160,
        #gsf-editor-overlay-v220 .gsf-editor-shell,
        #gsf-ai-overlay-v221 .gsf-ai-shell,
        #gsf-account-overlay-v223 .gsf-account-shell{{top:var(--gsf-v334-head)!important;bottom:calc(var(--gsf-v334-foot) + var(--gsf-v334-bar) + 6px + env(safe-area-inset-bottom))!important}}
        #gsf-short-overlay-v331{{padding:calc(var(--gsf-v334-head) + 4px) 8px calc(var(--gsf-v334-foot) + var(--gsf-v334-bar) + 8px + env(safe-area-inset-bottom))!important}}
        @media(min-width:761px){{#gsf-v334-header,#gsf-v334-gamebar,#gsf-v334-footer{{display:none!important}}}}
      `;
      if(!D.getElementById(css.id))D.head.appendChild(css);

      const el=(tag,id,cls='')=>{{let x=D.getElementById(id);if(x)return x;x=D.createElement(tag);x.id=id;if(cls)x.className=cls;D.body.appendChild(x);return x}};
      const header=el('header','gsf-v334-header');
      header.innerHTML=`<div class="v334Brand"><span class="v334Mark" aria-hidden="true"></span><span>GAMING SHORTS FACTORY</span></div><button class="v334Account" type="button"><span class="v334Avatar">D</span><span class="v334AccountName">Profilo</span></button>`;
      header.querySelector('.v334Account').onclick=()=>P.postMessage({{type:'GSF_SHELL_NAV',target:'hub',section:'profile'}},P.location.origin);

      const iconHome='<svg viewBox="0 0 24 24"><path d="M3 11.2 12 4l9 7.2"/><path d="M5.5 10.2V20h13v-9.8"/><path d="M9.5 20v-6h5v6"/></svg>';
      const iconHub='<svg viewBox="0 0 24 24"><rect x="4" y="4" width="6" height="6" rx="1.2"/><rect x="14" y="4" width="6" height="6" rx="1.2"/><rect x="4" y="14" width="6" height="6" rx="1.2"/><rect x="14" y="14" width="6" height="6" rx="1.2"/></svg>';
      const iconProjects='<svg viewBox="0 0 24 24"><path d="M3.5 7.5h6l1.6 2H20.5V19h-17z"/><path d="M3.5 7.5V5h6l1.4 2"/></svg>';
      const iconLive='<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="2"/><path d="M7.8 7.8a6 6 0 0 0 0 8.4M16.2 7.8a6 6 0 0 1 0 8.4M4.5 4.5a10.6 10.6 0 0 0 0 15M19.5 4.5a10.6 10.6 0 0 1 0 15"/></svg>';
      const bar=el('nav','gsf-v334-gamebar');
      bar.setAttribute('aria-label','Game Bar');
      bar.innerHTML=`<button data-page="home" class="active"><span class="v334Icon">${{iconHome}}</span><span>Home</span></button><button data-page="hub"><span class="v334Icon">${{iconHub}}</span><span>Hub</span></button><button data-page="projects"><span class="v334Icon">${{iconProjects}}</span><span>Progetti</span></button><button data-page="live"><span class="v334Icon">${{iconLive}}</span><span>Live</span></button>`;
      let current='home';
      const active=(p)=>{{current=p;bar.querySelectorAll('button').forEach(b=>b.classList.toggle('active',b.dataset.page===p))}};
      bar.querySelectorAll('button').forEach(b=>b.onclick=()=>{{const p=b.dataset.page;active(p);if(p==='home')P.postMessage({{type:'GSF_SHELL_NAV',target:'home'}},P.location.origin);else P.postMessage({{type:'GSF_SHELL_NAV',target:'hub',section:p==='hub'?'dashboard':p}},P.location.origin)}});

      const footer=el('footer','gsf-v334-footer');
      footer.setAttribute('aria-label','Footer');
      footer.innerHTML='<div class="v334Socials" aria-label="Canali social"></div><button class="v334Bug" type="button">Segnala bug</button>';
      footer.querySelector('.v334Bug').onclick=()=>{{const hit=[...D.querySelectorAll('button,a,[role="button"]')].find(x=>x!==footer.querySelector('.v334Bug')&&String(x.textContent||'').trim().toLowerCase().includes('segnala bug'));if(hit)hit.click()}};

      const homeFrame=()=>D.querySelector('iframe[title*="gsf_home_v154"],iframe[src*="home_v154"]');
      const syncSocials=()=>{{
        const dst=footer.querySelector('.v334Socials');if(!dst||dst.children.length)return;
        try{{const hd=homeFrame()?.contentDocument;const src=hd&&hd.querySelector('.footerSocial');if(src)dst.innerHTML=src.innerHTML}}catch(_e){{}}
        if(!dst.children.length)dst.innerHTML='<a aria-label="Facebook">f</a><a aria-label="Instagram">◎</a><a aria-label="YouTube">▶</a><a aria-label="TikTok">♪</a><a aria-label="Twitch">◫</a>';
      }};
      const syncAccount=()=>{{
        P.fetch('/creator-hub/state',{{cache:'no-store',credentials:'same-origin'}}).then(r=>r.json()).then(j=>{{
          const a=(j&&j.account)||{{}};const name=String(a.nickname||a.name||a.username||'Profilo');const photo=String(a.photo||a.avatar||a.image||a.picture||'');
          header.querySelector('.v334AccountName').textContent=name;
          const av=header.querySelector('.v334Avatar');
          if(photo)av.innerHTML='<img alt="" src="'+photo.replace(/"/g,'&quot;')+'">';else av.textContent=name.slice(0,1).toUpperCase()||'D';
        }}).catch(()=>{{}})
      }};
      P.addEventListener('message',e=>{{if(e.origin!==P.location.origin||!e.data||e.data.type!=='GSF_SHELL_NAV')return;const t=String(e.data.target||'');const s=String(e.data.section||'');if(t==='home'||t==='close')active('home');else if(t==='hub')active(s==='projects'?'projects':s==='live'?'live':'hub')}} ,true);
      let tries=0;const boot=()=>{{syncSocials();if(tries++<25&&!footer.querySelector('.v334Socials').children.length)P.setTimeout(boot,120)}};boot();syncAccount();
    }})(window.parent);
    </script></div>
    """,height=0)
'''


def main():
    if not HOME.is_file() or not APP.is_file():
        raise SystemExit('V334 runtime files missing')
    logo=logo_data()
    home=HOME.read_text(encoding='utf-8')
    if 'V334_GLOBAL_CHROME_HOME_SLOT' not in home:
        if '</body>' not in home:
            raise RuntimeError('V334 Home body anchor missing')
        home=home.replace('</body>',home_block()+'\n</body>',1)
        HOME.write_text(home,encoding='utf-8')
    shell=APP.read_text(encoding='utf-8')
    if MARK not in shell:
        shell=shell.rstrip()+'\n\n'+shell_block(logo)+'\n'
        compile(shell,str(APP),'exec')
        APP.write_text(shell,encoding='utf-8')
    print('V334 global chrome hard lock applied',flush=True)

if __name__=='__main__':
    main()
