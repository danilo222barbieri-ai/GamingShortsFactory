#!/usr/bin/env python3
from pathlib import Path
import sys

path=Path(sys.argv[1] if len(sys.argv)>1 else '/app/web/share_v156_component/index.html')
text=path.read_text(encoding='utf-8')
checks={
 'V292 publish intent marker':'GSF_V292_SHARE_PUBLISH_INTENT' in text,
 'connected social CTA says publish':'Pubblica su ' in text,
 'publish intent survives rerun':'sessionStorage.setItem(PUBLISH_INTENT_KEY' in text and 'resumePublishIntent();' in text,
 'publish bridge searches real publish controls':'t.includes("pubblica")||t.includes("publish")' in text,
 'publish bridge binds selected platform':'txt.includes(key)' in text and 'own.includes(key)' in text,
 'connected social click arms publish intent':'if(connected){armPublish(key);setTimeout(()=>parentClick([key]),180)}' in text,
 'disconnected social still uses connect flow':'else setTimeout(()=>parentClick([key]),650);' in text,
 'Facebook remains manual':'window.open("https://www.facebook.com/"' in text,
}
for name,ok in checks.items():
    print(('PASS' if ok else 'FAIL')+': '+name)
bad=[name for name,ok in checks.items() if not ok]
if bad:
    raise SystemExit('V292 share publish bridge failed: '+', '.join(bad))
print('V292 share publish resume bridge: PASS')
