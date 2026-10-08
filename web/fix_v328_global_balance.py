#!/usr/bin/env python3
from pathlib import Path
import re
import sys

ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
HOME=ROOT/'web/home_v154_component/index.html'
HUB=ROOT/'web/creator_hub_v156_component/index.html'
APP=ROOT/'GamingShortsFactory_V154_STRUCTURAL_HOME.py'

LOGO_DATA='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADgAAABPCAAAAACbylm7AAAEqklEQVR42p2YbWhWZRjH//eLPcsxK5sWTKv1srYQVl8ql1lTE6SyRhAxRM2GSMky6EUrmhVS0FhomIL5IYrQ6A36EBWLUhpClgYjaVFtMPai9vJstbWd+77/fdiz5znnPudsz7P723k4v3Nd539d53/d9wMAUMDag90jjkWugBugASFs43OrUdKaBw0hXNtu0ElRAkhoIe07GyyUKi0kpLRtGwJZKgZIe0ub0QKlg6pdiDlwkLeuoMJcwPvh5sJBNyKfKG2RkAGhayCnr4UuNhoy0BXTV0527b+kuLyd7ATyDejsYHMJ7yiyC0JXXbuOKV3Mm1riuLP5mIbmtQpIWVTIJ2kK34tx/OVBQAsAcqYlgKoR5yKfGj+qA2bvCYG9rSZcBkf1b9u+QNvaBSNSMgXrG4VcNBhOlqQhT90JrOoiUzzBcSOgcPsEg+jvhm7/5dCPDtOaZOt4GIDCuixN9NnWsX8jsPQAGbgkcPOUVdV8Ri8oA/KLG4G1J0iTBkIBzb10xs93bE85MtvPsVBpD4SUWNhu/awM+eO9wBVvxfLNg4ACVnT5WbmAPFIN3HHCe5MQCKGhnvibNpqVtRxu1cg8PhDJNwwCSuC6o0zI9+sGoOoQQ8pHQUAD67sT8nUdFwOrT5JBbo2bTb7lofzl//yiGseeZqBs+7nCby3wnFFZ1LevgY02udE48tIZLN1SQTk0IsiBHwZiTa+Bln6/dNZwdOf82QxTYPHhJJFONQJlWmuttRIpJoaV3ycV9c2qWexBKGSeytJYv/OHt+bsIXUp4PpPY51vyM6bCvYglIrGF2JKpOa+hM6f2FOBqftF6hzDpa+7WFHJn9YDCkJQPnTPkosY4sebBgWnitrQvtwrKq3G0Z29Cqg8HvtQl+XmidCQj/0R63zDsyuB8hOcNMaGl6nNDyIlUP1erKiTPHc1dnMyFrGuMMGSOz/gu+i1bkYQUuHCF8ejTuncX0iyvwg4VdRPfONJ9GqvQnYees/7IzIpYnBtJKIUWNNDG+2+00mgrQmDGup5TxwXsAmRAhljjAlM6B2FwjXfepW0jvuQKM6yQh2BrX96vR5w8lmowoSj6Pl5nhPg2PgQcpJpU7m3GTY8Bul095bvpEXoQTviXtD4q9flhjxQAQ2EwWdURimlVM4YNNQr3ifpAg425z7IEPg0dMQFar/xTMs6fl6F3HNTQAVsy8ZUmdiB/D2JoNBY/L5fPMPTDSGzSgIlcFdfXJU35offJQHUyHTEVRlqiu5iYqCQqO/ye4X8cAmiNuyDCtg2FlPln9bYpikKCo3LPvZUsZYn66F8C4+AGeC+Ps9hDNlxAeJ74DCoUNYeL8LvdwMJEyMS8eZTniqG/GBR8rgIg5uDmCrZlrStZOi2UV8Vx2N1SJmF8O6MhHOvKqSeDCK7yagqv62CSJ+jKYdSQ75dOeMQTTvMZjfNssFOwqzjVzekqpIOBrQvCMx2XopvuAOeuW0mVVJAQx5eiCKOZ7E0zz9SzLEDcJ4qndWzqZIQMaDZJVDkKXI4f0Jyht3Li1Altw5NN7YlD5YXGw7AVWenetSx/4HiVJle67LWkdZ9eSVK+SPhf/T/fMrHTSI9AAAAAElFTkSuQmCC'

HOME_STYLE='''<style id="v328HomeBalance">
#home154 .brandOnly{display:inline-flex!important;align-items:center!important;gap:7px!important}
#home154 .brandOnly:before{content:"";display:inline-block;flex:0 0 auto;width:17px;height:24px;background:currentColor;-webkit-mask:url("__LOGO__") center/contain no-repeat;mask:url("__LOGO__") center/contain no-repeat}
#home154 .footerBrand{display:none!important}
#home154 .siteFooter{height:28px!important;min-height:28px!important;max-height:28px!important;padding:2px 8px 1px!important;margin:0!important;display:flex!important;align-items:center!important;justify-content:center!important;gap:10px!important;overflow:hidden!important}
#home154 .footerSocial{display:flex!important;align-items:center!important;justify-content:center!important;gap:8px!important}
#home154 .footerSocialLink{width:17px!important;height:17px!important;min-width:17px!important;min-height:17px!important}
#home154 .footLinks{font-size:7px!important;gap:8px!important}
#home154 .bottomNav{margin-bottom:0!important}
@media(max-width:760px){
 #home154 .brandOnly{gap:5px!important}
 #home154 .brandOnly:before{width:12px;height:17px}
 #home154 .siteFooter{height:28px!important;min-height:28px!important;max-height:28px!important;padding:1px 6px!important}
 #home154 .footerSocialLink{width:15px!important;height:15px!important;min-width:15px!important;min-height:15px!important}
}
</style>'''.replace('__LOGO__',LOGO_DATA)

HUB_STYLE='''<style id="v328LiveCompact">
@media(max-width:760px){
 #hub .folderScroller:has(.livePlatformCard){display:block!important;height:100%!important;min-height:0!important;overflow-y:auto!important;overflow-x:hidden!important;padding:0 2px 104px!important;overscroll-behavior:contain!important;-webkit-overflow-scrolling:touch!important}
 #hub .hubLiveGuide{height:auto!important;min-height:28px!important;margin:0 0 6px!important;padding:4px 8px!important;font-size:10px!important;line-height:1.2!important}
 #hub .livePlatformCard{height:auto!important;min-height:0!important;max-height:none!important;margin:0 0 8px!important;padding:9px!important;border-radius:19px!important;display:grid!important;grid-template-rows:38px auto!important;gap:6px!important}
 #hub .livePlatformHead{min-height:38px!important;height:38px!important;padding:0 2px!important}
 #hub .livePlatformHead h2{font-size:19px!important;line-height:1!important}
 #hub .livePlatformHead p{font-size:8.5px!important;line-height:1.15!important;margin-top:2px!important}
 #hub .liveMiniFolders{display:grid!important;grid-template-rows:repeat(3,74px)!important;gap:6px!important;height:auto!important;min-height:0!important}
 #hub .liveMiniFolder{height:74px!important;min-height:74px!important;max-height:74px!important;padding:8px 10px!important;border-radius:16px!important}
 #hub .liveMiniFolder h3{font-size:14px!important;line-height:1.05!important;margin:0!important}
 #hub .liveMiniFolder p{font-size:8.5px!important;line-height:1.15!important;margin-top:2px!important}
 #hub .liveMiniFolder .folderIcon{width:34px!important;height:34px!important;min-width:34px!important;border-radius:11px!important}
}
</style>'''

SHELL_BLOCK='''
# V328_GLOBAL_BALANCE — stable mobile footer/nav, brand mark and reliable Short bridge.
if GSF_WEB_MODE:
    st.html(r"""
    <div style="display:none!important"><script>
    ((P)=>{
      if(P.__GSF_V328_GLOBAL_BALANCE)return;
      P.__GSF_V328_GLOBAL_BALANCE=true;
      const D=P.document;
      const LOGO='__LOGO__';
      const style=D.createElement('style');
      style.id='gsf-v328-global-style';
      style.textContent=`
        :root{--gsf-v328-footer-h:28px}
        .gsf-v328-brand-host{display:inline-flex!important;align-items:center!important;gap:6px!important}
        .gsf-v328-brand-mark{display:inline-block!important;flex:0 0 auto!important;width:14px!important;height:20px!important;background:currentColor!important;-webkit-mask:url("${LOGO}") center/contain no-repeat!important;mask:url("${LOGO}") center/contain no-repeat!important}
        #gsf-v328-global-footer{position:fixed;left:0;right:0;bottom:0;height:var(--gsf-v328-footer-h);min-height:var(--gsf-v328-footer-h);z-index:2147483000;display:none;align-items:center;justify-content:center;background:rgba(250,253,255,.88);border-top:1px solid rgba(150,184,214,.18);-webkit-backdrop-filter:blur(18px);backdrop-filter:blur(18px);pointer-events:auto}
        #gsf-v328-global-footer.show{display:flex}
        #gsf-v328-global-footer .v328Socials{display:flex;align-items:center;gap:10px}
        #gsf-v328-global-footer a{width:17px;height:17px;display:grid;place-items:center;border-radius:50%;text-decoration:none;color:#6e88aa;font:800 9px/1 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:rgba(239,247,253,.92)}
        @media(max-width:760px){
          .gsf-v328-brand-mark{width:12px!important;height:17px!important}
          #gsf-v328-global-footer{height:28px;min-height:28px}
          #gsf-page-nav-v249,[id^="gsf-page-nav"]{position:fixed!important;left:max(18px,env(safe-area-inset-left))!important;right:max(18px,env(safe-area-inset-right))!important;bottom:calc(var(--gsf-v328-footer-h) + env(safe-area-inset-bottom))!important;margin:0!important;z-index:2147483001!important}
        }
      `;
      if(!D.getElementById(style.id))D.head.appendChild(style);

      const footer=()=>{
        let f=D.getElementById('gsf-v328-global-footer');
        if(f)return f;
        f=D.createElement('footer');f.id='gsf-v328-global-footer';f.setAttribute('aria-label','Footer');
        f.innerHTML='<div class="v328Socials"><a href="https://www.facebook.com/profile.php?id=61595124112318&locale=it_IT" target="_blank" rel="noopener noreferrer" aria-label="Facebook">f</a><a href="https://www.instagram.com/gamingshortsfactory/" target="_blank" rel="noopener noreferrer" aria-label="Instagram">◎</a><a href="https://www.youtube.com/@Dans222nrg" target="_blank" rel="noopener noreferrer" aria-label="YouTube">▶</a></div>';
        D.body.appendChild(f);return f;
      };
      const visible=(el)=>!!(el&&el.getClientRects&&el.getClientRects().length&&P.getComputedStyle(el).visibility!=='hidden'&&P.getComputedStyle(el).display!=='none');
      const syncFooter=()=>{
        const f=footer();
        const nav=D.querySelector('#gsf-page-nav-v249,[id^="gsf-page-nav"]');
        const on=P.matchMedia('(max-width:760px)').matches&&visible(nav);
        f.classList.toggle('show',!!on);
      };
      const syncBrand=()=>{
        const nodes=[...D.querySelectorAll('header div,header span,header strong,div,span,strong')];
        for(const el of nodes){
          if(el.closest&&el.closest('#gsf-v328-global-footer'))continue;
          if(el.querySelector&&el.querySelector('.gsf-v328-brand-mark'))continue;
          if(el.children&&el.children.length)continue;
          const t=String(el.textContent||'').trim().replace(/\s+/g,' ').toLowerCase();
          if(t!=='gaming shorts factory')continue;
          const mark=D.createElement('span');mark.className='gsf-v328-brand-mark';mark.setAttribute('aria-hidden','true');
          el.classList.add('gsf-v328-brand-host');el.insertBefore(mark,el.firstChild);
        }
      };
      const v328TriggerShort=(attempt=0)=>{
        let target=D.querySelector('.st-key-gsf-major-create-short button,.st-key-create_final_short_v54 button');
        if(!target){
          const nodes=[...D.querySelectorAll('button,a,[role="button"]')];
          target=nodes.find(x=>{const t=String(x.innerText||x.textContent||'').trim().toLowerCase();return t.includes('crea short finale')||t==='crea short'||t.includes('crea il tuo short')});
        }
        if(target){target.click();return true}
        if(attempt<8){P.setTimeout(()=>v328TriggerShort(attempt+1),90+attempt*45)}
        return false;
      };
      P.addEventListener('message',(e)=>{
        if(e.origin!==P.location.origin||!e.data||e.data.type!=='GSF_SHELL_NAV')return;
        const target=String(e.data.target||'');
        if(target==='short')v328TriggerShort();
      },true);
      let raf=0;const sync=()=>{if(raf)return;raf=P.requestAnimationFrame(()=>{raf=0;syncBrand();syncFooter()})};
      new P.MutationObserver(sync).observe(D.documentElement,{subtree:true,childList:true,attributes:true,attributeFilter:['class','style','aria-hidden']});
      P.addEventListener('resize',sync,{passive:true});
      sync();
    })(window.parent);
    </script></div>
    """, height=0)
'''.replace('__LOGO__',LOGO_DATA)


def append_before(text,needle,block,label):
    if needle not in text: raise RuntimeError('V328 anchor missing: '+label)
    return text.replace(needle,block+'\n'+needle,1)


def patch_home():
    text=HOME.read_text(encoding='utf-8');before=text
    text=re.sub(r'\s*<span class="footerBrand">Gaming Shorts Factory</span>\s*','\n',text,count=1)
    if 'v328HomeBalance' not in text:
        text=append_before(text,'</head>',HOME_STYLE,'Home head')
    old='if(action==="short"){parentClick(["crea short","crea short finale","crea il tuo short"]);value({event:"create_short",duration,engine});}'
    new='if(action==="short"){const opened=parentClick(["crea short","crea short finale","crea il tuo short"]);if(!opened)shellNav("short");value({event:"create_short",duration,engine});}'
    if old in text:text=text.replace(old,new,1)
    elif 'if(!opened)shellNav("short")' not in text: raise RuntimeError('V328 Home Short action anchor missing')
    HOME.write_text(text,encoding='utf-8')
    print('V328 Home balance applied changed=',before!=text,flush=True)


def patch_hub():
    text=HUB.read_text(encoding='utf-8');before=text
    if 'v328LiveCompact' not in text:
        text=append_before(text,'</head>',HUB_STYLE,'Hub head')
    HUB.write_text(text,encoding='utf-8')
    print('V328 Live compact applied changed=',before!=text,flush=True)


def patch_shell():
    text=APP.read_text(encoding='utf-8');before=text
    if 'V328_GLOBAL_BALANCE' not in text:
        text=text.rstrip()+'\n\n'+SHELL_BLOCK+'\n'
    compile(text,str(APP),'exec')
    APP.write_text(text,encoding='utf-8')
    print('V328 global shell balance applied changed=',before!=text,flush=True)


def main():
    for p in (HOME,HUB,APP):
        if not p.is_file(): raise RuntimeError('V328 required file missing: '+str(p))
    patch_home();patch_hub();patch_shell()

if __name__=='__main__':main()
