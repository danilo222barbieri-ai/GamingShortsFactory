#!/usr/bin/env python3
from pathlib import Path
import sys

MARK='V376_MOBILE_EDITOR_REFERENCE'

# V376 correction: the approved mobile composition must fit as one Editor surface.
# Order stays: Editor header -> player -> actions -> timeline -> global Game Bar.
# The iframe itself must never become a second scrolling page.
EDITOR_PATCH=r'''
<!-- V376_MOBILE_EDITOR_REFERENCE -->
<style id="v376MobileEditorReference">
@media(max-width:760px){
  html,body{
    width:100%!important;height:100%!important;min-height:0!important;
    margin:0!important;padding:0!important;overflow:hidden!important;
    background:transparent!important;overscroll-behavior:none!important;
  }
  #ng27.v326Mobile{
    --v376-player-w:clamp(196px,56vw,224px);
    width:100%!important;height:100%!important;min-height:0!important;max-height:100%!important;
    box-sizing:border-box!important;margin:0!important;padding:4px 8px 6px!important;
    overflow:hidden!important;overscroll-behavior:none!important;
    background:radial-gradient(circle at 50% 5%,rgba(197,235,252,.98),transparent 31%),radial-gradient(circle at 12% 48%,rgba(218,246,255,.72),transparent 32%),linear-gradient(180deg,#F9FDFF 0%,#EEF8FD 100%)!important;
  }
  #ng27.v326Mobile .shell{
    width:100%!important;height:100%!important;min-height:0!important;max-width:500px!important;
    margin:0 auto!important;padding:0!important;overflow:hidden!important;background:transparent!important;
  }
  #ng27.v326Mobile .cockpit,#ng27.v326Mobile.expanded .cockpit{
    width:100%!important;max-width:490px!important;height:100%!important;min-height:0!important;
    margin:0 auto!important;padding:0 2px!important;overflow:hidden!important;
    display:grid!important;grid-template-columns:minmax(0,1fr)!important;
    grid-template-rows:minmax(0,1fr) 48px 92px!important;
    gap:7px!important;align-items:stretch!important;align-content:stretch!important;justify-items:stretch!important;
  }
  #ng27.v326Mobile .stageWrap{
    grid-column:1!important;grid-row:1!important;position:relative!important;
    width:var(--v376-player-w)!important;max-width:calc(100% - 12px)!important;height:auto!important;min-height:0!important;
    margin:0 auto!important;padding:0!important;align-self:start!important;justify-self:center!important;overflow:visible!important;
  }
  #ng27.v326Mobile .stage.r916,#ng27.v326Mobile.expanded .stage.r916{
    position:relative!important;width:100%!important;max-width:none!important;height:auto!important;aspect-ratio:9/16!important;margin:0!important;
    border-radius:22px!important;border:1px solid rgba(113,199,239,.58)!important;overflow:hidden!important;
    box-shadow:0 12px 30px rgba(49,103,145,.16),0 0 0 4px rgba(255,255,255,.52)!important;
    background:linear-gradient(180deg,#DDF4FE,#F5FBFF)!important;
  }
  #ng27.v326Mobile .v326Meta{top:8px!important;left:8px!important;right:8px!important}
  #ng27.v326Mobile .v326Time,#ng27.v326Mobile .v326Ratio{
    height:29px!important;padding:0 8px!important;border-radius:12px!important;font-size:8.2px!important;
    background:rgba(29,55,84,.72)!important;box-shadow:0 5px 14px rgba(7,22,38,.16)!important;
  }
  #ng27.v326Mobile .v326Ratio{margin-left:auto!important;margin-right:41px!important}
  #ng27.v326Mobile #zoomEditorBtn{
    top:8px!important;right:8px!important;width:35px!important;height:35px!important;min-width:35px!important;min-height:35px!important;
    border-radius:12px!important;background:rgba(29,55,84,.72)!important;box-shadow:0 5px 14px rgba(7,22,38,.16)!important;
  }
  #ng27.v326Mobile #zoomEditorBtn .ico{width:17px!important;height:17px!important}
  #ng27.v326Mobile .v326ToolDock{gap:6px!important}
  #ng27.v326Mobile .v326LeftDock{left:7px!important}
  #ng27.v326Mobile .v326RightDock{right:7px!important}
  #ng27.v326Mobile .v326ToolDock .railBtn{
    width:43px!important;height:52px!important;min-width:43px!important;min-height:52px!important;border-radius:15px!important;
    background:linear-gradient(145deg,rgba(28,53,80,.73),rgba(56,82,109,.59))!important;
    border:1px solid rgba(255,255,255,.74)!important;box-shadow:0 6px 17px rgba(11,28,44,.20),inset 0 1px 0 rgba(255,255,255,.27)!important;
  }
  #ng27.v326Mobile .v326ToolDock .railBtn .ico{width:18px!important;height:18px!important}
  #ng27.v326Mobile .v326ToolDock .railBtn span{font-size:6.6px!important;line-height:1!important;letter-spacing:.035em!important}
  #ng27.v326Mobile .v326PlaybackDock{bottom:42px!important;gap:9px!important}
  #ng27.v326Mobile #playBtn{
    width:52px!important;height:52px!important;min-width:52px!important;min-height:52px!important;
    box-shadow:0 8px 21px rgba(17,50,94,.32),inset 0 1px 0 rgba(255,255,255,.42)!important;
  }
  #ng27.v326Mobile #playBtn .ico{width:23px!important;height:23px!important}
  #ng27.v326Mobile .v326Skip{width:28px!important;height:34px!important;font-size:21px!important}
  #ng27.v326Mobile .v376PlayerProgress{
    position:absolute!important;left:15px!important;right:15px!important;bottom:12px!important;z-index:99!important;
    color:#fff!important;display:grid!important;grid-template-columns:auto 1fr auto!important;grid-template-rows:auto auto!important;
    gap:3px 7px!important;align-items:center!important;pointer-events:auto!important;font-size:6.9px!important;font-weight:900!important;text-shadow:0 2px 6px rgba(0,0,0,.40)!important;
  }
  #ng27.v326Mobile .v376ProgressTrack{
    grid-column:1/4;grid-row:1;height:5px!important;border-radius:999px!important;background:rgba(255,255,255,.44)!important;
    overflow:visible!important;position:relative!important;box-shadow:inset 0 1px 3px rgba(0,0,0,.16)!important;
  }
  #ng27.v326Mobile .v376ProgressFill{position:absolute!important;left:0!important;top:0!important;bottom:0!important;width:0;border-radius:999px!important;background:linear-gradient(90deg,#56C8FF,#2D8BFF)!important}
  #ng27.v326Mobile .v376ProgressKnob{position:absolute!important;top:50%!important;left:0;width:11px!important;height:11px!important;border-radius:50%!important;background:#fff!important;transform:translate(-50%,-50%)!important;box-shadow:0 2px 7px rgba(20,52,85,.28)!important}
  #ng27.v326Mobile .v376ProgressNow{grid-column:1;grid-row:2}
  #ng27.v326Mobile .v376ProgressEnd{grid-column:3;grid-row:2;text-align:right}

  /* Approved vertical order: player, paired actions, timeline. */
  #ng27.v326Mobile .cockpit>.v323EditorActions{
    grid-column:1!important;grid-row:2!important;width:100%!important;max-width:none!important;height:48px!important;min-height:48px!important;
    margin:0!important;padding:0!important;display:grid!important;grid-template-columns:minmax(0,1fr) minmax(0,1fr)!important;gap:7px!important;
  }
  #ng27.v326Mobile .cockpit>.v323EditorActions .v323EditorAction{
    height:48px!important;min-height:48px!important;padding:6px 8px!important;border-radius:17px!important;
    font-size:9.2px!important;line-height:1!important;letter-spacing:.01em!important;box-shadow:0 7px 19px rgba(62,107,151,.09)!important;
  }
  #ng27.v326Mobile .cockpit>.v323EditorActions .v323EditorAction.primary{background:linear-gradient(135deg,#58C1FB,#347FEA)!important;border-color:rgba(75,162,235,.42)!important}

  #ng27.v326Mobile .cockpit>.timeline{
    grid-column:1!important;grid-row:3!important;width:100%!important;max-width:none!important;height:92px!important;min-height:92px!important;
    margin:0!important;padding:7px 9px 6px!important;overflow:hidden!important;border-radius:17px!important;
    background:rgba(255,255,255,.84)!important;border:1px solid rgba(151,187,216,.24)!important;
    box-shadow:0 7px 20px rgba(79,118,157,.08),inset 0 1px 0 rgba(255,255,255,.92)!important;
  }
  #ng27.v326Mobile .cockpit>.timeline .tlMeta{margin:0 2px 5px!important;font-size:7.2px!important;font-weight:900!important}
  #ng27.v326Mobile .cockpit>.timeline .tlMeta span:nth-child(2){min-height:24px!important;padding:0 9px!important;border-radius:12px!important}
  #ng27.v326Mobile .cockpit>.timeline .tlMeta span:nth-child(2):after{font-size:7px!important}
  #ng27.v326Mobile .cockpit>.timeline .track{
    height:34px!important;border-radius:10px!important;border:1.5px solid rgba(69,174,228,.66)!important;position:relative!important;
    background:linear-gradient(180deg,rgba(105,198,243,.13),rgba(78,145,211,.08)),repeating-linear-gradient(90deg,rgba(110,181,225,.24) 0 36px,rgba(255,255,255,.68) 36px 39px)!important;
  }
  #ng27.v326Mobile .cockpit>.timeline .track:after{display:none!important}
  #ng27.v326Mobile .cockpit>.timeline .trimRow{margin-top:3px!important;font-size:6.8px!important}

  /* Real tool drawers may scroll; the Editor page itself may not. */
  #ng27.v326Mobile .drawer{max-height:min(48%,300px)!important;overflow-y:auto!important;overflow-x:hidden!important}
}
</style>
<script id="v376MobileEditorReferenceRuntime">
(()=>{
  const root=document.getElementById('ng27'); if(!root)return;
  const stage=root.querySelector('#stage'),video=root.querySelector('#video'); if(!stage||!video)return;
  let box=stage.querySelector('.v376PlayerProgress');
  if(!box){box=document.createElement('div');box.className='v376PlayerProgress';box.innerHTML='<div class="v376ProgressTrack"><div class="v376ProgressFill"></div><div class="v376ProgressKnob"></div></div><span class="v376ProgressNow">00:00</span><span class="v376ProgressEnd">00:15</span>';stage.appendChild(box)}
  const track=box.querySelector('.v376ProgressTrack'),fill=box.querySelector('.v376ProgressFill'),knob=box.querySelector('.v376ProgressKnob'),now=box.querySelector('.v376ProgressNow'),end=box.querySelector('.v376ProgressEnd');
  const fmt=(v)=>{const s=Math.max(0,Math.round(Number(v)||0));return String(Math.floor(s/60)).padStart(2,'0')+':'+String(s%60).padStart(2,'0')};
  const sync=()=>{const d=Math.max(.01,Number(video.duration)||Number(root.dataset.sourceDuration)||15),c=Math.max(0,Math.min(d,Number(video.currentTime)||0)),p=Math.max(0,Math.min(100,c/d*100));fill.style.width=p+'%';knob.style.left=p+'%';now.textContent=fmt(c);end.textContent=fmt(d)};
  track.addEventListener('click',(ev)=>{const r=track.getBoundingClientRect();if(!r.width)return;const p=Math.max(0,Math.min(1,(ev.clientX-r.left)/r.width)),d=Math.max(.01,Number(video.duration)||15);video.currentTime=p*d;sync()});
  video.addEventListener('timeupdate',sync,{passive:true});video.addEventListener('loadedmetadata',sync,{passive:true});sync();
})();
</script>
'''

SHELL_PATCH=r'''
<style id="v376EditorTitleCard">
@media(max-width:760px){
  #gsf-editor-overlay-v220{overflow:hidden!important}
  #gsf-editor-overlay-v220 .gsf-editor-head{
    display:flex!important;visibility:visible!important;opacity:1!important;position:relative!important;align-items:center!important;
    flex:0 0 auto!important;min-height:62px!important;height:62px!important;margin:5px 12px 6px!important;padding:9px 82px 9px 14px!important;
    border-radius:19px!important;background:rgba(255,255,255,.91)!important;border:1px solid rgba(174,204,225,.30)!important;
    box-shadow:0 7px 20px rgba(65,110,151,.08)!important;-webkit-backdrop-filter:blur(16px)!important;backdrop-filter:blur(16px)!important;
    color:#103A79!important;z-index:6!important;
  }
  #gsf-editor-overlay-v220 .gsf-editor-head>div{font-size:19px!important;line-height:1!important;font-weight:950!important;letter-spacing:-.02em!important}
  #gsf-editor-overlay-v220 .gsf-editor-head small{display:block!important;margin-top:5px!important;font-size:9.7px!important;line-height:1.1!important;font-weight:700!important;color:#6E81A5!important;letter-spacing:0!important}
  #gsf-editor-overlay-v220 .v326HeaderFull{
    display:flex!important;visibility:visible!important;opacity:1!important;align-items:center!important;justify-content:center!important;
    right:9px!important;top:11px!important;min-width:67px!important;width:67px!important;height:40px!important;border-radius:14px!important;padding:0 9px!important;
    font-size:9px!important;background:rgba(255,255,255,.95)!important;color:#2A4D86!important;border:1px solid rgba(156,190,218,.30)!important;
    box-shadow:0 6px 16px rgba(64,104,143,.09)!important;
  }
  #gsf-editor-overlay-v220 iframe.gsf-editor-frame,#gsf-editor-overlay-v220 iframe[title="Game Editor"]{
    width:100%!important;min-height:0!important;border:0!important;background:transparent!important;
  }
}
</style>
'''

def patch_editor(text:str)->str:
    if MARK in text:return text
    for anchor in ('V360_MOBILE_EDITOR_REFERENCE','id="v326MobileEditorExact"','id="v323EditorActions"'):
        if anchor not in text: raise RuntimeError('V376 editor baseline missing: '+anchor)
    if '</body>' not in text: raise RuntimeError('V376 editor body anchor missing')
    return text.replace('</body>',EDITOR_PATCH+'\n</body>',1)

def patch_shell(text:str)->str:
    if 'id="v376EditorTitleCard"' in text:return text
    if 'v326HeaderFull' not in text: raise RuntimeError('V376 parent Editor FULL baseline missing')
    marker='<style id="gsf-v220-editor-shell">'
    if marker not in text: raise RuntimeError('V376 parent Editor shell style anchor missing')
    out=text.replace(marker,SHELL_PATCH+'\n'+marker,1)
    compile(out,'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py','exec')
    return out

def main()->None:
    root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
    editor=root/'web'/'editor_2027_component'/'index.html'
    shell=root/'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py'
    if not editor.is_file() or not shell.is_file(): raise SystemExit('V376 runtime files missing')
    eb=editor.read_text(encoding='utf-8'); ea=patch_editor(eb); editor.write_text(ea,encoding='utf-8')
    sb=shell.read_text(encoding='utf-8'); sa=patch_shell(sb); shell.write_text(sa,encoding='utf-8')
    print('V376 mobile Editor reference applied editor_changed=',eb!=ea,'shell_changed=',sb!=sa,flush=True)

if __name__=='__main__': main()
