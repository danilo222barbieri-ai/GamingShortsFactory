#!/usr/bin/env python3
from pathlib import Path
import re,sys
MARK='V383_MOBILE_EDITOR_POSITION'
PATCH=r'''
<!-- V383_MOBILE_EDITOR_POSITION -->
<style id="v383MobileEditorPosition">
@media(max-width:760px){
/* One mobile composition: player -> timeline -> actions. No inherited tall floor. */
#ng27.v326Mobile{--v383-player-w:min(84vw,344px)!important;padding:8px 12px 96px!important;min-height:0!important;height:auto!important;overflow-x:hidden!important;overflow-y:auto!important}
#ng27.v326Mobile .shell{width:100%!important;max-width:430px!important;height:auto!important;min-height:0!important;margin:0 auto!important;padding:0!important}
#ng27.v326Mobile .cockpit,#ng27.v326Mobile.expanded .cockpit{display:grid!important;grid-template-columns:1fr!important;grid-template-rows:auto auto auto!important;gap:10px!important;width:100%!important;max-width:430px!important;height:auto!important;min-height:0!important;margin:0 auto!important;padding:0!important;align-items:start!important}
#ng27.v326Mobile .stageWrap{grid-row:1!important;width:var(--v383-player-w)!important;max-width:344px!important;height:auto!important;min-height:0!important;justify-self:center!important;margin:0!important}
#ng27.v326Mobile .stage.r916,#ng27.v326Mobile.expanded .stage.r916{width:100%!important;height:auto!important;aspect-ratio:9/16!important;max-height:none!important;border-radius:24px!important;margin:0!important}
#ng27.v326Mobile .cockpit>.timeline{grid-row:2!important;width:var(--v383-player-w)!important;max-width:344px!important;height:108px!important;min-height:108px!important;justify-self:center!important;margin:0!important}
#ng27.v326Mobile .cockpit>.v323EditorActions{grid-row:3!important;width:var(--v383-player-w)!important;max-width:344px!important;height:46px!important;min-height:46px!important;justify-self:center!important;margin:0!important;gap:8px!important}
#ng27.v326Mobile .v323EditorAction{height:46px!important;min-height:46px!important;font-size:8px!important;padding:4px 7px!important;border-radius:15px!important}
#ng27.v326Mobile .v326ToolDock .railBtn{width:46px!important;height:54px!important;min-width:46px!important;min-height:54px!important;border-radius:15px!important}
#ng27.v326Mobile .v326ToolDock .railBtn .ico{width:19px!important;height:19px!important}
#ng27.v326Mobile .v326ToolDock .railBtn span{font-size:6.2px!important}
#ng27.v326Mobile .v326LeftDock{left:8px!important;top:25%!important}
#ng27.v326Mobile .v326RightDock{right:8px!important;top:34%!important}
/* iOS fallback is a real full-screen state too. */
#ng27.v326Mobile.gsfFullscreenFallback,#ng27.v326Mobile.gsfFullscreenFallback .shell,#ng27.v326Mobile.gsfFullscreenFallback .cockpit,#ng27.v326Mobile.gsfFullscreenFallback .stageWrap,#ng27.v326Mobile.gsfFullscreenFallback .stage.r916{position:fixed!important;inset:0!important;width:100vw!important;height:100dvh!important;min-width:100vw!important;min-height:100dvh!important;max-width:none!important;max-height:none!important;margin:0!important;padding:0!important;border:0!important;border-radius:0!important;background:#08131c!important;z-index:2147483647!important}
#ng27.v326Mobile.gsfFullscreenFallback .stage.r916 video{width:100vw!important;height:100dvh!important;object-fit:cover!important}
#ng27.v326Mobile.gsfFullscreenFallback .timeline,#ng27.v326Mobile.gsfFullscreenFallback .v323EditorActions{display:none!important}
#ng27.v326Mobile.gsfFullscreenFallback .v326ToolDock{position:fixed!important;top:50%!important;transform:translateY(-50%)!important;z-index:2147483647!important}
#ng27.v326Mobile.gsfFullscreenFallback .v326LeftDock{left:max(8px,env(safe-area-inset-left))!important}
#ng27.v326Mobile.gsfFullscreenFallback .v326RightDock{right:max(8px,env(safe-area-inset-right))!important}
#ng27.v326Mobile.gsfFullscreenFallback .v326PlaybackDock{position:fixed!important;bottom:max(18px,env(safe-area-inset-bottom))!important;z-index:2147483647!important}
#ng27.v326Mobile.gsfFullscreenFallback .v380PlayerProgress{position:fixed!important;left:72px!important;right:72px!important;bottom:max(8px,env(safe-area-inset-bottom))!important;z-index:2147483647!important}
}
</style>
'''
def strip(t):return re.sub(r'\s*<!-- V383_MOBILE_EDITOR_POSITION -->.*?</style>\s*','\n',t,flags=re.S)
def main():
 root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app');p=root/'web'/'editor_2027_component'/'index.html';t=strip(p.read_text(encoding='utf-8'))
 if 'V382_MOBILE_EDITOR_TRUE_FULL' not in t:raise RuntimeError('V383 requires V382')
 p.write_text(t.replace('</body>',PATCH+'\n</body>',1),encoding='utf-8');print('V383 mobile Editor position applied',flush=True)
if __name__=='__main__':main()
