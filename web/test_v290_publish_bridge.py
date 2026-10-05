from pathlib import Path
import sys

share=Path(sys.argv[1]).read_text(encoding='utf-8')
shell=Path(sys.argv[2]).read_text(encoding='utf-8')


def need(name,ok):
    print(('PASS' if ok else 'FAIL')+': '+name)
    if not ok:
        raise AssertionError(name)

need('share emits explicit publish event', 'GSF_SOCIAL_PUBLISH' in share)
need('connected card says Pubblica', 'Pubblica su ' in share)
need('unconnected card opens social connector directly', '/social-connect' in share and 'window.open' in share)
need('share refreshes connection state on focus', 'addEventListener("focus"' in share or "addEventListener('focus'" in share)
need('social shell persists open state', 'gsf_social_overlay_open_v290' in shell)
need('shell persists publish phase', 'gsf_social_publish_pending_v290' in shell)
need('shell handles explicit publish event', 'GSF_SOCIAL_PUBLISH' in shell)
need('shell selects exact social platform', 'social_upload_v59_' in shell or 'clickExact' in shell)
need('shell advances to PUBBLICA', 'PUBBLICA' in shell and 'publishPending' in shell)
need('shell relays publish result', 'GSF_SOCIAL_RESULT' in shell)
print('V290 SOCIAL PUBLISH BRIDGE: PASS')
