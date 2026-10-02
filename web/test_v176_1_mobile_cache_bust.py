from pathlib import Path
embed=(Path("/app")/"web/home_v154_embed.py").read_text(encoding="utf-8")
home=(Path("/app")/"web/home_v154_component/index.html").read_text(encoding="utf-8")
checks={
 "Mobile cache-bust component name is V176":"gsf_home_v154_live_176" in embed,
 "Old component name removed":"gsf_home_v154_live_155" not in embed,
 "Render function unchanged":"def render_home_v154" in embed,
 "Stable Streamlit key preserved":'key="gsf_home_v155"' in embed,
 "Mobile parity CSS still present":"V176 MOBILE VISUAL PARITY" in home,
}
bad=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(("PASS" if v else "FAIL")+": "+k)
if bad: raise SystemExit("V176.1 mobile cache bust failed: "+", ".join(bad))
print("V176.1 mobile cache bust: PASS")
