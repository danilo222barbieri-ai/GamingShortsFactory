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

# App uses a per-browser persistent TikTok token, with legacy fallback intact.
need("def _gsf_shared_tiktok_load" in app,"TikTok persistent loader exists")
need("def _gsf_shared_tiktok_refresh" in app,"TikTok token refresh exists")
need('social-connections/{GSF_SESSION_ID}/tiktok.json' in app,"TikTok token is scoped to the browser session id")
need("def _gsf_tiktok_credentials_legacy" in app,"legacy TikTok auth fallback preserved")
need("return token,_gsf_app_credentials()" in app,"persistent token feeds existing app auth")
need('href="/social-connect"' in app,"Social Connect footer link present")

# Final render quality contract remains untouched.
tree=ast.parse(app)
core=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=="_gsf_render_core")
pairs=[]
for node in ast.walk(core):
    if isinstance(node,ast.List):
        vals=[e.value if isinstance(e,ast.Constant) else None for e in node.elts]
        for i in range(len(vals)-1):
            if isinstance(vals[i],str) and isinstance(vals[i+1],str):
                pairs.append((vals[i],vals[i+1]))
need(("-threads","1") in pairs,"memory-safe one-thread render preserved")
need(("-crf","14") in pairs,"CRF 14 preserved")
need(("-preset","medium") in pairs,"preset medium preserved")
need(("-fpsmax","60") in pairs,"60 fps cap preserved")

# Nginx exposes the connector without requiring a loaded Streamlit session.
need("location = /social-connect" in nginx,"exact /social-connect route exists")
need("location /social-connect/" in nginx,"social-connect subroutes exist")
need("127.0.0.1:8502" in nginx,"social connector bypasses Streamlit")
need("location = /" in nginx,"root callback interception exists")
need("@gsf_tiktok_oauth_callback" in nginx,"TikTok callback named route exists")
need("gsfsc_" in nginx,"only standalone OAuth states are intercepted")
need("X-GSF-Session-ID" in nginx,"browser session id is forwarded to connector")
need("Max-Age=31536000" in nginx,"stable browser id cookie enabled")

# Connector is public but per-browser; no secret URL key is exposed.
need('"/social-connect/tiktok/start"' in server,"TikTok start endpoint exists")
need('"/social-connect/tiktok/callback"' in server,"TikTok callback endpoint exists")
need("SOCIAL_CONNECT_KEY" not in server,"no secret query key required")
need('f"social-connections/{sid}/tiktok.json"' in server,"TikTok token stored per browser id")
need("tiktok_token.json" in server and "tiktok_config.json" in server,"callback writes app-compatible TikTok files")
need("https://www.tiktok.com/v2/auth/authorize/" in server,"official TikTok authorize endpoint used")
need("https://open.tiktokapis.com/v2/oauth/token/" in server,"official TikTok token endpoint used")
need('"scope":"user.info.basic,video.publish"' in server,"required TikTok scopes requested")
need("redirect_uri=PUBLIC_APP_URL" in server,"existing registered root redirect URI is reused")
need('state="gsfsc_"+' in server,"standalone OAuth state is namespaced")
need("Collega i social" in server,"no-video social connector page exists")

print("V104.4 per-browser Social Connect: PASS")
