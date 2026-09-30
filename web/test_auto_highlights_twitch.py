import hashlib, hmac
from web.auto_highlights.twitch_eventsub import verify_signature, verification_challenge, stream_offline_event

def test_signature():
    secret="0123456789abcdef"
    body=b'{"x":1}'
    headers={
      "Twitch-Eventsub-Message-Id":"abc",
      "Twitch-Eventsub-Message-Timestamp":"2026-09-30T06:00:00Z",
    }
    msg=b"abc"+b"2026-09-30T06:00:00Z"+body
    headers["Twitch-Eventsub-Message-Signature"]="sha256="+hmac.new(secret.encode(),msg,hashlib.sha256).hexdigest()
    assert verify_signature(secret,headers,body)

def test_challenge_and_offline():
    assert verification_challenge({"challenge":"ok"})=="ok"
    payload={"subscription":{"type":"stream.offline"},"event":{"broadcaster_user_id":"42","broadcaster_user_login":"dan"}}
    e=stream_offline_event(payload)
    assert e and e["broadcaster_user_id"]=="42"
