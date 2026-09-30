from web.auto_highlights.pipeline import queue_message, twitch_offline_job
from web.auto_highlights.twitch_vod import ArchivedVod, parse_latest_archive, videos_request

def test_videos_request_is_archive_only():
    url, params=videos_request(broadcaster_id="42")
    assert url.endswith("/helix/videos")
    assert params["user_id"]=="42" and params["type"]=="archive"

def test_archive_to_worker_message():
    vod=parse_latest_archive({"data":[{"id":"v1","type":"archive","title":"Live","url":"https://example.invalid/v1","created_at":"x","duration":"2h"}]})
    assert isinstance(vod,ArchivedVod)
    job=twitch_offline_job(broadcaster_id="42",vod=vod,target_highlights=5,target_duration=30)
    msg=queue_message(job)
    assert msg and msg.as_dict()["kind"]=="auto_highlights.scan"
    assert msg.vod_id=="v1"

def test_missing_vod_waits():
    assert queue_message(twitch_offline_job(broadcaster_id="42",vod=None)) is None
