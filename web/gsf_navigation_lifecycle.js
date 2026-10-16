/* One parent-owned navigation and document lifecycle. Installed in the TOP realm. */
(() => {
  if (window.GSFNavigation) return;
  const D = document;
  const ids = {
    hub: 'gsf-creator-hub-live-v160', editor: 'gsf-editor-overlay-v220',
    ai: 'gsf-ai-overlay-v221', short: 'gsf-short-overlay-v343',
    social: 'gsf-social-overlay-v159', account: 'gsf-account-overlay-v223',
  };
  const keys = {hub:'gsf_creator_hub_open_v107',editor:'gsf_editor_overlay_open_v223',
    ai:'gsf_ai_overlay_open_v221',social:'gsf_social_overlay_open_v159',account:'gsf_account_overlay_open_v223'};
  const surfaces = new Map(), bridges = new Map(), surfaceState = new Map();
  let currentData={};
  let current = {target:'home',section:''}, epoch = 0, transitioning = false;
  const normalize = data => {
    let target=String(data.target||'home'), section=String(data.section||'');
    if (target==='close') target='home';
    if (target==='profile'||target==='account') {target='hub';section='profile';}
    if (target==='projects'||target==='live') {section=target;target='hub';}
    if (target==='hub'&&!['dashboard','profile','projects','live','subscription','social'].includes(section)) section='dashboard';
    if (target!=='hub') section='';
    return {target,section};
  };
  const frameOf = key => D.getElementById(ids[key])?.querySelector('iframe');
  const post = (key, type) => frameOf(key)?.contentWindow?.postMessage({type},location.origin);
  function reconcile() {
    for (const [key,id] of Object.entries(ids)) {
      const el=D.getElementById(id); if (!el) continue;
      const on=key===current.target;
      if (el.classList.contains('is-open')!==on) el.classList.toggle('is-open',on);
      const values={opacity:on?'1':'0',visibility:on?'visible':'hidden',pointerEvents:on?'auto':'none'};
      for (const [name,value] of Object.entries(values)) if(el.style[name]!==value) el.style[name]=value;
      if (el.getAttribute('aria-hidden')!==String(!on)) el.setAttribute('aria-hidden',String(!on));
      if (el.inert===on) el.inert=!on;
    }
    D.documentElement.classList.toggle('v393EditorActive',current.target==='editor'&&innerWidth<=760);
    D.documentElement.classList.toggle('v394EditorActive',current.target==='editor'&&innerWidth<=760);
    if (current.target!=='editor') D.documentElement.classList.remove('gsf-mobile-editor-fullscreen');
    const selected=current.target==='hub'?(['projects','live'].includes(current.section)?current.section:'hub'):'home';
    D.querySelectorAll('#gsf-global-gamebar button').forEach(b=>b.classList.toggle('active',b.dataset.page===selected));
    for (const [key,name] of Object.entries(keys)) {
      try {sessionStorage.setItem(name,key===current.target?'1':'0');} catch (_) {}
    }
    try {sessionStorage.setItem('gsf_editor_overlay_open_v220',current.target==='editor'?'1':'0');} catch (_) {}
  }
  function navigate(data={}) {
    const next=normalize(data);
    if (next.target!=='home'&&!ids[next.target]) return false;
    const previous=current;
    ++epoch; transitioning=true;
    try {
      for (const [key,controller] of surfaces) if(key!==next.target) controller.close?.();
      if (previous.target!==next.target) post(previous.target,'GSF_APP_SUSPEND');
      current=next;
      currentData={...data,...next};
      surfaces.get(next.target)?.open?.({...data,...next});
      reconcile();
      return true;
    } finally {transitioning=false;reconcile();}
  }
  function suspend() {
    post(current.target,'GSF_APP_SUSPEND');
  }
  function resume() {
    // No route replay, media re-init, project reset, or new listeners/timers.
    reconcile();
    post(current.target,'GSF_APP_RESUME');
  }
  const api=window.GSFNavigation={
    navigate,resume,suspend,reconcile,
    snapshot:()=>({...current,epoch,transitioning,bridges:bridges.size,surfaces:surfaces.size}),
    surfaceState(key,initial) {if(!surfaceState.has(key))surfaceState.set(key,initial());return surfaceState.get(key);},
    registerSurface(key,controller) {
      surfaces.set(key,controller);
      if(current.target===key&&!controller.adopt?.()) controller.open?.({...currentData,...current});
      reconcile();
    },
    bridge(key,owner) {
      bridges.get(key)?.abort();
      const controller=new AbortController();
      bridges.set(key,controller);
      const signal=controller.signal;
      return {signal,owner,
        observe(target,options,callback) {
          const observer=new MutationObserver(callback);observer.observe(target,options);
          signal.addEventListener('abort',()=>observer.disconnect(),{once:true});return observer;
        },
        timeout(callback,delay) {
          const id=setTimeout(()=>{if(!signal.aborted)callback();},delay);
          signal.addEventListener('abort',()=>clearTimeout(id),{once:true});return id;
        },
      };
    },
  };
  window.addEventListener('message',e=>{
    if(e.origin!==location.origin||!e.data||e.data.type!=='GSF_SHELL_NAV') return;
    // Accept this document and its currently mounted frames, not removed frames.
    const mounted=e.source===window||[...D.querySelectorAll('iframe')].some(f=>f.contentWindow===e.source);
    if(mounted) navigate(e.data);
  });
  D.addEventListener('visibilitychange',()=>D.hidden?suspend():resume());
  window.addEventListener('pagehide',suspend);
  window.addEventListener('pageshow',resume);
  // Focusing an iframe also blurs the parent; it is not backgrounding.
  window.addEventListener('blur',()=>post(current.target,'GSF_APP_BLUR'));
  window.addEventListener('focus',resume);
  D.addEventListener('freeze',suspend);
  D.addEventListener('resume',resume);
  reconcile();
})();
