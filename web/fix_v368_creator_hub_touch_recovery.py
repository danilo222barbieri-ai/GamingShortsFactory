#!/usr/bin/env python3
from pathlib import Path
import sys

MARK = 'V368_CREATOR_HUB_TOUCH_RECOVERY'

RUNTIME = r'''
<!-- V368_CREATOR_HUB_TOUCH_RECOVERY -->
<style id="v368CreatorHubTouchRecoveryStyle">
#hub{pointer-events:auto!important;visibility:visible!important}
#hub .stage{pointer-events:auto!important}
#hub .view.active{pointer-events:auto!important;visibility:visible!important}
#hub button,
#hub [role="button"],
#hub .folder,
#hub .socialDot,
#hub [data-open-folder],
#hub [data-live-folder],
#hub [data-live-mini],
#hub [data-resume],
#hub [data-short-download],
#hub [data-short-delete],
#hub [data-quick],
#hub [data-connect]{touch-action:manipulation;-webkit-tap-highlight-color:transparent}
</style>
<script id="v368CreatorHubTouchRecoveryRuntime">
(()=>{
  if(window.__gsfV368TouchRecovery)return;
  window.__gsfV368TouchRecovery=1;
  const hub=document.getElementById('hub');
  if(!hub)return;

  function v368Telemetry(stage,message){
    try{
      const payload=JSON.stringify({stage:String(stage||'V368').slice(0,80),message:String(message||'').slice(0,300),href:String(location.pathname||'').slice(0,160)});
      if(navigator.sendBeacon){
        navigator.sendBeacon('/creator-hub/client-error',new Blob([payload],{type:'application/json'}));
      }else{
        fetch('/creator-hub/client-error',{method:'POST',credentials:'same-origin',keepalive:true,headers:{'Content-Type':'application/json'},body:payload}).catch(()=>{});
      }
    }catch(_e){}
  }

  function v368RepairActiveView(){
    try{
      const views=[...hub.querySelectorAll('.view[data-view]')];
      if(!views.length)return;
      let active=views.find(view=>view.classList.contains('active'));
      if(!active){
        active=views.find(view=>view.dataset.view==='dashboard')||views[0];
        active.classList.add('active');
      }
      views.forEach(view=>{
        const on=view===active;
        view.style.pointerEvents=on?'auto':'none';
        view.style.visibility=on?'visible':'hidden';
        if(on)view.removeAttribute('aria-hidden');
        else view.setAttribute('aria-hidden','true');
      });
      hub.style.pointerEvents='auto';
      hub.style.visibility='visible';
      const stage=hub.querySelector('.stage');
      if(stage)stage.style.pointerEvents='auto';

      // Same-origin, Hub-only parent repair. Never own navigation or input here:
      // the base Hub handlers are the single action path.
      const frame=window.frameElement;
      if(frame){
        frame.style.pointerEvents='auto';
        frame.style.visibility='visible';
        const overlay=frame.closest('#gsf-creator-hub-live-v160');
        if(overlay&&overlay.classList.contains('is-open')){
          overlay.style.pointerEvents='auto';
          overlay.style.visibility='visible';
          overlay.style.opacity='1';
          overlay.setAttribute('aria-hidden','false');
        }
      }
    }catch(err){v368Telemetry('V368_REPAIR_ERROR',err&&err.message||err)}
  }

  function v368RepairFromFocusMessage(event){
    try{
      if(event.origin!==location.origin||!event.data||event.data.type!=='GSF_HUB_FOCUS')return;
      setTimeout(v368RepairActiveView,0);
    }catch(_e){}
  }

  window.addEventListener('pageshow',v368RepairActiveView);
  window.addEventListener('focus',v368RepairActiveView);
  window.addEventListener('message',v368RepairFromFocusMessage);

  try{
    const stage=hub.querySelector('.stage');
    if(stage)new MutationObserver(v368RepairActiveView).observe(stage,{subtree:true,attributes:true,attributeFilter:['class']});
  }catch(_e){}

  v368RepairActiveView();
})();
</script>
'''


def patch_text(text: str) -> str:
    if MARK in text:
        return text
    if 'V366_CREATOR_HUB_STATE_STABILITY' not in text:
        # The repository source is intentionally pre-runtime-patch. V368 is also
        # unit-tested against that source, while production applies it after V366.
        if 'GSF_HUB_FOCUS' not in text or 'function openView' not in text:
            raise RuntimeError('V368 requires the Creator Hub runtime surface')
    if '</body>' not in text:
        raise RuntimeError('V368 Creator Hub body anchor missing')
    return text.replace('</body>', RUNTIME + '\n</body>', 1)


def main() -> None:
    path = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path('/app/web/creator_hub_v156_component/index.html')
    if not path.is_file():
        raise SystemExit('V368 Creator Hub target missing: ' + str(path))
    before = path.read_text(encoding='utf-8')
    after = patch_text(before)
    path.write_text(after, encoding='utf-8')
    print('V368 Creator Hub touch recovery applied changed=', before != after, flush=True)


if __name__ == '__main__':
    main()
