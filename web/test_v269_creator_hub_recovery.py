from pathlib import Path

root=Path("/app")/"web"
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
