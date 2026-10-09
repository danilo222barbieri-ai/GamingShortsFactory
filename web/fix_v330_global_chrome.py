#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
HOME=ROOT/'web/home_v154_component/index.html'
APP=ROOT/'GamingShortsFactory_V154_STRUCTURAL_HOME.py'

# Same GSF mark used by V328, converted to a real alpha mask. The previous
# grayscale PNG had no alpha channel, so Safari interpreted the whole rectangle
# as the mask instead of the actual symbol.
LOGO_ALPHA='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADgAAABPCAYAAAC+oQZnAAAHhElEQVR42t2beaxdUxTGf2doqaGmqlJBJYaaKgRpa4gaIiGEJoaYEiRqViRCBE1MEfPcUEOoiJmIpNQ8+8MQCUVUVBOhxFRUeu/9/PHWblePd9+9Z3rvvuq555577t1n72+vtb+11t7rRJLEqqUJJHb9EvA08DawCFgKZP/fayUFGsDDwAmp+0FWE+A14GrgFYZvWR7QenAxMAu40u5Hdq81DCSXLVEAKAOQACcCjzgVbVodtiV24GYZuBF2b1gD8wAT4AMDGBaoWE1KbJK6yK3D1QZcAPi+mYFodVHLLMBn3fVqV1KzeXSpmpFj2F7GtIqZ+MputLpoLCOhXi5hfP8GgH/mMCdTgLOAX3tYrcNYD/Di7EZyMbDQvp81bNwZSaOBP3K2mwJcC+xrzNvowbWZAFEkaW/gHVuUrS5IJnYRx0zgcmBd1zbuNX09wlQw6lJVA7gWcAOwG/C4PStu4wm1hqAqqOhiYKLFet2ai2zsBXCkhVgT+4krh3QNCjgPuC0z4DxaELygtc2nPdec9rA2F9g6H+1mOKoZ25bAukhqSvpJ0jhJSErsM2/17XaV9JpWllckTXa/RwX76KaGZz8ku2jYIN6UNNLupSUenrjrMyX9YM9fLulOSWPt97jEZA5Uw9jvDwDlQL4oabSTSNGZjl3b8WE2rSySNCMzoKgGgA94gB7kl5IO6adBmc6QdJCkj11/8yTt1UbFawHoQUrSXElb9qN6ZdR2lKRLJS21PpZJul3SGPffuE6AMtJp2vUvki50nZZRJz9Bu0h63vX5naRTK1LbjgD7k+ZbGRYsI02vtsdIWuj6eT2jtmmdACWpZewXAN8kaT1HJHEJEgptx0q61fWzTNItkjYtqLa5AHpptuz6K0lHV6ROXhP2k/SO63OxpNMy/43qAihny0J5TtKOFattJGmmpF9dP/Ml7Z4BMFBd08byYBGAgYTC+lwq6TJJa1RgO33bbYzFQ/knw7bd1HtlDyy6Teid6U9t63G+i8WK7tB5f/hYC8eCA/89cL/tQoTwbpz5uCEiioDNLMrZrIgE25GQbNbGV2DTvBu3jqRrJf1VZIBlAXq1DST0o6RTaiChXSW9mlHb5W3qClKsCmB/JPSGpN1qsJ1nGMNmnZJaJZhV24azaddnHPgyahs52zk7M7GtwQLYnye0QNJhFTnwXhOmSfqoTZ//AxhmvtFJ7B2k1xqAhOZK2qJiB36kOfB/OJDNLMCW6i3edv4s6XynbklFJDTRnI9VpBlJajmb8hjwArAY+N3u57GTo4BngE3b7NR52/mu2c73StrOcF4SbOcxwHXAVkAzSHCJpL0rCjg/c1LrZDubku6QtGFFDnyQ6MbG4sLcrRCijLA/Ja6zPDWR9EUHgP058AslHVeR7Rxhn2MkfYOkKzI/lK2fdwmwTgc+sPTx2LZEXOHGT16AWRL6W9LlFhUU3WKMrK4fA9/1QB5M7EhmlG0ef2LHCkXOO0KuwW9xDTvMZSYqCRlKxoJjyk5cXLHkUmBkwbZBi0ZY2LUzMKfLU692xwk7V33U1SowmHDsHE5mrwIOAr52p1h57WIQ3BVpwZlp92DlNNYhjSwFvgFOMgcgdo5B3vGFPIJzgCPrOPz4LIcdDGW2pA1KOuKpM3dXhz7SHGIXsC2wnRGBX78RsJYx4DifxjGASqbAz3Z096gjmUZBlWwAO9mWxh4rcvByzs7NFUb+r0rauqTD7R2BGS6iWOE85CWZf21dhM/+qrogkkuAaZa1kXZo105qod04YC5wt+UKNH32SFpAHRJWZgbnJZIFwOnAm24HrFGCSA42lRxvwOLsuOrOiGi6SbkH2MvA+UTcvHa2ZbbyZmCegQtH5VG7vK6qi5yq/AScDTxREZFMAu6yXJ1WJxx1SLDl1sjLxmhPuBnOa9sSN2Fnm52c4tZ03Emfq06Ei42ELrA1sqgCItmEvtcbbjdz1OxW+9IKVVL2vE+BM2wrIs5kAOZNqGsARwG3Apu3I5K6Jdh0a+QeYLKBSwv6pqHd2gbsKQcuyRv9pBURyY/ADFZmDycFpRakvbtFEpMyTFwo0CwjtRR4DtjTwKUliCRIe6YRySRH/4U1LS0Ibg1gGXAZcGMF9N+0APcO4FDHxqU5osgDEuBD80g+KRHaJM69m26u1sZVSK2sij4ITDVwZYikaQeX9wJPGrimU/PKsg3z/H8dl3ZZZCc6diZlH2C2nd42OwTTgybBpZn0ySL0D3Axfa8zTBzIjxwKCeY9q8gSyQTgPguV/Ct9te5H1rkl6P3Ik4ycpjm2rT2/O6352Q0jktuAkx3bpgxSyauieYlkf7NtO9RJJIMZTaQuXJpF3zvAO9RNJIMhQX8Iub0RydTBIpK6JZi4PZJT6HvJZKp9jxjiF0XiClSyCWxkUpsDbDjYRNJJRYvYNk8k0wzchKEikm4GWoRIYuAa+k6CJgwlkXSS4FhgSReG3HskO5qTPLkXiKSTBA/vYoCx80hOp++19Mm9QiSdJPitReRL2via4d542yOZ7jySXn+fl9gi6YfMpYoyayhI5kCj/+msfH2u58EB/Afox08T1+RPSwAAAABJRU5ErkJggg=='

HOME_STYLE=f'''<style id="v330HomeChrome">
#home154{{--gsf-v330-logo:url("{LOGO_ALPHA}");--gsf-v330-footer-h:30px}}
#home154 .brandOnly:before{{content:""!important;display:inline-block!important;flex:0 0 auto!important;width:12px!important;height:17px!important;background:currentColor!important;-webkit-mask-image:var(--gsf-v330-logo)!important;mask-image:var(--gsf-v330-logo)!important;-webkit-mask-position:center!important;mask-position:center!important;-webkit-mask-size:contain!important;mask-size:contain!important;-webkit-mask-repeat:no-repeat!important;mask-repeat:no-repeat!important}}
#home154 .footerBrand{{display:none!important}}
#home154 .siteFooter{{display:grid!important;grid-template-columns:1fr auto 1fr!important;align-items:center!important;gap:7px!important;height:var(--gsf-v330-footer-h)!important;min-height:var(--gsf-v330-footer-h)!important;max-height:var(--gsf-v330-footer-h)!important;padding:1px 8px!important;margin:0!important;overflow:hidden!important;border-top:1px solid rgba(150,184,214,.20)!important}}
#home154 .footerSocial{{grid-column:2!important;justify-self:center!important;display:flex!important;align-items:center!important;gap:7px!important}}
#home154 .footLinks{{grid-column:3!important;justify-self:end!important;display:flex!important;align-items:center!important;justify-content:flex-end!important;gap:6px!important;white-space:nowrap!important}}
#home154 .footerSocialLink{{width:17px!important;height:17px!important;min-width:17px!important;min-height:17px!important;padding:3px!important}}
#home154 .bottomNav{{margin-bottom:0!important}}
@media(max-width:760px){{
 html,body{{height:100%!important;min-height:100%!important;overflow:hidden!important}}
 #home154{{height:100dvh!important;min-height:100dvh!important;max-height:100dvh!important;overflow:hidden!important;padding-bottom:7px!important}}
 #home154 .ui{{height:100%!important;min-height:0!important;overflow:hidden!important}}
 #home154 #view{{flex:1 1 auto!important;min-height:0!important;overflow:hidden!important}}
 #home154 .stage{{min-height:0!important}}
 #home154 .brandOnly:before{{width:12px!important;height:17px!important}}
 #home154 .siteFooter{{flex:0 0 var(--gsf-v330-footer-h)!important}}
 #home154 .footerSocialLink{{width:16px!important;height:16px!important;min-width:16px!important;min-height:16px!important;padding:2px!important}}
 #home154 .footLinks,#home154 .footLinks button,#home154 .footLinks span{{font-size:7px!important;line-height:1!important}}
}}
</style>'''

SHELL_BLOCK=f'''
# V330_GLOBAL_CHROME — same header/footer frame on every internal page.
if GSF_WEB_MODE:
    st.html(r"""
    <div style="display:none!important"><script>
    ((P)=>{{
      if(P.__GSF_V330_GLOBAL_CHROME)return;
      P.__GSF_V330_GLOBAL_CHROME=true;
      const D=P.document;
      const LOGO='{LOGO_ALPHA}';
      const style=D.createElement('style');
      style.id='gsf-v330-global-style';
      style.textContent=`
        :root{{--gsf-v330-footer-h:30px}}
        .gsf-v328-brand-mark{{display:none!important}}
        .gsf-v330-inline-mark,#gsf-v330-global-brand .v330Mark{{display:inline-block!important;flex:0 0 auto!important;width:12px!important;height:17px!important;background:currentColor!important;-webkit-mask-image:url("${{LOGO}}")!important;mask-image:url("${{LOGO}}")!important;-webkit-mask-position:center!important;mask-position:center!important;-webkit-mask-size:contain!important;mask-size:contain!important;-webkit-mask-repeat:no-repeat!important;mask-repeat:no-repeat!important}}
        #gsf-v330-global-brand{{position:fixed;left:max(18px,env(safe-area-inset-left));top:8px;z-index:2147483604;display:none;align-items:center;gap:6px;color:#6c81a1;font:800 11px/1 "Avenir Next","SF Pro Display",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;letter-spacing:.26em;text-transform:uppercase;white-space:nowrap;pointer-events:none}}
        #gsf-v330-global-brand.show{{display:flex!important}}
        #gsf-v330-global-footer{{position:fixed;left:0;right:0;bottom:0;z-index:2147483602;height:var(--gsf-v330-footer-h);min-height:var(--gsf-v330-footer-h);display:none;grid-template-columns:1fr auto 1fr;align-items:center;padding:1px max(10px,env(safe-area-inset-right)) 1px max(10px,env(safe-area-inset-left));background:rgba(250,253,255,.91);border-top:1px solid rgba(150,184,214,.20);-webkit-backdrop-filter:blur(18px);backdrop-filter:blur(18px);color:#6e88aa}}
        #gsf-v330-global-footer.show{{display:grid!important}}
        #gsf-v330-global-footer .v330Socials{{grid-column:2;display:flex;align-items:center;justify-content:center;gap:7px}}
        #gsf-v330-global-footer .v330Socials a{{width:17px;height:17px;min-width:17px;min-height:17px;padding:2px;display:grid;place-items:center;border-radius:50%;text-decoration:none;background:rgba(255,255,255,.90);border:1px solid rgba(150,183,213,.22);box-sizing:border-box}}
        #gsf-v330-global-footer .v330Socials svg{{width:100%;height:100%;display:block;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}}
        #gsf-v330-global-footer .v330Bug{{grid-column:3;justify-self:end;border:0;background:transparent;color:#6983a4;font:800 7px/1 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;padding:4px 0;white-space:nowrap}}
        @media(max-width:760px){{
          #gsf-page-nav-v249,[id^="gsf-page-nav"]{{position:fixed!important;left:max(18px,env(safe-area-inset-left))!important;right:max(18px,env(safe-area-inset-right))!important;bottom:calc(var(--gsf-v330-footer-h) + env(safe-area-inset-bottom))!important;margin:0!important;z-index:2147483603!important}}
        }}
      `;
      if(!D.getElementById(style.id))D.head.appendChild(style);

      const visible=(el)=>{{
        if(!el||!el.getClientRects||!el.getClientRects().length)return false;
        const s=P.getComputedStyle(el);return s.display!=='none'&&s.visibility!=='hidden'&&Number(s.opacity||1)>.02;
      }};
      const overlayOpen=()=>[...D.querySelectorAll('[id*="overlay"],[class*="overlay"]')].some(el=>{{
        if(!visible(el))return false;
        const r=el.getBoundingClientRect();
        if(r.width<120||r.height<160)return false;
        const s=P.getComputedStyle(el);
        return el.classList.contains('is-open')||el.getAttribute('aria-hidden')==='false'||s.pointerEvents!=='none';
      }});
      const footer=()=>{{
        let f=D.getElementById('gsf-v330-global-footer');if(f)return f;
        f=D.createElement('footer');f.id='gsf-v330-global-footer';f.setAttribute('aria-label','Footer');
        f.innerHTML='<div class="v330Socials" aria-label="Canali social"></div><button class="v330Bug" type="button">Segnala bug</button>';
        f.querySelector('.v330Bug').addEventListener('click',()=>{{
          const hit=[...D.querySelectorAll('button,a,[role="button"]')].find(x=>x!==f.querySelector('.v330Bug')&&String(x.textContent||'').trim().toLowerCase().includes('segnala bug'));
          if(hit)hit.click();
        }});
        D.body.appendChild(f);return f;
      }};
      const fallbackBrand=()=>{{
        let b=D.getElementById('gsf-v330-global-brand');if(b)return b;
        b=D.createElement('div');b.id='gsf-v330-global-brand';b.innerHTML='<span class="v330Mark" aria-hidden="true"></span><span>Gaming Shorts Factory</span>';D.body.appendChild(b);return b;
      }};
      const syncSocials=()=>{{
        const host=footer().querySelector('.v330Socials');if(host.children.length)return;
        for(const frame of D.querySelectorAll('iframe')){{
          try{{
            const links=[...(frame.contentDocument&&frame.contentDocument.querySelectorAll('#home154 .footerSocialLink')||[])];
            if(!links.length)continue;
            for(const src of links){{
              const a=D.createElement('a');a.href=src.href;a.target='_blank';a.rel='noopener noreferrer';a.setAttribute('aria-label',src.getAttribute('aria-label')||'Social');a.title=src.title||src.getAttribute('aria-label')||'Social';a.innerHTML=src.innerHTML;a.style.color=P.getComputedStyle(src).color;host.appendChild(a);
            }}
            break;
          }}catch(_e){{}}
        }}
      }};
      const syncExistingBrand=()=>{{
        let any=false;
        for(const el of D.querySelectorAll('header div,header span,header strong,div,span,strong')){{
          if(el.closest&&el.closest('#gsf-v330-global-brand,#gsf-v330-global-footer'))continue;
          if(el.children&&[...el.children].some(x=>!x.classList.contains('gsf-v328-brand-mark')&&!x.classList.contains('gsf-v330-inline-mark')))continue;
          const t=String(el.textContent||'').trim().replace(/\s+/g,' ').toLowerCase();
          if(t!=='gaming shorts factory')continue;
          if(!el.querySelector('.gsf-v330-inline-mark')){{const m=D.createElement('span');m.className='gsf-v330-inline-mark';m.setAttribute('aria-hidden','true');el.insertBefore(m,el.firstChild)}}
          el.style.display='inline-flex';el.style.alignItems='center';el.style.gap='6px';
          if(visible(el))any=true;
        }}
        return any;
      }};
      const syncChrome=()=>{{
        const on=overlayOpen();
        const existing=syncExistingBrand();
        const b=fallbackBrand();b.classList.toggle('show',on&&!existing);
        const f=footer();f.classList.toggle('show',on);if(on)syncSocials();
      }};
      let raf=0;const schedule=()=>{{if(raf)return;raf=P.requestAnimationFrame(()=>{{raf=0;syncChrome()}})}};
      new P.MutationObserver(schedule).observe(D.documentElement,{{subtree:true,childList:true,attributes:true,attributeFilter:['class','style','aria-hidden']}});
      P.addEventListener('resize',schedule,{{passive:true}});
      schedule();
    }})(window.parent);
    </script></div>
    """, height=0)
'''


def inject_before(text,needle,block,label):
    if needle not in text:
        raise RuntimeError('V330 anchor missing: '+label)
    return text.replace(needle,block+'\n'+needle,1)


def patch_home():
    text=HOME.read_text(encoding='utf-8');before=text
    if 'v330HomeChrome' not in text:
        text=inject_before(text,'</head>',HOME_STYLE,'home head')
    HOME.write_text(text,encoding='utf-8')
    print('V330 Home chrome applied changed=',before!=text,flush=True)


def patch_app():
    text=APP.read_text(encoding='utf-8');before=text
    if 'V330_GLOBAL_CHROME' not in text:
        text=text.rstrip()+"\n\n"+SHELL_BLOCK+"\n"
    APP.write_text(text,encoding='utf-8')
    print('V330 global shell chrome applied changed=',before!=text,flush=True)


def main():
    patch_home();patch_app()

if __name__=='__main__':
    main()
