from pathlib import Path
import sys

app=Path(sys.argv[1] if len(sys.argv)>1 else "/app/GamingShortsFactory_V130_1_HOTFIX.py").read_text(encoding="utf-8")

required=[
    'st.session_state.pop("gsf_final_ready_sync_v111",None)',
    'st.button("SYNC SHORT READY",key="gsf_final_ready_sync_v111")',
    'if False and _v125_rank>0 and _v125_alternates:',
    'if False and _v130_pack.get("ready") and _v130_short:',
]
for marker in required:
    if marker not in app:
        raise SystemExit("V130.1 marker missing: "+marker)

bad='st.session_state["gsf_final_ready_sync_v111"]='
if bad in app:
    raise SystemExit("V130.1 forbidden direct sync-button assignment remains")

compile(app,"<v130.1>","exec")
print("V130.1 stability hotfix contracts: PASS")
