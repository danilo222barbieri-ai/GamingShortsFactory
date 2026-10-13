#!/usr/bin/env python3
from pathlib import Path
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
nginx=(root/'web'/'nginx.conf.template').read_text(encoding='utf-8')
companion=(root/'web'/'direct_upload_server.py').read_text(encoding='utf-8')
start=(root/'web'/'start_web.sh').read_text(encoding='utf-8')
continuation=(root/'web'/'fix_v373_creator_hub_spacing.py').read_text(encoding='utf-8')
smoke=(root/'web'/'runtime_smoke_v107.py').read_text(encoding='utf-8')


def require(text, token, label):
    if token not in text:
        raise AssertionError(f'{label}: missing {token}')


def forbid(text, token, label):
    if token in text:
        raise AssertionError(f'{label}: forbidden {token}')

# V397 composite production health.
require(nginx,'location = /healthz','composite nginx health route')
require(companion,'def _composite_health','composite companion health helper')
require(companion,'"/healthz"','companion health route')
require(companion,'127.0.0.1:8501/_stcore/health','Streamlit health probe')
require(companion,'"companion":True','companion health signal')
require(companion,'"streamlit":streamlit_ready','Streamlit health signal')
require(companion,'503','unhealthy composite status')
require(smoke,'request("/healthz"','runtime smoke composite health request')
require(smoke,'health.get("companion")','runtime smoke companion assertion')
require(smoke,'health.get("streamlit")','runtime smoke Streamlit assertion')
forbid(start,'python /app/web/runtime_smoke_v107.py &','runtime smoke must not be detached')

# Empty Editor media is an expected valid-session state, not an operational 404.
require(companion,'GSF_EDITOR_MEDIA_NOT_READY','expected empty Editor media marker')
require(companion,'handler.send_response(204)','expected empty Editor media HTTP 204')
require(smoke,'editor-media/current','runtime smoke empty Editor media coverage')

# Creator Hub social state is loaded once and reused in the response and count.
require(companion,'def _creator_social_snapshot','Creator Hub social snapshot helper')
require(companion,'social_snapshot=_creator_social_snapshot(sid,providers)','Creator Hub snapshot single acquisition')
require(companion,'"social":social_snapshot','Creator Hub snapshot response reuse')
require(companion,'sum(1 for connected in social_snapshot.values() if connected)','Creator Hub snapshot stats reuse')

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
