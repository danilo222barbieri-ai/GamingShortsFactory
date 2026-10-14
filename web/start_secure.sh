#!/bin/sh
set -eu

python /app/web/fix_v410_security_hardening.py /app
python /app/web/test_v410_security_hardening.py /app

exec sh /app/web/start_web.sh
