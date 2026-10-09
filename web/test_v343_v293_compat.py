#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
RUNNER=ROOT/'web/apply_v343_v293_compat.py'
START=ROOT/'web/start_web.sh'

if not RUNNER.is_file() or not START.is_file():
    raise SystemExit('V343/V293 compatibility files missing')

runner=RUNNER.read_text(encoding='utf-8')
start=START.read_text(encoding='utf-8')
runner_call='python /app/web/apply_v343_v293_compat.py'

checks={
    'project-reference shell mutation skips V343': (
        'V343 owns shell route' in runner
        and 'GSF_GLOBAL_SHELL_V343' in runner
    ),
    'legacy gamebar normalizer skips V343': (
        'V343 canonical shell owns routing' in runner
    ),
    'safe V293 runner is used': runner_call in start,
    'unsafe direct V293 call is retired': '\npython /app/web/apply_v293_render_memory_guard.py\n' not in start,
    'V343 is retested after V293': (
        start.rfind('python /app/web/test_v343_single_global_shell.py /app')
        > start.find(runner_call)
    ),
    'source shell compile runs after V293': (
        start.rfind('python -m py_compile /app/GamingShortsFactory_V154_STRUCTURAL_HOME.py')
        > start.find(runner_call)
    ),
    'generated runtime compile runs after V293': (
        start.rfind('python -m py_compile /app/GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py')
        > start.find(runner_call)
    ),
    'generated runtime retains V343': (
        "grep -q 'GSF_GLOBAL_SHELL_V343' /app/GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py" in start
    ),
}

failed=[name for name,ok in checks.items() if not ok]
for name,ok in checks.items():
    print(('PASS: ' if ok else 'FAIL: ')+name)
if failed:
    raise SystemExit('V343/V293 compatibility contract failed: '+', '.join(failed))
print('V343/V293 COMPATIBILITY CONTRACT: PASS',flush=True)
