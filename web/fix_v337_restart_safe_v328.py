#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
TARGET=ROOT/'web/fix_v328_global_balance.py'
V331=ROOT/'web/fix_v331_primary_actions_routing.py'
MARK='V337_RESTART_SAFE_V328'
V331_MARK='V337_RESTART_SAFE_V331'

OLD="""    if old in text:text=text.replace(old,new,1)\n    elif 'if(!opened)shellNav(\"short\")' not in text: raise RuntimeError('V328 Home Short action anchor missing')\n"""
NEW="""    if old in text:text=text.replace(old,new,1)\n    canonical_v331_short='if(action===\"short\"){shellNav(\"short\")'\n    if 'if(!opened)shellNav(\"short\")' not in text and canonical_v331_short not in text:\n        raise RuntimeError('V328 Home Short action anchor missing')\n"""

OLD_V331="""        if anchor not in text:\n            raise RuntimeError('V331 Home editor panel anchor missing')\n"""
NEW_V331="""        if anchor not in text:\n            # V337_RESTART_SAFE_V331 — V343/V372 canonical shell owns this route on modern Home.\n            if 'GSF_SHELL_NAV' in text and 'target===\"editor\"' in text:\n                return text\n            raise RuntimeError('V331 Home editor panel anchor missing')\n"""


def patch_v328()->bool:
    if not TARGET.is_file():
        raise SystemExit('V337 V328 patch file missing')
    text=TARGET.read_text(encoding='utf-8')
    if MARK in text:
        return False
    if OLD not in text:
        raise RuntimeError('V337 V328 restart-safety anchor missing')
    text=text.replace(OLD,NEW,1)
    text=text.replace("ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')\n",
                      "ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')\n# V337_RESTART_SAFE_V328 — accept V331 canonical Short routing on reruns.\n",1)
    compile(text,str(TARGET),'exec')
    TARGET.write_text(text,encoding='utf-8')
    return True


def patch_v331()->bool:
    if not V331.is_file():
        raise SystemExit('V337 V331 patch file missing')
    text=V331.read_text(encoding='utf-8')
    if V331_MARK in text:
        return False
    if OLD_V331 not in text:
        raise RuntimeError('V337 V331 restart-safety anchor missing')
    text=text.replace(OLD_V331,NEW_V331,1)
    compile(text,str(V331),'exec')
    V331.write_text(text,encoding='utf-8')
    return True


def main():
    changed328=patch_v328()
    changed331=patch_v331()
    print(f'{MARK} applied_v328={changed328} {V331_MARK} applied_v331={changed331}',flush=True)

if __name__=='__main__':
    main()
