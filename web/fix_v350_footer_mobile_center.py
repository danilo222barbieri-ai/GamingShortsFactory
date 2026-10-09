#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path('/app')
APP = ROOT / 'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py'
MARK = 'GSF_V350_FOOTER_MOBILE_CENTER'

BLOCK = r'''
# GSF_V350_FOOTER_MOBILE_CENTER
import streamlit.components.v1 as _gsf_components_v350
_gsf_components_v350.html(r"""
<script id="gsf-v350-footer-mobile-center">
(() => {
  const P = window.parent;
  const D = P.document;

  function ensureStyle(){
    let s = D.getElementById('gsf-v350-footer-style');
    if (s) return;
    s = D.createElement('style');
    s.id = 'gsf-v350-footer-style';
    s.textContent = `
      #gsf-global-footer{
        display:flex!important;
        align-items:center!important;
        justify-content:center!important;
        box-sizing:border-box!important;
        padding-left:12px!important;
        padding-right:12px!important;
      }
      #gsf-global-footer .gsf-v350-socials{
        position:absolute!important;
        left:50%!important;
        top:50%!important;
        transform:translate(-50%,-50%)!important;
        display:flex!important;
        align-items:center!important;
        justify-content:center!important;
        gap:10px!important;
        white-space:nowrap!important;
      }
      #gsf-global-footer .gsf-v350-socials > *{
        flex:0 0 auto!important;
        margin:0!important;
      }
      #gsf-global-footer .gsf-v350-legal{
        position:absolute!important;
        right:12px!important;
        top:50%!important;
        transform:translateY(-50%)!important;
        display:flex!important;
        align-items:center!important;
        justify-content:flex-end!important;
        gap:8px!important;
        white-space:nowrap!important;
      }
      #gsf-global-footer .gsf-v350-legal a{
        color:#6f829e!important;
        text-decoration:none!important;
        font-size:10px!important;
        line-height:1!important;
        font-weight:700!important;
        letter-spacing:.01em!important;
        opacity:.92!important;
      }
      #gsf-global-footer .gsf-v350-legal a:active{
        opacity:.58!important;
      }
      @media (max-width:430px){
        #gsf-global-footer .gsf-v350-socials{gap:8px!important;}
        #gsf-global-footer .gsf-v350-legal{right:8px!important;gap:6px!important;}
        #gsf-global-footer .gsf-v350-legal a{font-size:9px!important;}
      }
    `;
    D.head.appendChild(s);
  }

  function labelFor(el){
    return [
      el.textContent || '',
      el.getAttribute && el.getAttribute('aria-label') || '',
      el.getAttribute && el.getAttribute('title') || '',
      el.getAttribute && el.getAttribute('href') || ''
    ].join(' ').toLowerCase();
  }

  function isLegalOrBug(el){
    const v = labelFor(el);
    return /segnala|bug|privacy|term|contatt|contact/.test(v);
  }

  function isKnownSocial(el){
    const v = labelFor(el);
    return /facebook|instagram|youtube|youtu\.be|tiktok|twitch|twitter|x\.com/.test(v);
  }

  function apply(){
    ensureStyle();
    const f = D.getElementById('gsf-global-footer');
    if (!f) return;

    if (f.dataset.gsfV350 === '1') return;

    const clickable = [...f.querySelectorAll('a,button,[role="button"]')]
      .filter(el => !isLegalOrBug(el));

    let socials = clickable.filter(isKnownSocial);
    if (!socials.length) socials = clickable.slice(0, 4);

    // Keep only outermost unique clickable nodes so icon handlers/links survive.
    socials = socials.filter((el, i, arr) => !arr.some((other, j) => j !== i && other.contains(el)));

    const socialWrap = D.createElement('div');
    socialWrap.className = 'gsf-v350-socials';
    socials.forEach(el => socialWrap.appendChild(el));

    const legal = D.createElement('nav');
    legal.className = 'gsf-v350-legal';
    legal.setAttribute('aria-label', 'Informazioni legali');
    [
      ['Termini','/terms'],
      ['Privacy','/privacy'],
      ['Contatti','/contact']
    ].forEach(([label, href]) => {
      const a = D.createElement('a');
      a.textContent = label;
      a.href = href;
      a.target = '_self';
      legal.appendChild(a);
    });

    f.replaceChildren(socialWrap, legal);
    f.dataset.gsfV350 = '1';
  }

  apply();
  setTimeout(apply, 120);
  setTimeout(apply, 500);
  setTimeout(apply, 1200);
  try {
    new MutationObserver(() => {
      const f = D.getElementById('gsf-global-footer');
      if (f && f.dataset.gsfV350 !== '1') apply();
    }).observe(D.documentElement, {childList:true, subtree:true});
  } catch(_e) {}
})();
</script>
""", height=0)
'''

if not APP.is_file():
    raise SystemExit('V350 runtime app missing')
text = APP.read_text(encoding='utf-8')
if MARK in text:
    print('V350 footer mobile center already applied', flush=True)
    raise SystemExit(0)
if 'GSF_V349_FOOTER_CONTRACT' not in text:
    raise SystemExit('V350 requires V349 footer contract first')
APP.write_text(text + '\n' + BLOCK + '\n', encoding='utf-8')
print('V350 footer mobile center applied', flush=True)
