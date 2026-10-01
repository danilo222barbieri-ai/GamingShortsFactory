from pathlib import Path
p=Path("/app/web/director_orchestrator_v136.py")
assert p.exists()
src=p.read_text(encoding="utf-8")
for marker in ("build_director_evidence","build_frame_manifest","game_recognition","game_context","session_intelligence","cover_ai","privacy_visual_guard","retention_lab","creator_style_learning","audio_intelligence","publishing_intelligence","performance_learning","long_form_director","game_specific_director","readiness"):
    assert marker in src, marker
print("V136 Director orchestrator contracts: PASS")
