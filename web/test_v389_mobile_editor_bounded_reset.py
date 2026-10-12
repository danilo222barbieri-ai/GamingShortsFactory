#!/usr/bin/env python3
from pathlib import Path
import sys

root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
e=(root/'web'/'editor_2027_component'/'index.html').read_text(encoding='utf-8')
s=(root/'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py').read_text(encoding='utf-8')
p=(root/'web'/'fix_v373_creator_hub_spacing.py').read_text(encoding='utf-8')
legacy=[
 'V380_MOBILE_EDITOR_UNIFIED','V381_MOBILE_EDITOR_COMPACT_FULL','V382_MOBILE_EDITOR_TRUE_FULL',
 'V383_MOBILE_EDITOR_POSITION','V384_MOBILE_EDITOR_NO_SCROLL','V385_MOBILE_EDITOR_LOWER',
 'V386_MOBILE_EDITOR_REFERENCE_LOCK','V387_MOBILE_EDITOR_PLAYER_VISIBILITY',
 'V387_MOBILE_EDITOR_DEMO_LOCK','V388_MOBILE_EDITOR_REFERENCE_FINAL'
]
app_tail=p[p.find("app=Path('/app')"):]
checks={
 'marker':'V389_MOBILE_EDITOR_BOUNDED_RESET' in e,
 'legacy geometry removed':all(x not in e for x in legacy),
 'explicit 9x16 size':'--v389-player-w:min(70vw,272px,calc((100dvh - 112px) * 9 / 16))' in e and '--v389-player-h:calc(var(--v389-player-w) * 16 / 9)' in e,
 'no external timeline cta':'V389_NO_EXTERNAL_TIMELINE_CTA' in e and '.cockpit>.timeline' in e and '.cockpit>.v323EditorActions' in e,
 'required tools':'V389_REQUIRED_EDITOR_CONTROLS' in e and all(x in e for x in ['data-panel="frame"','data-panel="caption"','data-panel="look"','data-panel="audio"','data-panel="vision"']),
 'undo redo':'v389UndoRedo' in e and "#undoBtn" in e and "#redoBtn" in e,
 'in out':'v389InBtn' in e and 'v389OutBtn' in e and "#inRange" in e and "#outRange" in e,
 'play pause':'#playBtn' in e and 'v389PlaybackDock' in e,
 'progress':'v389PlayerProgress' in e and 'v389ProgressFill' in e,
 'full':'V389_FULLSCREEN_WORKSPACE' in e and 'object-fit:cover!important' in e,
 'full parent clean':'V389_FULLSCREEN_PARENT_CLEAN' in e and '#gsf-game-bar' in e and '.gsf-editor-head' in e,
 'single first paint':'layout();requestAnimationFrame(layout);setTimeout(layout,80);' not in e,
 'mobile resize guard':'V389_MOBILE_RESIZE_GUARD' in e,
 'parent editor only':'v389EditorParentBounded' in s and '#gsf-editor-overlay-v220' in s,
 'pipeline only new reset':"fix_v389_mobile_editor_bounded_reset.py" in app_tail and all(('fix_v38'+str(i)) not in app_tail for i in range(0,9)),
}
failed=[k for k,v in checks.items() if not v]
if failed:raise AssertionError('V389 bounded reset contract failed: '+'; '.join(failed))
print('V389 MOBILE EDITOR BOUNDED RESET CONTRACT: PASS',flush=True)
