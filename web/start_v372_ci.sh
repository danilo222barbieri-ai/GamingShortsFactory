#!/bin/sh
set -eu
python - <<'PY'
from pathlib import Path
p = Path('/app/web/start_web.sh')
s = p.read_text(encoding='utf-8')
line = 'python /app/web/test_v372_primary_routes_runtime.py /app\n'
anchor = 'rm -f /etc/nginx/sites-enabled/default /etc/nginx/conf.d/default.conf\n'
if line not in s:
    if anchor not in s:
        raise SystemExit('V372 CI wrapper: final startup anchor missing')
    s = s.replace(anchor, line + '\n' + anchor, 1)
    p.write_text(s, encoding='utf-8')
PY
exec /bin/sh /app/web/start_web.sh
