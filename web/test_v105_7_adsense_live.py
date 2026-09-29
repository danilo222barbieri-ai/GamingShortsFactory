from pathlib import Path
import sys

app=Path(sys.argv[1] if len(sys.argv)>1 else "/app/GamingShortsFactory_V105_7_ADSENSE_READY.py")
bridge=Path(sys.argv[2] if len(sys.argv)>2 else "/app/web/install_adsense_bridge.py")
s=app.read_text(encoding="utf-8")
b=bridge.read_text(encoding="utf-8")

checks=[
    ("V105.7 output marker","V105.7 AdSense Ready" in s),
    ("six renderer calls",all(f"_gsf_v1057_ad_markup({i})" in s for i in range(1,7))),
    ("publisher env","GSF_ADSENSE_CLIENT" in s),
    ("live class inside class attribute",'gsf-v1057-slot-{idx} gsf-v1057-live"\'' in s),
    ("six slot envs","GSF_ADSENSE_SLOT_" in s and "range(1,7)" in s),
    ("responsive format bridge",'data-ad-format","auto"' in b),
    ("responsive width bridge",'data-full-width-responsive","true"' in b),
    ("top-page mutation bridge","MutationObserver" in b),
    ("no iframe ads","iframe" not in b.lower() and "components.html" not in s),
    ("no timer refresh","setInterval" not in b and "setTimeout" not in b),
    ("safe default off",'GSF_ADS_MODE","off"' in s),
    ("download separation","gsf-v1057-slot-5{margin-top:68px" in s),
]
for label,ok in checks:
    if not ok:
        raise SystemExit("FAIL: "+label)
    print("PASS:",label)

compile(s,str(app),"exec")
print("V105.7 AdSense-ready contract: PASS")
