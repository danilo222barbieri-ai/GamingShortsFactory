from pathlib import Path

root = Path(__file__).resolve().parents[1]
req = (root / "requirements-web.txt").read_text(encoding="utf-8")
start = (root / "web" / "start_web.sh").read_text(encoding="utf-8")
v95_path = root / "GamingShortsFactory_V95_RENDER_TEXT_POLISH.py"
v95 = v95_path.read_text(encoding="utf-8") if v95_path.exists() else ""

checks = {
    "Streamlit compatibility pin": "streamlit==1.49.1" in req,
    "V95-V103 production lineage entrypoint": ("GamingShortsFactory_V95_RENDER_TEXT_POLISH.py" in start or "GamingShortsFactory_V98_EDITOR_POLISH.py" in start or "GamingShortsFactory_V98_1_EDITOR_HOTFIX.py" in start or "GamingShortsFactory_V98_2_UPLOAD_RECOVERY.py" in start or "GamingShortsFactory_V98_3_HOME_COMPACT.py" in start or "GamingShortsFactory_V98_4_EDITOR_CLEANUP.py" in start or "GamingShortsFactory_V98_5_STYLE_ONLY.py" in start or "GamingShortsFactory_V98_6_PLAYER_SIZES.py" in start or "GamingShortsFactory_V98_7_NEW_VIDEO_FIX.py" in start or "GamingShortsFactory_V98_8_UPLOAD_MEMORY_FIX.py" in start or "GamingShortsFactory_V98_9_DIRECT_UPLOAD.py" in start or "GamingShortsFactory_V98_10_SPEED_PASS1.py" in start or "GamingShortsFactory_V98_11_SPEED_ALL.py" in start or "GamingShortsFactory_V98_12_UPLOAD_64MB.py" in start or "GamingShortsFactory_V98_FINAL.py" in start or "GamingShortsFactory_V98_FINAL_6LANES.py" in start or "GamingShortsFactory_V99_AI_TURBO.py" in start or "GamingShortsFactory_V99_FINAL_ARCH.py" in start or "GamingShortsFactory_V100_SMART_REFRAME.py" in start or "GamingShortsFactory_V100_1_QUALITY_MOBILE.py" in start or "GamingShortsFactory_V100_2_MASTER_QUALITY.py" in start or "GamingShortsFactory_V100_3_NATIVE_CROP_HQ.py" in start or "GamingShortsFactory_V100_4_RENDER_STABLE.py" in start or "GamingShortsFactory_V100_5_MAX_UPLOAD.py" in start or "GamingShortsFactory_V100_6_FPS_GUARD.py" in start or "GamingShortsFactory_V100_7_MEMORY_SAFE_RENDER.py" in start or "GamingShortsFactory_V100_8_FAST_RENDER.py" in start or "GamingShortsFactory_V101_SUBTITLE_REFINEMENT.py" in start or "GamingShortsFactory_V102_SMART_HOOK.py" in start or "GamingShortsFactory_V103_FINAL_QUALITY.py" in start),
    "V95 generated artifact exists": bool(v95),
    "V95 render-text marker present": "V95 Render Text Polish" in v95,
    "approved player code remains present": "components" in v95 and "html" in v95,
}

failed = [name for name, ok in checks.items() if not ok]
for name, ok in checks.items():
    print(("PASS" if ok else "FAIL") + ": " + name)
if failed:
    raise SystemExit("V96 compatibility regression failed: " + ", ".join(failed))
print("V96 Streamlit compatibility regression: PASS")
