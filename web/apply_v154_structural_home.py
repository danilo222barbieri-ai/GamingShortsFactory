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
    <script>
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
          else if(t==='editor' || t==='resume_draft') clickTarget(['apri game editor','game editor','manuale']);
          else if(t==='ai') clickTarget(['crea con ia','crea con ai','analizza con ia']);
          else if(t==='social'){
            const so=document.getElementById('gsf-social-overlay-v159');
            if(so){so.classList.add('is-open');so.style.opacity='1';so.style.visibility='visible';so.style.pointerEvents='auto';}
          }
        },210);
      });
    })();
    </script>
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
        <iframe src="/share-v156/" title="Condividi o scarica"></iframe>
      </section>
    </div>
    <script>
    (()=>{
      const o=document.getElementById('gsf-social-overlay-v159');
      if(!o)return;
      const open=()=>{
        o.classList.add('is-open');
        o.style.opacity='1';o.style.visibility='visible';o.style.pointerEvents='auto';
        o.setAttribute('aria-hidden','false');
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
        if(t==='social')open();
        if(t==='close'||t==='home')close();
      });
    })();
    </script>
    """, unsafe_allow_html=True)
'''
s = s.rstrip() + "\n\n" + _social_surface_v159.lstrip()


# V160 — guaranteed Creator Hub overlay owned by the current production shell.
_hub_surface_v160 = r'''
if GSF_WEB_MODE:
    st.markdown(r"""
    <style id="gsf-v160-hub-shell">
    #gsf-creator-hub-live-v160{position:fixed;inset:0;z-index:2147483660;display:flex;align-items:center;justify-content:center;padding:15px;background:rgba(219,235,244,.52);-webkit-backdrop-filter:blur(4px) saturate(.96);backdrop-filter:blur(4px) saturate(.96);opacity:0;visibility:hidden;pointer-events:none;transition:opacity .22s ease,visibility .22s ease}
    #gsf-creator-hub-live-v160.is-open{opacity:1;visibility:visible;pointer-events:auto}
    #gsf-creator-hub-live-v160 .gsf-hub-shell-v160{position:relative;width:min(1920px,calc(100vw - 20px));height:calc(100dvh - 20px);border:1px solid #D3E3ED;border-radius:30px;overflow:hidden;background:#F7FBFF;box-shadow:0 30px 86px rgba(19,45,65,.24);transform:scale(.985);transition:transform .26s cubic-bezier(.2,.8,.2,1)}
    #gsf-creator-hub-live-v160.is-open .gsf-hub-shell-v160{transform:scale(1)}
    #gsf-creator-hub-live-v160 iframe{width:100%;height:100%;border:0;background:#F7FBFF}
    #gsf-creator-hub-live-v160 .gsf-hub-close-v160{position:absolute;z-index:5;right:14px;top:12px;width:34px;height:34px;border:1px solid #dce9f3;border-radius:12px;background:#fff;color:#617b9d;font-size:20px;cursor:pointer}
    @media(max-width:760px){#gsf-creator-hub-live-v160{padding:5px}#gsf-creator-hub-live-v160 .gsf-hub-shell-v160{width:calc(100vw - 10px);height:calc(100vh - 10px);border-radius:22px}}
    </style>
    <div id="gsf-creator-hub-live-v160" aria-hidden="true">
      <section class="gsf-hub-shell-v160" role="dialog" aria-modal="true" aria-label="Creator Hub">
        <button class="gsf-hub-close-v160" type="button" aria-label="Chiudi">×</button>
        <iframe src="/creator-hub-v156/" title="Creator Hub"></iframe>
      </section>
    </div>
    <script>
    (()=>{const o=document.getElementById('gsf-creator-hub-live-v160');if(!o)return;const close=()=>{o.classList.remove('is-open');o.style.opacity='0';o.style.visibility='hidden';o.style.pointerEvents='none'};o.querySelector('.gsf-hub-close-v160').onclick=close;o.addEventListener('click',e=>{if(e.target===o)close()});})();
    </script>
    """, unsafe_allow_html=True)
'''
s = s.rstrip() + "\n\n" + _hub_surface_v160.lstrip()

compile(s,str(out),"exec")
out.write_text(s,encoding="utf-8")
print("V154 STRUCTURAL HOME applied:",out)
