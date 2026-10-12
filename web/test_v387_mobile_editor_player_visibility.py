#!/usr/bin/env python3
from pathlib import Path
import sys

root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
e=(root/'web'/'editor_2027_component'/'index.html').read_text(encoding='utf-8')
s=(root/'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py').read_text(encoding='utf-8')
p=(root/'web'/'fix_v373_creator_hub_spacing.py').read_text(encoding='utf-8')

checks={
    'marker':'V387_MOBILE_EDITOR_PLAYER_VISIBILITY' in e,
    'player row cannot collapse':'grid-template-rows:auto 46px 94px!important' in e,
    'player wrapper owns ratio':'V387_NONZERO_PLAYER_ROW' in e and 'aspect-ratio:9/16!important' in e,
    'explicit compact player width':'--v387-player-w:min(60vw,236px)' in e,
    'editor title lives in iframe':'v387EditorTitleCard' in e and 'Il tuo gameplay resta nel progetto mentre modifichi.' in e,
    'real full control bridged':"querySelector('#zoomEditorBtn')" in e and 'original.click()' in e,
    'parent duplicate title hidden':'V387_EDITOR_IFRAME_FILL' in s and '.gsf-editor-head{display:none!important}' in s,
    'iframe fills editor viewport':'flex:1 1 0!important' in s and 'height:100%!important' in s,
    'v387 shell override wins after base':s.find('V387_EDITOR_IFRAME_FILL') > s.find('gsf-v220-editor-shell') >= 0,
    'actions preserved':'v323EditorActions' in e,
    'timeline preserved':'cockpit>.timeline' in e,
    'mobile only':'@media(max-width:760px)' in e and '@media(max-width:760px)' in s,
    'pipeline':'fix_v387_mobile_editor_player_visibility.py' in p,
}
failed=[k for k,v in checks.items() if not v]
if failed:
    raise AssertionError('V387 contract failed: '+'; '.join(failed))
print('V387 MOBILE EDITOR PLAYER VISIBILITY CONTRACT: PASS',flush=True)
