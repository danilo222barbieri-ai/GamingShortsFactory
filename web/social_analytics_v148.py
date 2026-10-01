from __future__ import annotations

import datetime as _dt
import json
import math
import urllib.parse
import urllib.request


def _clamp(v,lo=0.0,hi=1.0):
    try:return max(lo,min(hi,float(v)))
    except Exception:return 0.0


def _http_json(url,*,method="GET",headers=None,body=None,timeout=35):
    data=None
    if body is not None:
        data=json.dumps(body,ensure_ascii=False,separators=(",",":")).encode("utf-8")
    req=urllib.request.Request(url,data=data,headers=headers or {},method=method)
    with urllib.request.urlopen(req,timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def youtube_public_stats(access_token,video_id):
    q=urllib.parse.urlencode({"part":"statistics","id":str(video_id)})
    data=_http_json(
        "https://www.googleapis.com/youtube/v3/videos?"+q,
        headers={"Authorization":"Bearer "+str(access_token)},
    )
    rows=list(data.get("items") or [])
    if not rows:return {}
    stats=dict(rows[0].get("statistics") or {})
    return {
        "views":int(stats.get("viewCount",0) or 0),
        "likes":int(stats.get("likeCount",0) or 0),
        "comments":int(stats.get("commentCount",0) or 0),
        "favorites":int(stats.get("favoriteCount",0) or 0),
    }


def youtube_analytics(access_token,video_id,days=30):
    end=_dt.date.today()-_dt.timedelta(days=2)
    start=end-_dt.timedelta(days=max(1,int(days)))
    params={
        "ids":"channel==MINE",
        "startDate":start.isoformat(),
        "endDate":end.isoformat(),
        "metrics":"views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,likes,comments,shares",
        "filters":"video=="+str(video_id),
    }
    data=_http_json(
        "https://youtubeanalytics.googleapis.com/v2/reports?"+urllib.parse.urlencode(params),
        headers={"Authorization":"Bearer "+str(access_token)},
    )
    headers=[str(x.get("name") or "") for x in (data.get("columnHeaders") or [])]
    rows=list(data.get("rows") or [])
    if not rows:return {}
    row=rows[0]
    return {headers[i]:row[i] for i in range(min(len(headers),len(row)))}


def tiktok_publish_status(access_token,publish_id):
    data=_http_json(
        "https://open.tiktokapis.com/v2/post/publish/status/fetch/",
        method="POST",
        headers={"Authorization":"Bearer "+str(access_token),"Content-Type":"application/json; charset=UTF-8"},
        body={"publish_id":str(publish_id)},
    )
    payload=dict(data.get("data") or {})
    ids=list(payload.get("publicaly_available_post_id") or [])
    return {
        "status":str(payload.get("status") or ""),
        "post_ids":[str(x) for x in ids if str(x)],
        "fail_reason":str(payload.get("fail_reason") or ""),
    }


def tiktok_video_stats(access_token,video_id):
    fields="id,view_count,like_count,comment_count,share_count"
    url="https://open.tiktokapis.com/v2/video/query/?"+urllib.parse.urlencode({"fields":fields})
    data=_http_json(
        url,method="POST",
        headers={"Authorization":"Bearer "+str(access_token),"Content-Type":"application/json"},
        body={"filters":{"video_ids":[str(video_id)]}},
    )
    videos=list((data.get("data") or {}).get("videos") or [])
    if not videos:return {}
    v=dict(videos[0])
    return {
        "views":int(v.get("view_count",0) or 0),
        "likes":int(v.get("like_count",0) or 0),
        "comments":int(v.get("comment_count",0) or 0),
        "shares":int(v.get("share_count",0) or 0),
    }


def instagram_media_stats(access_token,media_id,api_host="https://graph.instagram.com"):
    base=str(api_host or "https://graph.instagram.com").rstrip("/")
    # First try professional insights. Metrics vary by media/API version, so
    # failure falls back to basic media counters instead of breaking learning.
    metrics=("views,reach,likes,comments,shares,saved,total_interactions")
    try:
        q=urllib.parse.urlencode({"metric":metrics,"access_token":str(access_token)})
        data=_http_json(f"{base}/{media_id}/insights?"+q)
        out={}
        for row in data.get("data") or []:
            if not isinstance(row,dict):continue
            name=str(row.get("name") or "")
            values=list(row.get("values") or [])
            val=(values[-1].get("value") if values and isinstance(values[-1],dict) else row.get("value"))
            if val is not None: out[name]=val
        if out:
            return {
                "views":int(out.get("views",0) or 0),
                "reach":int(out.get("reach",0) or 0),
                "likes":int(out.get("likes",0) or 0),
                "comments":int(out.get("comments",0) or 0),
                "shares":int(out.get("shares",0) or 0),
                "saves":int(out.get("saved",0) or 0),
                "interactions":int(out.get("total_interactions",0) or 0),
            }
    except Exception:
        pass
    q=urllib.parse.urlencode({"fields":"like_count,comments_count","access_token":str(access_token)})
    data=_http_json(f"{base}/{media_id}?"+q)
    return {
        "views":0,
        "likes":int(data.get("like_count",0) or 0),
        "comments":int(data.get("comments_count",0) or 0),
    }


def normalize_learning_metrics(platform,stats,analytics=None):
    stats=dict(stats or {}); analytics=dict(analytics or {})
    views=max(0.0,float(stats.get("views",analytics.get("views",0)) or 0))
    likes=max(0.0,float(stats.get("likes",analytics.get("likes",0)) or 0))
    comments=max(0.0,float(stats.get("comments",analytics.get("comments",0)) or 0))
    shares=max(0.0,float(stats.get("shares",analytics.get("shares",0)) or 0))
    saves=max(0.0,float(stats.get("saves",0) or 0))
    avg_pct=float(analytics.get("averageViewPercentage",0) or 0)
    completion=_clamp(avg_pct/100.0) if avg_pct else 0.0
    # Engagement is not substituted for watch-time. Missing provider metrics
    # stay explicitly unavailable and are handled by the dynamic score below.
    share_rate=(shares/views) if views else 0.0
    save_rate=(saves/views) if views else 0.0
    like_rate=(likes/views) if views else 0.0
    comment_rate=(comments/views) if views else 0.0
    return {
        "platform":str(platform or ""),
        "views":int(views),
        "watch_time_ratio":completion if avg_pct else None,
        "completion_rate":completion if avg_pct else None,
        "rewatch_rate":None,
        "share_rate":_clamp(share_rate),
        "save_rate":_clamp(save_rate),
        "scroll_stop_rate":None,
        "like_rate":_clamp(like_rate),
        "comment_rate":_clamp(comment_rate),
    }


def dynamic_performance_score(metrics):
    m=dict(metrics or {})
    weighted=(
        ("watch_time_ratio",.27),("completion_rate",.28),("rewatch_rate",.10),
        ("share_rate",.12),("save_rate",.08),("scroll_stop_rate",.10),
        ("like_rate",.03),("comment_rate",.02),
    )
    total=0.0; weight=0.0
    for key,w in weighted:
        value=m.get(key)
        if value is None:continue
        total+=_clamp(value)*w; weight+=w
    return round(total/weight,4) if weight else 0.0


def collect(platform,token,content_id,id_type=""):
    p=str(platform or "").lower()
    if p.startswith("you"):
        access=str(token.get("token") or token.get("access_token") or "")
        stats=youtube_public_stats(access,content_id)
        try: analytics=youtube_analytics(access,content_id)
        except Exception: analytics={}
    elif p.startswith("tik"):
        access=str(token.get("access_token") or "")
        resolved=str(content_id)
        if str(id_type or "").lower()=="publish_id" or resolved.startswith(("v_pub_","v_pub_url~","p_pub_")):
            status=tiktok_publish_status(access,resolved)
            ids=list(status.get("post_ids") or [])
            if not ids:
                return {
                    "platform":platform,"content_id":str(content_id),
        "resolved_content_id":locals().get("resolved",str(content_id)),
                    "resolved_content_id":"","publish_status":status,
                    "stats":{},"analytics":{},
                    "learning_metrics":normalize_learning_metrics(platform,{},{}),
                    "performance_score":0.0,
                }
            resolved=ids[0]
        stats=tiktok_video_stats(access,resolved); analytics={}
    elif p.startswith("inst"):
        access=str(token.get("access_token") or "")
        stats=instagram_media_stats(access,content_id,token.get("api_host") or "https://graph.instagram.com"); analytics={}
    else:
        raise ValueError("unsupported platform")
    metrics=normalize_learning_metrics(platform,stats,analytics)
    return {
        "platform":platform,"content_id":str(content_id),
        "stats":stats,"analytics":analytics,"learning_metrics":metrics,
        "performance_score":dynamic_performance_score(metrics),
    }
