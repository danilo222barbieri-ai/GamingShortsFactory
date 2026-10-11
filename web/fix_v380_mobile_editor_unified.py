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
  #ng27.v326Mobile{--v380-player-w:clamp(205px,56vw,230px);width:100%!important;height:100%!important;margin:0!important;padding:6px 10px 8px!important;overflow:hidden!important;background:radial-gradient(circle at 50% 10%,rgba(205,239,253,.82),transparent 34%),linear-gradient(180deg,#fbfdff 0%,#eef8fd 100%)!important}
  #ng27.v326Mobile .shell{width:100%!important;height:auto!important;max-width:500px!important;margin:0 auto!important;padding:0!important;overflow:visible!important;background:transparent!important;box-shadow:none!important}

  #ng27.v326Mobile .topline{display:flex!important;position:relative!important;width:100%!important;height:54px!important;min-height:54px!important;margin:0 auto 8px!important;padding:7px 9px 7px 13px!important;align-items:center!important;justify-content:space-between!important;gap:8px!important;border-radius:18px!important;background:rgba(255,255,255,.96)!important;border:1px solid rgba(166,203,226,.32)!important;box-shadow:0 7px 18px rgba(65,110,151,.07)!important;overflow:hidden!important;z-index:120!important}
  /* V380_HIDE_LEGACY_TOPLINE_CHILDREN: exactly one title + FULL */
  #ng27.v326Mobile .topline>*{display:none!important}
  #ng27.v326Mobile .topline>.v380EditorTitle,#ng27.v326Mobile .topline>#zoomEditorBtn{display:flex!important}
  #ng27.v326Mobile .v380EditorTitle{min-width:0!important;flex:1 1 auto!important;flex-direction:column!important;align-items:flex-start!important;justify-content:center!important;color:#123d7a!important;text-align:left!important}
  #ng27.v326Mobile .v380EditorTitle strong{font-size:17px!important;line-height:1!important;font-weight:950!important;letter-spacing:-.025em!important}
  #ng27.v326Mobile .v380EditorTitle span{max-width:245px!important;margin-top:4px!important;white-space:nowrap!important;overflow:hidden!important;text-overflow:ellipsis!important;font-size:8px!important;line-height:1!important;font-weight:750!important;color:#7183a3!important}
  #ng27.v326Mobile #zoomEditorBtn{position:relative!important;inset:auto!important;flex:0 0 auto!important;align-items:center!important;justify-content:center!important;gap:5px!important;width:66px!important;height:38px!important;padding:0 8px!important;border-radius:13px!important;background:#f7fbff!important;color:#2b4f86!important;border:1px solid rgba(154,190,219,.34)!important;box-shadow:none!important}
  #ng27.v326Mobile #zoomEditorBtn .mobileHide{display:inline!important;font-size:8px!important;font-weight:900!important}
  #ng27.v326Mobile #zoomEditorBtn .mobileHide::after{content:"FULL";font-size:0} /* FULL */

  #ng27.v326Mobile .cockpit,#ng27.v326Mobile.expanded .cockpit{width:100%!important;max-width:490px!important;height:auto!important;min-height:0!important;margin:0 auto!important;padding:0 2px!important;overflow:visible!important;display:grid!important;grid-template-columns:minmax(0,1fr)!important;grid-template-rows:auto 50px 122px!important;gap:8px!important;align-content:start!important;align-items:start!important;justify-items:stretch!important}
  #ng27.v326Mobile .stageWrap{grid-column:1!important;grid-row:1!important;position:relative!important;width:var(--v380-player-w)!important;max-width:calc(100% - 10px)!important;height:auto!important;margin:0 auto!important;padding:0!important;justify-self:center!important;overflow:visible!important}
  #ng27.v326Mobile .stage.r916,#ng27.v326Mobile.expanded .stage.r916{position:relative!important;width:100%!important;height:auto!important;aspect-ratio:9/16!important;margin:0!important;border-radius:22px!important;border:1px solid rgba(104,194,238,.56)!important;overflow:hidden!important;box-shadow:0 10px 25px rgba(49,103,145,.13),0 0 0 3px rgba(255,255,255,.58)!important;background:linear-gradient(180deg,#dff4fd,#f7fcff)!important}

  #ng27.v326Mobile .v326Meta{top:8px!important;left:8px!important;right:8px!important}
  #ng27.v326Mobile .v326Time,#ng27.v326Mobile .v326Ratio{height:28px!important;padding:0 8px!important;border-radius:11px!important;font-size:8px!important;background:rgba(29,55,84,.78)!important;box-shadow:0 4px 11px rgba(7,22,38,.14)!important}
  #ng27.v326Mobile .v326Ratio{margin-left:auto!important;margin-right:38px!important}
  #ng27.v326Mobile .v326ToolDock{gap:7px!important}
  #ng27.v326Mobile .v326LeftDock{left:8px!important}
  #ng27.v326Mobile .v326RightDock{right:8px!important}
  #ng27.v326Mobile .v326ToolDock .railBtn{width:43px!important;height:50px!important;min-width:43px!important;min-height:50px!important;border-radius:15px!important;background:linear-gradient(145deg,rgba(34,60,87,.82),rgba(67,91,117,.72))!important;border:1px solid rgba(255,255,255,.72)!important;box-shadow:0 5px 13px rgba(11,28,44,.17)!important;color:#fff!important}
  #ng27.v326Mobile .v326ToolDock .railBtn .ico{width:17px!important;height:17px!important}
  #ng27.v326Mobile .v326ToolDock .railBtn span{font-size:6.2px!important;line-height:1!important;color:#fff!important}
  #ng27.v326Mobile .v326PlaybackDock{bottom:38px!important;gap:9px!important}
  #ng27.v326Mobile #playBtn{width:50px!important;height:50px!important;min-width:50px!important;min-height:50px!important;box-shadow:0 7px 17px rgba(17,50,94,.28)!important}
  #ng27.v326Mobile .v326Skip{width:27px!important;height:31px!important;font-size:19px!important}

  #ng27.v326Mobile .v380PlayerProgress{position:absolute!important;left:14px!important;right:14px!important;bottom:10px!important;z-index:99!important;color:#fff!important;display:grid!important;grid-template-columns:auto 1fr auto!important;grid-template-rows:auto auto!important;gap:3px 6px!important;align-items:center!important;pointer-events:auto!important;font-size:6.8px!important;font-weight:900!important;text-shadow:0 2px 6px rgba(0,0,0,.38)!important}
  #ng27.v326Mobile .v380ProgressTrack{grid-column:1/4;grid-row:1;height:4px!important;border-radius:999px!important;background:rgba(255,255,255,.48)!important;position:relative!important}
  #ng27.v326Mobile .v380ProgressFill{position:absolute!important;inset:0 auto 0 0;width:0;border-radius:999px!important;background:linear-gradient(90deg,#56c8ff,#2d8bff)!important}
  #ng27.v326Mobile .v380ProgressKnob{position:absolute!important;top:50%!important;left:0;width:10px!important;height:10px!important;border-radius:50%!important;background:#fff!important;transform:translate(-50%,-50%)!important;box-shadow:0 2px 7px rgba(20,52,85,.28)!important}
  #ng27.v326Mobile .v380ProgressNow{grid-column:1;grid-row:2} #ng27.v326Mobile .v380ProgressEnd{grid-column:3;grid-row:2;text-align:right}

  #ng27.v326Mobile .cockpit>.v323EditorActions{grid-column:1!important;grid-row:2!important;width:100%!important;height:50px!important;margin:0!important;padding:0!important;display:grid!important;grid-template-columns:1fr 1fr!important;gap:8px!important}
  #ng27.v326Mobile .cockpit>.v323EditorActions .v323EditorAction{height:50px!important;min-height:50px!important;padding:6px 9px!important;border-radius:17px!important;font-size:9px!important;line-height:1!important;box-shadow:0 6px 16px rgba(62,107,151,.08)!important}
  #ng27.v326Mobile .cockpit>.v323EditorActions .primary{background:linear-gradient(135deg,#58c1fb,#347fea)!important}

  #ng27.v326Mobile .cockpit>.timeline{grid-column:1!important;grid-row:3!important;width:100%!important;height:122px!important;min-height:122px!important;margin:0!important;padding:9px 10px!important;overflow:hidden!important;border-radius:18px!important;background:rgba(255,255,255,.94)!important;border:1px solid rgba(151,187,216,.27)!important;box-shadow:0 6px 18px rgba(79,118,157,.07)!important;position:relative!important;z-index:5!important}
  #ng27.v326Mobile .timeline .tlMeta{margin:0 2px 7px!important;font-size:7.5px!important;font-weight:900!important}
  #ng27.v326Mobile .timeline .tlMeta span:nth-child(2){min-height:25px!important;padding:0 10px!important;border-radius:13px!important}
  #ng27.v326Mobile .timeline .track{height:48px!important;border-radius:11px!important;border:1.5px solid rgba(69,174,228,.68)!important;background:linear-gradient(180deg,rgba(105,198,243,.13),rgba(78,145,211,.08)),repeating-linear-gradient(90deg,rgba(110,181,225,.22) 0 38px,rgba(255,255,255,.72) 38px 41px)!important}
  #ng27.v326Mobile .timeline .track:after{display:none!important}
  #ng27.v326Mobile .timeline .trimRow{margin-top:5px!important;font-size:6.8px!important;position:relative!important;z-index:7!important}
  #ng27.v326Mobile .drawer{max-height:min(48%,300px)!important;overflow-y:auto!important;overflow-x:hidden!important}

  /* V380_IOS_STABLE_COMPOSITE */
  #ng27.v326Mobile .shell,#ng27.v326Mobile .topline,#ng27.v326Mobile .cockpit,#ng27.v326Mobile .stageWrap,#ng27.v326Mobile .stage,#ng27.v326Mobile video,#ng27.v326Mobile #videoBg,#ng27.v326Mobile .railBtn,#ng27.v326Mobile #zoomEditorBtn,#ng27.v326Mobile .v326PlaybackDock,#ng27.v326Mobile #playBtn{transition:none!important;animation:none!important;-webkit-backdrop-filter:none!important;backdrop-filter:none!important}
  #ng27.v326Mobile .stage,#ng27.v326Mobile video,#ng27.v326Mobile #videoBg{transform:translateZ(0)!important;-webkit-backface-visibility:hidden!important;backface-visibility:hidden!important}
}
</style>
<script id="v380MobileEditorUnifiedRuntime">
(()=>{
 const root=document.getElementById('ng27');if(!root)return;
 const top=root.querySelector('.topline');if(top){top.querySelector('.v380EditorTitle')?.remove();const title=document.createElement('div');title.className='v380EditorTitle';title.innerHTML='<strong>Game Editor</strong><span>Il tuo gameplay resta nel progetto mentre modifichi.</span>';top.insertBefore(title,top.firstChild);const z=top.querySelector('#zoomEditorBtn');if(z){const m=z.querySelector('.mobileHide');if(m)m.textContent='FULL'}}
 const stage=root.querySelector('#stage'),video=root.querySelector('#video');if(!stage||!video)return;
 let box=stage.querySelector('.v380PlayerProgress');if(!box){box=document.createElement('div');box.className='v380PlayerProgress';box.innerHTML='<div class="v380ProgressTrack"><div class="v380ProgressFill"></div><div class="v380ProgressKnob"></div></div><span class="v380ProgressNow">00:00</span><span class="v380ProgressEnd">00:15</span>';stage.appendChild(box)}
 const track=box.querySelector('.v380ProgressTrack'),fill=box.querySelector('.v380ProgressFill'),knob=box.querySelector('.v380ProgressKnob'),now=box.querySelector('.v380ProgressNow'),end=box.querySelector('.v380ProgressEnd');
 const fmt=v=>{const s=Math.max(0,Math.round(Number(v)||0));return String(Math.floor(s/60)).padStart(2,'0')+':'+String(s%60).padStart(2,'0')};
 const sync=()=>{const d=Math.max(.01,Number(video.duration)||Number(root.dataset.sourceDuration)||15),c=Math.max(0,Math.min(d,Number(video.currentTime)||0)),p=Math.max(0,Math.min(100,c/d*100));fill.style.width=p+'%';knob.style.left=p+'%';now.textContent=fmt(c);end.textContent=fmt(d)};
 track.addEventListener('click',ev=>{const r=track.getBoundingClientRect();if(!r.width)return;video.currentTime=Math.max(0,Math.min(1,(ev.clientX-r.left)/r.width))*Math.max(.01,Number(video.duration)||15);sync()});video.addEventListener('timeupdate',sync,{passive:true});video.addEventListener('loadedmetadata',sync,{passive:true});sync();
})();
</script>
'''

SHELL_PATCH=r'''
<style id="v380EditorParentUnified">
@media(max-width:760px){#gsf-editor-overlay-v220{overflow:hidden!important}#gsf-editor-overlay-v220 .gsf-editor-head{display:none!important}#gsf-editor-overlay-v220 iframe.gsf-editor-frame,#gsf-editor-overlay-v220 iframe[title="Game Editor"]{width:100%!important;min-height:0!important;border:0!important;background:transparent!important;transform:translate3d(0,0,0)!important;isolation:isolate!important}}
</style>
<script id="V380_HIDE_DUPLICATE_FINAL_CTA">
(()=>{const clean=()=>document.querySelectorAll('button,a,[role="button"],div').forEach(el=>{if(el.children.length>5)return;const t=String(el.textContent||'').replace(/\s+/g,' ').trim().toUpperCase();if(t.includes('HAI FINITO')&&t.includes('CREA IL TUO SHORT')){const target=el.closest('button,a,[role="button"]')||el;target.style.setProperty('display','none','important');target.setAttribute('data-v380-hidden-final-cta','1')}});clean();try{new MutationObserver(clean).observe(document.body,{childList:true,subtree:true})}catch(_e){}})();
</script>
'''

def strip_editor(text:str)->str:
    pats=[
      r'\s*<!-- V376_MOBILE_EDITOR_REFERENCE -->.*?<script id="v376MobileEditorReferenceRuntime">.*?</script>\s*',
      r'\s*<!-- V378_MOBILE_EDITOR_STACK -->.*?</style>\s*',
      r'\s*<!-- V379_MOBILE_EDITOR_FINAL_COMPOSE -->.*?<script id="v379MobileEditorFinalComposeRuntime">.*?</script>\s*',
      r'\s*<!-- V380_MOBILE_EDITOR_UNIFIED -->.*?<script id="v380MobileEditorUnifiedRuntime">.*?</script>\s*',
    ]
    for p in pats:text=re.sub(p,'\n',text,flags=re.S)
    return text

def strip_shell(text:str)->str:
    pats=[
      r'\s*<style id="v376EditorTitleCard">.*?</style>\s*',
      r'\s*<style id="v379EditorParentCleanup">.*?<script id="V379_HIDE_DUPLICATE_FINAL_CTA">.*?</script>\s*',
      r'\s*<style id="v380EditorParentUnified">.*?<script id="V380_HIDE_DUPLICATE_FINAL_CTA">.*?</script>\s*',
    ]
    for p in pats:text=re.sub(p,'\n',text,flags=re.S)
    return text

def patch_editor(text:str)->str:
    text=strip_editor(text)
    if '</body>' not in text:raise RuntimeError('V380 editor body anchor missing')
    return text.replace('</body>',EDITOR_PATCH+'\n</body>',1)

def patch_shell(text:str)->str:
    text=strip_shell(text)
    marker='<style id="gsf-v220-editor-shell">'
    if marker not in text:raise RuntimeError('V380 parent Editor shell anchor missing')
    out=text.replace(marker,SHELL_PATCH+'\n'+marker,1)
    compile(out,'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py','exec')
    return out

def main()->None:
    root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
    editor=root/'web'/'editor_2027_component'/'index.html';shell=root/'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py'
    if not editor.is_file() or not shell.is_file():raise SystemExit('V380 runtime files missing')
    eb=editor.read_text(encoding='utf-8');ea=patch_editor(eb);editor.write_text(ea,encoding='utf-8')
    sb=shell.read_text(encoding='utf-8');sa=patch_shell(sb);shell.write_text(sa,encoding='utf-8')
    print('V380 clean mobile Editor applied editor_changed=',eb!=ea,'shell_changed=',sb!=sa,flush=True)

if __name__=='__main__':main()
