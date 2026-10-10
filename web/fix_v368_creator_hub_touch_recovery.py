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
  let lastPointerTarget=null;
  let lastPointerAt=0;

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

      // Same-origin, Hub-only parent repair. Never touch any other surface.
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

  function v368HubAction(target){
    if(!target||typeof target.closest!=='function')return null;
    const inside=(el)=>!!el&&hub.contains(el);
    let el=target.closest('.folder');
    if(inside(el)){
      openView(el.dataset.folder||'dashboard');
      return ['folder:'+(el.dataset.folder||'dashboard'),el];
    }
    el=target.closest('[data-open-folder]');
    if(inside(el)){
      openView(el.dataset.openFolder||'dashboard');
      return ['open-folder:'+(el.dataset.openFolder||'dashboard'),el];
    }
    el=target.closest('.backBtn');
    if(inside(el)){
      openView('dashboard');
      return ['back',el];
    }
    el=target.closest('.closeTop');
    if(inside(el)){
      shell('home');
      return ['close',el];
    }
    el=target.closest('.socialDot');
    if(inside(el)){
      openView('social');
      return ['social:'+(el.dataset.social||''),el];
    }
    el=target.closest('[data-live-folder]');
    if(inside(el)){
      openLiveFolder(el.dataset.liveFolder||'');
      return ['live-folder:'+(el.dataset.liveFolder||''),el];
    }
    el=target.closest('[data-live-mini]');
    if(inside(el)){
      openLiveMini(el.dataset.liveMini||'');
      return ['live-mini:'+(el.dataset.liveMini||''),el];
    }
    el=target.closest('[data-resume]');
    if(inside(el)){
      resumeDraft(el.dataset.resume||'');
      return ['resume',el];
    }
    el=target.closest('[data-short-download]');
    if(inside(el)){
      location.href='/shorts/file?id='+encodeURIComponent(el.dataset.shortDownload||'');
      return ['short-download',el];
    }
    el=target.closest('[data-short-delete]');
    if(inside(el)){
      confirmDeleteShort(el.dataset.shortDelete||'');
      return ['short-delete',el];
    }
    el=target.closest('[data-quick]');
    if(inside(el)){
      const q=el.dataset.quick||'';
      if(q==='social')openView('profile');
      else if(q)shell(q);
      return ['quick:'+q,el];
    }
    el=target.closest('[data-connect]');
    if(inside(el)){
      connectSocial(el.dataset.connect||'');
      return ['connect:'+(el.dataset.connect||''),el];
    }
    el=target.closest('#saveProfileBtn');
    if(inside(el)){
      saveProfile();
      return ['save-profile',el];
    }
    return null;
  }

  function v368RunAction(target,source){
    try{
      const result=v368HubAction(target);
      if(!result)return false;
      v368Telemetry('V368_HUB_TAP',source+':'+result[0]);
      v368RepairActiveView();
      setTimeout(v368RepairActiveView,0);
      return true;
    }catch(err){
      v368Telemetry('V368_ACTION_ERROR',String(err&&err.message||err));
      return false;
    }
  }

  function v368PointerUp(event){
    if(!v368RunAction(event.target,'pointerup'))return;
    lastPointerTarget=event.target;
    lastPointerAt=Date.now();
    event.stopPropagation();
  }

  function v368Click(event){
    const recent=lastPointerTarget&&Date.now()-lastPointerAt<750;
    if(recent&&(event.target===lastPointerTarget||(lastPointerTarget.contains&&lastPointerTarget.contains(event.target)))){
      event.stopPropagation();
      return;
    }
    if(v368RunAction(event.target,'click'))event.stopPropagation();
  }

  function v368RepairFromFocusMessage(event){
    try{
      if(event.origin!==location.origin||!event.data||event.data.type!=='GSF_HUB_FOCUS')return;
      setTimeout(v368RepairActiveView,0);
    }catch(_e){}
  }

  document.addEventListener('pointerup',v368PointerUp,true);
  document.addEventListener('click',v368Click,true);
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
