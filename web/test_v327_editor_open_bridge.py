#!/usr/bin/env python3
from pathlib import Path
import sys

root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
shell=(root/'GamingShortsFactory_V154_STRUCTURAL_HOME.py').read_text(encoding='utf-8')

checks={
    'editor iframe is eager again':'src="/editor-live/?v=327"' in shell and 'data-src="/editor-live/"' in shell and 'data-loaded="1"' in shell,
    'AI remains lazy':'src="about:blank"' in shell and 'data-src="/ai-v221/"' in shell and 'data-loaded="0"' in shell,
    'Hub remains lazy':'data-src="/creator-hub-v156/"' in shell,
    'Social remains lazy':'data-src="/share-v156/"' in shell,
    'Account remains lazy':'data-src="/account/"' in shell,
}
failed=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(('PASS: ' if v else 'FAIL: ')+k)
if failed: raise SystemExit('V327 editor open bridge contract failed: '+', '.join(failed))
print('V327 EDITOR OPEN BRIDGE CONTRACT: PASS')
