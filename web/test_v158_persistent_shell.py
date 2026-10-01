from pathlib import Path

root=Path("/app")
checks={
    "nginx static hub route":"location /creator-hub-v156/" in (root/"web/nginx.conf.template").read_text(encoding="utf-8"),
    "nginx hub state API":"location = /creator-hub/state" in (root/"web/nginx.conf.template").read_text(encoding="utf-8"),
    "server hub state endpoint":'if clean=="/creator-hub/state":' in (root/"web/direct_upload_server.py").read_text(encoding="utf-8"),
    "hub shell messaging":'GSF_SHELL_NAV' in (root/"web/creator_hub_v156_component/index.html").read_text(encoding="utf-8"),
    "hub uses live state":'fetch("/creator-hub/state"' in (root/"web/creator_hub_v156_component/index.html").read_text(encoding="utf-8"),
    "production shell bridge":"gsf-v158-shell-bridge" in (root/"web/apply_v154_structural_home.py").read_text(encoding="utf-8"),
    "account project bucket":'creator-accounts/{account_id}/projects/' in (root/"web/project_state_v157.py").read_text(encoding="utf-8"),
}
bad=[name for name,ok in checks.items() if not ok]
for name,ok in checks.items():
    print(("PASS" if ok else "FAIL")+": "+name)
if bad:
    raise SystemExit("V158 shell contract failed: "+", ".join(bad))
print("V158 persistent shell contract: PASS")
