#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
TARGET=ROOT/'web/fix_v328_global_balance.py'
MARK='V337_RESTART_SAFE_V328'

OLD="""    if old in text:text=text.replace(old,new,1)\n    elif 'if(!opened)shellNav(\"short\")' not in text: raise RuntimeError('V328 Home Short action anchor missing')\n"""
NEW="""    if old in text:text=text.replace(old,new,1)\n    canonical_v331_short='if(action===\"short\"){shellNav(\"short\")'\n    if 'if(!opened)shellNav(\"short\")' not in text and canonical_v331_short not in text:\n        raise RuntimeError('V328 Home Short action anchor missing')\n"""


def main():
    if not TARGET.is_file():
        raise SystemExit('V337 V328 patch file missing')
    text=TARGET.read_text(encoding='utf-8')
    if MARK in text:
        print(f'{MARK} already applied',flush=True)
        return
    if OLD not in text:
        raise RuntimeError('V337 V328 restart-safety anchor missing')
    text=text.replace(OLD,NEW,1)
    # Put an explicit marker outside the embedded JavaScript strings.
    text=text.replace("ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')\n",
                      "ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')\n# V337_RESTART_SAFE_V328 — accept V331 canonical Short routing on reruns.\n",1)
    compile(text,str(TARGET),'exec')
    TARGET.write_text(text,encoding='utf-8')
    print(f'{MARK} applied',flush=True)

if __name__=='__main__':
    main()
