from pathlib import Path
import re
embed=(Path("/app")/"web/home_v154_embed.py").read_text(encoding="utf-8")
home=(Path("/app")/"web/home_v154_component/index.html").read_text(encoding="utf-8")
m=re.search(r'gsf_home_v154_live_([0-9]+)',embed)
version=int(m.group(1)) if m else 0
checks={
 "Mobile cache-bust component is V176 or newer":version>=176,
 "Ancient component name removed":"gsf_home_v154_live_155" not in embed,
 "Render function unchanged":"def render_home_v154" in embed,
 "Stable Streamlit key preserved":'key="gsf_home_v155"' in embed,
 "Mobile parity CSS still present":"V176 MOBILE VISUAL PARITY" in home,
}
bad=[k for k,v in checks.items() if not v]
for k,v in checks.items():
    print(("PASS" if v else "FAIL")+": "+k)
if bad:
    raise SystemExit("V176.1 mobile cache bust failed: "+", ".join(bad))
print(f"V176.1 mobile cache bust: PASS (component v{version})")
