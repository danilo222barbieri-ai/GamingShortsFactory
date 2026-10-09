#!/usr/bin/env python3
from pathlib import Path
import ast
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path('/app')
APP = ROOT / 'GamingShortsFactory_V154_STRUCTURAL_HOME.py'
MARKER = 'GSF_V348_TRANSPARENT_LOGO_FOOTER'
# Vectorized directly from the user-approved GSF symbol; the SVG has no background.
LOGO_SVG_B64 = 'PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA0MTcgNDE3Ij48cGF0aCBmaWxsPSIjMjEzYzUxIiBkPSJNIDIwNiwxMjQgMjg2LDE3MCAzMjAsMTY5IDMyMCwxMjQgWiBNIDMyMCw1NCAxMzcsNTQgMTE4LDYxIDEwMiw3NyA5Nyw4OSA5NiwxMDcgMTAxLDEyMiAxMTMsMTM2IDI2MCwyMjMgMTQ0LDMwMiAxNDMsMjQ2IDE4MywyNDUgMTgzLDIwMSAxMTcsMjAwIDEwNiwyMDQgOTksMjExIDk2LDIxOCA5NiwzMjAgMTQzLDM2MiAzMjAsMjM4IDMyMCwyMDYgMTQzLDEwMCAzMTksOTkgWiIvPjwvc3ZnPg=='

if not APP.is_file():
    raise SystemExit('V348 source shell missing')


def call_name(node):
    fn = node.func
    if isinstance(fn, ast.Attribute) and isinstance(fn.value, ast.Name):
        return f'{fn.value.id}.{fn.attr}'
    return ''


def find_v343_bridge(source):
    tree = ast.parse(source)
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not node.args:
            continue
        if call_name(node) != '_gsf_components_v343.html':
            continue
        arg = node.args[0]
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str) and 'GSF_GLOBAL_SHELL_V343' in arg.value:
            found.append((arg.value, ast.get_source_segment(source, arg)))
    if len(found) != 1:
        raise RuntimeError(f'V348 expected exactly one V343 executable bridge, found {len(found)}')
    return found[0]


def inject_addon(bridge):
    if MARKER in bridge:
        return bridge, False

    logo = 'data:image/svg+xml;base64,' + LOGO_SVG_B64
    addon = r'''
<!-- __MARKER__ -->
<script>
(function(){
  const P=window.parent.document;
  const LOGO='__LOGO__';
  const STYLE_ID='gsf-v348-brand-footer-style';

  function ensureStyle(){
    let style=P.getElementById(STYLE_ID);
    if(!style){
      style=P.createElement('style');
      style.id=STYLE_ID;
      (P.head||P.documentElement).appendChild(style);
    }
    style.textContent=`
      :root{--gsf-v348-footer-space:34px;}
      #gsf-global-logo-v348{
        width:30px!important;height:30px!important;
        object-fit:contain!important;object-position:center!important;
        background:transparent!important;border:0!important;border-radius:0!important;
        box-shadow:none!important;outline:0!important;padding:0!important;
        margin:0 8px 0 0!important;flex:0 0 30px!important;
      }
      #gsf-global-logo-v348-parent{
        background:transparent!important;border:0!important;box-shadow:none!important;
      }
      #gsf-global-footer{
        display:flex!important;visibility:visible!important;opacity:1!important;
        position:fixed!important;left:0!important;right:0!important;bottom:0!important;
        width:100%!important;
        min-height:calc(var(--gsf-v348-footer-space) + env(safe-area-inset-bottom,0px))!important;
        height:auto!important;box-sizing:border-box!important;transform:none!important;
        pointer-events:auto!important;z-index:2147483000!important;
      }
      #gsf-global-footer>*{visibility:visible!important;opacity:1!important;}
      #gsf-global-gamebar{
        bottom:calc(var(--gsf-v348-footer-space) + env(safe-area-inset-bottom,0px) + 8px)!important;
        z-index:2147483001!important;
      }
      @media (max-width:720px){
        :root{--gsf-v348-footer-space:32px;}
        #gsf-global-logo-v348{
          width:28px!important;height:28px!important;flex-basis:28px!important;margin-right:7px!important;
        }
      }
    `;
  }

  function findBrandLogo(header){
    let oldLogo=header.querySelector('img[src^="data:image/svg+xml"]');
    if(oldLogo)return oldLogo;
    oldLogo=header.querySelector('img[id*="logo" i],img[class*="logo" i]');
    if(oldLogo)return oldLogo;
    const box=header.getBoundingClientRect();
    return Array.from(header.querySelectorAll('img')).find((img)=>{
      const r=img.getBoundingClientRect();
      return r.width>0 && r.width<=60 && r.left<box.left+110;
    })||null;
  }

  function apply(){
    ensureStyle();
    const header=P.getElementById('gsf-global-header');
    if(header){
      const oldLogo=findBrandLogo(header);
      if(oldLogo){
        oldLogo.src=LOGO;
        oldLogo.id='gsf-global-logo-v348';
        oldLogo.alt='Gaming Shorts Factory';
        oldLogo.decoding='async';
        oldLogo.style.setProperty('background','transparent','important');
        oldLogo.style.setProperty('border','0','important');
        oldLogo.style.setProperty('box-shadow','none','important');
        oldLogo.style.setProperty('border-radius','0','important');
        oldLogo.style.setProperty('padding','0','important');
        if(oldLogo.parentElement){
          oldLogo.parentElement.id='gsf-global-logo-v348-parent';
          oldLogo.parentElement.style.setProperty('background','transparent','important');
          oldLogo.parentElement.style.setProperty('border','0','important');
          oldLogo.parentElement.style.setProperty('box-shadow','none','important');
        }
      }
    }

    const footer=P.getElementById('gsf-global-footer');
    if(footer){
      footer.hidden=false;
      footer.removeAttribute('aria-hidden');
      footer.style.setProperty('display','flex','important');
      footer.style.setProperty('visibility','visible','important');
      footer.style.setProperty('opacity','1','important');
      footer.style.setProperty('position','fixed','important');
      footer.style.setProperty('left','0','important');
      footer.style.setProperty('right','0','important');
      footer.style.setProperty('bottom','0','important');
      footer.style.setProperty('transform','none','important');
      footer.style.setProperty('z-index','2147483000','important');
    }

    const gamebar=P.getElementById('gsf-global-gamebar');
    if(gamebar){
      gamebar.style.setProperty('bottom','calc(var(--gsf-v348-footer-space) + env(safe-area-inset-bottom,0px) + 8px)','important');
    }
  }

  apply();
  let queued=false;
  const observer=new MutationObserver(()=>{
    if(queued)return;
    queued=true;
    requestAnimationFrame(()=>{queued=false;apply();});
  });
  observer.observe(P.documentElement,{childList:true,subtree:true});
  setTimeout(apply,120);setTimeout(apply,600);setTimeout(apply,1500);
})();
</script>
'''.replace('__MARKER__', MARKER).replace('__LOGO__', logo)

    lower = bridge.lower()
    idx = lower.rfind('</body>')
    if idx < 0:
        idx = lower.rfind('</html>')
    if idx < 0:
        return bridge + addon, True
    return bridge[:idx] + addon + bridge[idx:], True


source = APP.read_text(encoding='utf-8')
bridge, literal = find_v343_bridge(source)
new_bridge, changed = inject_addon(bridge)

if not changed:
    print('V348 transparent logo/footer already applied', flush=True)
    raise SystemExit(0)
if not literal:
    raise RuntimeError('V348 could not recover V343 bridge source literal')
if source.count(literal) != 1:
    raise RuntimeError(f'V348 bridge literal count={source.count(literal)}')

updated = source.replace(literal, repr(new_bridge), 1)
compile(updated, str(APP), 'exec')
APP.write_text(updated, encoding='utf-8')
print('V348 transparent logo + fixed footer applied', flush=True)
