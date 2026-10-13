#!/usr/bin/env python3
from pathlib import Path
import sys

root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
e=(root/'web'/'editor_2027_component'/'index.html').read_text(encoding='utf-8')
s=(root/'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py').read_text(encoding='utf-8')
p=(root/'web'/'fix_v392_mobile_editor_premium_skin.py').read_text(encoding='utf-8')
chain=(root/'web'/'fix_v373_creator_hub_spacing.py').read_text(encoding='utf-8')
checks={
 'V392 marker':'V392_MOBILE_EDITOR_PREMIUM_SKIN' in e,
 'mobile-only skin':'@media(max-width:760px)' in e and 'v392MobileEditorPremiumSkin' in e,
 'player geometry untouched':'--v389-player-w:' not in p and '--v389-player-h:' not in p,
 'top controls glass':'#ng27 .v389UndoRedo #undoBtn' in e and 'blur(12px)' in e,
 'side controls glass':'#ng27 .v389ToolDock .railBtn' in e and 'rgba(255,255,255,.92)' in e,
 'active control remains clear':'#ng27 .v389ToolDock .railBtn.active' in e,
 'timeline visually lightened':'#ng27 .timeline' in e and 'remove the heavy grey slab' in e,
 'play remains primary':'#ng27 .v389PlaybackDock #playBtn' in e and '#70d4f3' in e,
 'project actions preserved':'SALVA BOZZA' in e and 'CREA SHORT' in e and 'v391EditorActions' in e,
 'full still hides project actions':'gsfFullscreen .v391EditorActions' in e,
 'X removal scoped to Editor overlay':'#gsf-editor-overlay-v220 .v392EditorCloseGone' in s and 'v392EditorCloseCleanup' in s,
 'X removal is semantic':'aria-label' in s and "includes('close')" in s and "includes('chiudi')" in s,
 'global gamebar geometry untouched':'.gsf-game-bar' not in p and '#gsf-game-bar' not in p,
 'home hub untouched':'home_v154_component' not in p and 'creator_hub_v156_component' not in p,
 'no resize owner added':"addEventListener('resize'" not in p and 'addEventListener("resize"' not in p,
 'no repeated first paint':'requestAnimationFrame(layout)' not in p and 'setTimeout(layout' not in p,
 'external timeline CTA remain hidden':'V389_NO_EXTERNAL_TIMELINE_CTA' in e,
 'pipeline V392 after V391':chain.find("fix_v391_mobile_editor_top_actions.py") < chain.find("fix_v392_mobile_editor_premium_skin.py"),
}
failed=[k for k,v in checks.items() if not v]
if failed:raise AssertionError('V392 mobile Editor premium skin contract failed: '+'; '.join(failed))
compile(s,str(root/'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py'),'exec')
print('V392 MOBILE EDITOR PREMIUM SKIN CONTRACT: PASS',flush=True)
