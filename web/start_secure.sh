#!/bin/sh
set -eu

# The historical GSF boot still performs runtime migrations. Inject V410 only
# after those migrations and immediately before Nginx/the companion servers
# start, so no legacy patch can overwrite the security layer afterwards.
python - <<'PY'
from pathlib import Path

source=Path('/app/web/start_web.sh')
target=Path('/tmp/gsf-start-v410.sh')
text=source.read_text(encoding='utf-8')
needle='rm -f /etc/nginx/sites-enabled/default /etc/nginx/conf.d/default.conf\n'
hook=(
    'python /app/web/fix_v410_security_hardening.py /app\n'
    'python /app/web/fix_v410_1_edge_identity.py /app\n'
    'python /app/web/test_v410_security_hardening.py /app\n'
)
if needle not in text:
    raise SystemExit('V410 secure boot anchor missing')
text=text.replace(needle,hook+needle,1)
target.write_text(text,encoding='utf-8')
target.chmod(0o700)
PY

exec sh /tmp/gsf-start-v410.sh
