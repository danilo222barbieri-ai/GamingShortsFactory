from pathlib import Path
import sys

p=Path(sys.argv[1])
s=p.read_text(encoding='utf-8')
compile(s,str(p),'exec')

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print('PASS:',msg)

need('Gaming Shorts Factory · V104.2 Mobile Spacing' in s,'V104.2 marker')
need('gsf-section-gap-final' in s,'final-short section gap present')
need('gsf-section-gap-social' in s,'social section gap present')
need('height:30px' in s,'mobile section gap is 30px')
need('Crea lo Short finale' in s,'final-short title preserved')
need('Pubblicazione diretta' in s,'direct-publication title preserved')
need('_gsf_tiktok_direct_post(bytes(video), pack)' in s,'TikTok direct publishing preserved')
need('_gsf_instagram_publish_reel_auto(bytes(video), pack)' in s,'Instagram direct publishing preserved')
need('_gsf_youtube_upload(' in s,'YouTube publishing preserved')
need('GSF_FINAL_RENDER_START' in s,'render diagnostics preserved')
need('"-crf","14"' in s and '"-preset","medium"' in s,'render quality preserved')
print('V104.2 Mobile Spacing regression: PASS')
