from pathlib import Path
import sys

p=Path(sys.argv[1])
s=p.read_text(encoding="utf-8")

checks={
    "ad mode env": 'GSF_ADS_MODE' in s,
    "preview/live/off": '{"preview","live","off"}' in s,
    "preview cards": s.count("gsf-v1056-ad") >= 3,
    "preview badge": "gsf-v1056-ad-preview" in s,
    "desktop size": "min-height:96px" in s,
    "mobile size": "min-height:104px" in s and "@media(max-width:750px)" in s,
    "stable engine owner": "st-key-v1055_ad_engine" in s,
    "stable ai owner": "st-key-v1055_ad_after_ai" in s,
    "stable final owners": "st-key-v1054_ad_after_final_action" in s and "st-key-v1054_ad_after_final_result" in s,
    "stable footer owner": "st-key-v1053_ad_footer" in s,
    "version": "Gaming Shorts Factory · V105.6 Ads Preview" in s,
}
bad=[k for k,v in checks.items() if not v]
if bad:
    raise SystemExit("V105.6 ads contract failed: "+", ".join(bad))
compile(s,str(p),"exec")
print("V105.6 ads preview contract: PASS")
