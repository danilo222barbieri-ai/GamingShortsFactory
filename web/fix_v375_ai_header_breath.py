#!/usr/bin/env python3
from pathlib import Path
import sys

MARK = 'V375_AI_HEADER_BREATH'

PATCH = r'''
<!-- V375_AI_HEADER_BREATH -->
<style id="v375AiHeaderBreath">
@media(max-width:920px){
  /* Keep the AI page clear of the parent global header without changing its internal layout. */
  body{padding-top:30px!important}
}
</style>
'''


def patch_text(text: str) -> str:
    if MARK in text:
        return text
    if 'V308 MOBILE AI FLOW' not in text:
        raise RuntimeError('V375 requires V308 mobile AI flow baseline')
    if 'Scegli il tuo Motore IA' not in text:
        raise RuntimeError('V375 AI title anchor missing')
    if '</head>' not in text:
        raise RuntimeError('V375 AI head anchor missing')
    return text.replace('</head>', PATCH + '\n</head>', 1)


def main() -> None:
    path = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path('/app/web/ai_v221_component/index.html')
    if not path.is_file():
        raise SystemExit('V375 AI target missing: ' + str(path))
    before = path.read_text(encoding='utf-8')
    after = patch_text(before)
    path.write_text(after, encoding='utf-8')
    print('V375 AI header breath applied changed=', before != after, flush=True)


if __name__ == '__main__':
    main()
