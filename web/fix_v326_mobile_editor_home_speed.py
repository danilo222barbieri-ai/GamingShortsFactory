#!/usr/bin/env python3
from pathlib import Path
import re
import sys

STYLE_ID='v326MobileEditorExact'
SCRIPT_ID='v326MobileEditorRuntime'

STYLE=r'''<style id="v326MobileEditorExact">
/* V326: exact mobile composition is keyed from parent viewport, never iframe media width. */
#ng27.v326Mobile{
  --v326-player-w:274px;
  width:100%!important;height:100%!important;min-height:0!important;max-height:100%!important;
  padding:0 6px 2px!important;margin:0!important;overflow:hidden!important;border-radius:0!important;
  background:radial-gradient(circle at 50% 7%,rgba(201,235,250,.92),transparent 35%),linear-gradient(180deg,#F8FDFF 0%,#EFF8FD 100%)!important;
}
#ng27.v326Mobile .shell{
  width:100%!important;max-width:none!important;height:100%!important;min-height:0!important;
  margin:0!important;padding:0!important;display:flex!important;flex-direction:column!important;
  justify-content:flex-start!important;align-items:stretch!important;overflow:hidden!important;background:transparent!important;
}
#ng27.v326Mobile .topline,#ng27.v326Mobile .gsfGuide,#ng27.v326Mobile .footNote{display:none!important}
#ng27.v326Mobile .cockpit,#ng27.v326Mobile.expanded .cockpit{
  position:relative!important;width:100%!important;max-width:430px!important;height:auto!important;min-height:0!important;
  margin:0 auto!important;padding:1px 0 2px!important;display:grid!important;
  grid-template-columns:minmax(0,1fr)!important;grid-template-rows:auto auto auto!important;
  gap:8px!important;align-items:start!important;align-content:start!important;justify-items:stretch!important;overflow:visible!important;
}
#ng27.v326Mobile .cockpit>.rail{display:none!important}
#ng27.v326Mobile .stage>.rail.v325Rail{display:none!important}
#ng27.v326Mobile .stageWrap{
  grid-column:1!important;grid-row:1!important;justify-self:center!important;position:relative!important;
  width:var(--v326-player-w)!important;max-width:calc(100% - 18px)!important;height:auto!important;min-height:0!important;
  margin:0 auto!important;padding:0!important;display:block!important;overflow:visible!important;
}
#ng27.v326Mobile .stage.r916,#ng27.v326Mobile.expanded .stage.r916{
  position:relative!important;width:100%!important;max-width:none!important;height:auto!important;aspect-ratio:9/16!important;
  margin:0!important;border-radius:22px!important;overflow:hidden!important;border:1px solid rgba(111,199,238,.42)!important;
  background:linear-gradient(180deg,#dff4fd,#f5fbff)!important;
  box-shadow:0 12px 28px rgba(48,103,142,.15),0 0 0 5px rgba(255,255,255,.40)!important;
}
#ng27.v326Mobile .stage video{width:100%!important;height:100%!important;object-fit:cover!important}

/* Exact approved tool set: 3 left + 2 right. Legacy Cover/HUD remain functional on desktop only. */
#ng27.v326Mobile .v326ToolDock{
  position:absolute!important;top:50%!important;z-index:96!important;display:flex!important;flex-direction:column!important;
  gap:8px!important;transform:translateY(-50%)!important;pointer-events:none!important;
}
#ng27.v326Mobile .v326LeftDock{left:8px!important}
#ng27.v326Mobile .v326RightDock{right:8px!important}
#ng27.v326Mobile .v326ToolDock .railBtn{
  pointer-events:auto!important;display:flex!important;width:48px!important;height:58px!important;min-width:48px!important;min-height:58px!important;
  margin:0!important;padding:0!important;border-radius:17px!important;border:1px solid rgba(255,255,255,.68)!important;
  background:linear-gradient(145deg,rgba(30,56,83,.66),rgba(48,75,103,.50))!important;color:#fff!important;
  box-shadow:0 7px 18px rgba(11,28,44,.20),inset 0 1px 0 rgba(255,255,255,.25)!important;
  -webkit-backdrop-filter:blur(14px) saturate(1.12)!important;backdrop-filter:blur(14px) saturate(1.12)!important;
}
#ng27.v326Mobile .v326ToolDock .railBtn .ico{width:21px!important;height:21px!important;color:#fff!important}
#ng27.v326Mobile .v326ToolDock .railBtn span{font-size:7.4px!important;line-height:1!important;color:#fff!important;text-shadow:0 1px 4px rgba(0,0,0,.28)!important}
#ng27.v326Mobile .v326ToolDock .railBtn.active{background:linear-gradient(145deg,rgba(72,168,236,.92),rgba(57,112,211,.84))!important}
#ng27.v326Mobile [data-panel="cover"],#ng27.v326Mobile [data-panel="hud"]{display:none!important}
#ng27.v326Mobile #undoBtn,#ng27.v326Mobile #redoBtn,#ng27.v326Mobile #doneBtn{display:none!important}

#ng27.v326Mobile .v326Meta{position:absolute!important;left:10px!important;right:10px!important;top:10px!important;z-index:98!important;display:flex!important;align-items:center!important;pointer-events:none!important}
#ng27.v326Mobile .v326Time,#ng27.v326Mobile .v326Ratio{
  height:30px!important;display:flex!important;align-items:center!important;padding:0 10px!important;border-radius:13px!important;
  color:#fff!important;background:rgba(24,48,74,.64)!important;border:1px solid rgba(255,255,255,.36)!important;
  -webkit-backdrop-filter:blur(13px)!important;backdrop-filter:blur(13px)!important;box-shadow:0 5px 13px rgba(6,20,34,.14)!important;
  font-size:8.8px!important;font-weight:950!important;letter-spacing:.01em!important;
}
#ng27.v326Mobile .v326Ratio{margin-left:auto!important;margin-right:45px!important}
#ng27.v326Mobile #zoomEditorBtn{
  display:flex!important;position:absolute!important;top:9px!important;right:9px!important;z-index:101!important;
  width:39px!important;min-width:39px!important;height:39px!important;padding:0!important;border-radius:12px!important;
  border:1px solid rgba(255,255,255,.68)!important;background:rgba(24,48,74,.64)!important;color:#fff!important;
  -webkit-backdrop-filter:blur(13px)!important;backdrop-filter:blur(13px)!important;
}
#ng27.v326Mobile #zoomEditorBtn .ico{width:19px!important;height:19px!important;color:#fff!important;margin:auto!important}
#ng27.v326Mobile #zoomEditorBtn span{display:none!important}

#ng27.v326Mobile .v326PlaybackDock{
  position:absolute!important;left:50%!important;bottom:23px!important;z-index:100!important;transform:translateX(-50%)!important;
  display:flex!important;align-items:center!important;gap:12px!important;
}
#ng27.v326Mobile .v326Skip{width:27px!important;height:34px!important;padding:0!important;border:0!important;background:transparent!important;color:#fff!important;font-size:23px!important;font-weight:950!important;text-shadow:0 2px 8px rgba(0,0,0,.46)!important}
#ng27.v326Mobile #playBtn{
  display:grid!important;place-items:center!important;position:relative!important;width:57px!important;height:57px!important;min-width:57px!important;min-height:57px!important;
  padding:0!important;border-radius:50%!important;border:1px solid rgba(255,255,255,.82)!important;
  background:linear-gradient(145deg,#4fb5fa,#3378e4)!important;color:#fff!important;
  box-shadow:0 9px 23px rgba(17,50,94,.32),inset 0 1px 0 rgba(255,255,255,.38)!important;
}
#ng27.v326Mobile #playBtn .ico{width:27px!important;height:27px!important;color:#fff!important}
#ng27.v326Mobile #playBtn span{display:none!important}
#ng27.v326Mobile .captionPreview.v326DefaultCaption{display:none!important}

/* Approved order: PLAYER -> CREATE/SAVE -> TIMELINE. */
#ng27.v326Mobile .cockpit>.v323EditorActions{
  grid-column:1!important;grid-row:2!important;position:relative!important;z-index:82!important;width:100%!important;max-width:430px!important;
  margin:0!important;padding:0!important;display:grid!important;grid-template-columns:minmax(0,1fr) minmax(0,1fr)!important;gap:8px!important;
}
#ng27.v326Mobile .cockpit>.v323EditorActions .v323EditorAction{
  width:100%!important;min-width:0!important;min-height:49px!important;padding:8px 9px!important;border-radius:17px!important;
  font-size:9.6px!important;line-height:1.02!important;white-space:normal!important;font-weight:950!important;
}
#ng27.v326Mobile .cockpit>.timeline{
  grid-column:1!important;grid-row:3!important;position:relative!important;left:auto!important;right:auto!important;top:auto!important;bottom:auto!important;
  z-index:76!important;width:100%!important;max-width:430px!important;height:auto!important;min-height:0!important;margin:0!important;padding:9px 10px 8px!important;
  transform:none!important;border-radius:18px!important;border:1px solid rgba(151,187,216,.24)!important;
  background:rgba(255,255,255,.76)!important;box-shadow:0 8px 20px rgba(79,118,157,.08),inset 0 1px 0 rgba(255,255,255,.84)!important;
  -webkit-backdrop-filter:blur(14px)!important;backdrop-filter:blur(14px)!important;
}
#ng27.v326Mobile .cockpit>.timeline .tlMeta{margin:0 2px 7px!important;color:#6c81a1!important;font-size:8.2px!important}
#ng27.v326Mobile .cockpit>.timeline .tlMeta span:nth-child(2){display:flex!important;align-items:center!important;justify-content:center!important;min-height:26px!important;padding:0 10px!important;border-radius:13px!important;background:rgba(191,244,229,.62)!important;color:#277a72!important;font-size:0!important}
#ng27.v326Mobile .cockpit>.timeline .tlMeta span:nth-child(2):after{content:"CC  Caption AUTO ✓";font-size:8.1px!important;font-weight:950!important}
#ng27.v326Mobile .cockpit>.timeline .track{height:50px!important;border-radius:11px!important;border:1px solid rgba(82,160,221,.38)!important;overflow:hidden!important;background:linear-gradient(180deg,rgba(98,186,239,.18),rgba(78,145,211,.10)),repeating-linear-gradient(90deg,rgba(77,150,210,.15) 0 34px,rgba(255,255,255,.45) 34px 36px)!important}
#ng27.v326Mobile .cockpit>.timeline .trimRow{margin-top:5px!important;font-size:7.6px!important;color:#69819d!important}

#ng27.v326Mobile.gsfFullscreen .v326ToolDock,#ng27.v326Mobile:fullscreen .v326ToolDock,#ng27.v326Mobile:-webkit-full-screen .v326ToolDock{position:absolute!important}
#ng27.v326Mobile.gsfFullscreen .v326PlaybackDock,#ng27.v326Mobile:fullscreen .v326PlaybackDock,#ng27.v326Mobile:-webkit-full-screen .v326PlaybackDock{bottom:max(24px,env(safe-area-inset-bottom))!important}
</style>'''

SCRIPT=r'''<script id="v326MobileEditorRuntime">
(function(){
  const root=document.getElementById('ng27'); if(!root)return;
  const stage=root.querySelector('#stage');
  const cockpit=root.querySelector('.cockpit');
  const actions=root.querySelector('#v323EditorActions');
  const timeline=root.querySelector('.timeline');
  const playBtn=root.querySelector('#playBtn');
  const fullBtn=root.querySelector('#zoomEditorBtn');
  if(!stage||!cockpit||!actions||!timeline||!playBtn)return;
  const P=window.parent;
  const wantedLeft=['frame','caption','look'];
  const wantedRight=['audio','vision'];
  const qPanel=(name)=>root.querySelector('[data-panel="'+name+'"]');
  const coverBtn=root.querySelector('[data-panel="cover"]');
  const hudBtn=root.querySelector('[data-panel="hud"]');
  let raf=0;

  function ensureDock(cls){
    let d=stage.querySelector('.'+cls);
    if(!d){d=document.createElement('div');d.className='v326ToolDock '+cls;stage.appendChild(d)}
    return d;
  }
  function ensureMeta(){
    let m=stage.querySelector('.v326Meta');
    if(!m){m=document.createElement('div');m.className='v326Meta';m.innerHTML='<span class="v326Time">00:00 / 00:15</span><span class="v326Ratio">9:16</span>';stage.appendChild(m)}
    return m;
  }
  function ensurePlayback(){
    let d=stage.querySelector('.v326PlaybackDock');
    if(!d){
      d=document.createElement('div');d.className='v326PlaybackDock';
      const back=document.createElement('button');back.className='v326Skip';back.type='button';back.textContent='‹';back.onclick=()=>{const v=root.querySelector('#video');if(v)v.currentTime=Math.max(0,(v.currentTime||0)-1)};
      const next=document.createElement('button');next.className='v326Skip';next.type='button';next.textContent='›';next.onclick=()=>{const v=root.querySelector('#video');if(v)v.currentTime=Math.min(Number(v.duration)||1e9,(v.currentTime||0)+1)};
      d.append(back,playBtn,next);stage.appendChild(d);
    }else if(playBtn.parentNode!==d){const next=d.lastElementChild; if(next)d.insertBefore(playBtn,next); else d.appendChild(playBtn)}
    return d;
  }
  function updateTime(){
    const video=root.querySelector('#video');const chip=stage.querySelector('.v326Time');if(!chip)return;
    const d=Math.max(.01,Number(video&&video.duration)||Number(root.dataset.sourceDuration)||15);
    const c=Math.max(0,Number(video&&video.currentTime)||0);
    const f=(v)=>{const s=Math.max(0,Math.round(v));return String(Math.floor(s/60)).padStart(2,'0')+':'+String(s%60).padStart(2,'0')};
    chip.textContent=f(c)+' / '+f(d);
  }
  function isMobile(){
    const pw=Number(P&&P.innerWidth)||Number(window.innerWidth)||9999;
    return pw<=760 || (!!navigator.maxTouchPoints && pw<=1024);
  }
  function layout(){
    const mobile=isMobile();root.classList.toggle('v326Mobile',mobile);if(!mobile)return;
    root.classList.remove('expanded');
    const left=ensureDock('v326LeftDock'),right=ensureDock('v326RightDock');
    wantedLeft.forEach(n=>{const b=qPanel(n);if(b&&b.parentNode!==left)left.appendChild(b)});
    wantedRight.forEach(n=>{const b=qPanel(n);if(b&&b.parentNode!==right)right.appendChild(b)});
    if(coverBtn)coverBtn.style.display='none'; if(hudBtn)hudBtn.style.display='none';
    const legacyRails=stage.querySelectorAll('.rail.v325Rail');legacyRails.forEach(r=>r.style.display='none');
    ensureMeta();ensurePlayback();
    if(fullBtn&&fullBtn.parentNode!==stage)stage.appendChild(fullBtn);
    const stageWrap=root.querySelector('.stageWrap');
    if(stageWrap){
      if(actions.previousElementSibling!==stageWrap)stageWrap.insertAdjacentElement('afterend',actions);
      if(timeline.previousElementSibling!==actions)actions.insertAdjacentElement('afterend',timeline);
    }
    const caption=root.querySelector('#captionPreview');
    if(caption&&/^\s*CAPTION\s+AUTO\s*$/i.test(caption.textContent||''))caption.classList.add('v326DefaultCaption');
    const fh=Math.max(430,Math.floor((window.frameElement&&window.frameElement.getBoundingClientRect().height)||Number(P&&P.innerHeight)||700));
    const playerH=Math.max(340,Math.min(500,fh-168));
    const playerW=Math.max(205,Math.min(282,Math.round(playerH*9/16)));
    root.style.setProperty('--v326-player-w',playerW+'px');
    updateTime();
  }
  const video=root.querySelector('#video');
  if(video){video.addEventListener('timeupdate',updateTime,{passive:true});video.addEventListener('loadedmetadata',updateTime,{passive:true})}
  window.addEventListener('resize',()=>{cancelAnimationFrame(raf);raf=requestAnimationFrame(layout)},{passive:true});
  window.addEventListener('message',e=>{if(!e.data||e.data.type!=='GSF_EDITOR_FULLSCREEN_V326')return;if(fullBtn)fullBtn.click()});
  layout();requestAnimationFrame(layout);setTimeout(layout,80);
})();
</script>'''

BOOT_SNIPPET="""/* V326_BOOT_HOME_RESET */
try{
  if(!P.__GSF_BOOT_HOME_RESET_V326){
    P.__GSF_BOOT_HOME_RESET_V326=true;
    ['gsf_creator_hub_open_v107','gsf_editor_overlay_open_v220','gsf_editor_overlay_open_v223','gsf_ai_overlay_open_v221','gsf_social_overlay_open_v159','gsf_account_overlay_open_v223'].forEach(k=>{try{sessionStorage.setItem(k,'0')}catch(_e){}});
    P.postMessage({type:'GSF_SHELL_NAV',target:'home',section:''},P.location.origin);
  }else if(sessionStorage.getItem(KEY)==='1'){
    setTimeout(()=>open(false),90);
  }
}catch(e){}"""

HEADER_FULL='''<button class="v326HeaderFull" type="button" aria-label="Schermo intero"><span>↗</span> FULL</button>'''
HEADER_STYLE='''<style id="v326EditorHeaderFullStyle">
@media(max-width:760px){#gsf-editor-overlay-v220 .gsf-editor-head{padding-right:106px!important}#gsf-editor-overlay-v220 .v326HeaderFull{position:absolute;right:48px;top:7px;height:34px;min-width:66px;padding:0 10px;border-radius:13px;border:1px solid rgba(158,190,216,.30);background:rgba(255,255,255,.92);color:#48688d;font-size:10px;font-weight:950;letter-spacing:.035em;box-shadow:0 6px 16px rgba(64,104,143,.08)}}
</style>'''
HEADER_WIRE="""/* V326_HEADER_FULL_WIRE */
setTimeout(()=>{const b=document.querySelector('#gsf-editor-overlay-v220 .v326HeaderFull');if(b&&!b.dataset.wired){b.dataset.wired='1';b.addEventListener('click',()=>{try{frame.contentWindow.postMessage({type:'GSF_EDITOR_FULLSCREEN_V326'},location.origin)}catch(_e){}})}},0);"""


def patch_editor_text(text:str)->str:
    if f'id="{STYLE_ID}"' not in text:
        if '</head>' not in text: raise RuntimeError('V326 editor </head> missing')
        text=text.replace('</head>',STYLE+'\n</head>',1)
    if f'id="{SCRIPT_ID}"' not in text:
        if '</body>' not in text: raise RuntimeError('V326 editor </body> missing')
        text=text.replace('</body>',SCRIPT+'\n</body>',1)
    return text


def _lazy_iframe(text:str,path:str)->str:
    # Normalize eager hidden overlay iframe to lazy. Existing open() functions already load data-src.
    pat=re.compile(r'<iframe(?P<pre>[^>]*?)\bsrc="'+re.escape(path)+r'(?:\?[^\"]*)?"(?P<mid>[^>]*?)\bdata-src="'+re.escape(path)+r'"(?P<post>[^>]*?)\bdata-loaded="1"(?P<end>[^>]*)>',re.I)
    def repl(m):
        return '<iframe'+m.group('pre')+'src="about:blank"'+m.group('mid')+'data-src="'+path+'"'+m.group('post')+'data-loaded="0"'+m.group('end')+'>'
    return pat.sub(repl,text)


def patch_shell_text(text:str)->str:
    # 1) Fresh browser boot always starts Home. Same-page Streamlit reruns still preserve an intentionally open overlay.
    legacy_re=r"try\{if\(sessionStorage\.getItem\(KEY\)==='1'\)setTimeout\(\(\)=>open\(false\),90\)\}catch\(e\)\{\};?"
    if 'V326_BOOT_HOME_RESET' not in text:
        text,n=re.subn(legacy_re,BOOT_SNIPPET,text,count=1)
        if n==0:
            raise RuntimeError('V326 AI/editor auto-restore anchor missing')

    # 2) Hidden surfaces must not all boot at once. Their ensureFrame/open bridges stay authoritative.
    for path in ('/share-v156/','/creator-hub-v156/','/editor-live/','/ai-v221/','/account/'):
        text=_lazy_iframe(text,path)
    text=text.replace("if(frame && !String(frame.src||'').includes('/creator-hub-v156/')) frame.src='/creator-hub-v156/';",
                      "if(frame && frame.dataset.loaded==='1' && !String(frame.src||'').includes('/creator-hub-v156/')) frame.src='/creator-hub-v156/';")

    # 3) Parent header FULL mirrors the approved reference and triggers the real editor fullscreen control.
    if 'class="v326HeaderFull"' not in text:
        anchor='<div class="gsf-editor-head"><div>Game Editor<small>Il tuo gameplay resta nel progetto mentre modifichi.</small></div></div>'
        if anchor in text:
            text=text.replace(anchor,'<div class="gsf-editor-head"><div>Game Editor<small>Il tuo gameplay resta nel progetto mentre modifichi.</small></div>'+HEADER_FULL+'</div>',1)
        else:
            raise RuntimeError('V326 editor header anchor missing')
    if 'id="v326EditorHeaderFullStyle"' not in text:
        marker='<style id="gsf-v220-editor-shell">'
        if marker in text:text=text.replace(marker,HEADER_STYLE+'\n'+marker,1)
        else:text=HEADER_STYLE+'\n'+text
    if 'V326_HEADER_FULL_WIRE' not in text:
        # Insert where the editor overlay script already owns `frame` and `location`.
        marker="const sendRender=()=>{"
        if marker in text:text=text.replace(marker,HEADER_WIRE+'\n      '+marker,1)
        else: raise RuntimeError('V326 editor script anchor missing')
    return text


def main():
    root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
    editor=root/'web'/'editor_2027_component'/'index.html'
    shell=root/'GamingShortsFactory_V154_STRUCTURAL_HOME.py'
    if not editor.is_file() or not shell.is_file(): raise SystemExit('V326 required runtime files missing')
    eb=editor.read_text(encoding='utf-8'); ea=patch_editor_text(eb); editor.write_text(ea,encoding='utf-8')
    sb=shell.read_text(encoding='utf-8'); sa=patch_shell_text(sb); compile(sa,str(shell),'exec'); shell.write_text(sa,encoding='utf-8')
    print('V326 mobile editor exact + Home boot + lazy overlays applied', 'editor_changed=',eb!=ea,'shell_changed=',sb!=sa,flush=True)

if __name__=='__main__': main()
