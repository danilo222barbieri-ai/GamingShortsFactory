#!/usr/bin/env python3
from pathlib import Path

root=Path('/app')
hub=(root/'web/creator_hub_v156_component/index.html').read_text(encoding='utf-8')
server=(root/'web/direct_upload_server.py').read_text(encoding='utf-8')
app=(root/'GamingShortsFactory_V154_STRUCTURAL_HOME.py').read_text(encoding='utf-8')
checks={
 'hub_marker':'V304 PROJECT FOLDER DETAILS' in hub,
 'detail_overlay':'projectDetailOverlay' in hub,
 'draft_open':'data-open-draft' in hub,
 'current_open':'data-open-current' in hub,
 'rename_route':'/drafts/rename' in server and '/creator-hub/project/rename' in server,
 'delete_route':'/drafts/delete-json' in server and '/creator-hub/project/delete' in server,
 'save_route':'/creator-hub/project/save-draft' in server,
 'current_title':'gsf_project_title' in server,
 'cache':'/creator-hub-v156/?v=304' in app,
}
failed=[k for k,v in checks.items() if not v]
if failed:raise SystemExit('V304 FAIL: '+', '.join(failed))
print('V304 project folder details: PASS')
