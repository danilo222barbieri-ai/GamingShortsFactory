#!/usr/bin/env python3
from pathlib import Path
import ast
import sys

MARK = 'GSF_SINGLE_ACTIVE_SURFACE_V367'

ARBITER = r'''
<!-- GSF_SINGLE_ACTIVE_SURFACE_V367 -->
<script id="gsfSingleActiveSurfaceV367">
((P)=>{
  if(P.__GSF_SINGLE_ACTIVE_SURFACE_V367)return;
  P.__GSF_SINGLE_ACTIVE_SURFACE_V367=true;
  const D=P.document;
  const SURFACES=[
    'gsf-editor-overlay-v220',
    'gsf-short-overlay-v343',
    'gsf-creator-hub-live-v160',
    'gsf-ai-overlay-v221',
    'gsf-social-overlay-v159',
    'gsf-account-overlay-v223'
  ];
  let wanted;
  let raf=0;
  let retryToken=0;

  const routeSurface=(target)=>{
    target=String(target||'').toLowerCase();
    if(target==='home'||target==='close')return null;
    if(target==='editor')return 'gsf-editor-overlay-v220';
    if(target==='short')return 'gsf-short-overlay-v343';
    if(target==='hub'||target==='profile'||target==='projects'||target==='live'||target==='subscription')return 'gsf-creator-hub-live-v160';
    if(target==='ai')return 'gsf-ai-overlay-v221';
    if(target==='social')return 'gsf-social-overlay-v159';
    if(target==='account')return 'gsf-account-overlay-v223';
    return undefined;
  };

  const score=(el)=>{
    if(!el)return -1;
    let n=0;
    try{
      if(el.classList.contains('is-open'))n+=8;
      if(el.getAttribute('aria-hidden')==='false')n+=4;
      const cs=P.getComputedStyle(el);
      if(cs.display!=='none'&&cs.visibility!=='hidden'&&Number(cs.opacity||1)>.01)n+=2;
      if(cs.pointerEvents!=='none')n+=1;
    }catch(_e){}
    return n;
  };

  const setInteractive=(el,on)=>{
    if(!el)return;
    el.style.pointerEvents=on?'auto':'none';
    el.toggleAttribute('inert',!on);
    el.setAttribute('aria-hidden',on?'false':'true');
    if(on){
      el.style.visibility='visible';
      el.style.opacity='1';
      el.classList.add('gsf-v367-interactive');
    }else{
      el.style.visibility='hidden';
      el.style.opacity='0';
      el.classList.remove('gsf-v367-interactive');
    }
  };

  const inferredActive=()=>{
    let best=null,bestScore=0;
    SURFACES.forEach((id)=>{
      const s=score(D.getElementById(id));
      if(s>bestScore){best=id;bestScore=s}
    });
    return best;
  };

  const reconcile=()=>{
    let active=wanted;
    if(active===undefined)active=inferredActive();
    SURFACES.forEach((id)=>{
      const el=D.getElementById(id);
      if(el)setInteractive(el,active!==null&&id===active);
    });
  };

  const schedule=()=>{
    retryToken+=1;
    const token=retryToken;
    if(!raf){
      raf=P.requestAnimationFrame(()=>{raf=0;reconcile()});
    }
    [0,60,180,520,1200].forEach((delay)=>P.setTimeout(()=>{
      if(token===retryToken)reconcile();
    },delay));
  };

  P.addEventListener('message',(e)=>{
    if(e.origin!==P.location.origin||!e.data||e.data.type!=='GSF_SHELL_NAV')return;
    const mapped=routeSurface(e.data.target);
    if(mapped===undefined)return;
    wanted=mapped;
    schedule();
  },true);

  P.addEventListener('pageshow',()=>{wanted=undefined;schedule()},{passive:true});
  D.addEventListener('visibilitychange',()=>{if(!D.hidden){wanted=undefined;schedule()}},{passive:true});
  P.addEventListener('orientationchange',schedule,{passive:true});
  P.addEventListener('resize',schedule,{passive:true});

  // Safari can restore a BFCache snapshot with stale inline pointer-events.
  // Reconcile a few bounded times at boot; do not add another MutationObserver.
  wanted=undefined;
  schedule();
})(window.parent);
</script>
'''


def _is_v343_call(node: ast.AST) -> bool:
    if not isinstance(node, ast.Call) or not node.args:
        return False
    fn = node.func
    if not (
        isinstance(fn, ast.Attribute)
        and fn.attr == 'html'
        and isinstance(fn.value, ast.Name)
        and fn.value.id == '_gsf_components_v343'
    ):
        return False
    arg = node.args[0]
    return isinstance(arg, ast.Constant) and isinstance(arg.value, str) and '__GSF_GLOBAL_SHELL_V343' in arg.value


def patch_app(text: str, path: Path) -> tuple[str, bool]:
    tree = ast.parse(text)
    calls = [node for node in ast.walk(tree) if _is_v343_call(node)]
    if len(calls) != 1:
        raise RuntimeError(f'V367 expected one V343 shell bridge in {path.name}, found {len(calls)}')
    call = calls[0]
    arg = call.args[0]
    bridge = arg.value
    if MARK in bridge:
        return text, False
    old_source = ast.get_source_segment(text, arg)
    if not old_source:
        raise RuntimeError(f'V367 could not locate V343 bridge source in {path.name}')
    new_bridge = bridge.rstrip() + '\n' + ARBITER.strip() + '\n'
    updated = text.replace(old_source, repr(new_bridge), 1)
    compile(updated, str(path), 'exec')
    return updated, True


def main() -> None:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path('/app')
    targets = [
        root/'GamingShortsFactory_V154_STRUCTURAL_HOME.py',
        root/'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py',
    ]
    existing = [path for path in targets if path.is_file()]
    if not existing:
        raise SystemExit('V367 runtime shell targets missing')

    patched = 0
    for path in existing:
        before = path.read_text(encoding='utf-8')
        if '__GSF_GLOBAL_SHELL_V343' not in before:
            if path.name.endswith('V293_RENDER_MEMORY_GUARD.py'):
                raise RuntimeError('V367 final V293 runtime is missing the V343 shell bridge')
            continue
        after, changed = patch_app(before, path)
        path.write_text(after, encoding='utf-8')
        patched += int(changed)
        print(f'V367 single-active-surface {path.name}: changed={changed}', flush=True)

    final = root/'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py'
    if final.is_file() and MARK not in final.read_text(encoding='utf-8'):
        raise RuntimeError('V367 marker missing from final V293 runtime')
    print(f'V367 single active surface applied files_changed={patched}', flush=True)


if __name__ == '__main__':
    main()
