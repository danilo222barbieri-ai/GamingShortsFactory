#!/usr/bin/env python3
from pathlib import Path
import re
import sys

MARK='V380_MOBILE_EDITOR_UNIFIED'

EDITOR_PATCH=r'''
<!-- V380_MOBILE_EDITOR_UNIFIED -->
<style id="v380MobileEditorUnified">
.v380EditorTitle{display:none}
@media(max-width:760px){
  html,body{width:100%!important;height:100%!important;margin:0!important;padding:0!important;overflow:hidden!important;background:transparent!important;overscroll-behavior:none!important}
  #ng27.v326Mobile{
    --v380-player-w:clamp(172px,46vw,188px);
    width:100%!important;height:100%!important;min-height:0!important;margin:0!important;padding:5px 8px 7px!important;overflow:hidden!important;
    background:radial-gradient(circle at 50% 8%,rgba(201,236,252,.92),transparent 31%),linear-gradient(180deg,#FAFDFF 0%,#EEF8FD 100%)!important;
  }
  #ng27.v326Mobile .shell{width:100%!important;height:auto!important;min-height:0!important;max-width:500px!important;margin:0 auto!important;padding:0!important;overflow:visible!important;background:transparent!important;box-shadow:none!important}
  #ng27.v326Mobile .topline{
    display:flex!important;position:relative!important;width:100%!important;height:56px!important;min-height:56px!important;margin:0 auto 7px!important;padding:7px 8px 7px 12px!important;
    align-items:center!important;justify-content:space-between!important;gap:8px!important;border-radius:18px!important;background:#fff!important;border:1px solid rgba(166,203,226,.34)!important;
    box-shadow:0 7px 20px rgba(65,110,151,.08)!important;overflow:hidden!important;z-index:120!important;
  }
  #ng27.v326Mobile .v380EditorTitle{display:flex!important;min-width:0!important;flex:1 1 auto!important;flex-direction:column!important;align-items:flex-start!important;justify-content:center!important;color:#103A79!important;text-align:left!important}
  #ng27.v326Mobile .v380EditorTitle strong{display:block!important;font-size:17px!important;line-height:1!important;font-weight:950!important;letter-spacing:-.025em!important}
  #ng27.v326Mobile .v380EditorTitle span{display:block!important;max-width:245px!important;margin-top:4px!important;white-space:nowrap!important;overflow:hidden!important;text-overflow:ellipsis!important;font-size:8px!important;line-height:1.05!important;font-weight:750!important;color:#7183A3!important}
  #ng27.v326Mobile .topline #zoomEditorBtn{position:relative!important;inset:auto!important;flex:0 0 auto!important;display:flex!important;align-items:center!important;justify-content:center!important;gap:5px!important;width:66px!important;min-width:66px!important;height:39px!important;min-height:39px!important;padding:0 8px!important;border-radius:13px!important;background:#F7FBFF!important;color:#2B4F86!important;border:1px solid rgba(154,190,219,.34)!important;box-shadow:0 5px 14px rgba(64,104,143,.08)!important}
  #ng27.v326Mobile .topline #zoomEditorBtn .mobileHide{display:inline!important;font-size:8px!important;font-weight:900!important}
  #ng27.v326Mobile .topline #zoomEditorBtn .ico{width:15px!important;height:15px!important}

  #ng27.v326Mobile .cockpit,#ng27.v326Mobile.expanded .cockpit{
    width:100%!important;max-width:490px!important;height:auto!important;min-height:0!important;margin:0 auto!important;padding:0 2px!important;overflow:visible!important;
    display:grid!important;grid-template-columns:minmax(0,1fr)!important;grid-template-rows:auto 48px 108px!important;gap:7px!important;align-content:start!important;align-items:start!important;justify-items:stretch!important;
  }
  #ng27.v326Mobile .stageWrap{grid-column:1!important;grid-row:1!important;position:relative!important;width:var(--v380-player-w)!important;max-width:calc(100% - 12px)!important;height:auto!important;min-height:0!important;margin:0 auto!important;padding:0!important;align-self:start!important;justify-self:center!important;overflow:visible!important}
  #ng27.v326Mobile .stage.r916,#ng27.v326Mobile.expanded .stage.r916{position:relative!important;width:100%!important;max-width:none!important;height:auto!important;aspect-ratio:9/16!important;margin:0!important;border-radius:21px!important;border:1px solid rgba(113,199,239,.56)!important;overflow:hidden!important;box-shadow:0 11px 26px rgba(49,103,145,.14),0 0 0 3px rgba(255,255,255,.56)!important;background:linear-gradient(180deg,#DDF4FE,#F5FBFF)!important}
  #ng27.v326Mobile .v326Meta{top:7px!important;left:7px!important;right:7px!important}
  #ng27.v326Mobile .v326Time,#ng27.v326Mobile .v326Ratio{height:27px!important;padding:0 7px!important;border-radius:11px!important;font-size:7.8px!important;background:rgba(29,55,84,.76)!important;box-shadow:0 4px 12px rgba(7,22,38,.15)!important}
  #ng27.v326Mobile .v326Ratio{margin-left:auto!important;margin-right:37px!important}
  #ng27.v326Mobile .v326ToolDock{gap:5px!important}
  #ng27.v326Mobile .v326LeftDock{left:6px!important}
  #ng27.v326Mobile .v326RightDock{right:6px!important}
  #ng27.v326Mobile .v326ToolDock .railBtn{width:39px!important;height:46px!important;min-width:39px!important;min-height:46px!important;border-radius:14px!important;background:linear-gradient(145deg,rgba(28,53,80,.76),rgba(56,82,109,.62))!important;border:1px solid rgba(255,255,255,.70)!important;box-shadow:0 5px 14px rgba(11,28,44,.18),inset 0 1px 0 rgba(255,255,255,.24)!important}
  #ng27.v326Mobile .v326ToolDock .railBtn .ico{width:16px!important;height:16px!important}
  #ng27.v326Mobile .v326ToolDock .railBtn span{font-size:6px!important;line-height:1!important;letter-spacing:.025em!important}
  #ng27.v326Mobile .v326PlaybackDock{bottom:38px!important;gap:8px!important}
  #ng27.v326Mobile #playBtn{width:48px!important;height:48px!important;min-width:48px!important;min-height:48px!important;box-shadow:0 7px 18px rgba(17,50,94,.30),inset 0 1px 0 rgba(255,255,255,.40)!important}
  #ng27.v326Mobile #playBtn .ico{width:21px!important;height:21px!important}
  #ng27.v326Mobile .v326Skip{width:26px!important;height:31px!important;font-size:19px!important}

  #ng27.v326Mobile .v380PlayerProgress{position:absolute!important;left:13px!important;right:13px!important;bottom:10px!important;z-index:99!important;color:#fff!important;display:grid!important;grid-template-columns:auto 1fr auto!important;grid-template-rows:auto auto!important;gap:3px 6px!important;align-items:center!important;pointer-events:auto!important;font-size:6.6px!important;font-weight:900!important;text-shadow:0 2px 6px rgba(0,0,0,.40)!important}
  #ng27.v326Mobile .v380ProgressTrack{grid-column:1/4;grid-row:1;height:4px!important;border-radius:999px!important;background:rgba(255,255,255,.45)!important;overflow:visible!important;position:relative!important;box-shadow:inset 0 1px 3px rgba(0,0,0,.16)!important}
  #ng27.v326Mobile .v380ProgressFill{position:absolute!important;left:0!important;top:0!important;bottom:0!important;width:0;border-radius:999px!important;background:linear-gradient(90deg,#56C8FF,#2D8BFF)!important}
  #ng27.v326Mobile .v380ProgressKnob{position:absolute!important;top:50%!important;left:0;width:10px!important;height:10px!important;border-radius:50%!important;background:#fff!important;transform:translate(-50%,-50%)!important;box-shadow:0 2px 7px rgba(20,52,85,.28)!important}
  #ng27.v326Mobile .v380ProgressNow{grid-column:1;grid-row:2} #ng27.v326Mobile .v380ProgressEnd{grid-column:3;grid-row:2;text-align:right}

  #ng27.v326Mobile .cockpit>.v323EditorActions{grid-column:1!important;grid-row:2!important;width:100%!important;height:48px!important;min-height:48px!important;margin:0!important;padding:0!important;display:grid!important;grid-template-columns:minmax(0,1fr) minmax(0,1fr)!important;gap:7px!important}
  #ng27.v326Mobile .cockpit>.v323EditorActions .v323EditorAction{height:48px!important;min-height:48px!important;padding:6px 8px!important;border-radius:17px!important;font-size:9px!important;line-height:1!important;letter-spacing:.01em!important;box-shadow:0 7px 18px rgba(62,107,151,.09)!important}
  #ng27.v326Mobile .cockpit>.v323EditorActions .v323EditorAction.primary{background:linear-gradient(135deg,#58C1FB,#347FEA)!important;border-color:rgba(75,162,235,.42)!important}

  #ng27.v326Mobile .cockpit>.timeline{grid-column:1!important;grid-row:3!important;width:100%!important;max-width:none!important;height:108px!important;min-height:108px!important;margin:0!important;padding:8px 9px 7px!important;overflow:visible!important;border-radius:17px!important;background:rgba(255,255,255,.92)!important;border:1px solid rgba(151,187,216,.26)!important;box-shadow:0 7px 20px rgba(79,118,157,.08),inset 0 1px 0 rgba(255,255,255,.96)!important;position:relative!important;z-index:5!important}
  #ng27.v326Mobile .cockpit>.timeline .tlMeta{margin:0 2px 6px!important;font-size:7.2px!important;font-weight:900!important}
  #ng27.v326Mobile .cockpit>.timeline .tlMeta span:nth-child(2){min-height:24px!important;padding:0 9px!important;border-radius:12px!important}
  #ng27.v326Mobile .cockpit>.timeline .track{height:43px!important;border-radius:10px!important;border:1.5px solid rgba(69,174,228,.66)!important;position:relative!important;background:linear-gradient(180deg,rgba(105,198,243,.13),rgba(78,145,211,.08)),repeating-linear-gradient(90deg,rgba(110,181,225,.24) 0 36px,rgba(255,255,255,.68) 36px 39px)!important}
  #ng27.v326Mobile .cockpit>.timeline .track:after{display:none!important}
  #ng27.v326Mobile .cockpit>.timeline .trimRow{margin-top:4px!important;font-size:6.8px!important;position:relative!important;z-index:7!important;overflow:visible!important}
  #ng27.v326Mobile .cockpit>.timeline input[type="range"]{position:relative!important;z-index:8!important}
  #ng27.v326Mobile .drawer{max-height:min(48%,300px)!important;overflow-y:auto!important;overflow-x:hidden!important}

  /* V380_IOS_STABLE_COMPOSITE */
  #ng27.v326Mobile .shell,#ng27.v326Mobile .topline,#ng27.v326Mobile .cockpit,#ng27.v326Mobile .stageWrap,#ng27.v326Mobile .stage,#ng27.v326Mobile video,#ng27.v326Mobile #videoBg,#ng27.v326Mobile .v326ToolDock .railBtn,#ng27.v326Mobile #zoomEditorBtn,#ng27.v326Mobile .v326PlaybackDock,#ng27.v326Mobile #playBtn{transition:none!important;animation:none!important;-webkit-backdrop-filter:none!important;backdrop-filter:none!important}
  #ng27.v326Mobile .stage{transform:translateZ(0)!important;-webkit-backface-visibility:hidden!important;backface-visibility:hidden!important;contain:layout paint!important}
  #ng27.v326Mobile video,#ng27.v326Mobile #videoBg{transform:translateZ(0)!important;-webkit-backface-visibility:hidden!important;backface-visibility:hidden!important}
}
</style>
<script id="v380MobileEditorUnifiedRuntime">
(()=>{
  const root=document.getElementById('ng27'); if(!root)return;
  const top=root.querySelector('.topline');
  if(top&&!top.querySelector('.v380EditorTitle')){
    const title=document.createElement('div'); title.className='v380EditorTitle';
    title.innerHTML='<strong>Game Editor</strong><span>Il tuo gameplay resta nel progetto mentre modifichi.</span>';
    top.insertBefore(title,top.firstChild);
  }
  const stage=root.querySelector('#stage'),video=root.querySelector('#video'); if(!stage||!video)return;
  let box=stage.querySelector('.v380PlayerProgress');
  if(!box){box=document.createElement('div');box.className='v380PlayerProgress';box.innerHTML='<div class="v380ProgressTrack"><div class="v380ProgressFill"></div><div class="v380ProgressKnob"></div></div><span class="v380ProgressNow">00:00</span><span class="v380ProgressEnd">00:15</span>';stage.appendChild(box)}
  const track=box.querySelector('.v380ProgressTrack'),fill=box.querySelector('.v380ProgressFill'),knob=box.querySelector('.v380ProgressKnob'),now=box.querySelector('.v380ProgressNow'),end=box.querySelector('.v380ProgressEnd');
  const fmt=(v)=>{const s=Math.max(0,Math.round(Number(v)||0));return String(Math.floor(s/60)).padStart(2,'0')+':'+String(s%60).padStart(2,'0')};
  const sync=()=>{const d=Math.max(.01,Number(video.duration)||Number(root.dataset.sourceDuration)||15),c=Math.max(0,Math.min(d,Number(video.currentTime)||0)),p=Math.max(0,Math.min(100,c/d*100));fill.style.width=p+'%';knob.style.left=p+'%';now.textContent=fmt(c);end.textContent=fmt(d)};
  track.addEventListener('click',(ev)=>{const r=track.getBoundingClientRect();if(!r.width)return;const p=Math.max(0,Math.min(1,(ev.clientX-r.left)/r.width)),d=Math.max(.01,Number(video.duration)||15);video.currentTime=p*d;sync()});
  video.addEventListener('timeupdate',sync,{passive:true}); video.addEventListener('loadedmetadata',sync,{passive:true}); sync();
})();
</script>
'''

SHELL_PATCH=r'''
<style id="v380EditorParentUnified">
@media(max-width:760px){
  #gsf-editor-overlay-v220{overflow:hidden!important}
  #gsf-editor-overlay-v220 .gsf-editor-head{display:none!important}
  #gsf-editor-overlay-v220 iframe.gsf-editor-frame,#gsf-editor-overlay-v220 iframe[title="Game Editor"]{width:100%!important;min-height:0!important;border:0!important;background:transparent!important;-webkit-backface-visibility:hidden!important;backface-visibility:hidden!important;transform:translate3d(0,0,0)!important;isolation:isolate!important}
}
</style>
<script id="V380_HIDE_DUPLICATE_FINAL_CTA">
(()=>{
  const root=document.getElementById('gsf-editor-overlay-v220'); if(!root)return;
  const clean=()=>root.querySelectorAll('button,a,[role="button"]').forEach((el)=>{const t=String(el.textContent||'').replace(/\s+/g,' ').trim().toUpperCase();if(t.includes('HAI FINITO')&&t.includes('CREA IL TUO SHORT')){el.style.setProperty('display','none','important');el.setAttribute('data-v380-hidden-final-cta','1')}});
  clean(); try{new MutationObserver(clean).observe(root,{childList:true,subtree:true})}catch(_e){}
})();
</script>
'''

def strip_legacy_editor(text:str)->str:
    patterns=[
        r'\s*<!-- V376_MOBILE_EDITOR_REFERENCE -->\s*<style id="v376MobileEditorReference">.*?</style>\s*<script id="v376MobileEditorReferenceRuntime">.*?</script>\s*',
        r'\s*<!-- V378_MOBILE_EDITOR_STACK -->\s*<style id="v378MobileEditorStack">.*?</style>\s*',
        r'\s*<!-- V379_MOBILE_EDITOR_FINAL_COMPOSE -->\s*<style id="v379MobileEditorFinalCompose">.*?</style>\s*<script id="v379MobileEditorFinalComposeRuntime">.*?</script>\s*',
    ]
    for p in patterns:text=re.sub(p,'\n',text,flags=re.S)
    return text

def strip_legacy_shell(text:str)->str:
    patterns=[
        r'\s*<style id="v376EditorTitleCard">.*?</style>\s*',
        r'\s*<style id="v379EditorParentCleanup">.*?</style>\s*<script id="V379_HIDE_DUPLICATE_FINAL_CTA">.*?</script>\s*',
    ]
    for p in patterns:text=re.sub(p,'\n',text,flags=re.S)
    return text

def patch_editor(text:str)->str:
    text=strip_legacy_editor(text)
    if MARK in text:return text
    if '</body>' not in text:raise RuntimeError('V380 editor body anchor missing')
    return text.replace('</body>',EDITOR_PATCH+'\n</body>',1)

def patch_shell(text:str)->str:
    text=strip_legacy_shell(text)
    if 'V380_HIDE_DUPLICATE_FINAL_CTA' in text:return text
    marker='<style id="gsf-v220-editor-shell">'
    if marker not in text:raise RuntimeError('V380 parent Editor shell anchor missing')
    out=text.replace(marker,SHELL_PATCH+'\n'+marker,1)
    compile(out,'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py','exec')
    return out

def main()->None:
    root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
    editor=root/'web'/'editor_2027_component'/'index.html'; shell=root/'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py'
    if not editor.is_file() or not shell.is_file():raise SystemExit('V380 runtime files missing')
    eb=editor.read_text(encoding='utf-8'); ea=patch_editor(eb); editor.write_text(ea,encoding='utf-8')
    sb=shell.read_text(encoding='utf-8'); sa=patch_shell(sb); shell.write_text(sa,encoding='utf-8')
    print('V380 unified mobile Editor applied editor_changed=',eb!=ea,'shell_changed=',sb!=sa,flush=True)

if __name__=='__main__':main()
