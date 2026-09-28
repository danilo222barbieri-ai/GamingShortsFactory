from pathlib import Path
import ast,sys

p=Path(sys.argv[1])
s=p.read_text(encoding='utf-8')
compile(s,str(p),'exec')
tree=ast.parse(s)

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print('PASS:',msg)

core_node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_gsf_render_core')
core=ast.get_source_segment(s,core_node) or ''

need('Gaming Shorts Factory · V104.1 Render Diagnostics' in s,'V104.1 marker')
need('GSF_FINAL_RENDER_START' in core,'render start diagnostic')
need('GSF_FINAL_RENDER_EXIT' in core,'render exit diagnostic')
need('GSF_FINAL_RENDER_TIMEOUT' in core,'timeout diagnostic')
need('GSF_FINAL_RENDER_EXCEPTION' in core,'exception diagnostic')
need('GSF_FINAL_RENDER_VALIDATION_FAIL' in core,'validator diagnostic')
need('GSF_FINAL_RENDER_FAIL' in core,'ffmpeg failure diagnostic')
need('except subprocess.TimeoutExpired as e:' in core,'timeout is captured explicitly')

# Diagnostics must not alter V103/V104 production quality or timeout settings.
need('"-preset","medium"' in core,'medium preset unchanged')
need('"-crf","14"' in core,'CRF14 unchanged')
need('"-threads","2"' in core,'two render threads unchanged')
need('rc-lookahead=16:ref=2:bframes=2' in core,'x264 memory bounds unchanged')
need('"-profile:v","high"' in core and '"-level:v","4.2"' in core,'H.264 profile unchanged')
need('"-pix_fmt","yuv420p"' in core,'pixel format unchanged')
need('"-fpsmax","60"' in core,'fps ceiling unchanged')
need('scale=1080:1920:flags=lanczos' in s,'1080x1920 Smart Reframe unchanged')
need('_diag_timeout=max(420.0,min(3600.0,duration*36.0))' in core,'existing timeout formula unchanged')
need('_gsf_validate_social_master(output_path,fmt=fmt)' in core,'social master validation unchanged')

# V104 direct-social paths remain present.
need('_gsf_tiktok_direct_post(bytes(video), pack)' in s,'TikTok direct post preserved')
need('_gsf_instagram_publish_reel_auto(bytes(video), pack)' in s,'Instagram direct Reel preserved')
need('_gsf_youtube_upload(' in s,'YouTube upload preserved')
need('st.session_state["hook_enabled_v102"]=False' in s,'hook remains disabled')

print('V104.1 Render Diagnostics regression: PASS')
