#!/usr/bin/env python3
from pathlib import Path
import sys

root=Path(sys.argv[1]) if len(sys.argv)>1 else Path('/app')
hub=(root/'web/creator_hub_v156_component/index.html').read_text(encoding='utf-8')
server=(root/'web/direct_upload_server.py').read_text(encoding='utf-8')
app=(root/'GamingShortsFactory_V154_STRUCTURAL_HOME.py').read_text(encoding='utf-8')

checks={
 'hub marker':'/* V304 PROJECT FOLDER DETAILS */' in hub,
 'detail view':'data-view="projectDetail"' in hub,
 'draft opens as folder':'data-draft-open=' in hub,
 'current opens as folder':'data-current-open=' in hub,
 'rename draft endpoint':'/drafts/rename' in server and 'def _draft_rename' in server,
 'delete draft json endpoint':'/drafts/delete-json' in server,
 'current rename endpoint':'/projects/current/rename' in server,
 'current save draft endpoint':'/projects/current/save-draft' in server,
 'current delete endpoint':'/projects/current/delete' in server,
 'project title in state':'"title":str(pdata.get("title") or "Progetto corrente")' in server,
 'hub cache v304':'/creator-hub-v156/?v=304' in app,
}
failed=[name for name,ok in checks.items() if not ok]
if failed:
    raise SystemExit('V304 FAIL: '+', '.join(failed))
print('V304 project folder details: PASS')
