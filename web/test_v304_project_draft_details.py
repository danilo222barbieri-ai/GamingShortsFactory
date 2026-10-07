#!/usr/bin/env python3
from pathlib import Path
import py_compile
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '/app')
hub = (root/'web/creator_hub_v156_component/index.html').read_text(encoding='utf-8')
server_path = root/'web/direct_upload_server.py'
server = server_path.read_text(encoding='utf-8')
app = (root/'GamingShortsFactory_V154_STRUCTURAL_HOME.py').read_text(encoding='utf-8')

checks = {
    'hub_v304_marker': 'V304 PROJECT + DRAFT DETAILS' in hub,
    'detail_runtime': 'v304ProjectDraftRuntime' in hub and 'v304ItemDetail' in hub,
    'outer_schema_preserved': 'projectBox' in hub and 'Progetto corrente' in hub and 'draftRows' in hub,
    'detail_actions': all(x in hub for x in ['Salva nome','Salva bozza','Elimina','Apri nell’Editor']),
    'hub_hooks': 'window.GSFHubV304={openView,loadState,resumeDraft,shell}' in hub,
    'draft_api': all(x in server for x in ['/creator-hub/draft/rename','/creator-hub/draft/delete','def _draft_rename']),
    'project_api': all(x in server for x in ['/creator-hub/project/rename','/creator-hub/project/save-draft','/creator-hub/project/delete','def _current_project_rename']),
    'project_title_state': 'active_project_title' in server and '"title":str(pdata.get("title")' in server,
    'mobile_v303_kept': 'V303 MOBILE HUB COMPACT' in hub,
    'cache_v304': '/creator-hub-v156/?v=304' in app,
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit('V304 FAIL: ' + ', '.join(failed))
py_compile.compile(str(server_path), doraise=True)
print('V304 project/draft detail contract: PASS')
