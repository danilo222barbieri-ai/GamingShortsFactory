#!/usr/bin/env python3
from pathlib import Path
import ast
import re
import sys

ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
APP=ROOT/'GamingShortsFactory_V154_STRUCTURAL_HOME.py'
MARK='V335_RUNTIME_SHELL_RECOVERY'

# Repair only legacy st.html(..., height=0) calls. V343 already uses
# streamlit.components.v1.html directly and must never be rewritten here.
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
    required=[
        'GSF_GLOBAL_SHELL_V343',
        'GSF_SHELL_NAV',
        'gsf-editor-overlay-v220',
        'gsf-short-overlay-v343',
        'gsf-global-header',
        'gsf-global-gamebar',
        'gsf-global-footer',
        '_gsf_components_v343.html',
    ]
    missing=[x for x in required if x not in after]
    if missing:
        raise RuntimeError('V335 V343 shell integrity failed: '+', '.join(missing))
    compile(after,str(APP),'exec')
    if after!=before:
        APP.write_text(after,encoding='utf-8')
    print(f'{MARK} repaired={count} previous_bad={len(before_bad)} remaining_bad={len(after_bad)} v343=preserved',flush=True)

if __name__=='__main__':
    main()
