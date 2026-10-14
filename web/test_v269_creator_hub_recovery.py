from pathlib import Path
import shutil
import subprocess

app_root = Path("/app")
root = app_root / "web"
hub=(root/"creator_hub_v156_component/index.html").read_text(encoding="utf-8")
ng=(root/"nginx.conf.template").read_text(encoding="utf-8")

checks={
 "V269 visual recovery exists":"V269 CREATOR HUB RECOVERY" in hub,
 "Folder cards restored":"background:rgba(255,255,255,.86)!important" in hub and "border-radius:20px!important" in hub,
 "Folder icons restored":"#hub .folderIcon{" in hub and 'data-folder="profile"' in hub and 'data-folder="projects"' in hub and 'data-folder="live"' in hub,
 "Folder click handlers use querySelectorAll":'$$(".folder").forEach' in hub,
 "Live folder handlers use querySelectorAll":'$$("[data-live-folder]").forEach' in hub and '$$("[data-live-mini]").forEach' in hub,
 "No broken collection handlers remain":'\n $("[data-live-folder]").forEach' not in hub and '\n $("[data-live-mini]").forEach' not in hub and '\n $(".folder").forEach' not in hub,
 "State load still starts":'openView("dashboard");loadState();' in hub,
 "Profile fetch retained":'fetch("/creator-hub/state"' in hub,
 "Profile save retained":'fetch("/creator-hub/profile"' in hub,
 "Creator Hub action proxy exists":"V269 Creator Hub action routes" in ng and "location /creator-hub/" in ng,
 "Creator Hub proxy forwards session":"proxy_set_header X-GSF-Session-ID $gsf_session_cookie;" in ng,
}
for name,ok in checks.items():
    print(("PASS" if ok else "FAIL")+": "+name)
bad=[name for name,ok in checks.items() if not ok]
if bad:
    raise SystemExit("V269 Creator Hub recovery failed: "+", ".join(bad))
print("V269 Creator Hub recovery: PASS")

# V404 production build hook. Dockerfile already executes this test late in the
# image build. Preserve the historical startup as a fallback, materialize the
# runtime migration chain once, then replace only the image copy of start_web
# with the minimal startup path. The repository source remains unchanged.
materializer = root / "materialize_runtime_patches.sh"
legacy_start = root / "start_web.sh"
legacy_backup = root / "start_web_legacy.sh"
fast_start = root / "start_web_fast.sh"
if app_root.is_dir() and materializer.is_file() and fast_start.is_file():
    shutil.copyfile(legacy_start, legacy_backup)
    subprocess.run(["/bin/sh", str(materializer)], check=True)
    if not (app_root / ".gsf-ui-materialized").is_file():
        raise SystemExit("V404 materialization marker missing after build hook")
    shutil.copyfile(fast_start, legacy_start)
    baked = legacy_start.read_text(encoding="utf-8")
    if "V404 fast startup" not in baked or "fix_v312_global_navigation.py" in baked:
        raise SystemExit("V404 fast startup was not baked correctly")
    print("V404 build hook + fast startup bake: PASS")
