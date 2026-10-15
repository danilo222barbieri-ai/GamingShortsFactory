#!/usr/bin/env python3
from pathlib import Path
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
nginx=(root/'web'/'nginx.conf.template').read_text(encoding='utf-8')
companion=(root/'web'/'direct_upload_server.py').read_text(encoding='utf-8')
start=(root/'web'/'start_web.sh').read_text(encoding='utf-8')
editor=(root/'web'/'editor_2027_component'/'index.html').read_text(encoding='utf-8')
share=(root/'web'/'share_v156_component'/'index.html').read_text(encoding='utf-8')
app_path=root/'app.py' if (root/'app.py').is_file() else root/'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py'
app=app_path.read_text(encoding='utf-8')
smoke=(root/'web'/'runtime_smoke_v107.py').read_text(encoding='utf-8')
gate_path=root/'.github'/'workflows'/'v397-production-gate.yml'
gate=gate_path.read_text(encoding='utf-8') if gate_path.is_file() else ''


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

# Blocking current production gate: source contract + real image + live container smoke.
require(gate,'main','production gate targets main')
require(gate,'python web/test_v397_production_hardening.py .','production gate source contract')
require(gate,'docker build','production gate builds production image')
require(gate,'/healthz','production gate waits on composite health')
require(gate,'docker exec','production gate enters built container')
require(gate,'/app/web/runtime_smoke_v107.py','production gate runs runtime smoke synchronously')
require(gate,'docker logs','production gate preserves failure evidence')

# Existing production ownership must stay intact. Since the canonical UI
# pipeline, the approved work is present in the canonical files themselves and
# the startup path only verifies and launches (no migration chain to retain).
require(app,'GSF_GLOBAL_SHELL_V343','V343 global shell present in canonical app')
require(start,'gsf_ui_manifest.py verify','startup verifies the canonical UI manifest')
forbid(start,'fix_v','startup must not replay legacy migrations')
for token in (
    'V389_MOBILE_EDITOR_BOUNDED_RESET',
    'V390_MOBILE_EDITOR_OWNER_CLEANUP',
    'V391_MOBILE_EDITOR_TOP_ACTIONS',
    'V392_MOBILE_EDITOR_PREMIUM_SKIN',
    'V393_MOBILE_EDITOR_CLEAN_TRANSPORT',
    'V394_MOBILE_EDITOR_FOOTER_RESTORE',
    'V395_MOBILE_EDITOR_ATOMIC_SKIN',
):
    require(editor,token,'V389-V395 mobile editor retained in canonical editor')
require(share,'V396_MOBILE_SHARE_PUBLISH_SURFACE','V396 share/publish surface retained in canonical share')

print('V397 production hardening structural contract: PASS')
