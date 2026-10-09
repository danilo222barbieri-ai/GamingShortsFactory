#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path('/app')
APP = ROOT / 'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py'
MARK = 'GSF_V355_FOOTER_BOTTOM_LOCK'

BLOCK = r'''
# GSF_V355_FOOTER_BOTTOM_LOCK
import streamlit.components.v1 as _gsf_components_v355
_gsf_components_v355.html(r"""
<script id="gsf-v355-footer-bottom-lock">
(() => {
  const D = window.parent.document;
  function lockFooter(){
    let style = D.getElementById('gsf-v355-footer-bottom-style');
    if (!style) {
      style = D.createElement('style');
      style.id = 'gsf-v355-footer-bottom-style';
      style.textContent = `
        #gsf-global-footer{
          position:fixed!important;
          left:0!important;
          right:0!important;
          bottom:0!important;
          top:auto!important;
          width:100%!important;
          z-index:9997!important;
          display:block!important;
          overflow:visible!important;
          box-sizing:border-box!important;
        }
      `;
      D.head.appendChild(style);
    }
    const footer = D.getElementById('gsf-global-footer');
    if (footer) footer.dataset.gsfV355 = '1';
  }
  lockFooter();
  setTimeout(lockFooter,80);
  setTimeout(lockFooter,300);
  setTimeout(lockFooter,900);
  setTimeout(lockFooter,1800);
  try {
    new MutationObserver(lockFooter).observe(D.documentElement,{childList:true,subtree:true});
  } catch(_e) {}
})();
</script>
""", height=0)
'''

if not APP.is_file():
    raise SystemExit('V355 runtime app missing')
text = APP.read_text(encoding='utf-8')
if MARK in text:
    print('V355 footer bottom lock already applied', flush=True)
    raise SystemExit(0)
if 'GSF_V354_FOOTER_TRUE_CENTER_SAFE_SIDES' not in text:
    raise SystemExit('V355 requires V354 footer first')
APP.write_text(text + '\n' + BLOCK + '\n', encoding='utf-8')
print('V355 footer bottom lock applied', flush=True)
