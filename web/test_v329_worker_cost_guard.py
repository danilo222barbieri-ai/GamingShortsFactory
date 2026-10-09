#!/usr/bin/env python3
from pathlib import Path
import sys

root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
direct=(root/'web/direct_upload_server.py').read_text(encoding='utf-8')
bridge=(root/'web/gsf_bucket_bridge.py').read_text(encoding='utf-8')

checks={
    'prescan has retry helper':'def _worker_request_with_retry(' in direct,
    'prescan retry handles cold boot':'HTTPError' in direct and '502' in direct and '503' in direct,
    'prescan uses retry helper':'_worker_request_with_retry(req,timeout=12' in direct,
    'status has retry helper':'def _worker_status_request(' in bridge,
    'status retries cold boot':'for attempt in range(3)' in bridge and 'time.sleep(' in bridge,
    'status still falls back safely':'return {"reachable":False,"state":"unavailable"}' in bridge,
}
failed=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(('PASS: ' if v else 'FAIL: ')+k)
if failed: raise SystemExit('V329 worker cost guard contract failed: '+', '.join(failed))
compile(direct,str(root/'web/direct_upload_server.py'),'exec')
compile(bridge,str(root/'web/gsf_bucket_bridge.py'),'exec')
print('V329 WORKER COST GUARD CONTRACT: PASS')
