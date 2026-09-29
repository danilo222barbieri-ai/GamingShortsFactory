from pathlib import Path
import sys

nginx=Path(sys.argv[1] if len(sys.argv)>1 else "/app/web/nginx.conf.template").read_text(encoding="utf-8")
start=Path(sys.argv[2] if len(sys.argv)>2 else "/app/web/start_web.sh").read_text(encoding="utf-8")

checks=[
    ("root ads.txt route",'location = /ads.txt' in nginx),
    ("ads.txt temp alias",'alias /tmp/gsf-ads.txt;' in nginx),
    ("publisher env read",'GSF_ADSENSE_CLIENT' in start),
    ("google ads.txt authority",'f08c47fec0942fa0' in start),
    ("DIRECT relationship",'DIRECT' in start),
    ("publisher prefix conversion",'ca-pub-' in start and 'pub-' in start),
]
for label,ok in checks:
    if not ok:
        raise SystemExit("FAIL: "+label)
    print("PASS:",label)
print("V105.7 ads.txt contract: PASS")
