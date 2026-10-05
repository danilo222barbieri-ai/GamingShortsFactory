from pathlib import Path
import ast, re, sys

APP=Path(sys.argv[1])
SHARE=Path(sys.argv[2])
SERVER=Path(sys.argv[3])
NGINX=Path(sys.argv[4])

app=APP.read_text(encoding='utf-8')
share=SHARE.read_text(encoding='utf-8')
server=SERVER.read_text(encoding='utf-8')
nginx=NGINX.read_text(encoding='utf-8')


def need(name, ok):
    print(('PASS' if ok else 'FAIL')+': '+name)
    if not ok:
        raise AssertionError(name)

need('generated app parses', bool(ast.parse(app)))
need('upload backend still mounted', 'direct_upload' in app.lower() or 'upload_complete' in app)
need('AI three-moment flow present', 'numero_clip=3' in app and ('best' in app or 'action' in app))
need('final short render control present', 'crea short finale' in app.lower() or 'create_final_short' in app.lower())
need('YouTube publish implementation present', 'def _gsf_youtube_upload' in app)
need('TikTok direct publish implementation present', 'def _gsf_tiktok_direct_post' in app and '_gsf_tiktok_direct_post(bytes(video), pack)' in app)
need('Instagram reel publish implementation present', 'def _gsf_instagram_publish_reel_auto' in app and '/media_publish' in app)
need('publish loop covers YouTube TikTok Instagram', all(x in app for x in ('YouTube','TikTok','Instagram')) and '_gsf_publish' in app)

need('V289 share surface present', 'V289 SHARE FINAL' in share or 'Condividi o scarica' in share)
need('share has no visible video element', '<video' not in share.split('<script>',1)[0].lower())
need('share state endpoint wired', 'fetch("/share/state"' in share)
need('share final fallback wired', 'a.href="/share/final"' in share)
need('share parent social bridge wired', 'parentClick([key])' in share)

need('share state backend exists', '"/share/state"' in server)
need('share final backend exists', '"/share/final"' in server)
need('TikTok OAuth and direct scopes exist', 'video.publish' in server and '/social-connect/tiktok/start' in server)
need('YouTube OAuth upload scope exists', 'youtube.upload' in server and '/social-connect/youtube/start' in server)
need('Instagram OAuth endpoint exists', '/social-connect/instagram/start' in server)
need('nginx routes share state', 'location = /share/state' in nginx)
need('nginx routes share final', 'location = /share/final' in nginx)
need('nginx routes social connect', 'location /social-connect' in nginx)

for platform in ('youtube','tiktok','instagram'):
    pattern=re.compile(r'.{0,220}'+platform+r'.{0,220}',re.I|re.S)
    snippets=pattern.findall(app)
    clickable=any(('st.button' in s or 'button(' in s or 'link_button' in s) for s in snippets)
    need(f'parent app exposes clickable {platform} control', clickable)

print('V290 FULL FLOW AUDIT: PASS')
