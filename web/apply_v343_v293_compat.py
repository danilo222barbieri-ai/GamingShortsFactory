#!/usr/bin/env python3
from pathlib import Path

SRC=Path('/app/web/apply_v293_render_memory_guard.py')
if not SRC.is_file():
    raise SystemExit('V343/V293 source missing')

text=SRC.read_text(encoding='utf-8')

project_anchor='''    shell = APP_SRC.read_text(encoding="utf-8")\n    target = "/creator-hub-v156/?v=3115&ui=projects-ref-2"\n'''
project_replacement='''    shell = APP_SRC.read_text(encoding="utf-8")\n    if "GSF_GLOBAL_SHELL_V343" in shell:\n        print("V311 project pages reference: V343 owns shell route", flush=True)\n        return\n    target = "/creator-hub-v156/?v=3115&ui=projects-ref-2"\n'''
if text.count(project_anchor)!=1:
    raise RuntimeError(f'V343/V293 project-reference anchor count={text.count(project_anchor)}')
text=text.replace(project_anchor,project_replacement,1)

gamebar_anchor='''    shell = APP_SRC.read_text(encoding="utf-8")\n\n    def set_attr(button, name, value):\n'''
gamebar_replacement='''    shell = APP_SRC.read_text(encoding="utf-8")\n    if "GSF_GLOBAL_SHELL_V343" in shell:\n        print("Game Bar routes normalized: V343 canonical shell owns routing", flush=True)\n        return\n\n    def set_attr(button, name, value):\n'''
if text.count(gamebar_anchor)!=1:
    raise RuntimeError(f'V343/V293 gamebar anchor count={text.count(gamebar_anchor)}')
text=text.replace(gamebar_anchor,gamebar_replacement,1)

compile(text,str(SRC),'exec')
ns={'__name__':'__main__','__file__':str(SRC)}
exec(compile(text,str(SRC),'exec'),ns,ns)

# V401: remove full-buffer fallback upload duplication after V293 materializes
# the final Streamlit runtime. The patch is intentionally idempotent because
# this compatibility bootstrap runs on every service restart.
from fix_v401_frontend_memory import patch_runtime_file
patch_runtime_file(Path('/app/GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py'))
