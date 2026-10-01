from pathlib import Path
import sys

sys.path.insert(0,"/app/web")
import social_analytics_v148 as sa

m=sa.normalize_learning_metrics(
    "YouTube",
    {"views":1000,"likes":80,"comments":12,"shares":20,"saves":5},
    {"averageViewPercentage":72.0},
)
assert m["views"]==1000
assert abs(m["completion_rate"]-.72)<1e-9
assert m["share_rate"]>.0
score=sa.dynamic_performance_score(m)
assert 0.0<score<=1.0

orig=sa._http_json
try:
    def fake(url,**kwargs):
        if "status/fetch" in url:
            return {"data":{"status":"PUBLISH_COMPLETE","publicaly_available_post_id":["123456"]},"error":{"code":"ok"}}
        if "video/query" in url:
            return {"data":{"videos":[{"id":"123456","view_count":1200,"like_count":100,"comment_count":10,"share_count":25}]}}
        raise AssertionError(url)
    sa._http_json=fake
    r=sa.collect("TikTok",{"access_token":"x"},"v_pub_url~abc",id_type="publish_id")
    assert r["resolved_content_id"]=="123456"
    assert r["stats"]["views"]==1200
finally:
    sa._http_json=orig

if len(sys.argv)>1:
    server=Path(sys.argv[1]).read_text(encoding="utf-8")
    for marker in (
        "/social-analytics/register","/social-analytics/collect","/social-analytics/context",
        "GSF_V148_ANALYTICS_REFRESH","video.list","yt-analytics.readonly",
        "_analytics_collect_one","performance_score",
    ):
        assert marker in server,marker

if len(sys.argv)>2:
    app=Path(sys.argv[2]).read_text(encoding="utf-8")
    for marker in (
        "_gsf_v148_api","GSF_V148_ANALYTICS_REGISTERED",
        "/social-analytics/register",
    ):
        assert marker in app,marker

print("V148 Social Analytics Learning: PASS")
