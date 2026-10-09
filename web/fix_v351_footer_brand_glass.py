#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path('/app')
APP = ROOT / 'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py'
MARK = 'GSF_V351_FOOTER_BRAND_GLASS'

BLOCK = r'''
# GSF_V351_FOOTER_BRAND_GLASS
# GSF_V353_FOOTER_BALANCE_HIRES
# GSF_V354_FOOTER_TRUE_CENTER_SAFE_SIDES
import streamlit.components.v1 as _gsf_components_v351
_gsf_components_v351.html(r"""
<script id="gsf-v351-footer-brand-glass">
(() => {
  const P = window.parent;
  const D = P.document;

  function ensureStyle(){
    let s = D.getElementById('gsf-v351-footer-style');
    if (s) s.remove();
    s = D.createElement('style');
    s.id = 'gsf-v351-footer-style';
    s.textContent = `
      #gsf-global-footer{
        position:relative!important;
        display:block!important;
        box-sizing:border-box!important;
        padding:3px 14px!important;
        background:linear-gradient(180deg,rgba(255,255,255,.94),rgba(245,251,255,.90))!important;
        border-top:1px solid rgba(139,185,218,.20)!important;
        box-shadow:0 -8px 24px rgba(66,112,154,.05),inset 0 1px 0 rgba(255,255,255,.98)!important;
        backdrop-filter:blur(18px)!important;
        -webkit-backdrop-filter:blur(18px)!important;
        overflow:visible!important;
      }
      #gsf-global-footer .gsf-v351-brand{
        position:absolute!important;
        left:max(14px,env(safe-area-inset-left))!important;
        top:50%!important;
        transform:translateY(-50%)!important;
        z-index:2!important;
        color:#6e86a5!important;
        font-size:9px!important;
        line-height:1!important;
        font-weight:950!important;
        letter-spacing:.12em!important;
        white-space:nowrap!important;
        opacity:.94!important;
      }
      #gsf-global-footer .gsf-v351-socials{
        position:absolute!important;
        left:50%!important;
        top:50%!important;
        transform:translate(-50%,-50%)!important;
        z-index:3!important;
        display:flex!important;
        align-items:center!important;
        justify-content:center!important;
        gap:6px!important;
        white-space:nowrap!important;
      }
      #gsf-global-footer .gsf-v351-social{
        width:23px!important;
        height:23px!important;
        min-width:23px!important;
        min-height:23px!important;
        border-radius:8px!important;
        display:grid!important;
        place-items:center!important;
        overflow:hidden!important;
        border:1px solid rgba(255,255,255,.92)!important;
        box-shadow:0 2px 8px rgba(55,91,127,.10),inset 0 1px 0 rgba(255,255,255,.38)!important;
        line-height:1!important;
        user-select:none!important;
        -webkit-user-select:none!important;
      }
      #gsf-global-footer .gsf-v351-social svg{
        display:block!important;
        width:15px!important;
        height:15px!important;
        shape-rendering:geometricPrecision!important;
        text-rendering:geometricPrecision!important;
      }
      #gsf-global-footer .gsf-v351-youtube{background:#ff1744!important;color:#fff!important}
      #gsf-global-footer .gsf-v351-tiktok{background:#101820!important;color:#fff!important}
      #gsf-global-footer .gsf-v351-instagram{background:linear-gradient(145deg,#6f55d8 0%,#d84f94 49%,#f4a044 100%)!important;color:#fff!important}
      #gsf-global-footer .gsf-v351-facebook{background:#1877f2!important;color:#fff!important}
      #gsf-global-footer .gsf-v351-twitch{background:#9146ff!important;color:#fff!important}
      #gsf-global-footer .gsf-v351-legal{
        position:absolute!important;
        right:max(14px,env(safe-area-inset-right))!important;
        top:50%!important;
        transform:translateY(-50%)!important;
        z-index:2!important;
        display:flex!important;
        align-items:center!important;
        justify-content:flex-end!important;
        gap:4px!important;
        white-space:nowrap!important;
        overflow:visible!important;
      }
      #gsf-global-footer .gsf-v351-legal a{
        color:#6e86a5!important;
        text-decoration:none!important;
        font-size:7.2px!important;
        line-height:1!important;
        font-weight:820!important;
        letter-spacing:-.01em!important;
        opacity:.97!important;
      }
      #gsf-global-footer .gsf-v351-legal a:active{opacity:.55!important}
      #gsf-global-footer .gsf-v351-dot{
        width:2px!important;height:2px!important;border-radius:50%!important;background:#b5c7d7!important;display:block!important;flex:0 0 auto!important;
      }
      @media (max-width:390px){
        #gsf-global-footer{padding-left:12px!important;padding-right:12px!important}
        #gsf-global-footer .gsf-v351-brand{left:max(12px,env(safe-area-inset-left))!important;font-size:8px!important;letter-spacing:.08em!important}
        #gsf-global-footer .gsf-v351-socials{gap:5px!important}
        #gsf-global-footer .gsf-v351-social{width:22px!important;height:22px!important;min-width:22px!important;min-height:22px!important}
        #gsf-global-footer .gsf-v351-social svg{width:14px!important;height:14px!important}
        #gsf-global-footer .gsf-v351-legal{right:max(12px,env(safe-area-inset-right))!important;gap:3px!important}
        #gsf-global-footer .gsf-v351-legal a{font-size:6.65px!important}
      }
      @media (max-width:350px){
        #gsf-global-footer .gsf-v351-brand{font-size:7px!important}
        #gsf-global-footer .gsf-v351-social{width:20px!important;height:20px!important;min-width:20px!important;min-height:20px!important}
        #gsf-global-footer .gsf-v351-socials{gap:4px!important}
        #gsf-global-footer .gsf-v351-legal a{font-size:6px!important}
      }
    `;
    D.head.appendChild(s);
  }

  const SOCIAL_HTML = `
    <span class="gsf-v351-social gsf-v351-youtube" data-social="youtube" role="img" aria-label="YouTube" title="YouTube">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M19.8 7.1a2.6 2.6 0 0 0-1.8-1.8C16.4 4.9 12 4.9 12 4.9s-4.4 0-6 .4a2.6 2.6 0 0 0-1.8 1.8A27 27 0 0 0 3.8 12a27 27 0 0 0 .4 4.9A2.6 2.6 0 0 0 6 18.7c1.6.4 6 .4 6 .4s4.4 0 6-.4a2.6 2.6 0 0 0 1.8-1.8 27 27 0 0 0 .4-4.9 27 27 0 0 0-.4-4.9ZM10.3 15.1V8.9l5.4 3.1-5.4 3.1Z"/></svg>
    </span>
    <span class="gsf-v351-social gsf-v351-tiktok" data-social="tiktok" role="img" aria-label="TikTok" title="TikTok">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M15.3 3.5c.4 2.3 1.7 3.7 4.1 3.9v3.1a8.2 8.2 0 0 1-4.1-1.2v6.2a5.4 5.4 0 1 1-4.7-5.4v3.1a2.3 2.3 0 1 0 1.5 2.2V3.5h3.2Z"/></svg>
    </span>
    <span class="gsf-v351-social gsf-v351-instagram" data-social="instagram" role="img" aria-label="Instagram" title="Instagram">
      <svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4.4" y="4.4" width="15.2" height="15.2" rx="4.2" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="3.5" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="17.4" cy="6.8" r="1.05" fill="currentColor"/></svg>
    </span>
    <span class="gsf-v351-social gsf-v351-facebook" data-social="facebook" role="img" aria-label="Facebook" title="Facebook">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M13.8 20v-7h2.4l.4-2.8h-2.8V8.4c0-.8.2-1.4 1.4-1.4h1.5V4.5c-.3 0-1.2-.1-2.3-.1-2.3 0-3.8 1.4-3.8 4v1.8H8V13h2.6v7h3.2Z"/></svg>
    </span>
    <span class="gsf-v351-social gsf-v351-twitch" data-social="twitch" role="img" aria-label="Twitch" title="Twitch">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M5 3h16v10.8l-4.5 4.5h-3.3L11 20.5H8.8v-2.2H5V3Zm2.2 2.2v10.9h3.7v2l2-2h3l2.9-2.9v-8H7.2Zm4 2h2v5h-2v-5Zm4.2 0h2v5h-2v-5Z"/></svg>
    </span>
  `;

  function build(){
    ensureStyle();
    const f = D.getElementById('gsf-global-footer');
    if (!f) return;

    const brand = D.createElement('div');
    brand.className = 'gsf-v351-brand gsf-v351-footer-shell';
    brand.innerHTML = '<span>GSF</span>';

    const socials = D.createElement('div');
    socials.className = 'gsf-v351-socials';
    socials.setAttribute('aria-label','Social Gaming Shorts Factory');
    socials.innerHTML = SOCIAL_HTML;

    const legal = D.createElement('nav');
    legal.className = 'gsf-v351-legal';
    legal.setAttribute('aria-label','Informazioni legali');
    [
      ['Termini','/terms'],
      ['Privacy','/privacy'],
      ['Contatti','/contact']
    ].forEach(([label, href], idx, all) => {
      const a = D.createElement('a');
      a.textContent = label;
      a.href = href;
      a.target = '_self';
      legal.appendChild(a);
      if (idx < all.length - 1) {
        const dot = D.createElement('span');
        dot.className = 'gsf-v351-dot';
        dot.setAttribute('aria-hidden','true');
        legal.appendChild(dot);
      }
    });

    f.replaceChildren(brand, socials, legal);
    f.dataset.gsfV351 = '1';
    f.dataset.gsfV353 = '1';
    f.dataset.gsfV354 = '1';
  }

  build();
  setTimeout(build, 80);
  setTimeout(build, 300);
  setTimeout(build, 900);
  setTimeout(build, 1800);
  try {
    new MutationObserver(() => {
      const f = D.getElementById('gsf-global-footer');
      if (!f || f.dataset.gsfV354 !== '1' || !f.querySelector('.gsf-v351-socials')) build();
    }).observe(D.documentElement,{childList:true,subtree:true});
  } catch(_e) {}
})();
</script>
""", height=0)
'''

if not APP.is_file():
    raise SystemExit('V351 runtime app missing')
text = APP.read_text(encoding='utf-8')
if MARK in text:
    print('V351 footer brand glass already applied', flush=True)
    raise SystemExit(0)
if 'GSF_V350_FOOTER_MOBILE_CENTER' not in text:
    raise SystemExit('V351 requires V350 footer patch first')
APP.write_text(text + '\n' + BLOCK + '\n', encoding='utf-8')
print('V351/V354 true-centered safe-area footer applied', flush=True)
