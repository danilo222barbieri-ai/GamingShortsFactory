#!/usr/bin/env python3
from pathlib import Path
import re,sys
MARK='V381_MOBILE_EDITOR_COMPACT_FULL'
PATCH=r'''
<!-- V381_MOBILE_EDITOR_COMPACT_FULL -->
<style id="v381MobileEditorCompactFull">
@media(max-width:760px){
#ng27.v326Mobile{--v381-player-w:min(46vw,188px);padding:4px 10px 78px!important}
#ng27.v326Mobile .cockpit,#ng27.v326Mobile.expanded .cockpit{max-width:420px!important;grid-template-rows:auto 92px 34px!important;gap:6px!important}
#ng27.v326Mobile .stageWrap{width:var(--v381-player-w)!important}
#ng27.v326Mobile .stage.r916,#ng27.v326Mobile.expanded .stage.r916{border-radius:18px!important}
/* V381_TOOLS_IN_VIDEO / V381_FRAME_IN_VIDEO */
#ng27.v326Mobile .v326ToolDock{gap:4px!important}
#ng27.v326Mobile .v326LeftDock{left:5px!important;top:25%!important}
#ng27.v326Mobile .v326RightDock{right:5px!important;top:34%!important}
#ng27.v326Mobile .v326ToolDock .railBtn{width:34px!important;height:39px!important;min-width:34px!important;min-height:39px!important;border-radius:11px!important;padding:2px!important}
#ng27.v326Mobile .v326ToolDock .railBtn .ico{width:14px!important;height:14px!important}
#ng27.v326Mobile .v326ToolDock .railBtn span{font-size:4.8px!important;letter-spacing:.02em!important}
#ng27.v326Mobile .v326Time,#ng27.v326Mobile .v326Ratio{height:24px!important;padding:0 6px!important;font-size:6.4px!important;border-radius:9px!important}
#ng27.v326Mobile .v326Ratio{margin-right:29px!important}
#ng27.v326Mobile #zoomEditorBtn{width:27px!important;min-width:27px!important;height:27px!important;top:5px!important;right:5px!important;border-radius:9px!important}
#ng27.v326Mobile #zoomEditorBtn .ico{width:14px!important;height:14px!important}
#ng27.v326Mobile .v326PlaybackDock{bottom:25px!important;gap:5px!important}
#ng27.v326Mobile #playBtn{width:39px!important;height:39px!important;min-width:39px!important;min-height:39px!important}
#ng27.v326Mobile #playBtn .ico{width:19px!important;height:19px!important}
#ng27.v326Mobile .v326Skip{width:18px!important;height:22px!important;font-size:15px!important}
#ng27.v326Mobile .v380PlayerProgress{left:8px!important;right:8px!important;bottom:5px!important;font-size:5.2px!important}
/* V381_TINY_ACTIONS */
#ng27.v326Mobile .cockpit>.v323EditorActions{grid-row:3!important;height:34px!important;max-width:330px!important;justify-self:center!important;gap:6px!important}
#ng27.v326Mobile .v323EditorAction{height:34px!important;min-height:34px!important;border-radius:12px!important;padding:2px 6px!important;font-size:6.8px!important;box-shadow:0 3px 8px rgba(64,108,150,.06)!important}
#ng27.v326Mobile .cockpit>.timeline{grid-row:2!important;height:92px!important;min-height:92px!important;padding:6px 8px!important;border-radius:14px!important}
#ng27.v326Mobile .timeline .tlMeta{margin-bottom:4px!important;font-size:6px!important}
#ng27.v326Mobile .timeline .tlMeta span:nth-child(2){min-height:19px!important;padding:0 7px!important}
#ng27.v326Mobile .timeline .track{height:34px!important}
#ng27.v326Mobile .timeline .trimRow{margin-top:3px!important;font-size:5.7px!important}
/* V381_FULLSCREEN_SIDE_CONTROLS */
#ng27.v326Mobile.gsfFullscreen,#ng27.v326Mobile:fullscreen,#ng27.v326Mobile:-webkit-full-screen{--v381-player-w:min(100vw,calc(100dvh * 9 / 16));padding:0!important;background:#08131c!important;overflow:hidden!important}
#ng27.v326Mobile.gsfFullscreen .shell,#ng27.v326Mobile:fullscreen .shell,#ng27.v326Mobile:-webkit-full-screen .shell{width:100vw!important;height:100dvh!important;max-width:none!important;display:block!important}
#ng27.v326Mobile.gsfFullscreen .cockpit,#ng27.v326Mobile:fullscreen .cockpit,#ng27.v326Mobile:-webkit-full-screen .cockpit{display:block!important;width:100vw!important;height:100dvh!important;max-width:none!important}
#ng27.v326Mobile.gsfFullscreen .stageWrap,#ng27.v326Mobile:fullscreen .stageWrap,#ng27.v326Mobile:-webkit-full-screen .stageWrap{position:absolute!important;inset:0!important;width:100vw!important;height:100dvh!important;display:flex!important;align-items:center!important;justify-content:center!important}
#ng27.v326Mobile.gsfFullscreen .stage.r916,#ng27.v326Mobile:fullscreen .stage.r916,#ng27.v326Mobile:-webkit-full-screen .stage.r916{width:min(100vw,calc(100dvh * 9 / 16))!important;height:min(100dvh,calc(100vw * 16 / 9))!important;max-height:100dvh!important;border-radius:0!important}
#ng27.v326Mobile.gsfFullscreen .v326ToolDock,#ng27.v326Mobile:fullscreen .v326ToolDock,#ng27.v326Mobile:-webkit-full-screen .v326ToolDock{position:fixed!important;top:50%!important;transform:translateY(-50%)!important;gap:8px!important}
#ng27.v326Mobile.gsfFullscreen .v326LeftDock,#ng27.v326Mobile:fullscreen .v326LeftDock,#ng27.v326Mobile:-webkit-full-screen .v326LeftDock{left:max(8px,env(safe-area-inset-left))!important}
#ng27.v326Mobile.gsfFullscreen .v326RightDock,#ng27.v326Mobile:fullscreen .v326RightDock,#ng27.v326Mobile:-webkit-full-screen .v326RightDock{right:max(8px,env(safe-area-inset-right))!important}
#ng27.v326Mobile.gsfFullscreen .v326ToolDock .railBtn,#ng27.v326Mobile:fullscreen .v326ToolDock .railBtn,#ng27.v326Mobile:-webkit-full-screen .v326ToolDock .railBtn{width:46px!important;height:52px!important;min-width:46px!important;min-height:52px!important;border-radius:15px!important}
#ng27.v326Mobile.gsfFullscreen .v326ToolDock .railBtn .ico,#ng27.v326Mobile:fullscreen .v326ToolDock .railBtn .ico,#ng27.v326Mobile:-webkit-full-screen .v326ToolDock .railBtn .ico{width:20px!important;height:20px!important}
#ng27.v326Mobile.gsfFullscreen .v326ToolDock .railBtn span,#ng27.v326Mobile:fullscreen .v326ToolDock .railBtn span,#ng27.v326Mobile:-webkit-full-screen .v326ToolDock .railBtn span{font-size:6.4px!important}
/* V381_FULLSCREEN_CLEAN */
#ng27.v326Mobile.gsfFullscreen .timeline,#ng27.v326Mobile:fullscreen .timeline,#ng27.v326Mobile:-webkit-full-screen .timeline,#ng27.v326Mobile.gsfFullscreen .v323EditorActions,#ng27.v326Mobile:fullscreen .v323EditorActions,#ng27.v326Mobile:-webkit-full-screen .v323EditorActions{display:none!important}
#ng27.v326Mobile.gsfFullscreen .v326PlaybackDock,#ng27.v326Mobile:fullscreen .v326PlaybackDock,#ng27.v326Mobile:-webkit-full-screen .v326PlaybackDock{position:fixed!important;bottom:max(18px,env(safe-area-inset-bottom))!important}
#ng27.v326Mobile.gsfFullscreen .v380PlayerProgress,#ng27.v326Mobile:fullscreen .v380PlayerProgress,#ng27.v326Mobile:-webkit-full-screen .v380PlayerProgress{position:fixed!important;left:72px!important;right:72px!important;bottom:max(8px,env(safe-area-inset-bottom))!important}
}
</style>
'''
def strip(t):return re.sub(r'\s*<!-- V381_MOBILE_EDITOR_COMPACT_FULL -->.*?</style>\s*','\n',t,flags=re.S)
def main():
 root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app');p=root/'web'/'editor_2027_component'/'index.html';t=strip(p.read_text(encoding='utf-8'))
 if 'V380_MOBILE_EDITOR_UNIFIED' not in t:raise RuntimeError('V381 requires V380')
 p.write_text(t.replace('</body>',PATCH+'\n</body>',1),encoding='utf-8');print('V381 compact/full mobile Editor applied',flush=True)
if __name__=='__main__':main()
