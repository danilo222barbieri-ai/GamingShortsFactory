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
        <iframe src="/share-v156/?v=226" data-src="/share-v156/" data-loaded="1" title="Condividi o scarica"></iframe>
      </section>
    </div>
    <div class="gsf-script-guard" style="display:none!important"></div>
    """, unsafe_allow_html=True)
    import streamlit.components.v1 as components
    components.html(r"""<!doctype html><html><body style="margin:0;display:none"><script>
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
    </script></body></html>""", height=0, scrolling=False)
    """, unsafe_allow_html=True)
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
        <iframe src="/creator-hub-v156/?v=226" data-src="/creator-hub-v156/" data-loaded="1" title="Creator Hub"></iframe>
      </section>
    </div>
    <div class="gsf-script-guard" style="display:none!important"><script>
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
    </script></div>
    """, unsafe_allow_html=True)
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
          <iframe class="gsf-editor-frame" src="/editor-live/?v=226" data-src="/editor-live/" data-loaded="1" title="Game Editor"></iframe>
          <div class="editor-note right"><span id="gsf-editor-note-right">Tocca uno strumento<br>e guarda cosa cambia</span></div>
        </div>
      </section>
    </div>
    <div class="gsf-script-guard" style="display:none!important"><script>
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
      const open=async(remember=true)=>{
        try{
          const r=await fetch('/editor/state',{cache:'no-store',credentials:'same-origin'});
          const j=await r.json();
          if(r.ok&&j&&j.ok)editorMeta=j;
        }catch(e){}
        if(frame.dataset.loaded!=='1'){
          frame.src=(frame.dataset.src||'/editor-live/')+'?v=224';
          frame.dataset.loaded='1';
        }else{
          setTimeout(sendRender,40);
        }
        o.classList.add('is-open');o.style.opacity='1';o.style.visibility='visible';o.style.pointerEvents='auto';o.setAttribute('aria-hidden','false');
        if(remember)try{sessionStorage.setItem(KEY,'1')}catch(e){}
        guide('idle');
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
    </script></div>
    """, unsafe_allow_html=True)
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
        <iframe src="/ai-v221/?v=226" data-src="/ai-v221/" data-loaded="1" title="Motori IA"></iframe>
      </section>
    </div>
    <div class="gsf-script-guard" style="display:none!important"><script>
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
    </script></div>
    """, unsafe_allow_html=True)
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
    <div class="gsf-script-guard" style="display:none!important"><script>
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
        if(t==='account'){open();return}
        if(t==='home'||t==='close'||t==='hub'||t==='editor'||t==='social'||t==='ai')close();
      });
    })();
    </script></div>
    """, unsafe_allow_html=True)
'''
s = s.rstrip() + "\n\n" + _account_surface_v223.lstrip()


# V223.4 — V223.2 inline render-state injection removed.
# Editor state remains persisted by /editor/state and /editor/state/save.
# Final-render reconciliation will be attached through a safe boundary, not by
# splicing inside an existing try/except block.

# V224 legacy JS-regex escape cleanup: generated Python source must contain
# a doubled backslash so Python emits the intended JS /\s/ regex without SyntaxWarning.
s=s.replace("replace(/"+chr(92)+"s/g,'')","replace(/"+chr(92)+chr(92)+"s/g,'')")
# V221 final write must happen AFTER V220 + V221 surfaces are appended.
compile(s,str(out),"exec")
out.write_text(s,encoding="utf-8")
print("V221 AI SURFACE applied:",out)
