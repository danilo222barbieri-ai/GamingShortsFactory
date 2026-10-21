/* One parent-owned navigation and document lifecycle. Installed in the TOP realm. */
(() => {
  if (window.GSFNavigation) return;
  const D = document;
  // Streamlit owns reconnection. Close its live transport cleanly before the
  // browser caches the document instead of letting Chrome abort it. Ordinary
  // background/freeze keeps the connection and mounted Home intact.
  const streamlitSockets=new Set(),NativeWebSocket=window.WebSocket;
  window.WebSocket=class extends NativeWebSocket {
    constructor(...args) {
      super(...args);
      if(new URL(String(args[0]),location.href).pathname==='/_stcore/stream') {
        streamlitSockets.add(this);
        this.addEventListener('close',()=>streamlitSockets.delete(this),{once:true});
      }
    }
  };
  const closeStreamlitTransport=()=>{
    for(const socket of streamlitSockets)if(socket.readyState===NativeWebSocket.OPEN)socket.close(1000,'document suspended');
  };
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
    // "Crea Short" always opens the canonical Crea Short page (/share-v156/);
    // the social surface starts the render when no final Short is ready yet.
    if (target==='short') return {target:'social',section:'',createShort:true,requestedAt:Date.now()};
    if (target==='profile'||target==='account') {target='hub';section='profile';}
    if (target==='projects'||target==='live') {section=target;target='hub';}
    if (target==='hub'&&!['dashboard','profile','projects','live','subscription','social'].includes(section)) section='dashboard';
    if (target!=='hub') section='';
    return {target,section};
  };
  const routeFromUrl=()=>{
    const q=new URL(location.href).searchParams;
    // Existing OAuth callbacks use this legacy entry point. Resolve it in
    // the canonical router before any surface mounts, including cold starts.
    if(!q.has('gsf_page')&&q.get('gsf_hub')==='social'){
      let section='social';
      if(q.has('oauth_return'))try{
        const pending=JSON.parse(sessionStorage.getItem('gsf-source-oauth-return')||'null');
        sessionStorage.removeItem('gsf-source-oauth-return');
        const age=Date.now()-Number(pending?.created);
        if(pending?.provider==='twitch'&&age>=0&&age<600000&&['live','videos','clips','imported'].includes(pending.folder)){
          sessionStorage.setItem('gsf-source-view',JSON.stringify({provider:'twitch',folder:pending.folder}));section='live';
        }
      }catch(_e){}
      const url=new URL(location.href);
      url.searchParams.delete('gsf_hub');url.searchParams.delete('oauth_return');
      url.searchParams.set('gsf_page','hub');url.searchParams.set('gsf_section',section);
      history.replaceState(history.state,'',url);
      return {target:'hub',section};
    }
    const route={target:q.get('gsf_page')||'home',section:q.get('gsf_section')||''};
    // Unknown URL routes recover to Home. Internal protocol messages (such
    // as ai-state) must keep being ignored by navigate's allowlist.
    return ['home','short','profile','account','projects','live'].includes(route.target)||ids[route.target]?route:{target:'home',section:''};
  };
  current=normalize(routeFromUrl());currentData={...current};
  const writeHistory=()=>{
    const url=new URL(location.href);
    const target=current.createShort?'short':current.target;
    if(target==='home'){url.searchParams.delete('gsf_page');url.searchParams.delete('gsf_section');}
    else {url.searchParams.set('gsf_page',target);if(current.section)url.searchParams.set('gsf_section',current.section);else url.searchParams.delete('gsf_section');}
    if(url.href!==location.href)history.pushState(null,'',url);
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
  function navigate(data={},options={}) {
    const next=normalize(data);
    if (next.target!=='home'&&!ids[next.target]) return false;
    const previous=current;
    ++epoch; transitioning=true;
    try {
      for (const [key,controller] of surfaces) if(key!==next.target) controller.close?.();
      if (previous.target!==next.target) post(previous.target,'GSF_APP_SUSPEND');
      current=next;
      window.dispatchEvent(new CustomEvent("gsf:surfacechange",{detail:{...current}}));
      currentData={...data,...next};
      if(options.history!==false)writeHistory();
      surfaces.get(next.target)?.open?.({...data,...next});
      // GSF_NIGHT_ARENA shared-element reveal (CSS only, never delays the route).
      try{const o=window.__gsfNavOrigin,el=D.getElementById(ids[next.target]);window.__gsfNavOrigin=null;if(el&&o&&Date.now()-o.t<1500&&!matchMedia('(prefers-reduced-motion: reduce)').matches){const r=el.getBoundingClientRect();el.style.setProperty('--na-ox',(o.x-r.left)+'px');el.style.setProperty('--na-oy',(o.y-r.top)+'px');el.style.setProperty('--na-oc',o.color||'#27AEF3');el.classList.remove('na-reveal');void el.offsetWidth;el.classList.add('na-reveal');setTimeout(()=>el.classList.remove('na-reveal'),700)}}catch(_e){}
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
          if(signal.aborted)return null;
          const cancel=()=>clearTimeout(id);
          const id=setTimeout(()=>{
            signal.removeEventListener('abort',cancel);
            if(!signal.aborted)callback();
          },delay);
          signal.addEventListener('abort',cancel,{once:true});return id;
        },
      };
    },
  };
  (()=>{
  if(typeof navigator==='undefined'||!window.matchMedia)return;
  // GSF is a portrait phone app. Manifest/API lock where supported; Safari
  // tabs cannot lock the OS, so cover landscape without reloading any surface.
  const phone=/Android|iPhone|iPod|Mobile/i.test(navigator.userAgent);
  const portraitMedia=window.matchMedia('(orientation: landscape)');
  let portraitBlocked=false;
  function portraitGuard(){
    if(!phone||!D.body)return;
    let guard=D.getElementById('gsf-portrait-guard');
    if(!guard){
      const style=D.createElement('style');style.id='gsf-portrait-style';
      style.textContent='#gsf-portrait-guard{position:fixed;inset:0;z-index:2147483647;display:none;place-content:center;gap:12px;padding:24px max(24px,env(safe-area-inset-right)) max(24px,env(safe-area-inset-bottom)) max(24px,env(safe-area-inset-left));box-sizing:border-box;text-align:center;background:#050D16;color:#EAF6FF;font:600 16px/1.4 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;touch-action:none}#gsf-portrait-guard:not([hidden]){display:grid}#gsf-portrait-guard b{font-size:24px;color:#79D2FF}';
      D.head.appendChild(style);guard=D.createElement('div');guard.id='gsf-portrait-guard';guard.hidden=true;guard.setAttribute('role','status');guard.setAttribute('aria-live','polite');guard.innerHTML='<b>Ruota il telefono</b><span>GSF si usa in verticale.</span>';D.body.appendChild(guard);
    }
    const angle=window.screen.orientation?.angle??window.orientation;
    const physicallyLandscape=Number.isFinite(angle)?Math.abs(angle)%180===90:portraitMedia.matches;
    const landscape=physicallyLandscape&&portraitMedia.matches;
    guard.hidden=!landscape;
    if(landscape!==portraitBlocked){portraitBlocked=landscape;if(landscape)suspend();else resume()}
  }
  let orientationRequest=false;
  async function requestPortrait(){
    if(!phone||orientationRequest||!window.screen.orientation?.lock)return;
    if(!window.matchMedia('(display-mode: standalone)').matches&&!D.fullscreenElement)return;
    orientationRequest=true;
    try{await window.screen.orientation.lock('portrait')}catch(_e){}finally{orientationRequest=false}
  }
  D.addEventListener('pointerdown',requestPortrait,{passive:true});
  // WebKit can update the media query after its resize/orientation event.
  if(portraitMedia.addEventListener)portraitMedia.addEventListener('change',portraitGuard);
  else portraitMedia.addListener?.(portraitGuard);
  window.addEventListener('orientationchange',portraitGuard);
  window.addEventListener('resize',portraitGuard,{passive:true});
  if(D.body)portraitGuard();else D.addEventListener('DOMContentLoaded',portraitGuard,{once:true});
  })();
  window.addEventListener('popstate',()=>navigate(routeFromUrl(),{history:false}));
  window.addEventListener('message',e=>{
    if(e.origin!==location.origin||!e.data||e.data.type!=='GSF_SHELL_NAV') return;
    // Accept this document and its currently mounted frames, not removed frames.
    const mounted=e.source===window||[...D.querySelectorAll('iframe')].some(f=>f.contentWindow===e.source);
    if(mounted) navigate(e.data);
  });
  D.addEventListener('visibilitychange',()=>D.hidden?suspend():resume());
  window.addEventListener('pagehide',()=>{suspend();closeStreamlitTransport();});
  window.addEventListener('pageshow',resume);
  // Focusing an iframe also blurs the parent; it is not backgrounding.
  window.addEventListener('blur',()=>post(current.target,'GSF_APP_BLUR'));
  window.addEventListener('focus',resume);
  D.addEventListener('freeze',suspend);
  D.addEventListener('resume',resume);
  reconcile();
})();
