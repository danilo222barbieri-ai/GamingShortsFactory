#!/usr/bin/env python3
from pathlib import Path
import py_compile
import sys

root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path('/app')
hub = root/'web'/'creator_hub_v156_component'/'index.html'
server = root/'web'/'direct_upload_server.py'
assert hub.is_file(), 'V366 Hub target missing'
assert server.is_file(), 'V366 server target missing'

h = hub.read_text(encoding='utf-8')
s = server.read_text(encoding='utf-8')

required_hub = (
    'V366_CREATOR_HUB_STATE_STABILITY',
    'stateLoadPromise',
    'reportHubError("render",renderError)',
    '.socialCard[data-platform],.profileSocialRefRow[data-platform]',
    'if(!st||!btn)return',
    'Profilo non disponibile · Riprova',
    'profileOverviewPlan',
    'profileOverviewSocial',
)
for token in required_hub:
    assert token in h, 'V366 Hub contract missing: ' + token

assert '$$("[data-platform]").forEach(card=>{' not in h, 'V366 broad social selector still active'
assert h.count('let stateLoadPromise=null;') == 1, 'V366 single-flight loader must be unique'

required_server = (
    '# V366_CREATOR_HUB_STATE_STABILITY',
    'if clean=="/creator-hub/avatar":',
    'if path=="/creator-hub/client-error":',
    'youtube_state=_youtube_user_load(sid)',
    'tiktok_state=_tiktok_user_load(sid)',
    'instagram_state=_instagram_user_load(sid)',
    'bool(youtube_state)',
    'bool(tiktok_state)',
    'bool(instagram_state)',
    'GSF_HUB_CLIENT_ERROR',
    '"/creator-hub/avatar" if str(profile.get("avatar") or "").startswith("data:image/")',
)
for token in required_server:
    assert token in s, 'V366 server contract missing: ' + token

# The state route must not reload the same three social providers twice.
state_block = s.split('if clean=="/creator-hub/state":',1)[1].split('if clean=="/account":',1)[0]
assert state_block.count('_youtube_user_load(sid)') == 1
assert state_block.count('_tiktok_user_load(sid)') == 1
assert state_block.count('_instagram_user_load(sid)') == 1

py_compile.compile(str(server), doraise=True)
print('V366 CREATOR HUB PROFILE STATE STABILITY: PASS', flush=True)
