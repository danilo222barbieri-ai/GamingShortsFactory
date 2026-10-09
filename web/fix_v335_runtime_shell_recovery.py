#!/usr/bin/env python3
from pathlib import Path
import ast
import re
import sys

ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
APP=ROOT/'GamingShortsFactory_V154_STRUCTURAL_HOME.py'
MARK='V335_RUNTIME_SHELL_RECOVERY'

# Late mobile-shell patches V328/V330/V331/V332/V334 used the components.html
# layout API shape on Streamlit's st.html. In the deployed Streamlit version
# st.html does not accept height=, so the parent script aborts before chrome and
# navigation listeners are installed. Repair only st.html(..., height=0) calls;
# do not touch components.html calls where height is valid.
PATTERN=re.compile(
    r'(st\.html\(\s*[rRuUbBfF]*"""(?:(?!""").)*?""")\s*,\s*height\s*=\s*0\s*\)',
    re.DOTALL,
)


def bad_height_lines(source:str):
    tree=ast.parse(source)
    bad=[]
    for node in ast.walk(tree):
        if not isinstance(node,ast.Call):
            continue
        fn=node.func
        if isinstance(fn,ast.Attribute) and fn.attr=='html' and isinstance(fn.value,ast.Name) and fn.value.id=='st':
            if any(k.arg=='height' for k in node.keywords):
                bad.append(getattr(node,'lineno','?'))
    return bad


def main():
    if not APP.is_file():
        raise SystemExit('V335 shell app missing')
    before=APP.read_text(encoding='utf-8')
    before_bad=bad_height_lines(before)
    after,count=PATTERN.subn(lambda m:m.group(1)+')',before)
    after_bad=bad_height_lines(after)
    if after_bad:
        raise RuntimeError('V335 unsupported st.html height keyword remains at lines '+','.join(map(str,after_bad)))
    if before_bad and count!=len(before_bad):
        raise RuntimeError(f'V335 repair mismatch: bad={len(before_bad)} repaired={count}')
    # Ensure the repair did not remove the two runtime features the user needs.
    required=['V331_PRIMARY_ACTIONS_ROUTING','V334_GLOBAL_CHROME_HARD_LOCK','GSF_SHELL_NAV','gsf-editor-overlay-v220','gsf-short-overlay-v331']
    missing=[x for x in required if x not in after]
    if missing:
        raise RuntimeError('V335 shell integrity failed: '+', '.join(missing))
    compile(after,str(APP),'exec')
    if after!=before:
        APP.write_text(after,encoding='utf-8')
    print(f'{MARK} repaired={count} previous_bad={len(before_bad)} remaining_bad={len(after_bad)}',flush=True)

if __name__=='__main__':
    main()
