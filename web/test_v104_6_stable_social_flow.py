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

# In-app OAuth must not replace the prepared Streamlit page anymore.
need('st.session_state["social_auth_url_v77"] = "/social-connect"' in app,
     "unconnected social routes to standalone connector")
need('target="_blank"' in app and 'href="/social-connect"' in app,
     "social connection opens in a new tab")
need('_gsf_social_web_auth_url(_platform)' not in app,
     "in-app direct OAuth launch removed")
need("Il video pronto resta aperto e non viene azzerato." in app,
     "UI explains preserved prepared video")
need('st.session_state.pop("social_auth_url_v77",None)' in app,
     "stale social auth state cleared after connection")

# All three platforms share the same persistent-browser model.
need("def _gsf_shared_tiktok_load" in app,"TikTok persistent bridge preserved")
need("def _gsf_shared_youtube_load" in app,"YouTube persistent bridge preserved")
need("def _gsf_shared_instagram_load" in app,"Instagram persistent bridge exists")
need('social-connections/{GSF_SESSION_ID}/instagram.json' in app,
     "Instagram connection scoped to browser")
need("_gsf_shared_instagram_save(_payload)" in app,
     "Instagram connect persists to shared storage")

# TikTok unaudited clients automatically retry SELF_ONLY.
need("unaudited_client_can_only_post_to_private_accounts" in app,
     "TikTok unaudited fallback exists")
need('privacy="SELF_ONLY"' in app,"TikTok SELF_ONLY fallback exists")

# Standalone page offers all 3 connectors and a close-tab return path.
for social in ("TikTok","YouTube","Instagram"):
    need(f"✅ {social} collegato" in server,f"{social} connected status rendered")
    need(f'href="/social-connect/{social.lower()}/start"' in server,
         f"{social} standalone connect button exists")
need('onclick="window.close()"' in server,"connector can close back to original app tab")
need("Gaming Shorts Factory resta aperta nell'altra scheda" in server,
     "connector explicitly preserves original app tab")

# Instagram OAuth prepared; if Meta env vars are absent it fails in-place, never resets app.
need('META_APP_ID=_env_first("GSF_META_APP_ID"' in server,"Meta app id read from server")
need('META_APP_SECRET=_env_first("GSF_META_APP_SECRET"' in server,"Meta app secret read from server")
need('state="gsfig_"+' in server,"Instagram OAuth state namespaced")
need('"/social-connect/instagram/start"' in server,"Instagram start endpoint exists")
need('"/social-connect/instagram/callback"' in server,"Instagram callback endpoint exists")
need('f"social-connections/{sid}/instagram.json"' in server,
     "Instagram token stored per browser")

# OAuth successes land back on Social Connect, not the app root.
need(server.count('_redirect(handler,"/social-connect")') >= 3,
     "all successful OAuth callbacks return to Social Connect")

# Nginx diverts only namespaced provider callbacks.
need("@gsf_tiktok_oauth_callback" in nginx and "^gsfsc_" in nginx,
     "TikTok callback interception preserved")
need("@gsf_youtube_oauth_callback" in nginx and "^gsfyt_" in nginx,
     "YouTube callback interception preserved")
need("@gsf_instagram_oauth_callback" in nginx and "^gsfig_" in nginx,
     "Instagram callback interception added")
need("rewrite ^ /social-connect/instagram/callback break;" in nginx,
     "Instagram callback routes to standalone connector")

# Frozen final render contract remains unchanged.
tree=ast.parse(app)
core=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=="_gsf_render_core")
pairs=[]
for node in ast.walk(core):
    if isinstance(node,ast.List):
        vals=[e.value if isinstance(e,ast.Constant) else None for e in node.elts]
        for i in range(len(vals)-1):
            if isinstance(vals[i],str) and isinstance(vals[i+1],str):
                pairs.append((vals[i],vals[i+1]))
need(("-threads","1") in pairs,"memory-safe render preserved")
need(("-crf","14") in pairs,"CRF 14 preserved")
need(("-preset","medium") in pairs,"preset medium preserved")
need(("-fpsmax","60") in pairs,"60 fps cap preserved")

print("V104.6 Stable Social Flow: PASS")
