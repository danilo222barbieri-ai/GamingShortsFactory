from web.auto_highlights.live_folder import build_live_folder
from web.auto_highlights.models import HighlightCandidate
from web.auto_highlights.store import JsonLiveFolderStore
from web.auto_highlights.creator_hub import creator_hub_payload

def test_folder_persists_and_is_creator_hub_ready(tmp_path):
    folder=build_live_folder(provider="twitch",account_id="42",broadcast_id="live1",title="FC27",
      ended_at="2026-09-30T08:00:00Z",
      candidates=[HighlightCandidate(100,130,.94,"reazione","reazioni"),HighlightCandidate(300,330,.87,"azione","azione")])
    store=JsonLiveFolderStore(tmp_path)
    store.save(folder)
    rows=store.list_for_account("twitch","42")
    assert rows[0]["title"]=="FC27"
    assert rows[0]["highlights"][0]["score_percent"]==94
    assert rows[0]["highlights"][0]["status"]=="ready_for_editor"
    payload=creator_hub_payload(rows)
    assert payload["ready_live_count"]==1 and payload["highlight_count"]==2
