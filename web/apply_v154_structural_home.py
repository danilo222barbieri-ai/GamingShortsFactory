from pathlib import Path

src=Path("/app/GamingShortsFactory_V152_UI_RESET.py")
out=Path("/app/GamingShortsFactory_V154_STRUCTURAL_HOME.py")
s=src.read_text(encoding="utf-8")

anchor='with st.container(key="v73-upload-shell"):\n'
if anchor not in s:
    raise RuntimeError("V154 uploader anchor missing")

# V157: restore the active project before rendering any navigable surface.
# This complements the older reconnect snapshot with an explicit project id.
state_anchor='with st.container(key="v73-upload-shell"):\\n'
if state_anchor in s and "restore_project as _gsf_restore_project_v157" not in s:
    state_block='''# V157 ACTIVE PROJECT STATE\nif GSF_WEB_MODE:\n    try:\n        from web.project_state_v157 import restore_project as _gsf_restore_project_v157\n        _gsf_restore_project_v157(st.session_state, GSF_SESSION_ROOT)\n    except Exception:\n        pass\n\n'''
    s=s.replace(state_anchor,state_block+state_anchor,1)

block=r'''
# V154 Structural Home — real custom component, not a CSS reskin.
# The existing V98.9/V99 direct-upload backend, AI engine and Editor remain
# authoritative. This component replaces only the Home presentation layer.
if GSF_WEB_MODE:
    from web.home_v154_embed import render_home_v154 as _gsf_render_home_v154

    st.html(r"""
    <style id="gsf-v154-parent-shell">
    /* V161 VIEWPORT CONTRACT — desktop reference 1920×1080, fit actual browser viewport. */
    @media (min-width:761px){
      html,body,[data-testid="stAppViewContainer"],[data-testid="stMain"],.stApp{
        min-height:100dvh !important;
      }
      [data-testid="stMainBlockContainer"]{
        max-width:none !important;
        padding-top:0 !important;
        padding-bottom:0 !important;
        padding-left:0 !important;
        padding-right:0 !important;
      }
      iframe[title*="gsf_home_v154"],iframe[src*="web.home_v154_embed"]{
        width:100% !important;
        max-width:1920px !important;
        margin:0 auto !important;
      }
    }
    /* V161 VIEWPORT CONTRACT */
    /* V161.1 ZERO-SCROLL CONTRACT */
    @media (min-width:761px){
      html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"]{
        height:100dvh !important;
        max-height:100dvh !important;
        overflow:hidden !important;
      }
      [data-testid="stMainBlockContainer"],.main .block-container{
        height:100dvh !important;
        max-height:100dvh !important;
        min-height:0 !important;
        overflow:hidden !important;
        margin:0 !important;
      }
      /* Streamlit execution chrome can sit below the custom shell and create
         an otherwise pointless scrollbar. It is not GSF render/upload progress. */
      [data-testid="stStatusWidget"],
      [data-testid="stToolbar"],
      [data-testid="stDecoration"],
      [data-testid="stHeader"]{
        display:none !important;
      }
      iframe[title*="gsf_home_v154_live_155"],
      iframe[title*="gsf_home_v154"],
      iframe[src*="home_v154"]{
        display:block !important;
        max-height:100dvh !important;
        border:0 !important;
      }
    }
    /* V162.1 HOME LIFT — keep the fixed desktop composition pinned to the top. */
    @media (min-width:761px){
      [data-testid="stElementContainer"]:has(iframe[title*="gsf_home_v154"]),
      [data-testid="stElementContainer"]:has(iframe[title*="gsf_home_v154_live_155"]){
        margin-top:-8px !important;
        margin-bottom:0 !important;
        padding-top:0 !important;
      }
    }


    /* V165 FLUID HOME SHELL — let the Home component use the complete desktop viewport. */
    @media (min-width:761px){
      iframe[title*="gsf_home_v154_live_155"],
      iframe[title*="gsf_home_v154"],
      iframe[src*="home_v154"]{
        width:100% !important;
        max-width:none !important;
        margin:0 !important;
      }
      [data-testid="stElementContainer"]:has(iframe[title*="gsf_home_v154"]),
      [data-testid="stElementContainer"]:has(iframe[title*="gsf_home_v154_live_155"]){
        width:100% !important;
        max-width:none !important;
        margin-top:0 !important;
        margin-bottom:0 !important;
      }
    }

    /* The new component owns the production Home. Keep the old uploader
       mounted only as an invisible fallback so its backend/state contracts
       remain available during migration. */
    .st-key-v73-upload-shell{
        display:none !important;
        height:0 !important;
        min-height:0 !important;
        margin:0 !important;
        padding:0 !important;
        overflow:hidden !important;
    }
    .gsf-living-brand,
    .gsf-living-bar{
        display:none !important;
    }

    /* V154.1 owns these Home CTAs. Keep the real Streamlit widgets mounted
       as action targets for the component, but remove their duplicate UI. */
    .st-key-gsf-major-create-ai,
    .st-key-gsf-major-personalize,
    [class*="st-key-gsf-major-game-editor_"],
    .st-key-gsf-major-create-short,
    [class*="st-key-edit_ai_"],
    .st-key-create_final_short_v54{
        position:absolute !important;
        width:1px !important;
        height:1px !important;
        overflow:hidden !important;
        opacity:0 !important;
        pointer-events:none !important;
        margin:0 !important;
        padding:0 !important;
    }

    /* Remove only the legacy chrome that TinyFish sees under V154 Home. */
    [data-testid="sync-short-ready-button"],
    .st-sync-ready,
    .sync-short-ready,
    [data-testid="footer"],
    .st-footer,
    .gsf-footer-v4{
        display:none !important;
    }

    /* V166 CANONICAL FLUID HOME SHELL — the component owns the entire browser work area. */
    @media (min-width:761px){
      [data-testid="stMainBlockContainer"],.main .block-container{
        width:100vw !important;
        max-width:none !important;
        height:100dvh !important;
        min-height:0 !important;
        padding:0 !important;
        margin:0 !important;
      }
      [data-testid="stElementContainer"]:has(iframe[title*="gsf_home_v154"]),
      [data-testid="stElementContainer"]:has(iframe[title*="gsf_home_v154_live_155"]){
        width:100vw !important;
        max-width:none !important;
        height:100dvh !important;
        margin:0 !important;
        padding:0 !important;
        transform:none !important;
      }
      iframe[title*="gsf_home_v154_live_155"],
      iframe[title*="gsf_home_v154"],
      iframe[src*="home_v154"]{
        display:block !important;
        width:100vw !important;
        max-width:none !important;
        height:100dvh !important;
        max-height:100dvh !important;
        margin:0 !important;
        padding:0 !important;
        border:0 !important;
        transform:none !important;
      }
    }

    
    /* V166.1 REAL VIEWPORT CLEANUP — reclaim the dead Streamlit band above Home. */
    @media (min-width:761px){
      html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"]{
        width:100vw !important;
        max-width:none !important;
        height:100dvh !important;
        max-height:100dvh !important;
        margin:0 !important;
        padding:0 !important;
        overflow:hidden !important;
      }
      [data-testid="stMainBlockContainer"],.main .block-container{
        width:100vw !important;
        max-width:none !important;
        height:100dvh !important;
        max-height:100dvh !important;
        margin:0 !important;
        padding:0 !important;
        overflow:hidden !important;
      }
      body:has(iframe[title*="gsf_home_v154"]) [data-testid="stVerticalBlock"],
      body:has(iframe[title*="gsf_home_v154_live_155"]) [data-testid="stVerticalBlock"]{
        row-gap:0 !important;
        gap:0 !important;
      }
      [data-testid="stCustomComponentV1"]:has(iframe[title*="gsf_home_v154"]),
      [data-testid="stCustomComponentV1"]:has(iframe[title*="gsf_home_v154_live_155"]),
      [data-testid="stElementContainer"]:has(iframe[title*="gsf_home_v154"]),
      [data-testid="stElementContainer"]:has(iframe[title*="gsf_home_v154_live_155"]){
        width:100% !important;
        max-width:none !important;
        min-height:0 !important;
        margin:0 !important;
        padding:0 !important;
        transform:none !important;
      }
    }
</style>
    """)

    _gsf_v154_duration=int(st.session_state.get("gsf_v154_duration",15) or 15)
    if _gsf_v154_duration not in (15,30):
        _gsf_v154_duration=15
    _gsf_v154_engine=str(st.session_state.get("gsf_v154_engine","") or "")

    _gsf_v154_event=_gsf_render_home_v154(
        loaded=bool(video is not None),
        duration=_gsf_v154_duration,
        engine=_gsf_v154_engine,
        height=900,
        key="gsf_home_v154_live",
    )

    if isinstance(_gsf_v154_event,dict):
        _v154_event=str(_gsf_v154_event.get("event") or "")
        _v154_duration=int(_gsf_v154_event.get("duration") or _gsf_v154_duration or 15)
        _v154_engine=str(_gsf_v154_event.get("engine") or _gsf_v154_engine or "")
        if _v154_duration in (15,30):
            st.session_state["gsf_v154_duration"]=_v154_duration
        if _v154_engine in ("","auto","best","action","reaction","manual"):
            st.session_state["gsf_v154_engine"]=_v154_engine

        # Direct upload finishes in the existing upload server before the
        # component emits this event. A clean rerun lets _gsf_v989_direct_ready
        # materialize the source into the existing pipeline.
        if _v154_event=="upload_complete" and video is None:
            st.rerun()

'''
s=s.replace(anchor,block+anchor,1)

s=s.replace(
    "Gaming Shorts Factory · V152 UI Reset",
    "Gaming Shorts Factory · V154 Structural Home",
)

# Hard migration guards.
for marker in (
    "render_home_v154",
    'key="gsf_home_v154_live"',
    "gsf-v154-parent-shell",
    'with st.container(key="v73-upload-shell")',
):
    if marker not in s:
        raise RuntimeError("V154 marker missing: "+marker)

s=s.rstrip()+"\n# V157: persist lightweight project/UI state at the end of every successful rerun.\n# Video/render payloads stay on disk and are referenced by path, never serialized here.\nif 'GSF_WEB_MODE' in globals() and GSF_WEB_MODE:\n    try:\n        from web.project_state_v157 import save_project as _gsf_save_project_v157\n        _gsf_save_project_v157(st.session_state, GSF_SESSION_ROOT)\n    except Exception:\n        pass\n"+"\n"


# V158 — persistent shell bridge. Creator Hub is a true browser overlay:
# opening/closing it does not rerun Streamlit or unmount the current work.
_shell_v158 = r'''
if GSF_WEB_MODE:
    st.markdown(r"""
    <style id="gsf-v158-shell-bridge">
    #gsf-creator-hub-portal-v107 .gsf-creator-hub-overlay{
      background:transparent !important;
      transition:opacity .22s ease,visibility .22s ease !important;
    }
    #gsf-creator-hub-portal-v107 .gsf-creator-hub-backdrop{
      background:rgba(219,235,244,.52) !important;
      -webkit-backdrop-filter:blur(4px) saturate(.96) !important;
      backdrop-filter:blur(4px) saturate(.96) !important;
      transition:opacity .22s ease !important;
    }
    #gsf-creator-hub-portal-v107 .gsf-creator-hub-shell{
      width:min(1920px,calc(100vw - 20px)) !important;
      height:calc(100dvh - 20px) !important;
      border-radius:30px !important;
      background:#F7FBFF !important;
      transform:scale(.985) !important;
      transition:transform .26s cubic-bezier(.2,.8,.2,1),opacity .22s ease !important;
      opacity:0 !important;
      overflow:hidden !important;
    }
    #gsf-creator-hub-portal-v107 .gsf-creator-hub-overlay.is-open .gsf-creator-hub-shell,
    #gsf-creator-hub-portal-v107 .gsf-creator-hub-overlay:target .gsf-creator-hub-shell{
      transform:scale(1) !important;
      opacity:1 !important;
    }
    #gsf-creator-hub-portal-v107 .gsf-creator-hub-head{display:none !important}
    #gsf-creator-hub-portal-v107 .gsf-creator-hub-frame{
      width:100% !important;height:100% !important;background:#F7FBFF !important;
    }
    @media(max-width:760px){
      #gsf-creator-hub-portal-v107 .gsf-creator-hub-shell{
        width:calc(100vw - 10px) !important;height:calc(100vh - 10px) !important;border-radius:22px !important;
      }
    }
    </style>
    <div class="gsf-script-guard" style="display:none!important"><script>
    (()=>{
      const KEY='gsf_creator_hub_open_v107';
      const closeHub=()=>{
        const panel=document.getElementById('gsf-creator-hub-live-v160')||document.getElementById('gsf-creator-hub-panel');
        if(!panel)return;
        panel.classList.remove('is-open');
        panel.style.opacity='0';panel.style.visibility='hidden';panel.style.pointerEvents='none';
        try{sessionStorage.setItem(KEY,'0')}catch(e){}
        if(location.hash==='#gsf-creator-hub-panel') history.replaceState(null,'',location.pathname+location.search);
      };
      const clickTarget=(words)=>{
        const nodes=[...document.querySelectorAll('button,a,[role=button]')].filter(x=>!x.closest('#gsf-creator-hub-portal-v107'));
        const el=nodes.find(x=>words.some(w=>(x.innerText||x.textContent||'').toLowerCase().includes(w)));
        if(el){el.click();return true}return false;
      };
      const sync=()=>{
        const frame=document.querySelector('#gsf-creator-hub-portal-v107 .gsf-creator-hub-frame');
        if(frame && !String(frame.src||'').includes('/creator-hub-v156/')) frame.src='/creator-hub-v156/';
      };
      sync();
      new MutationObserver(sync).observe(document.body,{childList:true,subtree:true});
      window.addEventListener('message',ev=>{
        if(ev.origin!==location.origin || !ev.data || ev.data.type!=='GSF_SHELL_NAV')return;
        const t=String(ev.data.target||'');
        if(t==='close' || t==='home'){
          closeHub();
          const so=document.getElementById('gsf-social-overlay-v159');
          if(so){so.classList.remove('is-open');so.style.opacity='0';so.style.visibility='hidden';so.style.pointerEvents='none';}
          return
        }
        if(t==='hub'){
          const so=document.getElementById('gsf-social-overlay-v159');
          if(so){so.classList.remove('is-open');so.style.opacity='0';so.style.visibility='hidden';so.style.pointerEvents='none';}
          const hp=document.getElementById('gsf-creator-hub-live-v160');
          if(hp){hp.classList.add('is-open');hp.style.opacity='1';hp.style.visibility='visible';hp.style.pointerEvents='auto';}
          return
        }
        closeHub();
        setTimeout(()=>{
          if(t==='new') clickTarget(['nuovo video','carica il tuo gameplay']);
          else if(t==='resume_draft') clickTarget(['apri game editor','game editor','manuale']);
          else if(t==='social'){
            const so=document.getElementById('gsf-social-overlay-v159');
            if(so){so.classList.add('is-open');so.style.opacity='1';so.style.visibility='visible';so.style.pointerEvents='auto';}
          }
        },210);
      });
    })();
    </script></div>
    """, unsafe_allow_html=True)
'''
s = s.rstrip() + "\n\n" + _shell_v158.lstrip()


# V159 — Social/Share is a persistent surface over the live project.
# V219: compact app-layer shell. Home stays mounted; bottom Game Bar remains visible and clickable.
_social_surface_v159 = r'''
if GSF_WEB_MODE:
    st.markdown(r"""
    <style id="gsf-v159-social-shell">
    #gsf-social-overlay-v159{
      position:fixed;
      left:0;right:0;top:0;bottom:78px;
      z-index:2147483650;
      display:flex;align-items:center;justify-content:center;
      padding:34px clamp(16px,3vw,46px) 14px;
      background:rgba(222,238,247,.48);
      -webkit-backdrop-filter:blur(5px) saturate(.98);
      backdrop-filter:blur(5px) saturate(.98);
      opacity:0;visibility:hidden;pointer-events:none;
      transition:opacity .24s ease,visibility .24s ease;
    }
    #gsf-social-overlay-v159.is-open{opacity:1;visibility:visible;pointer-events:auto}
    #gsf-social-overlay-v159 .gsf-social-shell{
      position:relative;
      width:min(1180px,calc(100vw - 34px));
      height:min(690px,calc(100dvh - 132px));
      border:1px solid rgba(159,193,218,.34);
      border-radius:30px;
      overflow:hidden;
      background:#F7FCFF;
      box-shadow:0 30px 86px rgba(19,45,65,.22),inset 0 1px 0 rgba(255,255,255,.92);
      transform:translateY(10px) scale(.975);
      opacity:0;
      transition:transform .32s cubic-bezier(.16,.84,.24,1),opacity .24s ease;
    }
    #gsf-social-overlay-v159.is-open .gsf-social-shell{transform:translateY(0) scale(1);opacity:1}
    #gsf-social-overlay-v159 iframe{width:100%;height:100%;border:0;background:#F7FCFF}
    #gsf-social-overlay-v159 .gsf-social-close{
      position:absolute;z-index:5;right:13px;top:12px;width:34px;height:34px;
      border:1px solid rgba(158,190,216,.34);border-radius:12px;
      background:rgba(255,255,255,.94);color:#617B9D;font-size:20px;cursor:pointer;
      box-shadow:0 7px 18px rgba(64,104,143,.09)
    }
    @media(max-width:760px){
      #gsf-social-overlay-v159{
        bottom:70px;
        padding:12px 6px 8px;
        align-items:flex-start;
        background:rgba(225,240,248,.44);
      }
      #gsf-social-overlay-v159 .gsf-social-shell{
        width:calc(100vw - 12px);
        height:calc(100dvh - 92px);
        border-radius:22px;
      }
      #gsf-social-overlay-v159 .gsf-social-close{right:9px;top:8px;width:31px;height:31px}
    }
    </style>
    <div id="gsf-social-overlay-v159" aria-hidden="true">
      <section class="gsf-social-shell" role="dialog" aria-modal="false" aria-label="Condividi o scarica">
        <button class="gsf-social-close" type="button" aria-label="Chiudi">×</button>
        <iframe src="/share-v156/?v=281" data-src="/share-v156/" data-loaded="1" title="Condividi o scarica"></iframe>
      </section>
    </div>
    <div class="gsf-script-guard" style="display:none!important"></div>

    """, unsafe_allow_html=True)

    import streamlit.components.v1 as components
    components.html(r"""<!doctype html><html><body style="margin:0;display:none">
    <script>
    ((P)=>{
      const window=P;
      const document=P.document;
      const location=P.location;
    (()=>{
      const o=document.getElementById('gsf-social-overlay-v159');
      if(!o)return;
      const frame=o.querySelector('iframe');
      const ensureFrame=()=>{
        if(frame.dataset.loaded==='1')return;
        frame.src=frame.dataset.src||'/share-v156/';
        frame.dataset.loaded='1';
      };
      const open=(platform='')=>{
        ensureFrame();
        o.classList.add('is-open');
        o.style.opacity='1';o.style.visibility='visible';o.style.pointerEvents='auto';
        o.setAttribute('aria-hidden','false');
        if(platform)setTimeout(()=>{try{frame.contentWindow.postMessage({type:'GSF_SHARE_FOCUS',platform},location.origin)}catch(e){}},90);
      };
      const close=()=>{
        o.classList.remove('is-open');
        o.style.opacity='0';o.style.visibility='hidden';o.style.pointerEvents='none';
        o.setAttribute('aria-hidden','true');
      };
      o.querySelector('.gsf-social-close').onclick=close;
      o.addEventListener('click',e=>{if(e.target===o)close()});

      // Old Streamlit share controls route into the same app layer instead of causing a page change/rerun.
      document.addEventListener('click',e=>{
        const target=e.target&&e.target.closest?e.target.closest('button,a,[role=button]'):null;
        if(!target||target.closest('#gsf-social-overlay-v159'))return;
        const label=(target.innerText||target.textContent||'').trim().toLowerCase();
        if(label.includes('condividi o scarica')||label.includes('apri share hub')){
          e.preventDefault();e.stopPropagation();open();
        }
      },true);

      window.addEventListener('message',e=>{
        if(e.origin!==location.origin||!e.data||e.data.type!=='GSF_SHELL_NAV')return;
        const t=String(e.data.target||'');
        if(t==='social')open(String(e.data.platform||''));
        if(t==='close'||t==='home'||t==='hub'||t==='editor'||t==='ai'||t==='account')close();
      });
    })();

    })(window.parent);
    </script>
    </body></html>""", height=0, scrolling=False)
'''
s = s.rstrip() + "\n\n" + _social_surface_v159.lstrip()


# V160 — guaranteed Creator Hub overlay owned by the current production shell.
# V222: profile-first Creator Hub, app-layer over Home with Game Bar left accessible.
_hub_surface_v160 = r'''
if GSF_WEB_MODE:
    st.markdown(r"""
    <style id="gsf-v160-hub-shell">
    #gsf-creator-hub-live-v160{
      position:fixed;left:0;right:0;top:0;bottom:78px;
      z-index:2147483660;display:flex;align-items:center;justify-content:center;
      padding:24px clamp(14px,2.5vw,38px) 12px;
      background:rgba(222,238,247,.46);
      -webkit-backdrop-filter:blur(5px) saturate(.98);
      backdrop-filter:blur(5px) saturate(.98);
      opacity:0;visibility:hidden;pointer-events:none;
      transition:opacity .24s ease,visibility .24s ease
    }
    #gsf-creator-hub-live-v160.is-open{opacity:1;visibility:visible;pointer-events:auto}
    #gsf-creator-hub-live-v160 .gsf-hub-shell-v160{
      position:relative;width:min(1220px,calc(100vw - 30px));height:min(720px,calc(100dvh - 118px));
      border:1px solid rgba(157,193,219,.35);border-radius:30px;overflow:hidden;background:#F7FCFF;
      box-shadow:0 30px 86px rgba(19,45,65,.22),inset 0 1px 0 rgba(255,255,255,.94);
      transform:scale(.985);opacity:0;
      transition:transform .30s cubic-bezier(.16,.84,.24,1),opacity .24s ease
    }
    #gsf-creator-hub-live-v160.is-open .gsf-hub-shell-v160{transform:scale(1);opacity:1}
    #gsf-creator-hub-live-v160 iframe{width:100%;height:100%;border:0;background:#F7FCFF}
    #gsf-creator-hub-live-v160 .gsf-hub-close-v160{
      position:absolute;z-index:7;right:13px;top:11px;width:34px;height:34px;
      border:1px solid rgba(158,190,216,.34);border-radius:12px;background:rgba(255,255,255,.94);
      color:#617B9D;font-size:20px;cursor:pointer;box-shadow:0 7px 18px rgba(64,104,143,.09)
    }
    @media(max-width:760px){
      #gsf-creator-hub-live-v160{bottom:70px;padding:8px 5px}
      #gsf-creator-hub-live-v160 .gsf-hub-shell-v160{
        width:calc(100vw - 10px);height:calc(100dvh - 84px);border-radius:22px
      }
      #gsf-creator-hub-live-v160 .gsf-hub-close-v160{right:8px;top:7px;width:31px;height:31px}
    }
    </style>
    <div id="gsf-creator-hub-live-v160" aria-hidden="true">
      <section class="gsf-hub-shell-v160" role="dialog" aria-modal="false" aria-label="Creator Hub">
        <button class="gsf-hub-close-v160" type="button" aria-label="Chiudi">×</button>
        <iframe src="/creator-hub-v156/?v=283" data-src="/creator-hub-v156/" data-loaded="1" title="Creator Hub"></iframe>
      </section>
    </div>
    <div class="gsf-script-guard" style="display:none!important"></div>

    """, unsafe_allow_html=True)

    import streamlit.components.v1 as components
    components.html(r"""<!doctype html><html><body style="margin:0;display:none">
    <script>
    ((P)=>{
      const window=P;
      const document=P.document;
      const location=P.location;

    (()=>{
      const o=document.getElementById('gsf-creator-hub-live-v160');if(!o)return;
      const frame=o.querySelector('iframe');
      const close=()=>{o.classList.remove('is-open');o.style.opacity='0';o.style.visibility='hidden';o.style.pointerEvents='none';o.setAttribute('aria-hidden','true')};
      const ensureFrame=()=>{
        if(frame.dataset.loaded==='1')return false;
        frame.src=frame.dataset.src||'/creator-hub-v156/';
        frame.dataset.loaded='1';
        return true;
      };
      const open=()=>{
        const firstLoad=ensureFrame();
        const so=document.getElementById('gsf-social-overlay-v159');if(so){so.classList.remove('is-open');so.style.opacity='0';so.style.visibility='hidden';so.style.pointerEvents='none'}
        const ed=document.getElementById('gsf-editor-overlay-v220');if(ed){ed.classList.remove('is-open');ed.style.opacity='0';ed.style.visibility='hidden';ed.style.pointerEvents='none'}
        const ai=document.getElementById('gsf-ai-overlay-v221');if(ai){ai.classList.remove('is-open');ai.style.opacity='0';ai.style.visibility='hidden';ai.style.pointerEvents='none'}
        o.classList.add('is-open');o.style.opacity='1';o.style.visibility='visible';o.style.pointerEvents='auto';o.setAttribute('aria-hidden','false')
      };
      o.querySelector('.gsf-hub-close-v160').onclick=close;
      o.addEventListener('click',e=>{if(e.target===o)close()});
      window.addEventListener('message',e=>{
        if(e.origin!==location.origin||!e.data||e.data.type!=='GSF_SHELL_NAV')return;
        const t=String(e.data.target||'');
        if(t==='hub'||t==='profile'){
          open();
          const section=String(e.data.section||(t==='profile'?'profile':'profile'));
          const focus=()=>{try{frame.contentWindow.postMessage({type:'GSF_HUB_FOCUS',section},location.origin)}catch(_e){}};
          if(frame.dataset.loaded==='1' && frame.contentWindow){
            if(frame.contentDocument && frame.contentDocument.readyState==='complete')setTimeout(focus,40);
            else frame.addEventListener('load',focus,{once:true});
          }
          return
        }
        if(t==='home'||t==='close'||t==='editor'||t==='social'||t==='ai'||t==='account')close();
      });
    })();
    
    })(window.parent);
    </script>
    </body></html>""", height=0, scrolling=False)
'''
s = s.rstrip() + "\n\n" + _hub_surface_v160.lstrip()

compile(s,str(out),"exec")
out.write_text(s,encoding="utf-8")
print("V154 STRUCTURAL HOME applied:",out)

# V220 — Game Editor is a persistent app-layer over the live Home.
# The existing editor_2027 component is embedded unchanged.
_editor_surface_v220 = r'''
if GSF_WEB_MODE:
    st.markdown(r"""
    <style id="gsf-v220-editor-shell">
    #gsf-editor-overlay-v220{position:fixed;left:0;right:0;top:0;bottom:78px;z-index:2147483655;display:flex;align-items:center;justify-content:center;padding:24px clamp(14px,2.5vw,38px) 12px;background:rgba(222,238,247,.46);-webkit-backdrop-filter:blur(5px) saturate(.98);backdrop-filter:blur(5px) saturate(.98);opacity:0;visibility:hidden;pointer-events:none;transition:opacity .24s ease,visibility .24s ease}
    #gsf-editor-overlay-v220.is-open{opacity:1;visibility:visible;pointer-events:auto}
    #gsf-editor-overlay-v220 .gsf-editor-shell{position:relative;width:min(1260px,calc(100vw - 30px));height:min(760px,calc(100dvh - 118px));border:1px solid rgba(157,193,219,.35);border-radius:30px;overflow:hidden;background:radial-gradient(circle at 8% 6%,rgba(126,214,255,.20),transparent 25%),radial-gradient(circle at 92% 7%,rgba(127,236,197,.18),transparent 26%),linear-gradient(180deg,#FCFEFF,#F6FBFF);box-shadow:0 30px 86px rgba(19,45,65,.22),inset 0 1px 0 rgba(255,255,255,.94);transform:translateY(10px) scale(.975);opacity:0;transition:transform .32s cubic-bezier(.16,.84,.24,1),opacity .24s ease}
    #gsf-editor-overlay-v220.is-open .gsf-editor-shell{transform:translateY(0) scale(1);opacity:1}
    #gsf-editor-overlay-v220 .gsf-editor-head{height:54px;display:flex;align-items:center;justify-content:space-between;padding:0 54px 0 20px;border-bottom:1px solid rgba(148,183,213,.20);color:#0D2A66;font-size:14px;font-weight:900}
    #gsf-editor-overlay-v220 .gsf-editor-head small{display:block;color:#7185A6;font-size:9px;font-weight:700;margin-top:2px}
    #gsf-editor-overlay-v220 .gsf-editor-close{position:absolute;z-index:6;right:13px;top:10px;width:34px;height:34px;border-radius:12px;border:1px solid rgba(158,190,216,.34);background:rgba(255,255,255,.94);color:#617B9D;font-size:20px;cursor:pointer;box-shadow:0 7px 18px rgba(64,104,143,.09)}
    #gsf-editor-overlay-v220 .gsf-editor-body{position:absolute;left:0;right:0;top:54px;bottom:0;display:grid;grid-template-columns:180px 1fr 180px;align-items:center}
    #gsf-editor-overlay-v220 .gsf-editor-frame{width:100%;height:100%;border:0;background:transparent}
    #gsf-editor-overlay-v220 .editor-note{color:#637DA8;font-family:"Segoe Print","Bradley Hand","Comic Sans MS",cursive;font-size:16px;font-weight:600;line-height:1.08;text-align:center;padding:14px;pointer-events:none}
    #gsf-editor-overlay-v220 .editor-note.left{transform:rotate(-4deg)}
    #gsf-editor-overlay-v220 .editor-note.right{transform:rotate(4deg)}
    #gsf-editor-overlay-v220 .editor-note span{display:block;transition:opacity .42s ease,filter .42s ease,transform .42s ease}
    #gsf-editor-overlay-v220 .editor-note span.out{opacity:0;filter:blur(7px);transform:translateY(-8px) scale(.93)}
    @keyframes gsfEditorWrite{0%{opacity:0;filter:blur(8px);transform:translateY(10px) scale(.91)}70%{opacity:1;filter:blur(.5px);transform:translateY(-2px) scale(1.02)}100%{opacity:1;filter:none;transform:none}}
    #gsf-editor-overlay-v220 .editor-note span.in{animation:gsfEditorWrite 1.05s cubic-bezier(.18,.72,.2,1) 1}
    @media(max-width:900px){#gsf-editor-overlay-v220{bottom:70px;padding:8px 5px}#gsf-editor-overlay-v220 .gsf-editor-shell{width:calc(100vw - 10px);height:calc(100dvh - 84px);border-radius:22px}#gsf-editor-overlay-v220 .gsf-editor-body{grid-template-columns:1fr;top:48px}#gsf-editor-overlay-v220 .editor-note{display:none}#gsf-editor-overlay-v220 .gsf-editor-head{height:48px;padding-left:14px}#gsf-editor-overlay-v220 .gsf-editor-close{top:7px;right:8px;width:31px;height:31px}}
    </style>
    <div id="gsf-editor-overlay-v220" aria-hidden="true">
      <section class="gsf-editor-shell" role="dialog" aria-modal="false" aria-label="Game Editor">
        <button class="gsf-editor-close" type="button" aria-label="Chiudi">×</button>
        <div class="gsf-editor-head"><div>Game Editor<small>Il tuo gameplay resta nel progetto mentre modifichi.</small></div></div>
        <div class="gsf-editor-body">
          <div class="editor-note left"><span id="gsf-editor-note-left">Qui modelli<br>la tua giocata</span></div>
          <iframe class="gsf-editor-frame" src="/editor-live/?v=281" data-src="/editor-live/" data-loaded="1" title="Game Editor"></iframe>
          <div class="editor-note right"><span id="gsf-editor-note-right">Tocca uno strumento<br>e guarda cosa cambia</span></div>
        </div>
      </section>
    </div>
    <div class="gsf-script-guard" style="display:none!important"></div>

    """, unsafe_allow_html=True)

    import streamlit.components.v1 as components
    components.html(r"""<!doctype html><html><body style="margin:0;display:none">
    <script>
    ((P)=>{
      const window=P;
      const document=P.document;
      const location=P.location;

    (()=>{
      const o=document.getElementById('gsf-editor-overlay-v220'); if(!o)return;
      const frame=o.querySelector('.gsf-editor-frame'),left=document.getElementById('gsf-editor-note-left'),right=document.getElementById('gsf-editor-note-right');
      let seq=0;
      const copies={idle:['Qui modelli<br>la tua giocata','Tocca uno strumento<br>e guarda cosa cambia'],frame:['Trova il punto<br>giusto','Inquadra l’azione<br>senza perdere il gameplay'],cover:['Scegli il frame<br>che racconta tutto','La cover deve<br>fermarsi negli occhi'],look:['Dagli il tuo<br>look','Più pulito, più gaming<br>o più cinematico'],caption:['Fai parlare<br>il momento','Le parole entrano<br>dove serve'],audio:['Fallo sentire','Voce, gioco e impatto<br>devono respirare insieme'],ai:['Lascia leggere<br>la scena alla Game AI','Ti aiuta a seguire<br>ciò che conta davvero'],play:['Guardalo vivere','Controlla il risultato<br>prima di chiudere'],done:['Ci siamo','Quando ti convince<br>torna al tuo Short']};
      const morph=(el,html,s)=>{if(!el||el.innerHTML===html)return;el.classList.remove('in');el.classList.add('out');setTimeout(()=>{if(s!==seq)return;el.innerHTML=html;el.classList.remove('out');void el.offsetWidth;el.classList.add('in');setTimeout(()=>el.classList.remove('in'),1100)},420)};
      const guide=(key)=>{const c=copies[key]||copies.idle,s=++seq;morph(left,c[0],s);morph(right,c[1],s)};
      const wire=()=>{try{const d=frame.contentDocument;if(!d)return;d.addEventListener('click',ev=>{const b=ev.target.closest&&ev.target.closest('button');if(!b)return;const t=(b.innerText||b.textContent||'').trim().toUpperCase();if(t.includes('FRAME'))guide('frame');else if(t.includes('COVER'))guide('cover');else if(t.includes('LOOK'))guide('look');else if(t.includes('CAPTION'))guide('caption');else if(t.includes('AUDIO'))guide('audio');else if(t.includes('GAME AI'))guide('ai');else if(t.includes('PLAY')||t.includes('PAUSE'))guide('play');else if(t.includes('DONE'))guide('done')},true)}catch(e){}};
      const KEY='gsf_editor_overlay_open_v223';
      let editorMeta={video_url:'',initial_state:{}};
      const sendRender=()=>{
        try{
          frame.contentWindow.postMessage({
            type:'streamlit:render',
            args:{
              video_url:String(editorMeta.video_url||'/editor-media/current'),
              initial_state:(editorMeta.initial_state&&typeof editorMeta.initial_state==='object')?editorMeta.initial_state:{},
              event_map:[],
              event_duration:Number((editorMeta.initial_state||{}).sourceDuration)||15,
              vision_profile:'Auto',vision_zones:[],brain_context:{},height:720
            }
          },location.origin);
        }catch(e){}
      };
      frame.addEventListener('load',()=>{wire();setTimeout(sendRender,70)});
      const open=(remember=true)=>{
        // V249: switch page immediately; refresh editor state after the surface is visible.
        o.classList.add('is-open');o.style.opacity='1';o.style.visibility='visible';o.style.pointerEvents='auto';o.setAttribute('aria-hidden','false');
        if(remember)try{sessionStorage.setItem(KEY,'1')}catch(e){}
        guide('idle');

        if(frame.dataset.loaded!=='1'){
          frame.src=(frame.dataset.src||'/editor-live/')+'?v=224';
          frame.dataset.loaded='1';
        }else{
          setTimeout(sendRender,16);
        }

        fetch('/editor/state',{cache:'no-store',credentials:'same-origin'})
          .then(r=>r.json().then(j=>({ok:r.ok,j})))
          .then(({ok,j})=>{
            if(ok&&j&&j.ok){
              editorMeta=j;
              setTimeout(sendRender,0);
            }
          })
          .catch(()=>{});
      };
      const close=()=>{o.classList.remove('is-open');o.style.opacity='0';o.style.visibility='hidden';o.style.pointerEvents='none';o.setAttribute('aria-hidden','true');try{sessionStorage.setItem(KEY,'0')}catch(e){}};
      o.querySelector('.gsf-editor-close').onclick=close;o.addEventListener('click',e=>{if(e.target===o)close()});
      window.addEventListener('message',e=>{
        if(e.source===frame.contentWindow&&e.data&&e.data.type==='streamlit:setComponentValue'){
          const state=e.data.value;
          if(state&&typeof state==='object'){
            editorMeta.initial_state=state;
            fetch('/editor/state/save',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json'},body:JSON.stringify({state})}).catch(()=>{});
            guide('done');
          }
          return;
        }
        if(e.origin!==location.origin||!e.data||e.data.type!=='GSF_SHELL_NAV')return;
        const t=String(e.data.target||'');
        if(t==='editor'){open();return}
        if(t==='close'||t==='home'||t==='social'||t==='hub'||t==='ai'||t==='account')close();
      });
      try{if(sessionStorage.getItem(KEY)==='1')setTimeout(()=>open(false),90)}catch(e){};
    })();
    
    })(window.parent);
    </script>
    </body></html>""", height=0, scrolling=False)
'''
s = s.rstrip() + "\n\n" + _editor_surface_v220.lstrip()

# V221 — AI engines are a persistent app-layer over the live Home.
_ai_surface_v221 = r'''
if GSF_WEB_MODE:
    st.markdown(r"""
    <style id="gsf-v221-ai-shell">
    #gsf-ai-overlay-v221{position:fixed;left:0;right:0;top:0;bottom:78px;z-index:2147483654;display:flex;align-items:center;justify-content:center;padding:24px clamp(14px,2.5vw,38px) 12px;background:rgba(222,238,247,.46);-webkit-backdrop-filter:blur(5px) saturate(.98);backdrop-filter:blur(5px) saturate(.98);opacity:0;visibility:hidden;pointer-events:none;transition:opacity .24s ease,visibility .24s ease}
    #gsf-ai-overlay-v221.is-open{opacity:1;visibility:visible;pointer-events:auto}
    #gsf-ai-overlay-v221 .gsf-ai-shell{position:relative;width:min(1240px,calc(100vw - 30px));height:min(730px,calc(100dvh - 118px));border:1px solid rgba(157,193,219,.35);border-radius:30px;overflow:hidden;background:#F7FCFF;box-shadow:0 30px 86px rgba(19,45,65,.22),inset 0 1px 0 rgba(255,255,255,.94);transform:translateY(10px) scale(.975);opacity:0;transition:transform .32s cubic-bezier(.16,.84,.24,1),opacity .24s ease}
    #gsf-ai-overlay-v221.is-open .gsf-ai-shell{transform:translateY(0) scale(1);opacity:1}
    #gsf-ai-overlay-v221 iframe{width:100%;height:100%;border:0;background:#F7FCFF}
    #gsf-ai-overlay-v221 .gsf-ai-close{position:absolute;z-index:7;right:13px;top:11px;width:34px;height:34px;border-radius:12px;border:1px solid rgba(158,190,216,.34);background:rgba(255,255,255,.94);color:#617B9D;font-size:20px;cursor:pointer;box-shadow:0 7px 18px rgba(64,104,143,.09)}
    @media(max-width:760px){#gsf-ai-overlay-v221{bottom:70px;padding:8px 5px}#gsf-ai-overlay-v221 .gsf-ai-shell{width:calc(100vw - 10px);height:calc(100dvh - 84px);border-radius:22px}#gsf-ai-overlay-v221 .gsf-ai-close{right:8px;top:7px;width:31px;height:31px}}
    </style>
    <div id="gsf-ai-overlay-v221" aria-hidden="true">
      <section class="gsf-ai-shell" role="dialog" aria-modal="false" aria-label="Motori IA">
        <button class="gsf-ai-close" type="button" aria-label="Chiudi">×</button>
        <iframe src="/ai-v221/?v=281" data-src="/ai-v221/" data-loaded="1" title="Motori IA"></iframe>
      </section>
    </div>
    <div class="gsf-script-guard" style="display:none!important"></div>

    """, unsafe_allow_html=True)

    import streamlit.components.v1 as components
    components.html(r"""<!doctype html><html><body style="margin:0;display:none">
    <script>
    ((P)=>{
      const window=P;
      const document=P.document;
      const location=P.location;

    (()=>{
      const KEY='gsf_ai_overlay_open_v221';
      const o=document.getElementById('gsf-ai-overlay-v221');if(!o)return;
      const frame=o.querySelector('iframe');
      const broadcastHome=(payload)=>{
        document.querySelectorAll('iframe').forEach(f=>{
          try{if(f!==frame&&f.contentWindow)f.contentWindow.postMessage(payload,location.origin)}catch(e){}
        });
      };
      const forwardState=(data)=>{
        try{frame.contentWindow.postMessage({type:'GSF_AI_STATE',state:{loaded:!!data.loaded,duration:Number(data.duration)||15,engine:String(data.engine||''),previews:Array.isArray(data.previews)?data.previews:[]}},location.origin)}catch(e){}
      };
      const ensureFrame=()=>{
        if(frame.dataset.loaded==='1')return;
        frame.src=frame.dataset.src||'/ai-v221/';
        frame.dataset.loaded='1';
      };
      const open=(remember=true)=>{
        ensureFrame();
        const so=document.getElementById('gsf-social-overlay-v159');if(so){so.classList.remove('is-open');so.style.opacity='0';so.style.visibility='hidden';so.style.pointerEvents='none'}
        const ed=document.getElementById('gsf-editor-overlay-v220');if(ed){ed.classList.remove('is-open');ed.style.opacity='0';ed.style.visibility='hidden';ed.style.pointerEvents='none'}
        o.classList.add('is-open');o.style.opacity='1';o.style.visibility='visible';o.style.pointerEvents='auto';o.setAttribute('aria-hidden','false');
        if(remember)try{sessionStorage.setItem(KEY,'1')}catch(e){}
        setTimeout(()=>broadcastHome({type:'GSF_AI_COMMAND',action:'get_state'}),80);
      };
      const close=()=>{o.classList.remove('is-open');o.style.opacity='0';o.style.visibility='hidden';o.style.pointerEvents='none';o.setAttribute('aria-hidden','true');try{sessionStorage.setItem(KEY,'0')}catch(e){}};
      o.querySelector('.gsf-ai-close').onclick=close;o.addEventListener('click',e=>{if(e.target===o)close()});
      window.addEventListener('message',e=>{
        if(e.origin!==location.origin||!e.data)return;
        if(e.data.type==='GSF_AI_UI'){
          const action=String(e.data.action||'');
          if(action==='ready'){broadcastHome({type:'GSF_AI_COMMAND',action:'get_state'});return}
          broadcastHome({type:'GSF_AI_COMMAND',action,duration:e.data.duration,engine:e.data.engine,index:e.data.index});
          return;
        }
        if(e.data.type!=='GSF_SHELL_NAV')return;
        const t=String(e.data.target||'');
        if(t==='ai'){open();return}
        if(t==='ai-state'){forwardState(e.data);return}
        if(t==='editor'||t==='social'||t==='hub'||t==='home'||t==='close'||t==='account')close();
      });
      try{if(sessionStorage.getItem(KEY)==='1')setTimeout(()=>open(false),90)}catch(e){}
    })();
    
    })(window.parent);
    </script>
    </body></html>""", height=0, scrolling=False)
'''
s = s.rstrip() + "\n\n" + _ai_surface_v221.lstrip()


# V223.1 — account/profile access stays inside the app shell.
_account_surface_v223 = r'''
if GSF_WEB_MODE:
    st.markdown(r"""
    <style id="gsf-v223-account-shell">
    #gsf-account-overlay-v223{position:fixed;left:0;right:0;top:0;bottom:78px;z-index:2147483662;display:flex;align-items:center;justify-content:center;padding:24px clamp(14px,2.5vw,38px) 12px;background:rgba(222,238,247,.46);-webkit-backdrop-filter:blur(5px) saturate(.98);backdrop-filter:blur(5px) saturate(.98);opacity:0;visibility:hidden;pointer-events:none;transition:opacity .24s ease,visibility .24s ease}
    #gsf-account-overlay-v223.is-open{opacity:1;visibility:visible;pointer-events:auto}
    #gsf-account-overlay-v223 .gsf-account-shell{position:relative;width:min(980px,calc(100vw - 30px));height:min(680px,calc(100dvh - 118px));border:1px solid rgba(157,193,219,.35);border-radius:30px;overflow:hidden;background:#F7FCFF;box-shadow:0 30px 86px rgba(19,45,65,.22),inset 0 1px 0 rgba(255,255,255,.94);transform:translateY(10px) scale(.975);opacity:0;transition:transform .30s cubic-bezier(.16,.84,.24,1),opacity .24s ease}
    #gsf-account-overlay-v223.is-open .gsf-account-shell{transform:translateY(0) scale(1);opacity:1}
    #gsf-account-overlay-v223 iframe{width:100%;height:100%;border:0;background:#F7FCFF}
    #gsf-account-overlay-v223 .gsf-account-close{position:absolute;z-index:7;right:13px;top:11px;width:34px;height:34px;border:1px solid rgba(158,190,216,.34);border-radius:12px;background:rgba(255,255,255,.94);color:#617B9D;font-size:20px;cursor:pointer}
    @media(max-width:760px){#gsf-account-overlay-v223{bottom:70px;padding:8px 5px}#gsf-account-overlay-v223 .gsf-account-shell{width:calc(100vw - 10px);height:calc(100dvh - 84px);border-radius:22px}#gsf-account-overlay-v223 .gsf-account-close{right:8px;top:7px;width:31px;height:31px}}
    </style>
    <div id="gsf-account-overlay-v223" aria-hidden="true">
      <section class="gsf-account-shell" role="dialog" aria-modal="false" aria-label="Account">
        <button class="gsf-account-close" type="button" aria-label="Chiudi">×</button>
        <iframe src="/account/?v=226" data-src="/account/" data-loaded="1" title="Account"></iframe>
      </section>
    </div>
    <div class="gsf-script-guard" style="display:none!important"></div>

    """, unsafe_allow_html=True)

    import streamlit.components.v1 as components
    components.html(r"""<!doctype html><html><body style="margin:0;display:none">
    <script>
    ((P)=>{
      const window=P;
      const document=P.document;
      const location=P.location;

    (()=>{
      const o=document.getElementById('gsf-account-overlay-v223');if(!o)return;
      const frame=o.querySelector('iframe');
      const close=()=>{o.classList.remove('is-open');o.style.opacity='0';o.style.visibility='hidden';o.style.pointerEvents='none';o.setAttribute('aria-hidden','true')};
      const open=()=>{if(frame.dataset.loaded!=='1'){frame.src=(frame.dataset.src||'/account/')+'?v=224';frame.dataset.loaded='1'}o.classList.add('is-open');o.style.opacity='1';o.style.visibility='visible';o.style.pointerEvents='auto';o.setAttribute('aria-hidden','false')};
      o.querySelector('.gsf-account-close').onclick=close;
      o.addEventListener('click',e=>{if(e.target===o)close()});
      window.addEventListener('message',e=>{
        if(e.origin!==location.origin||!e.data||e.data.type!=='GSF_SHELL_NAV')return;
        const t=String(e.data.target||'');
        if(t==='account'){close();window.postMessage({type:'GSF_SHELL_NAV',target:'hub',section:'profile'},location.origin);return}
        if(t==='home'||t==='close'||t==='hub'||t==='editor'||t==='social'||t==='ai')close();
      });
    })();
    
    })(window.parent);
    </script>
    </body></html>""", height=0, scrolling=False)
'''
s = s.rstrip() + "\n\n" + _account_surface_v223.lstrip()


# V223.4 — V223.2 inline render-state injection removed.
# Editor state remains persisted by /editor/state and /editor/state/save.
# Final-render reconciliation will be attached through a safe boundary, not by
# splicing inside an existing try/except block.

# V224 legacy JS-regex escape cleanup: generated Python source must contain
# a doubled backslash so Python emits the intended JS /\s/ regex without SyntaxWarning.
s=s.replace("replace(/"+chr(92)+"s/g,'')","replace(/"+chr(92)+chr(92)+"s/g,'')")
# V249 FULL PAGE APP SHELL
# Navigation surfaces are true opaque pages. Home remains mounted for state,
# but is never visible behind Editor / AI / Hub / Projects / Social / Account.
# Each page gets its own persistent Game Bar, so transitions feel like moving
# inside the same app instead of opening a translucent modal.
_page_shell_v249 = r'''
if GSF_WEB_MODE:
    st.markdown(r"""
    <style id="gsf-v249-full-page-shell">
    :root{--gsf-pagebar-h:78px}

    #gsf-social-overlay-v159,
    #gsf-creator-hub-live-v160,
    #gsf-editor-overlay-v220,
    #gsf-ai-overlay-v221,
    #gsf-account-overlay-v223{
      position:fixed!important;
      inset:0!important;
      bottom:0!important;
      padding:0 0 var(--gsf-pagebar-h)!important;
      display:flex!important;
      align-items:stretch!important;
      justify-content:stretch!important;
      background:#F7FCFF!important;
      -webkit-backdrop-filter:none!important;
      backdrop-filter:none!important;
      opacity:0;
      visibility:hidden;
      pointer-events:none;
      transition:none!important;
      overflow:hidden!important;
    }

    #gsf-social-overlay-v159.is-open,
    #gsf-creator-hub-live-v160.is-open,
    #gsf-editor-overlay-v220.is-open,
    #gsf-ai-overlay-v221.is-open,
    #gsf-account-overlay-v223.is-open{
      opacity:1!important;
      visibility:visible!important;
      pointer-events:auto!important;
    }

    #gsf-social-overlay-v159 .gsf-social-shell,
    #gsf-creator-hub-live-v160 .gsf-hub-shell-v160,
    #gsf-editor-overlay-v220 .gsf-editor-shell,
    #gsf-ai-overlay-v221 .gsf-ai-shell,
    #gsf-account-overlay-v223 .gsf-account-shell{
      position:relative!important;
      width:100%!important;
      max-width:none!important;
      height:calc(100dvh - var(--gsf-pagebar-h))!important;
      max-height:none!important;
      margin:0!important;
      border:0!important;
      border-radius:0!important;
      background:#F7FCFF!important;
      box-shadow:none!important;
      opacity:1!important;
      transform:translateX(10px)!important;
      transition:transform .11s cubic-bezier(.2,.82,.25,1)!important;
      overflow:hidden!important;
    }

    #gsf-social-overlay-v159.is-open .gsf-social-shell,
    #gsf-creator-hub-live-v160.is-open .gsf-hub-shell-v160,
    #gsf-editor-overlay-v220.is-open .gsf-editor-shell,
    #gsf-ai-overlay-v221.is-open .gsf-ai-shell,
    #gsf-account-overlay-v223.is-open .gsf-account-shell{
      transform:translateX(0)!important;
      opacity:1!important;
    }

    #gsf-social-overlay-v159 iframe,
    #gsf-creator-hub-live-v160 iframe,
    #gsf-editor-overlay-v220 iframe,
    #gsf-ai-overlay-v221 iframe,
    #gsf-account-overlay-v223 iframe{
      background:#F7FCFF!important;
    }

    /* One Game Bar owned by the active page, never the Home underneath. */
    #gsf-page-nav-v249{
      position:fixed;
      left:50%;
      bottom:10px;
      transform:translateX(-50%);
      z-index:2147483647;
      width:min(760px,72vw);
      height:58px;
      min-height:58px;
      padding:4px 10px;
      display:grid;
      grid-template-columns:repeat(5,1fr);
      gap:4px;
      border:1px solid rgba(139,181,218,.30);
      border-radius:999px;
      background:rgba(255,255,255,.96);
      box-shadow:0 10px 28px rgba(59,104,148,.11),0 0 0 4px rgba(226,243,255,.30),inset 0 1px 0 #fff;
      -webkit-backdrop-filter:blur(22px);
      backdrop-filter:blur(22px);
      opacity:0;
      visibility:hidden;
      pointer-events:none;
      transition:none;
    }
    #gsf-page-nav-v249.is-open{
      opacity:1;
      visibility:visible;
      pointer-events:auto;
    }
    #gsf-page-nav-v249 .gsf-page-nav-item{
      border:0;
      background:transparent;
      border-radius:21px;
      padding:2px 3px;
      color:#8192AA;
      display:flex;
      flex-direction:column;
      align-items:center;
      justify-content:center;
      gap:2px;
      font-size:8px;
      font-weight:800;
      cursor:pointer;
    }
    #gsf-page-nav-v249 .gsf-page-nav-item svg{
      width:19px;
      height:19px;
      padding:5px;
      box-sizing:content-box;
      border-radius:50%;
      color:currentColor;
      fill:none;
      stroke:currentColor;
      stroke-width:2;
      stroke-linecap:round;
      stroke-linejoin:round;
      background:linear-gradient(145deg,#F9FCFF,#EDF5FC);
      border:1px solid rgba(150,184,215,.24);
    }
    #gsf-page-nav-v249 .gsf-page-nav-item.active{
      color:#4F93D7;
      background:rgba(219,241,255,.70);
    }
    #gsf-page-nav-v249 .gsf-page-nav-item.active svg{
      color:#4F93D7;
      background:linear-gradient(145deg,#E8F5FF,#D8EBFF);
    }

    @media(max-width:760px){
      :root{--gsf-pagebar-h:70px}
      #gsf-page-nav-v249{
        width:calc(100vw - 24px);
        height:58px;
        min-height:58px;
        bottom:6px;
        padding:4px 8px;
      }
      #gsf-page-nav-v249 .gsf-page-nav-item{font-size:7px}
      #gsf-page-nav-v249 .gsf-page-nav-item svg{width:18px;height:18px;padding:5px}
    }

    @media(prefers-reduced-motion:reduce){
      #gsf-social-overlay-v159 .gsf-social-shell,
      #gsf-creator-hub-live-v160 .gsf-hub-shell-v160,
      #gsf-editor-overlay-v220 .gsf-editor-shell,
      #gsf-ai-overlay-v221 .gsf-ai-shell,
      #gsf-account-overlay-v223 .gsf-account-shell{
        transition:none!important;
        transform:none!important;
      }
    }
    </style>

    <nav id="gsf-page-nav-v249" aria-label="Navigazione pagina">
      <button class="gsf-page-nav-item" data-target="home" type="button">
        <svg viewBox="0 0 32 32"><path d="M4 14 16 4l12 10"/><path d="M7 13v14h18V13"/><path d="M13 27v-8h6v8"/></svg><span>Home</span>
      </button>
      <button class="gsf-page-nav-item" data-target="hub" data-section="dashboard" type="button">
        <svg viewBox="0 0 32 32"><rect x="5" y="5" width="8" height="8" rx="2"/><rect x="19" y="5" width="8" height="8" rx="2"/><rect x="5" y="19" width="8" height="8" rx="2"/><rect x="19" y="19" width="8" height="8" rx="2"/></svg><span>Hub</span>
      </button>
      <button class="gsf-page-nav-item" data-target="hub" data-section="shorts" data-active="shorts" type="button">
        <svg viewBox="0 0 32 32"><rect x="7" y="4" width="18" height="24" rx="5"/><path d="m13 11 8 5-8 5Z"/></svg><span>Shorts</span>
      </button>
      <button class="gsf-page-nav-item" data-target="hub" data-section="project" data-active="projects" type="button">
        <svg viewBox="0 0 32 32"><path d="M4 10h9l3 3h12v14H4Z"/><path d="M4 10V7h10l3 3"/></svg><span>Progetti</span>
      </button>
      <button class="gsf-page-nav-item" data-target="hub" data-section="social" data-active="social" type="button">
        <svg viewBox="0 0 32 32"><circle cx="24" cy="7" r="3"/><circle cx="8" cy="16" r="3"/><circle cx="24" cy="25" r="3"/><path d="m11 14.5 10-5.7M11 17.5l10 5.7"/></svg><span>Social</span>
      </button>
    </nav>
    """, unsafe_allow_html=True)

    import streamlit.components.v1 as components
    components.html(r"""<!doctype html><html><body style="margin:0;display:none"><script>
    ((P)=>{
      const document=P.document;
      const nav=document.getElementById('gsf-page-nav-v249');
      if(!nav)return;

      const ids={
        hub:'gsf-creator-hub-live-v160',
        editor:'gsf-editor-overlay-v220',
        social:'gsf-social-overlay-v159',
        ai:'gsf-ai-overlay-v221',
        account:'gsf-account-overlay-v223'
      };

      let lastTarget='home',lastSection='';

      const anyOpen=()=>Object.values(ids).some(id=>{
        const el=document.getElementById(id);
        return !!(el&&el.classList.contains('is-open'));
      });

      const sync=()=>{
        nav.classList.toggle('is-open',anyOpen());
        nav.querySelectorAll('.gsf-page-nav-item').forEach(b=>{
          const target=String(b.dataset.target||'');
          const section=String(b.dataset.section||'');
          const activeKey=String(b.dataset.active||target);
          let active=false;
          if(activeKey==='projects') active=(lastTarget==='hub'&&lastSection==='project');
          else if(activeKey==='shorts') active=(lastTarget==='hub'&&lastSection==='shorts');
          else if(activeKey==='social') active=(lastTarget==='hub'&&lastSection==='social');
          else if(target==='hub') active=(lastTarget==='hub'&&lastSection!=='project'&&lastSection!=='shorts'&&lastSection!=='social');
          else active=(lastTarget===target);
          b.classList.toggle('active',active);
        });
      };

      const go=(target,section='')=>{
        lastTarget=target;
        lastSection=section;
        P.postMessage({type:'GSF_SHELL_NAV',target,section},P.location.origin);
        sync();
      };

      nav.querySelectorAll('.gsf-page-nav-item').forEach(b=>{
        b.addEventListener('click',()=>{
          go(String(b.dataset.target||'home'),String(b.dataset.section||''));
        });
      });

      P.addEventListener('message',e=>{
        if(e.origin!==P.location.origin||!e.data||e.data.type!=='GSF_SHELL_NAV')return;
        const t=String(e.data.target||'');
        if(t==='home'||t==='close'){
          lastTarget='home';lastSection='';
        }else if(t==='profile'){
          lastTarget='hub';lastSection='profile';
        }else if(t==='hub'){
          lastTarget='hub';lastSection=String(e.data.section||'profile');
        }else if(t==='editor'||t==='social'||t==='ai'||t==='account'){
          lastTarget=t;lastSection='';
        }
        queueMicrotask(sync);
      });

      const obs=new P.MutationObserver(sync);
      Object.values(ids).forEach(id=>{
        const el=document.getElementById(id);
        if(el)obs.observe(el,{attributes:true,attributeFilter:['class','style','aria-hidden']});
      });

      document.querySelectorAll(
        '#gsf-social-overlay-v159 .gsf-social-close,'+
        '#gsf-creator-hub-live-v160 .gsf-hub-close-v160,'+
        '#gsf-editor-overlay-v220 .gsf-editor-close,'+
        '#gsf-ai-overlay-v221 .gsf-ai-close,'+
        '#gsf-account-overlay-v223 .gsf-account-close'
      ).forEach(b=>b.addEventListener('click',()=>queueMicrotask(sync)));

      sync();
    })(window.parent);
    </script></body></html>""", height=0, scrolling=False)
'''
s = s.rstrip() + "\n\n" + _page_shell_v249.lstrip()
# END V249 FULL PAGE APP SHELL
# V250 PAGE VISUAL SYSTEM
# Shared chrome for all non-Home app pages. Home files remain untouched.
_page_visual_v250 = r'''
if GSF_WEB_MODE:
    st.markdown(r"""
    <style id="gsf-v250-page-visual-system">
    :root{
      --gsf-page-top:44px;
      --gsf-page-bottom:108px;
      --gsf-page-side:clamp(118px,9.5vw,160px);
      --gsf-page-gap:clamp(12px,1.4vw,24px);
      --gsf-page-bg:#F7FCFF;
      --gsf-page-ink:#0D2A66;
      --gsf-page-soft:#7185A6;
    }

    #gsf-social-overlay-v159,
    #gsf-creator-hub-live-v160,
    #gsf-editor-overlay-v220,
    #gsf-ai-overlay-v221,
    #gsf-account-overlay-v223{
      background:
        radial-gradient(circle at 12% 8%,rgba(111,209,255,.15),transparent 23%),
        radial-gradient(circle at 88% 10%,rgba(106,229,185,.13),transparent 24%),
        linear-gradient(180deg,#FEFFFF 0%,#FBFDFF 54%,#F7FCFF 100%)!important;
      overflow:hidden!important;
    }

    .gsf-page-top-v250{
      position:absolute;
      left:0;right:0;top:0;
      height:var(--gsf-page-top);
      display:flex;
      align-items:center;
      justify-content:space-between;
      padding:0 clamp(16px,2vw,34px);
      z-index:20;
      color:#6C81A1;
      pointer-events:none;
    }
    .gsf-page-brand-v250{
      font-size:clamp(10px,.8vw,13px);
      line-height:1;
      font-weight:800;
      letter-spacing:.28em;
      white-space:nowrap;
    }
    .gsf-page-title-v250{
      position:absolute;
      left:50%;
      transform:translateX(-50%);
      color:var(--gsf-page-ink);
      font-size:clamp(11px,.9vw,14px);
      font-weight:900;
      letter-spacing:.03em;
      white-space:nowrap;
    }
    .gsf-page-state-v250{
      min-width:64px;
      text-align:right;
      font-size:8px;
      font-weight:800;
      letter-spacing:.08em;
      opacity:.78;
    }

    .gsf-page-ad-v250{
      position:absolute;
      top:calc(var(--gsf-page-top) + 12px);
      bottom:calc(var(--gsf-page-bottom) + 12px);
      width:var(--gsf-page-side);
      z-index:16;
      display:flex;
      align-items:center;
      justify-content:center;
      padding:10px;
      border:1px solid rgba(150,184,214,.22);
      border-radius:20px;
      background:rgba(255,255,255,.72);
      box-shadow:0 12px 34px rgba(59,104,148,.07),inset 0 1px 0 rgba(255,255,255,.94);
      color:#7D90AD;
      font-size:clamp(8px,.65vw,10px);
      font-weight:700;
      letter-spacing:.03em;
      text-align:center;
      pointer-events:auto;
      overflow:hidden;
    }
    .gsf-page-ad-v250.left{left:clamp(12px,1.4vw,24px)}
    .gsf-page-ad-v250.right{right:clamp(12px,1.4vw,24px)}

    .gsf-page-footer-v250{
      position:absolute;
      left:0;right:0;
      bottom:72px;
      height:30px;
      z-index:20;
      display:grid;
      grid-template-columns:1fr auto 1fr;
      align-items:center;
      gap:12px;
      padding:0 clamp(16px,2vw,34px);
      border-top:1px solid rgba(150,184,214,.18);
      color:#7D90AD;
      pointer-events:none;
    }
    .gsf-page-footer-brand-v250{
      justify-self:start;
      font-size:7px;
      font-weight:700;
    }
    .gsf-page-footer-social-v250{
      justify-self:center;
      display:flex;
      align-items:center;
      gap:6px;
      pointer-events:auto;
    }
    .gsf-page-footer-social-v250 a{
      width:22px;height:22px;
      display:grid;
      place-items:center;
      border-radius:50%;
      background:rgba(255,255,255,.90);
      border:1px solid rgba(150,183,213,.24);
      box-shadow:0 5px 13px rgba(65,105,145,.08);
      text-decoration:none;
      font-size:8px;
      font-weight:900;
    }
    .gsf-page-footer-social-v250 a:nth-child(1){color:#1877F2}
    .gsf-page-footer-social-v250 a:nth-child(2){color:#C13584}
    .gsf-page-footer-social-v250 a:nth-child(3){color:#FF0033}
    .gsf-page-footer-social-v250 a:nth-child(4){color:#111827}
    .gsf-page-footer-social-v250 a:nth-child(5){color:#9146FF}
    .gsf-page-footer-meta-v250{
      justify-self:end;
      font-size:7px;
      font-weight:700;
    }

    /* Each page owns its content area; Home is completely covered. */
    #gsf-social-overlay-v159 .gsf-social-shell,
    #gsf-creator-hub-live-v160 .gsf-hub-shell-v160,
    #gsf-editor-overlay-v220 .gsf-editor-shell,
    #gsf-ai-overlay-v221 .gsf-ai-shell,
    #gsf-account-overlay-v223 .gsf-account-shell{
      position:absolute!important;
      top:var(--gsf-page-top)!important;
      bottom:var(--gsf-page-bottom)!important;
      left:calc(var(--gsf-page-side) + var(--gsf-page-gap) + 12px)!important;
      right:calc(var(--gsf-page-side) + var(--gsf-page-gap) + 12px)!important;
      width:auto!important;
      height:auto!important;
      max-width:none!important;
      max-height:none!important;
      margin:0!important;
      border:1px solid rgba(157,193,219,.22)!important;
      border-radius:24px!important;
      background:rgba(255,255,255,.82)!important;
      box-shadow:0 18px 54px rgba(42,86,126,.09),inset 0 1px 0 rgba(255,255,255,.96)!important;
      transform:none!important;
      transition:none!important;
      opacity:1!important;
      overflow:hidden!important;
    }

    #gsf-editor-overlay-v220 .gsf-editor-head{
      background:rgba(255,255,255,.88)!important;
      border-bottom:1px solid rgba(148,183,213,.18)!important;
    }

    #gsf-social-overlay-v159 iframe,
    #gsf-creator-hub-live-v160 iframe,
    #gsf-editor-overlay-v220 iframe,
    #gsf-ai-overlay-v221 iframe,
    #gsf-account-overlay-v223 iframe{
      width:100%!important;
      height:100%!important;
      border:0!important;
      background:#F7FCFF!important;
    }

    #gsf-page-nav-v249{
      bottom:10px!important;
      height:54px!important;
      min-height:54px!important;
      width:min(760px,72vw)!important;
      padding:3px 10px!important;
      z-index:30!important;
    }

    #gsf-social-overlay-v159 .gsf-social-close,
    #gsf-creator-hub-live-v160 .gsf-hub-close-v160,
    #gsf-editor-overlay-v220 .gsf-editor-close,
    #gsf-ai-overlay-v221 .gsf-ai-close,
    #gsf-account-overlay-v223 .gsf-account-close{
      top:7px!important;
      right:9px!important;
      width:30px!important;
      height:30px!important;
      border-radius:10px!important;
      z-index:24!important;
      box-shadow:0 5px 14px rgba(64,104,143,.07)!important;
    }

    /* Responsive scaling: no giant fixed desktop and no cramped small screen. */
    @media(min-width:1600px) and (min-height:850px){
      :root{
        --gsf-page-top:48px;
        --gsf-page-bottom:114px;
        --gsf-page-side:clamp(145px,9vw,180px);
        --gsf-page-gap:clamp(18px,1.6vw,28px);
      }
      .gsf-page-footer-v250{bottom:76px;height:32px}
      #gsf-page-nav-v249{height:58px!important;min-height:58px!important}
    }

    @media(min-width:761px) and (max-height:720px){
      :root{
        --gsf-page-top:38px;
        --gsf-page-bottom:96px;
        --gsf-page-side:clamp(102px,8.4vw,132px);
        --gsf-page-gap:10px;
      }
      .gsf-page-footer-v250{bottom:65px;height:24px}
      #gsf-page-nav-v249{
        bottom:7px!important;
        height:48px!important;
        min-height:48px!important;
      }
      .gsf-page-ad-v250{
        top:calc(var(--gsf-page-top) + 8px);
        bottom:calc(var(--gsf-page-bottom) + 8px);
      }
    }

    @media(max-width:1000px) and (min-width:761px){
      :root{
        --gsf-page-side:86px;
        --gsf-page-gap:8px;
      }
      .gsf-page-ad-v250{
        width:86px;
        border-radius:16px;
        font-size:8px;
      }
    }

    @media(max-width:760px){
      :root{
        --gsf-page-top:32px;
        --gsf-page-bottom:88px;
        --gsf-page-side:0px;
        --gsf-page-gap:0px;
      }

      .gsf-page-top-v250{
        height:32px;
        padding:0 10px;
      }
      .gsf-page-brand-v250{
        font-size:7.5px;
        letter-spacing:.22em;
      }
      .gsf-page-title-v250{
        font-size:9px;
      }
      .gsf-page-state-v250{font-size:7px}

      .gsf-page-ad-v250{
        display:none!important;
      }

      #gsf-social-overlay-v159 .gsf-social-shell,
      #gsf-creator-hub-live-v160 .gsf-hub-shell-v160,
      #gsf-editor-overlay-v220 .gsf-editor-shell,
      #gsf-ai-overlay-v221 .gsf-ai-shell,
      #gsf-account-overlay-v223 .gsf-account-shell{
        top:var(--gsf-page-top)!important;
        bottom:var(--gsf-page-bottom)!important;
        left:5px!important;
        right:5px!important;
        border-radius:18px!important;
      }

      .gsf-page-footer-v250{
        display:none!important;
      }

      #gsf-page-nav-v249{
        width:calc(100vw - 20px)!important;
        bottom:5px!important;
        height:56px!important;
        min-height:56px!important;
      }
    }
    </style>
    """, unsafe_allow_html=True)

    import streamlit.components.v1 as components
    components.html(r"""<!doctype html><html><body style="margin:0;display:none"><script>
    ((P)=>{
      const d=P.document;
      const pages=[
        ['gsf-social-overlay-v159','Social'],
        ['gsf-creator-hub-live-v160','Creator Hub'],
        ['gsf-editor-overlay-v220','Game Editor'],
        ['gsf-ai-overlay-v221','Crea con IA'],
        ['gsf-account-overlay-v223','Account']
      ];

      const chrome=(title)=>`
        <div class="gsf-page-top-v250">
          <div class="gsf-page-brand-v250">GAMING SHORTS FACTORY</div>
          <div class="gsf-page-title-v250">${title}</div>
          <div class="gsf-page-state-v250">GSF</div>
        </div>
        <aside class="gsf-page-ad-v250 left"><span>Spazio pubblicitario</span></aside>
        <aside class="gsf-page-ad-v250 right"><span>Spazio pubblicitario</span></aside>
        <footer class="gsf-page-footer-v250">
          <span class="gsf-page-footer-brand-v250">Gaming Shorts Factory</span>
          <div class="gsf-page-footer-social-v250" aria-label="Canali social">
            <a href="https://www.facebook.com/profile.php?id=61595124112318&amp;locale=it_IT" target="_blank" rel="noopener noreferrer" aria-label="Facebook">f</a>
            <a href="https://www.instagram.com/gamingshortsfactory/" target="_blank" rel="noopener noreferrer" aria-label="Instagram">◎</a>
            <a href="https://www.youtube.com/@Dans222nrg" target="_blank" rel="noopener noreferrer" aria-label="YouTube">▶</a>
            <a href="https://www.tiktok.com/@gamingshortsfactory" target="_blank" rel="noopener noreferrer" aria-label="TikTok">♪</a>
            <a href="https://www.twitch.tv/dan222s86" target="_blank" rel="noopener noreferrer" aria-label="Twitch">◈</a>
          </div>
          <span class="gsf-page-footer-meta-v250">© 2026</span>
        </footer>`;

      pages.forEach(([id,title])=>{
        const el=d.getElementById(id);
        if(!el||el.querySelector('.gsf-page-top-v250'))return;
        el.insertAdjacentHTML('afterbegin',chrome(title));
      });

      // Fast-open policy: keep all route frames warm. They are already mounted,
      // so page switches only toggle the active surface; no iframe reload.
      const warm=()=>{
        pages.forEach(([id])=>{
          const el=d.getElementById(id);
          if(!el)return;
          const f=el.querySelector('iframe');
          if(!f)return;
          f.loading='eager';
          try{f.contentWindow&&f.contentWindow.document}catch(_e){}
        });
      };

      if('requestIdleCallback' in P) P.requestIdleCallback(warm,{timeout:450});
      else P.setTimeout(warm,180);
    })(window.parent);
    </script></body></html>""",height=0,scrolling=False)
'''
s = s.rstrip() + "\n\n" + _page_visual_v250.lstrip()
# END V250 PAGE VISUAL SYSTEM


# V250 SHARED PAGE CHROME
# Secondary pages inherit the approved Home visual language without touching Home.
# Header, responsive ad rails and page Game Bar belong to the active page surface.
_page_chrome_v250 = r'''
if GSF_WEB_MODE:
    st.markdown(r"""
    <style id="gsf-v250-shared-page-chrome">
    :root{
      --gsf-shell-top:46px;
      --gsf-shell-bottom:78px;
      --gsf-shell-ad-w:clamp(118px,9.5vw,164px);
      --gsf-shell-side:calc(var(--gsf-shell-ad-w) + clamp(18px,2vw,30px));
    }

    /* Same approved Home canvas. */
    #gsf-social-overlay-v159,
    #gsf-creator-hub-live-v160,
    #gsf-editor-overlay-v220,
    #gsf-ai-overlay-v221,
    #gsf-account-overlay-v223{
      padding:
        var(--gsf-shell-top)
        var(--gsf-shell-side)
        var(--gsf-shell-bottom)!important;
      background:
        radial-gradient(circle at 12% 8%,rgba(111,209,255,.17),transparent 23%),
        radial-gradient(circle at 88% 10%,rgba(106,229,185,.15),transparent 24%),
        linear-gradient(180deg,#FEFFFF 0%,#FBFDFF 54%,#F7FCFF 100%)!important;
    }

    /* Content is a page, never a floating translucent modal. */
    #gsf-social-overlay-v159 .gsf-social-shell,
    #gsf-creator-hub-live-v160 .gsf-hub-shell-v160,
    #gsf-editor-overlay-v220 .gsf-editor-shell,
    #gsf-ai-overlay-v221 .gsf-ai-shell,
    #gsf-account-overlay-v223 .gsf-account-shell{
      width:100%!important;
      height:100%!important;
      max-width:none!important;
      max-height:none!important;
      border:0!important;
      border-radius:0!important;
      background:transparent!important;
      box-shadow:none!important;
      transform:translateX(7px)!important;
      transition:transform .075s cubic-bezier(.22,.78,.22,1)!important;
    }
    #gsf-social-overlay-v159.is-open .gsf-social-shell,
    #gsf-creator-hub-live-v160.is-open .gsf-hub-shell-v160,
    #gsf-editor-overlay-v220.is-open .gsf-editor-shell,
    #gsf-ai-overlay-v221.is-open .gsf-ai-shell,
    #gsf-account-overlay-v223.is-open .gsf-account-shell{
      transform:translateX(0)!important;
    }

    #gsf-social-overlay-v159 iframe,
    #gsf-creator-hub-live-v160 iframe,
    #gsf-editor-overlay-v220 iframe,
    #gsf-ai-overlay-v221 iframe,
    #gsf-account-overlay-v223 iframe{
      width:100%!important;
      height:100%!important;
      border:0!important;
      border-radius:0!important;
      background:transparent!important;
    }

    /* Old modal close buttons are redundant: Home in the page Game Bar handles exit. */
    #gsf-social-overlay-v159 .gsf-social-close,
    #gsf-creator-hub-live-v160 .gsf-hub-close-v160,
    #gsf-editor-overlay-v220 .gsf-editor-close,
    #gsf-ai-overlay-v221 .gsf-ai-close,
    #gsf-account-overlay-v223 .gsf-account-close{
      display:none!important;
    }

    #gsf-page-chrome-v250{
      position:fixed;
      inset:0;
      z-index:2147483590;
      pointer-events:none;
      opacity:0;
      visibility:hidden;
      transition:none;
      color:#637DA8;
      font-family:"Avenir Next","SF Pro Display","SF Pro Text",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
    }
    #gsf-page-chrome-v250.is-open{
      opacity:1;
      visibility:visible;
    }
    #gsf-page-chrome-v250.is-open .gsf-page-head{
      z-index:3;
      background:linear-gradient(180deg,rgba(254,255,255,.98),rgba(249,253,255,.94));
    }

    #gsf-page-chrome-v250 .gsf-page-head{
      position:absolute;
      left:clamp(14px,2vw,30px);
      right:clamp(14px,2vw,30px);
      top:0;
      height:var(--gsf-shell-top);
      display:flex;
      align-items:center;
      justify-content:space-between;
      gap:12px;
      pointer-events:none;
    }
    #gsf-page-chrome-v250 .gsf-page-brand{
      color:#6C81A1;
      font-size:clamp(9px,.75vw,12px);
      line-height:1;
      font-weight:850;
      letter-spacing:.25em;
      white-space:nowrap;
    }
    #gsf-page-chrome-v250 .gsf-page-account{
      pointer-events:auto;
      min-height:28px;
      max-width:190px;
      padding:4px 10px;
      display:flex;
      align-items:center;
      justify-content:center;
      gap:6px;
      border:1px solid rgba(145,181,214,.28);
      border-radius:999px;
      background:rgba(255,255,255,.88);
      color:#637DA8;
      box-shadow:0 7px 20px rgba(63,108,151,.08);
      font-size:9px;
      font-weight:800;
      cursor:pointer;
    }

    #gsf-page-chrome-v250 .gsf-page-ad{
      position:absolute;
      top:50%;
      transform:translateY(-50%);
      width:var(--gsf-shell-ad-w);
      height:clamp(300px,43vh,430px);
      box-sizing:border-box;
      display:flex;
      align-items:center;
      justify-content:center;
      padding:10px;
      border:1px solid rgba(150,184,214,.22);
      border-radius:20px;
      background:rgba(255,255,255,.72);
      box-shadow:0 12px 34px rgba(59,104,148,.07),inset 0 1px 0 rgba(255,255,255,.94);
      color:#7D90AD;
      font-size:clamp(8px,.65vw,10px);
      font-weight:750;
      letter-spacing:.04em;
      text-align:center;
    }
    #gsf-page-chrome-v250 .gsf-page-ad.left{left:clamp(12px,1.35vw,24px)}
    #gsf-page-chrome-v250 .gsf-page-ad.right{right:clamp(12px,1.35vw,24px)}

    /* V249 page Game Bar, rescaled to match Home across desktop sizes. */
    #gsf-page-nav-v249{
      width:min(760px,72vw)!important;
      height:clamp(52px,6.8vh,60px)!important;
      min-height:clamp(52px,6.8vh,60px)!important;
      bottom:clamp(7px,1vh,10px)!important;
      padding:4px 10px!important;
      background:rgba(255,255,255,.93)!important;
      border:1px solid rgba(139,181,218,.30)!important;
      box-shadow:0 10px 28px rgba(59,104,148,.11),0 0 0 4px rgba(226,243,255,.30),inset 0 1px 0 #fff!important;
    }
    #gsf-page-nav-v249 .gsf-page-nav-item{
      font-size:clamp(7.5px,.62vw,8.5px)!important;
    }
    #gsf-page-nav-v249 .gsf-page-nav-item svg{
      width:clamp(17px,2.35vh,21px)!important;
      height:clamp(17px,2.35vh,21px)!important;
    }

    /* Short laptops: keep ad rails useful without squeezing the content. */
    @media(min-width:1000px) and (max-height:720px){
      :root{
        --gsf-shell-top:40px;
        --gsf-shell-bottom:68px;
        --gsf-shell-ad-w:clamp(104px,8.5vw,134px);
        --gsf-shell-side:calc(var(--gsf-shell-ad-w) + 16px);
      }
      #gsf-page-chrome-v250 .gsf-page-ad{
        height:clamp(240px,38vh,320px);
      }
      #gsf-page-nav-v249{
        height:48px!important;
        min-height:48px!important;
      }
    }

    /* Compact landscape/tablet: preserve page space; ad rails collapse first. */
    @media(min-width:761px) and (max-width:999px){
      :root{
        --gsf-shell-top:40px;
        --gsf-shell-bottom:70px;
        --gsf-shell-side:14px;
      }
      #gsf-page-chrome-v250 .gsf-page-ad{display:none}
      #gsf-page-nav-v249{width:calc(100vw - 28px)!important}
    }

    /* Mobile pages keep the same approved Home language, without side rails. */
    @media(max-width:760px){
      :root{
        --gsf-shell-top:34px;
        --gsf-shell-bottom:70px;
        --gsf-shell-side:8px;
      }
      #gsf-social-overlay-v159,
      #gsf-creator-hub-live-v160,
      #gsf-editor-overlay-v220,
      #gsf-ai-overlay-v221,
      #gsf-account-overlay-v223{
        padding:
          var(--gsf-shell-top)
          var(--gsf-shell-side)
          var(--gsf-shell-bottom)!important;
      }
      #gsf-page-chrome-v250 .gsf-page-head{
        left:10px;right:10px;height:34px;
      }
      #gsf-page-chrome-v250 .gsf-page-brand{
        font-size:8px;
        letter-spacing:.22em;
      }
      #gsf-page-chrome-v250 .gsf-page-account{
        min-height:25px;
        padding:3px 8px;
        font-size:8px;
      }
      #gsf-page-chrome-v250 .gsf-page-ad{display:none}
      #gsf-page-nav-v249{
        width:calc(100vw - 24px)!important;
        height:58px!important;
        min-height:58px!important;
        bottom:6px!important;
        padding:4px 8px!important;
      }
      #gsf-page-nav-v249 .gsf-page-nav-item{font-size:7px!important}
      #gsf-page-nav-v249 .gsf-page-nav-item svg{width:18px!important;height:18px!important}
    }

    @media(prefers-reduced-motion:reduce){
      #gsf-social-overlay-v159 .gsf-social-shell,
      #gsf-creator-hub-live-v160 .gsf-hub-shell-v160,
      #gsf-editor-overlay-v220 .gsf-editor-shell,
      #gsf-ai-overlay-v221 .gsf-ai-shell,
      #gsf-account-overlay-v223 .gsf-account-shell{
        transition:none!important;
        transform:none!important;
      }
    }
    </style>

    <div id="gsf-page-chrome-v250" aria-hidden="true">
      <header class="gsf-page-head">
        <div class="gsf-page-brand">GAMING SHORTS FACTORY</div>
        <button class="gsf-page-account" type="button" aria-label="Apri account">Accedi</button>
      </header>
      <aside class="gsf-page-ad left"><span>Spazio pubblicitario</span></aside>
      <aside class="gsf-page-ad right"><span>Spazio pubblicitario</span></aside>
    </div>
    """, unsafe_allow_html=True)

    import streamlit.components.v1 as components
    components.html(r"""<!doctype html><html><body style="margin:0;display:none"><script>
    ((P)=>{
      const d=P.document;
      const chrome=d.getElementById('gsf-page-chrome-v250');
      const nav=d.getElementById('gsf-page-nav-v249');
      if(!chrome)return;

      const ids=[
        'gsf-social-overlay-v159',
        'gsf-creator-hub-live-v160',
        'gsf-editor-overlay-v220',
        'gsf-ai-overlay-v221',
        'gsf-account-overlay-v223'
      ];

      const anyOpen=()=>ids.some(id=>{
        const el=d.getElementById(id);
        return !!(el&&el.classList.contains('is-open'));
      });

      const findHomeDoc=()=>{
        for(const f of [...d.querySelectorAll('iframe')]){
          try{
            const fd=f.contentDocument;
            if(fd&&fd.getElementById('home154'))return fd;
          }catch(_e){}
        }
        return null;
      };

      const syncHomeHeader=(open)=>{
        const hd=findHomeDoc();
        if(!hd)return;
        const top=hd.querySelector('#home154 .topbar');
        if(!top)return;
        if(open){
          if(!top.dataset.gsfPageHidden){
            top.dataset.gsfPageHidden='1';
            top.dataset.gsfPrevVisibility=top.style.visibility||'';
            top.dataset.gsfPrevOpacity=top.style.opacity||'';
            top.dataset.gsfPrevPointerEvents=top.style.pointerEvents||'';
          }
          top.style.setProperty('visibility','hidden','important');
          top.style.setProperty('opacity','0','important');
          top.style.setProperty('pointer-events','none','important');
        }else if(top.dataset.gsfPageHidden==='1'){
          top.style.removeProperty('visibility');
          top.style.removeProperty('opacity');
          top.style.removeProperty('pointer-events');
          if(top.dataset.gsfPrevVisibility)top.style.visibility=top.dataset.gsfPrevVisibility;
          if(top.dataset.gsfPrevOpacity)top.style.opacity=top.dataset.gsfPrevOpacity;
          if(top.dataset.gsfPrevPointerEvents)top.style.pointerEvents=top.dataset.gsfPrevPointerEvents;
          delete top.dataset.gsfPageHidden;
          delete top.dataset.gsfPrevVisibility;
          delete top.dataset.gsfPrevOpacity;
          delete top.dataset.gsfPrevPointerEvents;
        }
      };

      const sync=()=>{
        const open=anyOpen();
        chrome.classList.toggle('is-open',open);
        chrome.setAttribute('aria-hidden',open?'false':'true');
        if(nav)nav.classList.toggle('is-open',open);
        syncHomeHeader(open);
      };

      const account=chrome.querySelector('.gsf-page-account');
      if(account){
        account.addEventListener('click',()=>{
          P.postMessage({type:'GSF_SHELL_NAV',target:'hub',section:'profile'},P.location.origin);
        });
        fetch('/creator-hub/state',{cache:'no-store',credentials:'same-origin'})
          .then(r=>r.json())
          .then(j=>{
            const a=(j&&j.ok&&j.account)?j.account:{};
            if(a.connected){
              const name=String(a.display_name||a.nickname||a.name||'Creator').trim()||'Creator';
              account.textContent=name;
              account.setAttribute('aria-label',name+' · apri account');
            }
          })
          .catch(()=>{});
      }

      const obs=new P.MutationObserver(sync);
      ids.forEach(id=>{
        const el=d.getElementById(id);
        if(el)obs.observe(el,{attributes:true,attributeFilter:['class','style','aria-hidden']});
      });
      const pageShellObs=new P.MutationObserver(()=>queueMicrotask(sync));
      pageShellObs.observe(d.body,{childList:true,subtree:true});

      P.addEventListener('message',e=>{
        if(e.origin!==P.location.origin||!e.data||e.data.type!=='GSF_SHELL_NAV')return;
        queueMicrotask(sync);
      });

      sync();
    })(window.parent);
    </script></body></html>""", height=0, scrolling=False)
'''
s = s.rstrip() + "\n\n" + _page_chrome_v250.lstrip()
# END V250 SHARED PAGE CHROME

# V251 ROUTE GUARD
_route_guard_v251 = r'''
if GSF_WEB_MODE:
    import streamlit.components.v1 as components
    components.html(r"""<!doctype html><html><body style="margin:0;display:none"><script>
    ((P)=>{
      const d=P.document;
      const ids={
        hub:'gsf-creator-hub-live-v160',
        editor:'gsf-editor-overlay-v220',
        social:'gsf-social-overlay-v159',
        ai:'gsf-ai-overlay-v221',
        account:'gsf-account-overlay-v223'
      };
      const hide=(el)=>{
        if(!el)return;
        el.classList.remove('is-open');
        el.style.opacity='0';
        el.style.visibility='hidden';
        el.style.pointerEvents='none';
        el.setAttribute('aria-hidden','true');
      };
      const show=(el)=>{
        if(!el)return;
        el.classList.add('is-open');
        el.style.opacity='1';
        el.style.visibility='visible';
        el.style.pointerEvents='auto';
        el.setAttribute('aria-hidden','false');
      };
      P.addEventListener('message',e=>{
        if(e.origin!==P.location.origin||!e.data||e.data.type!=='GSF_SHELL_NAV')return;
        const t=String(e.data.target||'');
        if(t==='ai-state')return;
        if(t==='home'||t==='close'){
          Object.values(ids).forEach(id=>hide(d.getElementById(id)));
          return;
        }
        const key=(t==='profile'||t==='account')?'hub':t;
        if(!ids[key])return;
        Object.entries(ids).forEach(([name,id])=>{
          const el=d.getElementById(id);
          if(name===key)show(el); else hide(el);
        });
      },true);
    })(window.parent);
    </script></body></html>""",height=0,scrolling=False)
'''
s = s.rstrip() + "\n\n" + _route_guard_v251.lstrip()
# END V251 ROUTE GUARD

# V253 LOSS-PROOF REPLACE UPLOAD + GLOBAL NOTIFICATIONS
_notification_bridge_v253 = r'''
if GSF_WEB_MODE:
    import streamlit.components.v1 as components
    components.html(r"""<!doctype html><html><body style="margin:0;display:none"><script>
    ((P)=>{
      const d=P.document;
      const _gsfLifecycleCompat=['Upload completato']; // legacy build token; never rendered

      const ensurePush=()=>{
        if(P.GSFNotify)return Promise.resolve(true);
        return new Promise((resolve)=>{
          let s=d.getElementById('gsf-global-push-client-v258');
          if(s){
            if(P.GSFNotify)return resolve(true);
            s.addEventListener('load',()=>resolve(!!P.GSFNotify),{once:true});
            setTimeout(()=>resolve(!!P.GSFNotify),900);
            return;
          }
          s=d.createElement('script');
          s.id='gsf-global-push-client-v258';
          s.src='/gsf-push.js?v=258';
          s.async=true;
          s.onload=()=>resolve(!!P.GSFNotify);
          s.onerror=()=>resolve(false);
          d.head.appendChild(s);
        });
      };

      // V258: replacement upload is owned by the Home uploader itself.
      // Existing global notifications remain available from every page.
      P.addEventListener('message',(e)=>{
        const data=e.data||{};
        if(data.type==='GSF_NOTIFY'&&P.GSFNotify){
          P.GSFNotify.show(
            String(data.title||'Gaming Shorts Factory'),
            String(data.body||''),
            String(data.kind||'success')
          );
        }
      });

      // Re-enable silent Web Push when permission already exists.
      ensurePush().then(()=>{
        try{P.GSFPush&&P.GSFPush.ensure&&P.GSFPush.ensure()}catch(_e){}
      });
    })(window.parent);
    </script></body></html>""",height=0,scrolling=False)
'''
s = s.rstrip() + "\n\n" + _notification_bridge_v253.lstrip()
# END V253 LOSS-PROOF REPLACE UPLOAD + GLOBAL NOTIFICATIONS

# V221 final write must happen AFTER V220 + V221 surfaces are appended.

# V281 GAMEBAR RETURN + TYPE SCALE
# Keep the page Game Bar visibly above Creator Hub and every other secondary surface.
_v281_gamebar_type = r'''
if GSF_WEB_MODE:
    st.markdown(r"""
    <style id="gsf-v281-gamebar-return-type">
      #gsf-social-overlay-v159,
      #gsf-creator-hub-live-v160,
      #gsf-editor-overlay-v220,
      #gsf-ai-overlay-v221,
      #gsf-account-overlay-v223{
        z-index:2147483500!important;
      }
      #gsf-page-chrome-v250{
        z-index:2147483550!important;
      }
      #gsf-page-nav-v249{
        z-index:2147483646!important;
      }
      #gsf-page-nav-v249.is-open{
        opacity:1!important;
        visibility:visible!important;
        pointer-events:auto!important;
      }
      #gsf-page-nav-v249 .gsf-page-nav-item{
        font-size:clamp(11px,.78vw,13px)!important;
      }
      @media(max-width:760px){
        #gsf-page-nav-v249 .gsf-page-nav-item{
          font-size:9.5px!important;
        }
      }
    </style>
    """, unsafe_allow_html=True)
'''
s = s.rstrip() + "\n\n" + _v281_gamebar_type.lstrip()
# END V281 GAMEBAR RETURN + TYPE SCALE

compile(s,str(out),"exec")
out.write_text(s,encoding="utf-8")
print("V221 AI SURFACE applied:",out)


# V263 FIXED SECONDARY PAGES — NO PAGE SCROLL / NO FADE
_page_guard_v263 = r'''
if GSF_WEB_MODE:
    st.markdown(r"""
    <style id="gsf-v263-fixed-pages">
    #gsf-social-overlay-v159,
    #gsf-creator-hub-live-v160,
    #gsf-editor-overlay-v220,
    #gsf-ai-overlay-v221,
    #gsf-account-overlay-v223{
      overflow:hidden!important;
    }
    #gsf-social-overlay-v159.is-open,
    #gsf-creator-hub-live-v160.is-open,
    #gsf-editor-overlay-v220.is-open,
    #gsf-ai-overlay-v221.is-open,
    #gsf-account-overlay-v223.is-open{
      opacity:1!important;
      visibility:visible!important;
      pointer-events:auto!important;
      background:#F7FCFF!important;
      -webkit-backdrop-filter:none!important;
      backdrop-filter:none!important;
    }
    #gsf-social-overlay-v159.is-open .gsf-social-shell,
    #gsf-creator-hub-live-v160.is-open .gsf-hub-shell-v160,
    #gsf-editor-overlay-v220.is-open .gsf-editor-shell,
    #gsf-ai-overlay-v221.is-open .gsf-ai-shell,
    #gsf-account-overlay-v223.is-open .gsf-account-shell{
      opacity:1!important;
      visibility:visible!important;
      background:#F7FCFF!important;
      transform:none!important;
    }
    #gsf-social-overlay-v159 iframe,
    #gsf-creator-hub-live-v160 iframe,
    #gsf-editor-overlay-v220 iframe,
    #gsf-ai-overlay-v221 iframe,
    #gsf-account-overlay-v223 iframe{
      background:#F7FCFF!important;
    }
    
    /* V266 SECONDARY HEADER REMOVED */
    :root{--gsf-shell-top:0px!important}
    #gsf-page-chrome-v250 .gsf-page-head{display:none!important}
    #gsf-social-overlay-v159,#gsf-creator-hub-live-v160,#gsf-editor-overlay-v220,#gsf-ai-overlay-v221,#gsf-account-overlay-v223{padding-top:0!important;font-family:"Avenir Next","SF Pro Display","SF Pro Text",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif!important}
    #gsf-page-chrome-v250,#gsf-page-nav-v249,#gsf-page-nav-v249 button{font-family:"Avenir Next","SF Pro Display","SF Pro Text",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif!important}
    @media(max-width:760px){#gsf-page-nav-v249 .gsf-page-nav-item{font-size:8px!important}}
</style>
    """, unsafe_allow_html=True)
    import streamlit.components.v1 as components
    components.html(r"""<!doctype html><html><body style="display:none"><script>
    ((P)=>{
      const d=P.document;
      const ids=['gsf-social-overlay-v159','gsf-creator-hub-live-v160','gsf-editor-overlay-v220','gsf-ai-overlay-v221','gsf-account-overlay-v223'];
      const lockFrame=(frame)=>{
        try{
          const fd=frame&&frame.contentDocument;if(!fd)return;
          fd.documentElement.style.setProperty('overflow','hidden','important');
          if(fd.body)fd.body.style.setProperty('overflow','hidden','important');
        }catch(_e){}
      };
      const enforce=()=>{
        let open=false;
        ids.forEach(id=>{
          const el=d.getElementById(id);if(!el)return;
          if(el.classList.contains('is-open')){
            open=true;
            el.style.setProperty('opacity','1','important');
            el.style.setProperty('visibility','visible','important');
            el.style.setProperty('background','#F7FCFF','important');
            const sh=el.querySelector('section');
            if(sh){sh.style.setProperty('opacity','1','important');sh.style.setProperty('background','#F7FCFF','important')}
            const fr=el.querySelector('iframe');if(fr)lockFrame(fr);
          }
        });
        if(open){
          d.documentElement.style.setProperty('overflow','hidden','important');
          d.body.style.setProperty('overflow','hidden','important');
        }else{
          d.documentElement.style.removeProperty('overflow');
          d.body.style.removeProperty('overflow');
        }
      };
      const obs=new P.MutationObserver(enforce);
      obs.observe(d.body,{childList:true,subtree:true,attributes:true,attributeFilter:['class','style']});
      d.querySelectorAll('iframe').forEach(f=>f.addEventListener('load',()=>{lockFrame(f);enforce()}));
      P.setInterval(enforce,800);
      enforce();

      const params=new URLSearchParams(P.location.search);
      const requested=params.get('gsf_hub');
      if(requested){
        P.setTimeout(()=>P.postMessage({type:'GSF_SHELL_NAV',target:'hub',section:requested},P.location.origin),450);
        try{params.delete('gsf_hub');const q=params.toString();P.history.replaceState({},'',P.location.pathname+(q?'?'+q:'')+P.location.hash)}catch(_e){}
      }
    })(window.parent);
    </script></body></html>""",height=0,scrolling=False)
'''
s = s.rstrip() + "\n\n" + _page_guard_v263.lstrip()


# V266 COMPLETE — Creator Hub folders, unified typography, compact secondary shell
