from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

_COMPONENT_DIR = Path(__file__).resolve().parent / "home_v154_component"
_HOME_V154_COMPONENT = components.declare_component(
    "gsf_home_v154_live_307",
    path=str(_COMPONENT_DIR),
)


def _render_v428_uploader_handoff_reset_bridge():
    """Keep source readiness while returning the Home uploader to its idle UI."""
    # GSF_V428_UPLOADER_HANDOFF_RESET
    # The custom Home intentionally keeps `loaded=True` after upload because AI,
    # Editor and Crea Short still need the current source.  Presentation is a
    # separate concern: once the direct uploader handed the source to the app,
    # the circle must become an uploader again.  This tiny same-origin bridge
    # clears only stale uploader media/classes; it never clears session/source
    # state and it leaves the existing safe replacement/draft flow intact.
    components.html(r"""
    <script>
    (()=>{
      const P=window.parent;
      let D=null;
      try{D=P.document}catch(_e){return}
      if(!D)return;

      try{P.__GSF_V428_UPLOADER_HANDOFF_RESET__?.cleanup?.()}catch(_e){}

      const HOME='iframe[title*="gsf_home_v154"],iframe[src*="home_v154"]';
      const CLOUD='<svg viewBox="0 0 64 64" aria-hidden="true"><path d="M18 42h-1C10.4 42 5 36.6 5 30s5.4-12 12-12c1.6 0 3.1.3 4.5.9C24.7 12.4 31.3 8 39 8c10.5 0 19 8.5 19 19 0 .7 0 1.4-.1 2.1C61.5 30.9 64 34.6 64 39c0 6.1-4.9 11-11 11H38"/><path d="M32 52V28"/><path d="m24 36 8-8 8 8"/></svg>';
      let raf=0;

      const frameDoc=(frame)=>{
        try{return frame?.contentDocument||null}catch(_e){return null}
      };

      /* GSF_V429_COMPACT_NOTIFICATIONS
         V428 became the sole event-notification surface, but its first mobile
         dimensions were closer to a panel than a toast. Keep the same runtime
         and semantics while making the visual footprint deliberately small. */
      const ensureCompactNotifications=()=>{
        let style=D.getElementById('gsf-v429-compact-notifications');
        if(!style){
          style=D.createElement('style');
          style.id='gsf-v429-compact-notifications';
          style.textContent=`
#gsf-site-toast-stack{width:min(300px,calc(100vw - 28px))!important;gap:6px!important}
.gsf-site-toast{grid-template-columns:20px minmax(0,1fr) 20px!important;gap:7px!important;min-height:48px!important;padding:7px 8px!important;border-radius:14px!important}
.gsf-site-toast-icon{width:20px!important;height:20px!important}
.gsf-site-toast-icon img{width:18px!important;height:18px!important;border-radius:5px!important}
.gsf-site-toast-title{font-size:14px!important;line-height:1.05!important}
.gsf-site-toast-body{font-size:12px!important;line-height:1.12!important;min-height:0!important;margin-top:2px!important;-webkit-line-clamp:1!important}
.gsf-site-toast-close{width:20px!important;height:24px!important;font-size:16px!important}
.gsf-site-toast-actions{gap:6px!important}
.gsf-site-toast-action{min-height:28px!important;padding:4px 9px!important;font-size:10px!important;border-radius:9px!important}
`;
          (D.head||D.documentElement).appendChild(style);
        }

        /* GSF_V429_SINGLE_EVENT_NOTIFICATIONS
           Alive V418 still owns guidance, heartbeat and carried progress. Its
           legacy event whisper is only a fallback when GSFNotify says an event
           was not handled. Mark non-toast-worthy event chatter as handled and
           route uncovered failures through the compact global surface instead. */
        const notify=P.GSFNotify;
        if(!notify||notify.__GSF_V429_SINGLE_EVENT_NOTIFICATIONS__)return;
        const originalAlive=notify.alive;
        notify.alive=function(state){
          let handled=false;
          try{handled=typeof originalAlive==='function'?originalAlive.call(notify,state):false}catch(_e){handled=false}
          if(handled)return true;
          const event=String(state?.last||'');
          if(event==='moment.selected'||event==='recovered')return true;
          if(event==='failure'){
            try{notify.show(String(state?.message||'Qualcosa si è fermato.'),'','error',{id:'alive:fallback-error'})}catch(_e){}
            return true;
          }
          return false;
        };
        notify.__GSF_V429_SINGLE_EVENT_NOTIFICATIONS__=true;
      };

      const clearStaleMedia=(doc,circle,rings)=>{
        doc.querySelectorAll('#circle video,#circle img,#circle canvas,.rings video,.rings img,.rings canvas').forEach((node)=>{
          try{node.remove()}catch(_e){}
        });
        for(const node of [circle,rings]){
          if(!node?.style)continue;
          const bg=String(node.style.backgroundImage||'');
          if(bg.includes('url(')||bg.includes('blob:'))node.style.removeProperty('background-image');
        }
      };

      const syncFrame=(frame)=>{
        const doc=frameDoc(frame);if(!doc)return;
        const circle=doc.getElementById('circle');
        const rings=doc.querySelector('.rings');
        const icon=doc.getElementById('uploadIcon');
        const label=doc.getElementById('uploadLabel');
        const hint=doc.getElementById('uploadHint');
        const status=doc.getElementById('status');
        const statusText=doc.getElementById('statusText');
        const bar=doc.getElementById('bar');
        const replaceConfirm=doc.getElementById('replaceConfirm');
        if(!circle||!rings||!icon||!label)return;

        // A new upload must never show the previous gameplay behind its progress.
        clearStaleMedia(doc,circle,rings);
        const busy=circle.classList.contains('busy')||rings.classList.contains('uploading');
        if(busy){
          circle.removeAttribute('data-gsf-uploader-idle');
          return;
        }

        const hadLoadedPresentation=
          circle.classList.contains('loaded')||
          rings.classList.contains('uploaded')||
          icon.classList.contains('loadedCheck')||
          circle.getAttribute('data-gsf-uploader-idle')==='true';
        if(!hadLoadedPresentation)return;

        // Source stays loaded internally. Only the uploader presentation returns
        // to idle, so the three Home actions still operate on the current video.
        circle.setAttribute('data-gsf-uploader-idle','true');
        circle.classList.remove('loaded','done');
        rings.classList.remove('uploaded');
        icon.classList.remove('loadedCheck');
        icon.innerHTML=CLOUD;
        label.innerHTML='CARICA<br>IL TUO GAMEPLAY';
        if(hint)hint.textContent='';
        if(replaceConfirm)replaceConfirm.setAttribute('data-gsf-safe-replace','true');

        // Successful handoff is complete; progress belongs only to the upload
        // that is currently running. Preserve an actual error message.
        if(status&&!status.classList.contains('error'))status.className='status';
        if(statusText&&!status?.classList.contains('error'))statusText.textContent='';
        if(bar&&!status?.classList.contains('error'))bar.style.width='0%';
      };

      const syncAll=()=>{
        raf=0;
        ensureCompactNotifications();
        D.querySelectorAll(HOME).forEach(syncFrame);
      };
      const schedule=()=>{
        if(raf)return;
        raf=P.requestAnimationFrame(syncAll);
      };
      const onMessage=(event)=>{
        if(event.origin!==P.location.origin||!event.data||event.data.type!=='gsf-upload')return;
        if(event.data.state==='running'||event.data.state==='done'||event.data.state==='error')schedule();
      };

      P.addEventListener('message',onMessage);
      const observer=new P.MutationObserver(schedule);
      observer.observe(D.documentElement,{childList:true,subtree:true});
      const timer=P.setInterval(schedule,450);
      schedule();

      P.__GSF_V428_UPLOADER_HANDOFF_RESET__={
        cleanup(){
          try{P.removeEventListener('message',onMessage)}catch(_e){}
          try{observer.disconnect()}catch(_e){}
          try{P.clearInterval(timer)}catch(_e){}
          try{if(raf)P.cancelAnimationFrame(raf)}catch(_e){}
        }
      };

      // The bridge is behavior-only and must not consume a pixel of Home.
      try{
        const own=P.document.querySelector('iframe[srcdoc]:last-of-type');
        if(window.frameElement){
          window.frameElement.style.display='none';
          window.frameElement.setAttribute('aria-hidden','true');
          const holder=window.frameElement.closest('[data-testid="stElementContainer"]');
          if(holder){holder.style.display='none';holder.style.height='0';holder.style.minHeight='0';holder.style.margin='0';holder.style.padding='0'}
        }
        void own;
      }catch(_e){}
    })();
    </script>
    """, height=0, width=0)


def render_home_v154(*, loaded=False, duration=15, engine="", height=900, key="gsf_home_v155"):
    # V181 MOBILE FULL-VIEWPORT SHELL
    # The parent owns the viewport. Home itself must now live inside the global
    # shell's content bounds so its stage/cards are never hidden by header/Game Bar.
    st.html(r"""
    <style id="gsf-mobile-full-viewport-v181">
    @media (max-width:760px){
      html,body,.stApp,
      [data-testid="stAppViewContainer"],
      [data-testid="stMain"]{
        width:100vw !important;
        height:100dvh !important;
        min-height:100dvh !important;
        max-height:100dvh !important;
        margin:0 !important;
        padding:0 !important;
        overflow:hidden !important;
        overscroll-behavior:none !important;
      }

      [data-testid="stHeader"],
      [data-testid="stToolbar"],
      [data-testid="stDecoration"],
      [data-testid="stStatusWidget"]{
        display:none !important;
        height:0 !important;
        min-height:0 !important;
        max-height:0 !important;
        margin:0 !important;
        padding:0 !important;
      }

      [data-testid="stMainBlockContainer"],
      .main .block-container{
        position:fixed !important;
        inset:0 !important;
        width:100vw !important;
        max-width:none !important;
        height:100dvh !important;
        min-height:0 !important;
        max-height:100dvh !important;
        margin:0 !important;
        padding:0 !important;
        overflow:hidden !important;
      }

      /* GSF_V429_HOME_SHELL_BOUNDS */
      [data-testid="stElementContainer"]:has(iframe[title*="gsf_home_v154"]){
        position:fixed !important;
        left:0 !important;
        right:0 !important;
        top:var(--gsf-shell-content-top,44px) !important;
        bottom:var(--gsf-shell-content-bottom,112px) !important;
        width:100vw !important;
        height:auto !important;
        min-height:0 !important;
        max-height:none !important;
        margin:0 !important;
        padding:0 !important;
        overflow:hidden !important;
        z-index:1 !important;
      }

      [data-testid="stCustomComponentV1"]:has(iframe[title*="gsf_home_v154"]){
        position:absolute !important;
        inset:0 !important;
        width:100% !important;
        height:100% !important;
        min-height:0 !important;
        max-height:none !important;
        margin:0 !important;
        padding:0 !important;
        overflow:hidden !important;
      }

      iframe[title*="gsf_home_v154"],
      iframe[src*="home_v154"]{
        position:absolute !important;
        inset:0 !important;
        display:block !important;
        width:100% !important;
        max-width:none !important;
        height:100% !important;
        min-height:0 !important;
        max-height:none !important;
        margin:0 !important;
        padding:0 !important;
        border:0 !important;
      }
    }

      /* V225 MOBILE APP-SURFACE STACKING
         The Home iframe stays inside the persistent shell and must not cover
         app surfaces rendered later in the Streamlit parent. */
      [data-testid="stElementContainer"]:has(#gsf-creator-hub-live-v160),
      [data-testid="stElementContainer"]:has(#gsf-social-overlay-v159),
      [data-testid="stElementContainer"]:has(#gsf-editor-overlay-v220),
      [data-testid="stElementContainer"]:has(#gsf-ai-overlay-v221){
        position:relative !important;
        z-index:120 !important;
        overflow:visible !important;
      }
    </style>
    """)

    value = _HOME_V154_COMPONENT(
        loaded=bool(loaded),
        duration=int(duration or 15),
        engine=str(engine or ""),
        height=int(height),
        key=str(key),
        default=None,
    )
    _render_v428_uploader_handoff_reset_bridge()
    return value if isinstance(value, dict) else None
