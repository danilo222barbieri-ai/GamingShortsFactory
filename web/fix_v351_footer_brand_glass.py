#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path('/app')
APP = ROOT / 'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py'
MARK = 'GSF_V351_FOOTER_BRAND_GLASS'

BLOCK = r'''
# GSF_V351_FOOTER_BRAND_GLASS
import streamlit.components.v1 as _gsf_components_v351
_gsf_components_v351.html(r"""
<script id="gsf-v351-footer-brand-glass">
(() => {
  const P = window.parent;
  const D = P.document;

  function ensureStyle(){
    let s = D.getElementById('gsf-v351-footer-style');
    if (s) return;
    s = D.createElement('style');
    s.id = 'gsf-v351-footer-style';
    s.textContent = `
      #gsf-global-footer{
        display:grid!important;
        grid-template-columns:minmax(0,1fr) auto minmax(0,1fr)!important;
        align-items:center!important;
        box-sizing:border-box!important;
        padding:3px 10px!important;
        background:linear-gradient(180deg,rgba(255,255,255,.92),rgba(245,251,255,.88))!important;
        border-top:1px solid rgba(139,185,218,.22)!important;
        box-shadow:0 -8px 24px rgba(66,112,154,.055),inset 0 1px 0 rgba(255,255,255,.96)!important;
        backdrop-filter:blur(18px)!important;
        -webkit-backdrop-filter:blur(18px)!important;
        overflow:visible!important;
      }
      #gsf-global-footer .gsf-v351-spacer{
        grid-column:1!important;
        min-width:0!important;
        pointer-events:none!important;
      }
      #gsf-global-footer .gsf-v351-socials{
        grid-column:2!important;
        justify-self:center!important;
        display:flex!important;
        align-items:center!important;
        justify-content:center!important;
        gap:5px!important;
        white-space:nowrap!important;
      }
      #gsf-global-footer .gsf-v351-social{
        width:21px!important;
        height:21px!important;
        min-width:21px!important;
        min-height:21px!important;
        border-radius:8px!important;
        display:grid!important;
        place-items:center!important;
        overflow:hidden!important;
        border:1px solid rgba(255,255,255,.90)!important;
        box-shadow:0 2px 7px rgba(55,91,127,.09),inset 0 1px 0 rgba(255,255,255,.36)!important;
        line-height:1!important;
        user-select:none!important;
        -webkit-user-select:none!important;
      }
      #gsf-global-footer .gsf-v351-social svg{
        display:block!important;
        width:13px!important;
        height:13px!important;
      }
      #gsf-global-footer .gsf-v351-youtube{background:#ff1744!important;color:#fff!important}
      #gsf-global-footer .gsf-v351-tiktok{background:#111820!important;color:#fff!important;font-size:14px!important;font-weight:900!important}
      #gsf-global-footer .gsf-v351-instagram{background:linear-gradient(145deg,#7b55d8 0%,#d84f94 48%,#f4a044 100%)!important;color:#fff!important}
      #gsf-global-footer .gsf-v351-facebook{background:#1877f2!important;color:#fff!important;font-size:15px!important;font-weight:950!important;font-family:Arial,sans-serif!important}
      #gsf-global-footer .gsf-v351-twitch{background:#9146ff!important;color:#fff!important;font-size:12px!important;font-weight:950!important}
      #gsf-global-footer .gsf-v351-legal{
        grid-column:3!important;
        justify-self:end!important;
        min-width:0!important;
        display:flex!important;
        align-items:center!important;
        justify-content:flex-end!important;
        gap:5px!important;
        white-space:nowrap!important;
      }
      #gsf-global-footer .gsf-v351-legal a{
        color:#6e86a5!important;
        text-decoration:none!important;
        font-size:7.8px!important;
        line-height:1!important;
        font-weight:820!important;
        letter-spacing:.005em!important;
        opacity:.95!important;
      }
      #gsf-global-footer .gsf-v351-legal a:active{opacity:.55!important}
      #gsf-global-footer .gsf-v351-legal .gsf-v351-dot{
        width:2px!important;height:2px!important;border-radius:50%!important;background:#b5c7d7!important;display:block!important;flex:0 0 auto!important;
      }
      @media (max-width:390px){
        #gsf-global-footer{padding-left:7px!important;padding-right:7px!important}
        #gsf-global-footer .gsf-v351-socials{gap:4px!important}
        #gsf-global-footer .gsf-v351-social{width:20px!important;height:20px!important;min-width:20px!important;min-height:20px!important;border-radius:7px!important}
        #gsf-global-footer .gsf-v351-social svg{width:12px!important;height:12px!important}
        #gsf-global-footer .gsf-v351-legal{gap:3px!important}
        #gsf-global-footer .gsf-v351-legal a{font-size:7.1px!important;letter-spacing:-.01em!important}
      }
      @media (max-width:350px){
        #gsf-global-footer .gsf-v351-social{width:18px!important;height:18px!important;min-width:18px!important;min-height:18px!important}
        #gsf-global-footer .gsf-v351-socials{gap:3px!important}
        #gsf-global-footer .gsf-v351-legal a{font-size:6.7px!important}
      }
    `;
    D.head.appendChild(s);
  }

  const SOCIAL_HTML = `
    <span class="gsf-v351-social gsf-v351-youtube" data-social="youtube" role="img" aria-label="YouTube" title="YouTube">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M9.4 7.8 17 12l-7.6 4.2V7.8Z"/></svg>
    </span>
    <span class="gsf-v351-social gsf-v351-tiktok" data-social="tiktok" role="img" aria-label="TikTok" title="TikTok">♪</span>
    <span class="gsf-v351-social gsf-v351-instagram" data-social="instagram" role="img" aria-label="Instagram" title="Instagram">
      <svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4.5" y="4.5" width="15" height="15" rx="4" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="3.4" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="17.2" cy="6.9" r="1" fill="currentColor"/></svg>
    </span>
    <span class="gsf-v351-social gsf-v351-facebook" data-social="facebook" role="img" aria-label="Facebook" title="Facebook">f</span>
    <span class="gsf-v351-social gsf-v351-twitch" data-social="twitch" role="img" aria-label="Twitch" title="Twitch">◧</span>
  `;

  function build(){
    ensureStyle();
    const f = D.getElementById('gsf-global-footer');
    if (!f) return;
    if (f.dataset.gsfV351 === '1' && f.querySelector('.gsf-v351-footer-shell')) return;

    const spacer = D.createElement('div');
    spacer.className = 'gsf-v351-spacer gsf-v351-footer-shell';

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

    f.replaceChildren(spacer, socials, legal);
    f.dataset.gsfV351 = '1';
  }

  build();
  setTimeout(build, 80);
  setTimeout(build, 300);
  setTimeout(build, 900);
  setTimeout(build, 1800);
  try {
    new MutationObserver(() => {
      const f = D.getElementById('gsf-global-footer');
      if (!f || f.dataset.gsfV351 !== '1' || !f.querySelector('.gsf-v351-socials')) build();
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
print('V351 footer brand glass applied', flush=True)
