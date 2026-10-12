#!/usr/bin/env python3
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
e=(root/'web'/'editor_2027_component'/'index.html').read_text(encoding='utf-8')
s=(root/'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py').read_text(encoding='utf-8')
p=(root/'web'/'fix_v373_creator_hub_spacing.py').read_text(encoding='utf-8')
checks={
 'marker':'V386_MOBILE_EDITOR_REFERENCE_LOCK' in e,
 'single stable layout':'grid-template-rows:minmax(0,1fr) 46px 94px!important' in e,
 'player height driven':'calc((100dvh - 164px) * 9 / 16)' in e,
 'actions before timeline':'V386_ACTIONS_ROW_2' in e and 'V386_TIMELINE_ROW_3' in e,
 'tools inside player':'V386_TOOLS_INSIDE_PLAYER' in e,
 'no old geometry blocks':all(x not in e for x in ['V381_MOBILE_EDITOR_COMPACT_FULL','V382_MOBILE_EDITOR_TRUE_FULL','V383_MOBILE_EDITOR_POSITION','V384_MOBILE_EDITOR_NO_SCROLL','V385_MOBILE_EDITOR_LOWER']),
 'no repeated initial layout':'layout();requestAnimationFrame(layout);setTimeout(layout,80);' not in e,
 'parent title card':'V386_EDITOR_TITLE_CARD' in s and 'Il tuo gameplay resta nel progetto mentre modifichi.' in s,
 'duplicate final cta cleanup':'V386_HIDE_DUPLICATE_FINAL_CTA' in s and "t.length<80" in s,
 'old parent override removed':'v380EditorParentUnified' not in s,
 'fullscreen gamebar hidden':'V386_FULLSCREEN_PARENT_CLEAN' in e,
 'pipeline':'fix_v386_mobile_editor_reference_lock.py' in p,
}
failed=[k for k,v in checks.items() if not v]
if failed:raise AssertionError('V386 contract failed: '+'; '.join(failed))
print('V386 MOBILE EDITOR REFERENCE LOCK CONTRACT: PASS',flush=True)
