from pathlib import Path
import ast
p=Path('/app/GamingShortsFactory_V104_4_SHARED_SOCIAL.py')
s=p.read_text(encoding='utf-8')
tree=ast.parse(s)
wanted={
    "_gsf_youtube_save_credentials",
    "_gsf_youtube_credentials",
    "_gsf_youtube_client_config",
    "_gsf_youtube_web_auth_url",
    "_gsf_youtube_web_complete",
    "_gsf_social_connection_status",
    "_gsf_process_oauth_callback",
}
print("GSF_YOUTUBE_INSPECT_BEGIN")
for n in tree.body:
    if isinstance(n,ast.FunctionDef) and n.name in wanted:
        print("###",n.name)
        print(ast.get_source_segment(s,n) or "")
        print("### END",n.name)
print("GSF_YOUTUBE_CONTEXT")
lines=s.splitlines()
for i in range(8825,9255):
    if i-1 < len(lines) and (
        "GSF_YOUTUBE_DIR" in lines[i-1] or
        "GSF_YOUTUBE_TOKEN" in lines[i-1] or
        "GSF_YOUTUBE_SCOPES" in lines[i-1]
    ):
        print(f"{i}: {lines[i-1]}")
print("GSF_YOUTUBE_INSPECT_END")
