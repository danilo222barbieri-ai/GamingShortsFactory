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
    # On phones the Home component must own the real viewport: no Streamlit
    # spacer above it and no parent-page scroll below it.
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

      [data-testid="stElementContainer"]:has(iframe[title*="gsf_home_v154"]){
        position:fixed !important;
        inset:0 !important;
        width:100vw !important;
        height:100dvh !important;
        min-height:0 !important;
        max-height:100dvh !important;
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
        width:100vw !important;
        max-width:none !important;
        height:100dvh !important;
        min-height:100dvh !important;
        max-height:100dvh !important;
        margin:0 !important;
        padding:0 !important;
        border:0 !important;
      }
    }

      /* V225 MOBILE APP-SURFACE STACKING
         The Home iframe must stay fullscreen but must not cover persistent
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
