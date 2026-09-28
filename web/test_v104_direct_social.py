from pathlib import Path
import ast,sys,re

p=Path(sys.argv[1])
s=p.read_text(encoding='utf-8')
compile(s,str(p),'exec')
tree=ast.parse(s)

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print('PASS:',msg)

need('Gaming Shorts Factory · V104 Direct Social' in s,'V104 marker')
need('Pubblicazione diretta' in s,'direct-publish UI label')
need('GSF_TIKTOK_DIRECT_INIT = "https://open.tiktokapis.com/v2/post/publish/video/init/"' in s,'TikTok Direct Post endpoint')
need('GSF_TIKTOK_CREATOR_INFO' in s,'TikTok creator-info endpoint')
need('user.info.basic,video.publish' in s,'TikTok video.publish OAuth scope')
need('Manca lo scope TikTok video.publish' in s,'TikTok connection requires direct-post scope')
need('_gsf_tiktok_direct_post(bytes(video), pack)' in s,'TikTok publish path uses Direct Post')
need('Completa il post dalla notifica/bozza TikTok' not in s,'TikTok draft hand-off removed from publish path')
need('Video pubblicato su TikTok' in s,'TikTok direct success message')
need('GSF_META_SCOPES = "pages_show_list,instagram_basic,instagram_content_publish,pages_read_engagement"' in s,'Instagram publish OAuth scopes')
need('def _gsf_instagram_web_auth_url' in s,'Instagram browser OAuth implemented')
need('def _gsf_instagram_web_complete' in s,'Instagram OAuth callback implemented')
need('elif platform == "Instagram":\n        ok, message = _gsf_instagram_web_complete' in s,'Instagram callback wired')
need('return _gsf_instagram_web_auth_url()' in s,'Instagram connect button uses OAuth')
need('_gsf_instagram_publish_reel_auto(bytes(video), pack)' in s,'Instagram direct Reel publishing preserved')
need('_gsf_youtube_upload(' in s,'YouTube direct API upload preserved')
need('prefs.setdefault("youtube_privacy","public")' in s,'YouTube direct publish defaults public')
need('st.success("✅ " + str(status.get("message")' in s,'social success reports real direct-publish result')

# No regressions outside V104 scope.
core=ast.get_source_segment(s,next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_gsf_render_core')) or ''
need('"-crf","14"' in core,'V103 render quality preserved')
need('"-preset","medium"' in core,'V103 render preset preserved')
need('"-threads","2"' in core,'V103 render speed preserved')
need('"-pix_fmt","yuv420p"' in core,'V103 pixel format preserved')
need('_gsf_refine_subtitle_words' in s,'V101 subtitles preserved')
need('st.session_state["hook_enabled_v102"]=False' in s,'hook remains disabled')
need('GSF_SMART_REFRAME_VERSION = "v100-gameplay-safe"' in s,'Smart Reframe preserved')
need('numero_clip=3' in s,'three AI clips preserved')
need('_profile="PLAYER 16:9"; _target_width=640; _max_vw="640px"; _cap=430' in s,'approved main player preserved')

# Static TikTok payload checks.
direct=ast.get_source_segment(s,next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_gsf_tiktok_direct_post')) or ''
for token in (
    '"post_info"', '"privacy_level"', '"source_info"', '"FILE_UPLOAD"',
    '"disable_comment"', '"disable_duet"', '"disable_stitch"',
    '"Content-Range"', 'PUBLIC_TO_EVERYONE', 'SELF_ONLY'
):
    need(token in direct,f'TikTok direct payload contains {token}')

# Instagram OAuth must discover a professional IG account via /me/accounts.
ig=ast.get_source_segment(s,next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_gsf_instagram_web_complete')) or ''
need('/me/accounts?' in ig,'Instagram OAuth discovers managed pages')
need('instagram_business_account' in ig,'Instagram OAuth resolves professional IG account')
need('_gsf_instagram_connect(ig_id,page_token)' in ig,'Instagram OAuth stores publish-capable account token')

print('V104 Direct Social regression: PASS')
