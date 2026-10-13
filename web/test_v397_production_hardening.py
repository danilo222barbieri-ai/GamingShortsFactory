#!/usr/bin/env python3
from pathlib import Path
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
nginx=(root/'web'/'nginx.conf.template').read_text(encoding='utf-8')
companion=(root/'web'/'direct_upload_server.py').read_text(encoding='utf-8')
start=(root/'web'/'start_web.sh').read_text(encoding='utf-8')
continuation=(root/'web'/'fix_v373_creator_hub_spacing.py').read_text(encoding='utf-8')


def require(text, token, label):
    if token not in text:
        raise AssertionError(f'{label}: missing {token}')


def forbid(text, token, label):
    if token in text:
        raise AssertionError(f'{label}: forbidden {token}')

# V397 production hardening contract.
require(nginx,'location = /healthz','composite nginx health route')
require(companion,'def _composite_health','composite companion health helper')
require(companion,'"/healthz"','companion health route')
forbid(start,'python /app/web/runtime_smoke_v107.py &','runtime smoke must not be detached')
require(companion,'GSF_EDITOR_MEDIA_NOT_READY','expected empty Editor media state')
require(companion,'def _creator_social_snapshot','Creator Hub social snapshot helper')

# Existing production ownership must stay intact in Phase 1.
require(start,'test_v343_single_global_shell.py','V343 global shell contract retained')
for token in (
    'fix_v389_mobile_editor_bounded_reset.py',
    'fix_v390_mobile_editor_owner_cleanup.py',
    'fix_v391_mobile_editor_top_actions.py',
    'fix_v392_mobile_editor_premium_skin.py',
    'fix_v393_mobile_editor_clean_transport.py',
    'fix_v394_mobile_editor_footer_restore.py',
    'fix_v395_mobile_editor_atomic_skin.py',
    'fix_v396_mobile_share_publish_surface.py',
):
    require(continuation,token,'V389-V396 continuation chain retained')

print('V397 production hardening structural contract: PASS')
