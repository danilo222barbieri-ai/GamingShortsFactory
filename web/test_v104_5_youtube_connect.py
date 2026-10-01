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

need("def _gsf_shared_youtube_load" in app,"YouTube persistent loader exists")
need("def _gsf_shared_youtube_save" in app,"YouTube persistent saver exists")
need('social-connections/{GSF_SESSION_ID}/youtube.json' in app,"YouTube token scoped to browser")
need('GSF_YOUTUBE_CLIENT_ID' in app and 'GSF_YOUTUBE_CLIENT_SECRET' in app,"Railway YouTube Web credentials supported")
need("def _gsf_youtube_credentials" in app,"existing YouTube credential flow preserved")
need("def _gsf_youtube_upload" in app,"existing YouTube direct upload preserved")

need('YOUTUBE_CLIENT_ID=_env_first("GSF_YOUTUBE_CLIENT_ID"' in server,"connector reads YouTube client ID")
need('YOUTUBE_CLIENT_SECRET=_env_first("GSF_YOUTUBE_CLIENT_SECRET"' in server,"connector reads YouTube client secret")
need('"/social-connect/youtube/start"' in server,"YouTube connect start endpoint exists")
need('"/social-connect/youtube/callback"' in server,"YouTube callback endpoint exists")
need("https://accounts.google.com/o/oauth2/v2/auth" in server,"official Google auth endpoint used")
need("https://oauth2.googleapis.com/token" in server,"official Google token endpoint used")
need("YOUTUBE_SCOPE=" in server and "https://www.googleapis.com/auth/youtube.upload" in server,"YouTube upload scope used")
need('f"social-connections/{sid}/youtube.json"' in server,"YouTube token stored per browser")
need("✅ YouTube collegato" in server,"Social Connect shows YouTube status")
need('href="/social-connect/youtube/start"' in server,"Social Connect has YouTube button")

need('error_page 419 = @gsf_youtube_oauth_callback;' in nginx,"YouTube root callback interception exists")
need('^gsfyt_' in nginx,"YouTube standalone OAuth state is namespaced")
need('rewrite ^ /social-connect/youtube/callback break;' in nginx,"YouTube callback routed to connector")

tree=ast.parse(app)
core=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=="_gsf_render_core")
pairs=[]
for node in ast.walk(core):
    if isinstance(node,ast.List):
        vals=[e.value if isinstance(e,ast.Constant) else None for e in node.elts]
        for i in range(len(vals)-1):
            if isinstance(vals[i],str) and isinstance(vals[i+1],str):
                pairs.append((vals[i],vals[i+1]))
need(("-threads","1") in pairs,"memory-safe final render preserved")
need(("-crf","14") in pairs,"CRF 14 preserved")
need(("-preset","medium") in pairs,"preset medium preserved")
need(("-fpsmax","60") in pairs,"60 fps cap preserved")

print("V104.5 YouTube Social Connect: PASS")
