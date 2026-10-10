#!/usr/bin/env python3
from pathlib import Path
import py_compile
import sys

root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path('/app')
hub = root/'web'/'creator_hub_v156_component'/'index.html'
server = root/'web'/'direct_upload_server.py'
source_shell = root/'GamingShortsFactory_V154_STRUCTURAL_HOME.py'
runtime_shell = root/'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py'
assert hub.is_file(), 'V366 Hub target missing'
assert server.is_file(), 'V366 server target missing'
assert source_shell.is_file(), 'V366 source shell missing'
assert runtime_shell.is_file(), 'V366 runtime shell missing'

h = hub.read_text(encoding='utf-8')
s = server.read_text(encoding='utf-8')
src = source_shell.read_text(encoding='utf-8')
run = runtime_shell.read_text(encoding='utf-8')

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

cache_target = '/creator-hub-v156/?v=3662&ui=profile-ref-2'
assert cache_target in src, 'V366 source shell cache key not bumped'
assert cache_target in run, 'V366 runtime shell cache key not bumped'
assert '/creator-hub-v156/?v=3115&ui=profile-ref-2' not in run, 'stale V3115 Hub cache key remains in live runtime'

py_compile.compile(str(server), doraise=True)
py_compile.compile(str(source_shell), doraise=True)
py_compile.compile(str(runtime_shell), doraise=True)
print('V366 CREATOR HUB PROFILE STATE STABILITY + CACHE BUST: PASS', flush=True)
