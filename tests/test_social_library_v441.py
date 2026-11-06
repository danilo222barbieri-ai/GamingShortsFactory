"""V441: social library errors and publish connections remain explicit."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SERVER=(ROOT/"web/direct_upload_server.py").read_text(encoding="utf-8")
HUB=(ROOT/"web/creator_hub_v156_component/index.html").read_text(encoding="utf-8")
SHARE=(ROOT/"web/share_v156_component/index.html").read_text(encoding="utf-8")

def test_twitch_all_does_not_swallow_all_provider_errors():
    source=SERVER.split('def _twitch_content(',1)[1].split('def _twitch_clip_source(',1)[0]
    assert 'if not succeeded:' in source
    assert 'if exc.status==401:' in source
    assert 'raise first_error or' in source
    assert '"partial":bool(failed)' in source

def test_hub_reports_youtube_error_payload_and_partial_twitch_content():
    assert 'if(!response.ok||!data.ok||data.error)' in HUB
    assert 'if(data.partial)' in HUB

def test_share_refreshes_oauth_snapshot_before_prompting_to_reconnect():
    section=SHARE.split("$('#publishBtn').onclick=async()=>{",1)[1].split("/* share + save */",1)[0]
    assert section.index("fetch('/share/state'")<section.index('const notConn=sel.find')
    assert "server.social=snapshot.social||{}" in section
    assert 'Impossibile verificare i social collegati' in section
