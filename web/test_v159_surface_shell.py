from pathlib import Path
root=Path("/app")
home=(root/"web/home_v154_component/index.html").read_text(encoding="utf-8")
share=(root/"web/share_v156_component/index.html").read_text(encoding="utf-8")
hub=(root/"web/creator_hub_v156_component/index.html").read_text(encoding="utf-8")
nginx=(root/"web/nginx.conf.template").read_text(encoding="utf-8")
server=(root/"web/direct_upload_server.py").read_text(encoding="utf-8")
apply=(root/"web/apply_v154_structural_home.py").read_text(encoding="utf-8")
checks={
    "Home component has no visible literal newline blocker":"\\n function parentClick" not in home,
    "Home social navigation uses shell":'shellNav("social")' in home,
    "Share surface uses live state":'fetch("/share/state"' in share,
    "Share uses real final URL":'video_url' in share and 'mini.classList.add("ready")' in share,
    "Hub routes Social into shell":'target:"social"' in hub,
    "Nginx serves share surface":"location /share-v156/" in nginx,
    "Nginx proxies share state":"location = /share/state" in nginx,
    "Nginx proxies final media":"location = /share/final" in nginx,
    "Server exposes share state":'if clean=="/share/state":' in server,
    "Server exposes final redirect":'if clean=="/share/final":' in server,
    "Production shell owns Social overlay":"gsf-social-overlay-v159" in apply,
}
bad=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(("PASS" if v else "FAIL")+": "+k)
if bad: raise SystemExit("V159 surface shell failed: "+", ".join(bad))
print("V159 persistent Social surface contract: PASS")
