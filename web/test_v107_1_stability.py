from pathlib import Path
import ast
import sys

p=Path(sys.argv[1] if len(sys.argv)>1 else "/app/GamingShortsFactory_V107_1_STABILITY.py")
s=p.read_text(encoding="utf-8")
tree=ast.parse(s)

checks={
    "preview byte cache released": '"gsf_ai_preview_cache_v71"' in s,
    "selected preview bytes released": '"preview_bytes"' in s,
    "publication preview bytes released": '"publication_preview_bytes"' in s,
    "final master byte cache released": '"gsf_final_master_cache_v44"' in s,
    "temporary preview aliases released": '"_mini_preview_bytes"' in s and '"_card_bytes"' in s,
    "short render-lock wait": '_GSF_V106_RENDER_LOCK.acquire(timeout=15.0)' in s,
    "no session final MP4 byte cache": 'cache=st.session_state.setdefault("gsf_final_master_cache_v44",{})' not in s,
    "manual source not duplicated into publication preview": '_gsf_manual_preview_bytes=video.getvalue()' not in s,
    "pre-render memory telemetry": "GSF_PRE_RENDER_MEMORY" in s,
    "preview QSV is hardware-gated": 'Path("/dev/dri/renderD128").exists()' in s,
    "preview x264 is one-thread bounded": '"-threads","1"' in s,
}
missing=[name for name,ok in checks.items() if not ok]
if missing:
    raise SystemExit("V107.1 stability contract failed: "+", ".join(missing))

# Every recipe/render function must still compile after the memory rewrite.
compile(s,str(p),"exec")
for name in ("_gsf_v93_release_analysis_memory","_gsf_v106_run_render_locked","_gsf_render_auto_master"):
    if not any(isinstance(n,ast.FunctionDef) and n.name==name for n in tree.body):
        raise SystemExit("V107.1 stability contract missing function: "+name)

print("V107.1 memory/stability contract: PASS")
