from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]

def read(path): return (ROOT/path).read_text(encoding="utf-8")
def write(path,text): (ROOT/path).write_text(text,encoding="utf-8")
def replace_once(text,old,new,label):
    n=text.count(old)
    if n!=1: raise SystemExit(f"{label}: expected exactly 1 match, got {n}")
    return text.replace(old,new,1)

# 1) Editor mini header: controls are already exposed below the preview.
p="web/game_editor_mobile_component/index.html"; t=read(p)
t=replace_once(t,
"/* editor page: surface-specific rules live in night_arena_v417.css */\n/* GSF_NIGHT_ARENA_PAGE:END */",
"/* editor page: surface-specific rules live in night_arena_v417.css */\n/* GSF_V427_MINI_EDITOR_HEADER_CLEANUP */\n.editor-app.is-mini .editor-header{display:none!important}\n/* GSF_NIGHT_ARENA_PAGE:END */",
"editor header")
write(p,t)

# 2) Home footer: retired local footer must never reserve/paint space, even before parent-ready.
p="web/home_v154_component/index.html"; t=read(p)
t=replace_once(t,
"/* The shell has no footer any more: the Home stops reserving room for it. */\nhtml.gsf-v343-parent-ready body #home154#home154 .siteFooter{display:none!important}",
"/* The shell has no footer any more: the Home stops reserving room for it. */\n/* GSF_V427_HOME_FOOTER_RACE */\nhtml body #home154#home154 .siteFooter{display:none!important}",
"home footer")
write(p,t)

# 3) AI duration: three choices, one row.
p="web/ai_v221_component/index.html"; t=read(p)
t=replace_once(t,
".seg{display:inline-grid;grid-template-columns:1fr 1fr;",
"/* GSF_V427_DURATION_INLINE */\n.seg{display:inline-grid;grid-template-columns:repeat(3,minmax(0,1fr));",
"duration selector")
write(p,t)

# 4) Alive carried-work status: icon-only in the top header, full pill only when bottom-docked.
p="web/gsf_alive_v418.js"; t=read(p)
t=replace_once(t,
"/* GSF_ALIVE_COMPACT_PILL */\n#gsf-alive-bubble{max-width:min(78vw,320px);overflow:hidden}\n#gsf-alive-bubble .l{display:block;min-width:0;overflow:hidden;text-overflow:ellipsis}\n#gsf-alive-bubble small{flex:0 0 auto}",
"/* GSF_ALIVE_COMPACT_PILL */\n#gsf-alive-bubble{max-width:min(78vw,320px);overflow:hidden}\n#gsf-alive-bubble .l{display:block;min-width:0;overflow:hidden;text-overflow:ellipsis}\n#gsf-alive-bubble small{flex:0 0 auto}\n/* GSF_V427_ALIVE_HEADER_DOT */\n#gsf-alive-bubble.header-dot{width:38px;height:38px;max-width:38px;padding:4px;border-radius:50%;gap:0;justify-content:center}\n#gsf-alive-bubble.header-dot .l,#gsf-alive-bubble.header-dot small{display:none!important}\n#gsf-alive-bubble.header-dot svg{width:28px;height:28px;margin:0}",
"alive css")
t=replace_once(t,
"    const m = mounted && visible() && !shared ? bubbleModel() : null;\n    bubbleGo = m ? m.go : null;",
"    const m = mounted && visible() && !shared ? bubbleModel() : null;\n    bubbleEl.classList.toggle(\"header-dot\",page.dock!==\"bottom\");\n    bubbleGo = m ? m.go : null;",
"alive class")
write(p,t)

# 5) Creator Hub: real archived Short as card preview, with glyph retained as fallback/overlay.
p="web/creator_hub_v156_component/index.html"; t=read(p)
t=replace_once(t,
".pcard .cover .glyph svg{width:17px;height:17px}",
".pcard .cover .glyph svg{width:17px;height:17px}\n/* GSF_V427_SHORT_CARD_PREVIEW */\n.pcard .cover .cardPreview{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;pointer-events:none;background:#06111d}\n.pcard .cover .tag,.pcard .cover .glyph{z-index:2}",
"hub preview css")
old='''  const title=esc(item.title||"Short");\n  const pub=(item.published||[]).map(p=>PLATFORM_NAMES[p]||p);\n  const mb=(Number(item.final_bytes)||0)>1048576?Math.max(1,Math.round(Number(item.final_bytes)/1048576))+" MB":"";\n  return '<div class="pcard short" data-kind="short" data-id="'+id+'"><button class="cover" type="button" data-act="menu" aria-label="Azioni '+title+'"><span class="tag'+(pub.length?" pub":"")+'">'+(pub.length?"Pubblicato":"Short")+'</span><span class="glyph">'+PLAY+'</span></button><button class="more" type="button" data-act="menu" aria-label="Azioni Short">'+DOTS+'</button><div class="ptitle">'+title+'</div><div class="pmeta">'+esc(pub.length?pub.join(", "):(item.completed_at?ago(item.completed_at):"Salvato"))+(mb?" · "+mb:"")+'</div></div>';'''
new='''  const title=esc(item.title||"Short");\n  const pub=(item.published||[]).map(p=>PLATFORM_NAMES[p]||p);\n  const mb=(Number(item.final_bytes)||0)>1048576?Math.max(1,Math.round(Number(item.final_bytes)/1048576))+" MB":"";\n  const preview="/creator-hub/short/file?id="+encodeURIComponent(item.id||"")+"&preview=1#t=0.1";\n  return '<div class="pcard short" data-kind="short" data-id="'+id+'"><button class="cover" type="button" data-act="menu" aria-label="Azioni '+title+'"><video class="cardPreview" playsinline muted preload="metadata" src="'+esc(preview)+'" aria-hidden="true"></video><span class="tag'+(pub.length?" pub":"")+'">'+(pub.length?"Pubblicato":"Short")+'</span><span class="glyph">'+PLAY+'</span></button><button class="more" type="button" data-act="menu" aria-label="Azioni Short">'+DOTS+'</button><div class="ptitle">'+title+'</div><div class="pmeta">'+esc(pub.length?pub.join(", "):(item.completed_at?ago(item.completed_at):"Salvato"))+(mb?" · "+mb:"")+'</div></div>';'''
t=replace_once(t,old,new,"hub preview markup")
write(p,t)

# 6) Instagram: prefer already-supported Meta professional flow when both configs exist.
p="web/direct_upload_server.py"; t=read(p)
old='''    # Prefer Meta's current Instagram Login flow. It does not require a\n    # Facebook Page and uses the Instagram App ID shown under\n    # Instagram > API setup with Instagram login.\n    if INSTAGRAM_APP_ID and INSTAGRAM_APP_SECRET:'''
new='''    # GSF_V427_INSTAGRAM_META_FIRST: when the Meta professional flow is\n    # configured, prefer it for publishing so users do not hit Instagram\n    # Login's development-role gate. Direct Instagram Login remains fallback.\n    if INSTAGRAM_APP_ID and INSTAGRAM_APP_SECRET and not (META_APP_ID and META_APP_SECRET):'''
t=replace_once(t,old,new,"instagram route")
# Inline media response for card previews; normal downloads remain attachments.
needle='''                key=str(row.get("bucket_key") or _short_object_key(sid,short_id))\n                filename=re.sub(r"[^A-Za-z0-9_.-]+","_",str(row.get("title") or short_id))[:100]+".mp4"\n                url=_s3().generate_presigned_url(\n                    "get_object",\n                    Params={\n                        "Bucket":S3_BUCKET,\n                        "Key":key,\n                        "ResponseContentDisposition":f'attachment; filename="{filename}"','''
repl='''                key=str(row.get("bucket_key") or _short_object_key(sid,short_id))\n                filename=re.sub(r"[^A-Za-z0-9_.-]+","_",str(row.get("title") or short_id))[:100]+".mp4"\n                preview=str((parse_qs(path.query).get("preview") or [""])[0]).strip().lower() in ("1","true","yes")\n                url=_s3().generate_presigned_url(\n                    "get_object",\n                    Params={\n                        "Bucket":S3_BUCKET,\n                        "Key":key,\n                        "ResponseContentDisposition":"inline" if preview else f'attachment; filename="{filename}"',\n                        "ResponseContentType":"video/mp4",'''
t=replace_once(t,needle,repl,"short preview response")
write(p,t)

# 7) AI: only after the normal ranker successfully returns an empty pool, build a bounded fallback.
p="web/ai_engines_v412.py"; t=read(p)
anchor='''def _score(row: Mapping[str, Any]) -> int | None:\n'''
helper='''def fallback_rank_pool(diagnostics: Mapping[str, Any] | None, *, source_duration: Any, clip_duration: Any, target: int = 3):\n    """Recover useful windows only when a successful analysis returned no rank pool.\n\n    Prefer real diagnostic signal peaks. If a valid source has no usable diagnostic\n    rows, return low-confidence deterministic coverage windows rather than an empty\n    result. Provider/decoder exceptions are not handled here and keep propagating.\n    """\n    source=max(0.0,_num(source_duration,0.0))\n    clip=max(0.1,_num(clip_duration,15.0))\n    count=max(1,min(8,int(target or 3)))\n    if source<=0:\n        return []\n    max_start=max(0.0,source-clip)\n    rows=[]\n    for raw_start, raw_row in dict(diagnostics or {}).items():\n        if str(raw_start).startswith("__") or not isinstance(raw_row,Mapping):\n            continue\n        try:\n            start=float(raw_start)\n        except (TypeError,ValueError):\n            start=_num(raw_row.get("start"),-1.0)\n        if start<0:\n            continue\n        features=raw_row.get("features") if isinstance(raw_row.get("features"),Mapping) else raw_row\n        event=max(0.0,_num(features.get("event_score"),0.0))\n        motion=max(0.0,_num(features.get("motion_burst"),0.0),_num(features.get("motion_avg"),0.0))\n        reaction=max(0.0,_num(features.get("reaction"),0.0),_num(features.get("reaction_cue"),0.0))\n        active=max(0.0,_num(features.get("active_ratio"),0.0))\n        synergy=max(0.0,_num(features.get("synergy"),0.0))\n        arc=max(0.0,_num(features.get("arc"),0.0))\n        hook=max(0.0,_num(features.get("hook"),0.0))\n        payoff=max(0.0,_num(features.get("payoff"),0.0))\n        dead=max(0.0,_num(features.get("dead_ratio"),0.0),_num(features.get("dead_streak_ratio"),0.0))\n        score=.34*event+.28*motion+.16*reaction+.08*active+.06*synergy+.04*arc+.02*hook+.02*payoff-.18*dead\n        rows.append((max(0.0,min(1.0,score)),max(0.0,min(max_start,start))))\n    if rows:\n        rows.sort(key=lambda pair:(pair[0],-pair[1]),reverse=True)\n        chosen=[]; min_gap=max(1.0,clip*.4)\n        for score,start in rows:\n            if any(abs(start-old_start)<min_gap for _,old_start in chosen):\n                continue\n            chosen.append((score,start))\n            if len(chosen)>=count:\n                break\n        if chosen:\n            return chosen\n    # Last-resort coverage for a valid decoded source: low confidence, bounded, unique.\n    starts=[max_start/2.0,0.0,max_start]\n    if count>3:\n        starts.extend(max_start*i/(count-1) for i in range(1,count-1))\n    out=[]\n    for start in starts:\n        start=max(0.0,min(max_start,float(start)))\n        if any(abs(start-old_start)<0.05 for _,old_start in out):\n            continue\n        out.append((max(.12,.25-.02*len(out)),start))\n        if len(out)>=count:\n            break\n    return out\n\n\n'''
t=replace_once(t,anchor,helper+anchor,"ai fallback helper")
write(p,t)

p="app.py"; t=read(p)
needle='''    _pool,_diagnostics=_gsf_v112_rank_base(\n        input_file,modalita,\n        clip_duration=clip_duration,\n        numero_clip=_pool_target,\n        cache_token=cache_token,\n    )\n'''
repl=needle+'''    # GSF_V427_AI_EMPTY_POOL_FALLBACK: preserve real ranker results, but do\n    # not strand a valid gameplay at zero moments when ranking yields no pool.\n    if not _pool:\n        from web.ai_engines_v412 import fallback_rank_pool as _gsf_v427_fallback_rank_pool\n        try:\n            _source_duration=float(durata_video(input_file) or 0.0)\n        except Exception:\n            _source_duration=0.0\n        _pool=_gsf_v427_fallback_rank_pool(\n            _diagnostics,\n            source_duration=_source_duration,\n            clip_duration=float(clip_duration),\n            target=_pool_target,\n        )\n        if _pool:\n            _diagnostics=dict(_diagnostics or {})\n            _meta=dict(_diagnostics.get("__meta__") or {})\n            _meta["empty_pool_fallback"]=True\n            _diagnostics["__meta__"]=_meta\n'''
t=replace_once(t,needle,repl,"app ai fallback")
write(p,t)

print("V427 one-shot source patch applied")
