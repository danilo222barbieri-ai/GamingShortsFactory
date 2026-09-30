from pathlib import Path
import sys

sys.path.insert(0,"/app/web")

app=Path(sys.argv[1] if len(sys.argv)>1 else "/app/GamingShortsFactory_V124_AI_OS.py").read_text(encoding="utf-8")
server=Path("/app/web/direct_upload_server.py").read_text(encoding="utf-8")
brain=Path("/app/web/game_brain_v112.py").read_text(encoding="utf-8")
editor=Path("/app/web/editor_2027_component/index.html").read_text(encoding="utf-8")
apply_patch=Path("/app/web/apply_v124_ai_os.py").read_text(encoding="utf-8")

for marker in (
    "gsf_v124_director_context",
    "gsf_v124_social_pack",
    "GSF_V124_AI_DIRECTOR",
):
    if marker not in app:
        raise SystemExit("V124 app brain state marker missing: "+marker)

for marker in (
    "AI QUALITY CHECK",
    "gsf_v124_social_pack",
    "_gsf_v124_feedback",
    "_gsf_v124_moment_for_start",
    '"opened_editor"',
    '"published"',
    '_ai_title_key=f"social_title_{_slug}_{_ctx}"',
    'st.session_state[_ai_title_key]=_ai_title',
    'st.session_state[_ai_description_key]=_ai_description',
    'st.session_state[_ai_hashtags_key]=_ai_hashtags',
):
    if marker not in app:
        raise SystemExit("V124 app visible AI OS marker missing: "+marker)

for marker in (
    "from quality_control_v124 import inspect_final_video as _quality_inspect",
    "from guardian_intelligence_v124 import diagnose as _guardian_diagnose",
    'clean=="/quality/status"',
    "def _quality_schedule(",
    "GSF_V124_QUALITY",
    'path=="/ai/feedback"',
    "GSF_V124_FEEDBACK",
    '"quality_status"',
    '"guardian_diagnosis"',
):
    if marker not in server:
        raise SystemExit("V124 server AI OS marker missing: "+marker)

for marker in (
    "from ai_director_v124 import attach_director_plans, build_alternates",
    '"engine":"game-brain-v124-ai-director"',
    '"director_plan":dict(c.get("director_plan") or {})',
    '"alternates":[',
    '"event_time":',
):
    if marker not in brain:
        raise SystemExit("V124 Game Brain Director marker missing: "+marker)

for marker in (
    "function directorPlanFromBrain()",
    "APPLICA AI DIRECTOR",
    "state.aiMode='AI Director'",
    "edit.trim_start",
    "framing.smart_reframe",
    "style.audio_mode",
    "AI DIRECTOR APPLICATO",
):
    if marker not in editor:
        raise SystemExit("V124 Editor Director marker missing: "+marker)

for marker in (
    "GamingShortsFactory_V113_GUARDIAN.py",
    "GamingShortsFactory_V124_AI_OS.py",
    "V124 AI Director social optimizer",
    "V124 AI QUALITY UI",
):
    if marker not in apply_patch:
        raise SystemExit("V124 patch marker missing: "+marker)

compile(app,"<v124-app>","exec")
compile(server,"<v124-server>","exec")
compile(brain,"<v124-brain>","exec")

print("V124 AI OS integration contracts: PASS")
