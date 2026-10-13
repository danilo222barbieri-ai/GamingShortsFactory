#!/usr/bin/env python3
from pathlib import Path
import sys

root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
e=(root/'web'/'editor_2027_component'/'index.html').read_text(encoding='utf-8')
p=(root/'web'/'fix_v373_creator_hub_spacing.py').read_text(encoding='utf-8')
checks={
 'marker':'V391_MOBILE_EDITOR_TOP_ACTIONS' in e,
 'reader raised':'#ng27 .shell{align-items:center!important;justify-content:flex-start!important;padding-top:18px!important}' in e,
 'column composition':'flex-direction:column!important' in e and 'justify-content:flex-start!important' in e,
 'actions under player':"v391StageWrap.insertAdjacentElement('afterend',v391Actions)" in e,
 'actions same player width':'width:var(--v389-player-w)!important' in e,
 'save draft':'SALVA BOZZA' in e and "v391FinalAction('save_draft')" in e,
 'create short':'CREA SHORT' in e and "v391FinalAction('create_short')" in e,
 'real editor state':'commit();' in e and 'const payload=cloneState();' in e and 'sendStateToPython(payload);' in e and 'persistLocalState();' in e,
 'timeline stays hidden':'V389_NO_EXTERNAL_TIMELINE_CTA' in e and '.cockpit>.timeline' in e,
 'full hides project actions':'gsfFullscreen .v391EditorActions' in e and 'gsfFullscreenFallback .v391EditorActions' in e,
 'pipeline runs V391':"fix_v391_mobile_editor_top_actions.py" in p and "test_v391_mobile_editor_top_actions.py" in p,
}
failed=[k for k,v in checks.items() if not v]
if failed:raise AssertionError('V391 mobile Editor top/actions contract failed: '+'; '.join(failed))
print('V391 MOBILE EDITOR TOP + ACTIONS CONTRACT: PASS',flush=True)
