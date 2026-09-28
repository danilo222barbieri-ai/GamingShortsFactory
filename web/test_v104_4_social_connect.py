from pathlib import Path
import ast
import sys

app=Path(sys.argv[1]).read_text(encoding="utf-8")
nginx=Path(sys.argv[2]).read_text(encoding="utf-8")
server=Path(sys.argv[3]).read_text(encoding="utf-8")

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print("PASS:",msg)

ast.parse(app)
ast.parse(server)

need("def _gsf_shared_tiktok_load" in app,"shared TikTok token loader exists")
need("def _gsf_shared_tiktok_refresh" in app,"shared TikTok token refresh exists")
need('social-connections/tiktok.json' in app,"app reads persistent TikTok token")
need("def _gsf_tiktok_credentials_legacy" in app,"legacy TikTok auth fallback preserved")
need("return token,_gsf_app_credentials()" in app,"shared token feeds existing app auth")

need("location /social-connect/" in nginx,"nginx social-connect route exists")
need("127.0.0.1:8502" in nginx,"social-connect bypasses Streamlit")

need('"/social-connect/tiktok/start"' in server,"TikTok start endpoint exists")
need('"/social-connect/tiktok/callback"' in server,"TikTok callback endpoint exists")
need("GSF_SOCIAL_CONNECT_KEY" in server,"social-connect admin key required")
need("https://www.tiktok.com/v2/auth/authorize/" in server,"official TikTok authorize endpoint used")
need("https://open.tiktokapis.com/v2/oauth/token/" in server,"official TikTok token endpoint used")
need("user.info.basic,video.publish" in server,"required TikTok scopes requested")
need("social-connections/tiktok.json" in server,"TikTok token stored persistently")
need("client_secret" in server and "TIKTOK_CLIENT_SECRET" in server,"client secret kept server-side")

print("V104.4 standalone social connect: PASS")
