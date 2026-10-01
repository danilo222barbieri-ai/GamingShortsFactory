from pathlib import Path
import sys
import ast

app_path=Path(sys.argv[1] if len(sys.argv)>1 else "/app/GamingShortsFactory_V130_2_STABILITY_UX.py")
s=app_path.read_text(encoding="utf-8")

required=[
    'gsf_v1302_new_video_confirm',
    '"SALVA BOZZA"',
    '"CONTINUA"',
    '"ANNULLA"',
    'st.session_state["gsf_v1302_social_open"]=True',
    'def _gsf_v1302_youtube_short_bytes(video_bytes):',
    'GSF_V1302_YOUTUBE_SHORT_NORMALIZED',
    'v1055_social_composer_shared',
    'gsf_v1302_target_youtube',
    'gsf_v1302_target_tiktok',
    'gsf_v1302_target_instagram',
    'gsf_v1302_publish_all',
    '_v1302_ai_social',
    '"published"',
    'CREO SHORT · IA Quality Check · Pronto',
    'SHORT PRONTO',
    'gsf-v1302-create-note',
    'gsf_v1302_icon_youtube',
    'gsf_v1302_save_share',
    '"SALVA / CONDIVIDI"',
    '[class*="st-key-gsf_share_download_top"]{display:none !important;}',
    '.gsf-v124-quality{display:none !important;',
    '.gsf-footer-v4 .bug-report',
    'position:static !important;',
    'display:flex;align-items:center;justify-content:center;text-align:center',
    'margin:-8px auto 0 !important;',
]
for marker in required:
    if marker not in s:
        raise SystemExit("V130.2 marker missing: "+marker)


# Validate the actual final renderer structurally; ast.unparse may choose either quote style.
_tree=ast.parse(s)
_core=next((n for n in _tree.body if isinstance(n,ast.FunctionDef) and n.name=="_gsf_render_core"),None)
if _core is None:
    raise SystemExit("V130.2 final render core missing")
_fast=0
for _node in ast.walk(_core):
    if isinstance(_node,ast.List):
        _elts=_node.elts
        for _i in range(len(_elts)-1):
            _a,_b=_elts[_i],_elts[_i+1]
            if isinstance(_a,ast.Constant) and _a.value=="-preset" and isinstance(_b,ast.Constant) and _b.value=="fast":
                _fast+=1
if _fast!=1:
    raise SystemExit("V130.2 final renderer fast preset contract failed: "+str(_fast))

for forbidden in (
    'on_click=_gsf_start_new_video,',
    'st.session_state["gsf_final_ready_sync_v111"]=',
):
    if forbidden in s:
        raise SystemExit("V130.2 forbidden marker remains: "+forbidden)

# V130.1 redundant UI remains disabled behind the scenes.
if 'if False and _v125_rank>0 and _v125_alternates:' not in s:
    raise SystemExit("V130.2 alternatives backend/UI separation regressed")
if 'if False and _v130_pack.get("ready") and _v130_short:' not in s:
    raise SystemExit("V130.2 One Click backend/UI separation regressed")

compile(s,str(app_path),"exec")
print("V130.2 stability UX contracts: PASS")
