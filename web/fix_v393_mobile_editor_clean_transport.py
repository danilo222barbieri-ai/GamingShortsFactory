#!/usr/bin/env python3
from pathlib import Path
import sys

MARK='V393_MOBILE_EDITOR_CLEAN_TRANSPORT'

EDITOR_PATCH=r'''
<!-- V393_MOBILE_EDITOR_CLEAN_TRANSPORT -->
<style id="v393MobileEditorCleanTransport">
@media(max-width:760px){
  #ng27{--v389-player-w:min(78vw,304px,calc((100dvh - 225px) * 9 / 16))!important;--v389-player-h:calc(var(--v389-player-w) * 16 / 9)!important}
  #ng27 .stage.r916,#ng27.expanded .stage.r916{border-radius:24px!important}

  /* V393_SINGLE_TRANSPORT_OWNER */
  #ng27 .timeline{display:none!important}
  #ng27 .v393TransportGlass{
    position:absolute!important;left:9px!important;right:9px!important;bottom:7px!important;height:78px!important;
    z-index:160!important;border:1px solid rgba(112,177,219,.22)!important;border-radius:18px!important;
    background:linear-gradient(145deg,rgba(255,255,255,.76),rgba(220,242,250,.68))!important;
    box-shadow:0 8px 22px rgba(49,100,137,.10),inset 0 1px 0 rgba(255,255,255,.86)!important;
    -webkit-backdrop-filter:blur(15px) saturate(1.08)!important;backdrop-filter:blur(15px) saturate(1.08)!important;
    pointer-events:none!important;
  }
  #ng27 .v389PlaybackDock{bottom:28px!important;z-index:173!important}
  #ng27 .v389PlaybackDock #playBtn{width:58px!important;height:58px!important;min-width:58px!important;min-height:58px!important}
  #ng27 .v389PlayerProgress{left:20px!important;right:20px!important;bottom:12px!important;z-index:172!important}
  #ng27 .v389ProgressTrack{height:5px!important;background:rgba(43,91,126,.24)!important}
  #ng27 .v389ProgressKnob{width:10px!important;height:10px!important}
  #ng27 .v389ProgressNow,#ng27 .v389ProgressEnd{font-size:6.8px!important;font-weight:950!important}

  /* V393_PAUSED_POSTER_FRAME */
  #ng27 .v393PosterFrame{
    position:absolute!important;inset:0!important;width:100%!important;height:100%!important;z-index:2!important;
    object-fit:cover!important;border-radius:inherit!important;opacity:0!important;visibility:hidden!important;
    pointer-events:none!important;transition:opacity .12s ease!important;
  }
  #ng27 .v393PosterFrame.is-visible{opacity:1!important;visibility:visible!important}

  #ng27 .v389TopBar{top:9px!important;left:8px!important;right:8px!important}
  #ng27 .v389ToolDock{gap:9px!important}
  #ng27 .v389ToolDock .railBtn{width:44px!important;height:52px!important;min-width:44px!important;min-height:52px!important}
  #ng27 .v389LeftDock{left:8px!important}#ng27 .v389RightDock{right:8px!important}

  #ng27 .v391EditorActions{width:var(--v389-player-w)!important;margin-top:8px!important;gap:8px!important}
  #ng27 .v393ChangeShort{
    width:var(--v389-player-w)!important;max-width:calc(100% - 20px)!important;height:28px!important;min-height:28px!important;
    margin:5px auto 0!important;padding:0 12px!important;border-radius:12px!important;
    border:1px solid rgba(100,170,217,.24)!important;background:rgba(255,255,255,.72)!important;color:#3a82b7!important;
    box-shadow:0 5px 14px rgba(49,98,137,.08)!important;font-size:8.2px!important;line-height:1!important;
    font-weight:950!important;letter-spacing:.01em!important;touch-action:manipulation!important;-webkit-tap-highlight-color:transparent!important;
    display:block!important;flex:0 0 auto!important;
  }
  #ng27 .v393ChangeShort:active{transform:scale(.985)!important}
  #ng27.gsfFullscreen .v393ChangeShort,#ng27.gsfFullscreenFallback .v393ChangeShort,#ng27:fullscreen .v393ChangeShort,#ng27:-webkit-full-screen .v393ChangeShort{display:none!important}
}
</style>
<script id="v393MobileEditorCleanTransportRuntime">
(()=>{
  const root=document.getElementById('ng27');if(!root)return;
  const stage=root.querySelector('#stage'),video=root.querySelector('#video');if(!stage||!video)return;

  root.querySelectorAll('.timeline').forEach(el=>{el.setAttribute('aria-hidden','true')});
  let glass=stage.querySelector('.v393TransportGlass');
  if(!glass){glass=document.createElement('div');glass.className='v393TransportGlass';glass.setAttribute('aria-hidden','true');stage.appendChild(glass)}

  let poster=stage.querySelector('.v393PosterFrame');
  if(!poster){poster=document.createElement('canvas');poster.className='v393PosterFrame';poster.setAttribute('aria-hidden','true');stage.insertBefore(poster,stage.firstChild)}
  const capturePoster=()=>{
    if(!video.paused||video.readyState<2||!video.videoWidth||!video.videoHeight)return;
    try{
      const maxW=720,scale=Math.min(1,maxW/video.videoWidth),w=Math.max(1,Math.round(video.videoWidth*scale)),h=Math.max(1,Math.round(video.videoHeight*scale));
      if(poster.width!==w)poster.width=w;if(poster.height!==h)poster.height=h;
      const ctx=poster.getContext('2d',{alpha:false});if(!ctx)return;
      ctx.drawImage(video,0,0,w,h);poster.classList.add('is-visible');
    }catch(_e){poster.classList.remove('is-visible')}
  };
  const hidePoster=()=>poster.classList.remove('is-visible');
  video.addEventListener('loadeddata',()=>{if(video.paused)capturePoster()},{passive:true});
  video.addEventListener('pause',capturePoster,{passive:true});
  video.addEventListener('seeked',()=>{if(video.paused)capturePoster()},{passive:true});
  video.addEventListener('play',hidePoster,{passive:true});
  if(video.readyState>=2&&video.paused)capturePoster();

  /* V393_CHANGE_SHORT */
  let change=root.querySelector('#v393ChangeShort');
  if(!change){
    change=document.createElement('button');change.type='button';change.id='v393ChangeShort';change.className='v393ChangeShort';
    change.textContent='CAMBIA SHORT';
    const actions=root.querySelector('#v391EditorActions');
    if(actions)actions.insertAdjacentElement('afterend',change);else root.querySelector('.cockpit')?.appendChild(change);
  }
  const resetAiSelectedPage=()=>{
    try{
      const P=window.parent,D=P.document,overlay=D.getElementById('gsf-ai-overlay-v221');
      const frame=overlay&&overlay.querySelector('iframe');
      const doc=frame&&frame.contentDocument;
      const btn=doc&&(doc.getElementById('selectedAnother')||doc.getElementById('selectedBack'));
      if(btn)btn.click();
    }catch(_e){}
  };
  change.onclick=()=>{
    const save=root.querySelector('#v391SaveDraft');if(save)save.click();
    const nav=()=>{
      try{
        const P=window.parent,origin=P.location.origin;
        P.postMessage({type:'GSF_SHELL_NAV',target:'ai'},origin);
        [80,220,520].forEach(ms=>setTimeout(resetAiSelectedPage,ms));
      }catch(_e){}
    };
    setTimeout(nav,90);
  };
})();
</script>
'''

SHELL_PATCH=r'''
<style id="v393EditorShellCleanup">
@media(max-width:760px){
  #gsf-editor-overlay-v220.is-open{overflow:hidden!important;background:linear-gradient(180deg,#f8fcff 0%,#eef8fd 100%)!important}
  #gsf-editor-overlay-v220.is-open [class*="close" i],
  #gsf-editor-overlay-v220.is-open [id*="close" i],
  .v393EditorChromeGone{display:none!important}
  #v393EditorBottomMask{
    position:fixed!important;left:0!important;right:0!important;bottom:0!important;display:none;
    background:linear-gradient(180deg,#f4fbff 0%,#eef8fd 100%)!important;z-index:2147482500!important;pointer-events:none!important;
  }
}
</style>
<script id="v393EditorParentCleanup">
(()=>{
  const P=window.parent,D=P.document;if(!D||P.__GSF_V393_EDITOR_PARENT_CLEANUP)return;P.__GSF_V393_EDITOR_PARENT_CLEANUP=true;
  const host=()=>D.getElementById('gsf-editor-overlay-v220');
  let mask=D.getElementById('v393EditorBottomMask');
  if(!mask){mask=D.createElement('div');mask.id='v393EditorBottomMask';mask.setAttribute('aria-hidden','true');D.body.appendChild(mask)}
  const closeSelector='button,a,[role="button"],[onclick],[class*="close" i],[id*="close" i]';
  const sync=()=>{
    const h=host(),mobile=P.innerWidth<=760,active=!!(h&&h.classList.contains('is-open')&&h.getAttribute('aria-hidden')!=='true');
    D.documentElement.classList.toggle('v393EditorActive',active&&mobile);
    D.querySelectorAll('.v393EditorChromeGone').forEach(el=>el.classList.remove('v393EditorChromeGone'));
    if(!active||!mobile){mask.style.display='none';return}
    const hr=h.getBoundingClientRect(),vw=P.innerWidth;
    D.querySelectorAll(closeSelector).forEach(el=>{
      if(el.closest('#gsf-global-header,#gsf-global-gamebar'))return;
      let r;try{r=el.getBoundingClientRect()}catch(_e){return}
      if(!r||r.width<10||r.height<10||r.width>90||r.height>90)return;
      const vals=[el.textContent,el.getAttribute('aria-label'),el.getAttribute('title'),el.id,el.className].map(v=>String(v||'').trim().toLowerCase());
      const semantic=vals.some(v=>v==='x'||v==='×'||v==='✕'||v==='✖'||v==='close'||v==='chiudi'||v.includes('editorclose')||v.includes('editor-close'));
      const nearEditorTop=r.right>=Math.min(vw,hr.right)-92&&r.top>=hr.top-12&&r.top<=hr.top+108;
      if(semantic&&nearEditorTop)el.classList.add('v393EditorChromeGone');
    });
    const gamebar=D.getElementById('gsf-global-gamebar');
    if(gamebar){
      const gr=gamebar.getBoundingClientRect(),top=Math.max(0,Math.ceil(gr.bottom+1));
      mask.style.top=top+'px';mask.style.display=top<P.innerHeight?'block':'none';
    }else mask.style.display='none';
  };
  const schedule=()=>{P.requestAnimationFrame(sync);[80,220,520,1100].forEach(ms=>P.setTimeout(sync,ms))};
  const h=host();if(h){try{new MutationObserver(schedule).observe(h,{attributes:true,attributeFilter:['class','aria-hidden'],childList:true,subtree:true})}catch(_e){}}
  schedule();
})();
</script>
'''

def patch_editor(text:str)->str:
    if MARK in text:return text
    for anchor in ('V389_MOBILE_EDITOR_BOUNDED_RESET','V391_MOBILE_EDITOR_TOP_ACTIONS','V392_MOBILE_EDITOR_PREMIUM_SKIN','</body>'):
        if anchor not in text:raise RuntimeError('V393 Editor anchor missing: '+anchor)
    return text.replace('</body>',EDITOR_PATCH+'\n</body>',1)

def patch_shell(text:str)->str:
    if 'id="v393EditorShellCleanup"' in text:return text
    anchor='<style id="gsf-v220-editor-shell">'
    if anchor not in text:raise RuntimeError('V393 parent Editor shell anchor missing')
    return text.replace(anchor,SHELL_PATCH+'\n'+anchor,1)

def main()->None:
    root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
    editor=root/'web'/'editor_2027_component'/'index.html';shell=root/'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py'
    if not editor.is_file() or not shell.is_file():raise SystemExit('V393 runtime files missing')
    eb=editor.read_text(encoding='utf-8');ea=patch_editor(eb);editor.write_text(ea,encoding='utf-8')
    sb=shell.read_text(encoding='utf-8');sa=patch_shell(sb);compile(sa,str(shell),'exec');shell.write_text(sa,encoding='utf-8')
    print('V393 mobile Editor clean transport + larger player applied editor_changed=',eb!=ea,'shell_changed=',sb!=sa,flush=True)

if __name__=='__main__':main()
