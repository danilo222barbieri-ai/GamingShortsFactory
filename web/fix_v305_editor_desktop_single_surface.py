#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path('/app')
EDITOR = ROOT / 'web' / 'editor_2027_component' / 'index.html'
EMBED = ROOT / 'web' / 'editor_2027_embed.py'
MARK = '/* V305 EDITOR DESKTOP SINGLE SURFACE */'

CSS = r'''
/* V305 EDITOR DESKTOP SINGLE SURFACE */
@media (min-width:901px){
  html,body{height:100%;min-height:0;margin:0;overflow:hidden}
  #ng27:not(.gsfFullscreen):not(.gsfFullscreenFallback):not(:fullscreen){
    width:100%!important;
    height:100%!important;
    min-height:0!important;
    max-height:100%!important;
    margin:0!important;
    padding:0 18px 6px!important;
    border-radius:24px!important;
    overflow:hidden!important;
    display:flex!important;
    align-items:stretch!important;
    justify-content:center!important;
    background:radial-gradient(circle at 16% 8%,rgba(128,217,255,.12),transparent 24%),radial-gradient(circle at 84% 8%,rgba(117,230,195,.10),transparent 24%),linear-gradient(180deg,#FEFFFF 0%,#F8FCFF 100%)!important;
  }
  #ng27:not(.gsfFullscreen):not(.gsfFullscreenFallback):not(:fullscreen) .shell{
    width:100%!important;
    max-width:980px!important;
    height:100%!important;
    min-height:0!important;
    margin:0 auto!important;
    padding:0 8px 6px!important;
    overflow:hidden!important;
    display:flex!important;
    flex-direction:column!important;
    justify-content:center!important;
  }
  #ng27:not(.gsfFullscreen):not(.gsfFullscreenFallback):not(:fullscreen) .topline{
    position:absolute!important;
    top:8px!important;
    right:10px!important;
    z-index:60!important;
    width:auto!important;
    padding:0!important;
  }
  #ng27:not(.gsfFullscreen):not(.gsfFullscreenFallback):not(:fullscreen) .topline:before{content:none!important}
  #ng27:not(.gsfFullscreen):not(.gsfFullscreenFallback):not(:fullscreen) .gsfGuide{display:none!important}
  #ng27:not(.gsfFullscreen):not(.gsfFullscreenFallback):not(:fullscreen) .cockpit{
    width:100%!important;
    max-width:760px!important;
    height:100%!important;
    min-height:0!important;
    margin:0 auto!important;
    padding:8px 14px 10px!important;
    display:grid!important;
    grid-template-columns:88px minmax(300px,420px) 88px!important;
    justify-content:center!important;
    align-items:center!important;
    gap:18px!important;
    border-radius:26px!important;
    border:1px solid rgba(153,189,216,.16)!important;
    background:rgba(255,255,255,.42)!important;
    box-shadow:0 16px 42px rgba(62,102,139,.06),inset 0 1px 0 rgba(255,255,255,.92)!important;
  }
  #ng27:not(.gsfFullscreen):not(.gsfFullscreenFallback):not(:fullscreen) .stageWrap{
    width:100%!important;
    height:100%!important;
    min-height:0!important;
    display:flex!important;
    flex-direction:column!important;
    align-items:center!important;
    justify-content:center!important;
  }
  #ng27:not(.gsfFullscreen):not(.gsfFullscreenFallback):not(:fullscreen) .stage.r916,
  #ng27:not(.gsfFullscreen):not(.gsfFullscreenFallback):not(:fullscreen).expanded .stage.r916{
    height:calc(100% - 104px)!important;
    width:auto!important;
    max-height:680px!important;
    max-width:390px!important;
    min-height:0!important;
    aspect-ratio:9/16!important;
    border-radius:22px!important;
    overflow:hidden!important;
    background:linear-gradient(180deg,#111D28 0%,#08111A 100%)!important;
    border:1px solid rgba(126,189,223,.28)!important;
    box-shadow:0 18px 46px rgba(38,72,104,.18),inset 0 1px 0 rgba(255,255,255,.08)!important;
  }
  #ng27:not(.gsfFullscreen):not(.gsfFullscreenFallback):not(:fullscreen) video{background:#0B141D!important}
  #ng27:not(.gsfFullscreen):not(.gsfFullscreenFallback):not(:fullscreen) .rail,
  #ng27:not(.gsfFullscreen):not(.gsfFullscreenFallback):not(:fullscreen).expanded .rail{
    width:88px!important;
    gap:8px!important;
    align-self:center!important;
  }
  #ng27:not(.gsfFullscreen):not(.gsfFullscreenFallback):not(:fullscreen) .railBtn,
  #ng27:not(.gsfFullscreen):not(.gsfFullscreenFallback):not(:fullscreen).expanded .railBtn{
    width:76px!important;
    height:60px!important;
    min-width:76px!important;
    min-height:60px!important;
    border-radius:15px!important;
  }
  #ng27:not(.gsfFullscreen):not(.gsfFullscreenFallback):not(:fullscreen) .railBtn .ico{width:22px!important;height:22px!important}
  #ng27:not(.gsfFullscreen):not(.gsfFullscreenFallback):not(:fullscreen) .railBtn span{font-size:8.8px!important;letter-spacing:.055em!important}
  #ng27:not(.gsfFullscreen):not(.gsfFullscreenFallback):not(:fullscreen) .timeline,
  #ng27:not(.gsfFullscreen):not(.gsfFullscreenFallback):not(:fullscreen).expanded .timeline{
    width:100%!important;
    max-width:420px!important;
    margin:8px auto 0!important;
    padding:7px 9px!important;
    border-radius:15px!important;
    border:1px solid rgba(151,187,216,.22)!important;
    background:rgba(255,255,255,.78)!important;
    box-shadow:0 8px 20px rgba(72,110,148,.06),inset 0 1px 0 rgba(255,255,255,.95)!important;
  }
  #ng27:not(.gsfFullscreen):not(.gsfFullscreenFallback):not(:fullscreen) .captionPreview{width:84%!important;font-size:clamp(24px,2vw,32px)!important}
  #ng27:not(.gsfFullscreen):not(.gsfFullscreenFallback):not(:fullscreen) .footNote{display:none!important}
}
/* END V305 EDITOR DESKTOP SINGLE SURFACE */
'''


def main():
    if not EDITOR.is_file() or not EMBED.is_file():
        raise RuntimeError('V305 required Editor files missing')

    html = EDITOR.read_text(encoding='utf-8')
    if MARK not in html:
        if '</style>' not in html:
            raise RuntimeError('V305 Editor style anchor missing')
        html = html.replace('</style>', CSS + '\n</style>', 1)

    html, count = re.subn(
        r'data-editor-build="[^"]+"',
        'data-editor-build="2027.6-v305"',
        html,
        count=1,
    )
    if count != 1:
        raise RuntimeError('V305 Editor build anchor missing')
    EDITOR.write_text(html, encoding='utf-8')

    embed = EMBED.read_text(encoding='utf-8')
    if '"gsf_editor_2027_v305"' not in embed:
        embed, count = re.subn(
            r'"gsf_editor_2027_v\d+"',
            '"gsf_editor_2027_v305"',
            embed,
            count=1,
        )
        if count != 1:
            raise RuntimeError('V305 editor cache key anchor missing')
        EMBED.write_text(embed, encoding='utf-8')

    print('V305 editor desktop single-surface: PASS', flush=True)


if __name__ == '__main__':
    main()
