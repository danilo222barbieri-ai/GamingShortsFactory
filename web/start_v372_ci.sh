#!/bin/sh
set -eu
python - <<'PY'
from pathlib import Path
p = Path('/app/web/start_web.sh')
s = p.read_text(encoding='utf-8')
block = '''# V372 isolated gate: primary Home routes only; Creator Hub untouched.
python /app/web/fix_v372_primary_routes_runtime.py /app
python /app/web/test_v372_primary_routes_runtime.py /app

'''
anchor = 'rm -f /etc/nginx/sites-enabled/default /etc/nginx/conf.d/default.conf\n'
if 'fix_v372_primary_routes_runtime.py' not in s:
    if anchor not in s:
        raise SystemExit('V372 CI wrapper: final startup anchor missing')
    s = s.replace(anchor, block + anchor, 1)
    p.write_text(s, encoding='utf-8')
PY
exec /bin/sh /app/web/start_web.sh
