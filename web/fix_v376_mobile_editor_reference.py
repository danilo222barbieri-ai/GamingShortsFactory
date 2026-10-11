#!/usr/bin/env python3
from pathlib import Path
import sys

MARK='V376_MOBILE_EDITOR_REFERENCE'

EDITOR_PATCH=r'''
<!-- V376_MOBILE_EDITOR_REFERENCE -->
<style id="v376MobileEditorReference">
@media(max-width:760px){
  html,body{background:transparent!important}
  #ng27.v326Mobile{
    --v376-player-w:min(82vw,430px);
    height:auto!important;min-height:100%!important;max-height:none!important;
    padding:14px 12px 118px!important;overflow-y:auto!important;overflow-x:hidden!important;
    -webkit-overflow-scrolling:touch!important;
    background:radial-gradient(circle at 50% 6%,rgba(197,235,252,.98),transparent 33%),radial-gradient(circle at 12% 48%,rgba(218,246,255,.74),transparent 34%),linear-gradient(180deg,#F9FDFF 0%,#EEF8FD 100%)!important;
  }
  #ng27.v326Mobile .shell{height:auto!important;min-height:0!important;max-width:520px!important;overflow:visible!important}
  #ng27.v326Mobile .cockpit,#ng27.v326Mobile.expanded .cockpit{width:100%!important;max-width:500px!important;height:auto!important;min-height:0!important;grid-template-rows:auto auto auto!important;gap:14px!important;overflow:visible!important}
  #ng27.v326Mobile .stageWrap{width:var(--v376-player-w)!important;max-width:calc(100% - 18px)!important;margin:0 auto!important;align-self:start!important}
  #ng27.v326Mobile .stage.r916,#ng27.v326Mobile.expanded .stage.r916{width:100%!important;aspect-ratio:9/16!important;border-radius:28px!important;border:1px solid rgba(113,199,239,.58)!important;box-shadow:0 18px 42px rgba(49,103,145,.18),0 0 0 7px rgba(255,255,255,.56)!important;background:linear-gradient(180deg,#DDF4FE,#F5FBFF)!important}
  #ng27.v326Mobile .v326Meta{top:14px!important;left:14px!important;right:14px!important}
  #ng27.v326Mobile .v326Time,#ng27.v326Mobile .v326Ratio{height:36px!important;padding:0 12px!important;border-radius:15px!important;font-size:10.8px!important;background:rgba(29,55,84,.72)!important;box-shadow:0 7px 18px rgba(7,22,38,.18)!important}
  #ng27.v326Mobile .v326Ratio{margin-right:52px!important}
  #ng27.v326Mobile #zoomEditorBtn{top:13px!important;right:13px!important;width:46px!important;height:46px!important;min-width:46px!important;min-height:46px!important;border-radius:15px!important;background:rgba(29,55,84,.72)!important;box-shadow:0 7px 18px rgba(7,22,38,.18)!important}
  #ng27.v326Mobile #zoomEditorBtn .ico{width:21px!important;height:21px!important}
  #ng27.v326Mobile .v326ToolDock{gap:10px!important}
  #ng27.v326Mobile .v326LeftDock{left:11px!important}
  #ng27.v326Mobile .v326RightDock{right:11px!important}
  #ng27.v326Mobile .v326ToolDock .railBtn{width:58px!important;height:68px!important;min-width:58px!important;min-height:68px!important;border-radius:20px!important;background:linear-gradient(145deg,rgba(28,53,80,.73),rgba(56,82,109,.59))!important;border:1px solid rgba(255,255,255,.74)!important;box-shadow:0 9px 24px rgba(11,28,44,.23),inset 0 1px 0 rgba(255,255,255,.29)!important}
  #ng27.v326Mobile .v326ToolDock .railBtn .ico{width:25px!important;height:25px!important}
  #ng27.v326Mobile .v326ToolDock .railBtn span{font-size:8.7px!important;letter-spacing:.04em!important}
  #ng27.v326Mobile .v326PlaybackDock{bottom:68px!important;gap:16px!important}
  #ng27.v326Mobile #playBtn{width:66px!important;height:66px!important;min-width:66px!important;min-height:66px!important;box-shadow:0 10px 27px rgba(17,50,94,.36),inset 0 1px 0 rgba(255,255,255,.44)!important}
  #ng27.v326Mobile #playBtn .ico{width:30px!important;height:30px!important}
  #ng27.v326Mobile .v326Skip{width:34px!important;height:42px!important;font-size:28px!important}
  #ng27.v326Mobile .v376PlayerProgress{position:absolute!important;left:24px!important;right:24px!important;bottom:20px!important;z-index:99!important;color:#fff!important;display:grid!important;grid-template-columns:auto 1fr auto!important;grid-template-rows:auto auto!important;gap:4px 10px!important;align-items:center!important;pointer-events:auto!important;font-size:8.8px!important;font-weight:900!important;text-shadow:0 2px 7px rgba(0,0,0,.42)!important}
  #ng27.v326Mobile .v376ProgressTrack{grid-column:1/4;grid-row:1;height:7px!important;border-radius:999px!important;background:rgba(255,255,255,.42)!important;overflow:visible!important;position:relative!important;box-shadow:inset 0 1px 3px rgba(0,0,0,.18)!important}
  #ng27.v326Mobile .v376ProgressFill{position:absolute!important;left:0!important;top:0!important;bottom:0!important;width:0;border-radius:999px!important;background:linear-gradient(90deg,#56C8FF,#2D8BFF)!important}
  #ng27.v326Mobile .v376ProgressKnob{position:absolute!important;top:50%!important;left:0;width:15px!important;height:15px!important;border-radius:50%!important;background:#fff!important;transform:translate(-50%,-50%)!important;box-shadow:0 2px 8px rgba(20,52,85,.32)!important}
  #ng27.v326Mobile .v376ProgressNow{grid-column:1;grid-row:2}
  #ng27.v326Mobile .v376ProgressEnd{grid-column:3;grid-row:2;text-align:right}
  #ng27.v326Mobile .cockpit>.v323EditorActions{max-width:500px!important;gap:12px!important}
  #ng27.v326Mobile .cockpit>.v323EditorActions .v323EditorAction{min-height:58px!important;border-radius:22px!important;font-size:11.5px!important;letter-spacing:.015em!important;box-shadow:0 10px 26px rgba(62,107,151,.11)!important}
  #ng27.v326Mobile .cockpit>.v323EditorActions .v323EditorAction.primary{background:linear-gradient(135deg,#58C1FB,#347FEA)!important;border-color:rgba(75,162,235,.42)!important}
  #ng27.v326Mobile .cockpit>.timeline{max-width:500px!important;padding:12px 13px 11px!important;border-radius:24px!important;background:rgba(255,255,255,.84)!important;box-shadow:0 10px 28px rgba(79,118,157,.10),inset 0 1px 0 rgba(255,255,255,.94)!important}
  #ng27.v326Mobile .cockpit>.timeline .tlMeta{margin:0 4px 9px!important;font-size:9.7px!important;font-weight:900!important}
  #ng27.v326Mobile .cockpit>.timeline .tlMeta span:nth-child(2){min-height:31px!important;padding:0 13px!important;border-radius:16px!important}
  #ng27.v326Mobile .cockpit>.timeline .tlMeta span:nth-child(2):after{font-size:9.2px!important}
  #ng27.v326Mobile .cockpit>.timeline .track{height:62px!important;border-radius:14px!important;border:2px solid rgba(69,174,228,.66)!important;position:relative!important;background:linear-gradient(180deg,rgba(105,198,243,.13),rgba(78,145,211,.08)),repeating-linear-gradient(90deg,rgba(110,181,225,.24) 0 48px,rgba(255,255,255,.68) 48px 51px)!important}
  #ng27.v326Mobile .cockpit>.timeline .track:after{content:"";position:absolute;left:10px;right:10px;bottom:-20px;height:18px;opacity:.52;pointer-events:none;background:repeating-linear-gradient(90deg,rgba(74,150,205,.72) 0 2px,transparent 2px 6px);-webkit-mask-image:linear-gradient(180deg,transparent 0,#000 25%,#000 75%,transparent 100%);mask-image:linear-gradient(180deg,transparent 0,#000 25%,#000 75%,transparent 100%)}
  #ng27.v326Mobile .cockpit>.timeline .trimRow{margin-top:27px!important;font-size:8.4px!important}
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
  #gsf-editor-overlay-v220 .gsf-editor-head{display:flex!important;position:relative!important;align-items:center!important;min-height:92px!important;margin:18px 16px 14px!important;padding:17px 104px 17px 20px!important;border-radius:24px!important;background:rgba(255,255,255,.90)!important;border:1px solid rgba(174,204,225,.30)!important;box-shadow:0 10px 28px rgba(65,110,151,.09)!important;-webkit-backdrop-filter:blur(18px)!important;backdrop-filter:blur(18px)!important;color:#103A79!important;z-index:6!important}
  #gsf-editor-overlay-v220 .gsf-editor-head>div{font-size:24px!important;line-height:1.02!important;font-weight:950!important;letter-spacing:-.02em!important}
  #gsf-editor-overlay-v220 .gsf-editor-head small{display:block!important;margin-top:8px!important;font-size:12px!important;line-height:1.18!important;font-weight:700!important;color:#6E81A5!important;letter-spacing:0!important}
  #gsf-editor-overlay-v220 .v326HeaderFull{display:flex!important;align-items:center!important;justify-content:center!important;right:14px!important;top:20px!important;min-width:84px!important;height:52px!important;border-radius:18px!important;padding:0 13px!important;font-size:11px!important;background:rgba(255,255,255,.94)!important;color:#2A4D86!important;border:1px solid rgba(156,190,218,.30)!important;box-shadow:0 8px 20px rgba(64,104,143,.10)!important}
  #gsf-editor-overlay-v220 iframe.gsf-editor-frame,#gsf-editor-overlay-v220 iframe[title="Game Editor"]{width:100%!important;border:0!important;background:transparent!important}
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
