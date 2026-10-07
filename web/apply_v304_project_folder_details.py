#!/usr/bin/env python3
from pathlib import Path
import re
import runpy

ROOT=Path('/app')
ns=runpy.run_path(str(ROOT/'web/fix_v304_project_folder_details.py'),run_name='v304_library')
ns['patch_hub']()
ns['patch_server']()

app=ROOT/'GamingShortsFactory_V154_STRUCTURAL_HOME.py'
text=app.read_text(encoding='utf-8')
text,count=re.subn(r'/creator-hub-v156/\?v=\d+','/creator-hub-v156/?v=304',text)
if count<1 and '/creator-hub-v156/?v=304' not in text:
    raise RuntimeError('V304 Creator Hub cache anchor missing')
app.write_text(text,encoding='utf-8')
print('V304 Creator Hub cache key: v304',flush=True)
