#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path('/app')
EDITOR = ROOT / 'web' / 'editor_2027_component' / 'index.html'
EMBED = ROOT / 'web' / 'editor_2027_embed.py'
MARK = '/* V305 DESKTOP EDITOR CLEANUP */'

CSS = r'''
/* V305 DESKTOP EDITOR CLEANUP */
@media (min-width:821px){
  #ng27{
    height:100dvh!important;
    min-height:640px!important;
    max-height:none!important;
    padding:10px 24px 8px!important;
    border-radius:28px!important;
    display:flex!important;
    align-items:stretch!important;
    justify-content:center!important;
    overflow:hidden!important;
    background:
      radial-gradient(circle at 16% 10%,rgba(126,214,255,.13),transparent 24%),
      radial-gradient(circle at 84% 10%,rgba(127,236,197,.11),transparent 24%),
      linear-gradient(180deg,#FEFFFF 0%,#F8FCFF 100%)!important;
  }
  #ng27 .shell{
    width:min(100%,1080px)!important;
    max-width:1080px!important;
    height:100%!important;
    margin:0 auto!important;
    padding:4px 12px 8px!important;
    display:flex!important;
    flex-direction:column!important;
    justify-content:flex-start!important;
    gap:4px!important;
    overflow:visible!important;
  }
  #ng27 .topline{
    flex:0 0 34px!important;
    min-height:34px!important;
    align-items:center!important;
    padding:0 8px 4px!important;
  }
  #ng27 .topline:before{
    font-size:13px!important;
    letter-spacing:.24em!important;
    color:#647D9B!important;
  }
  #ng27 .zoomEditorBtn{
    height:30px!important;
    padding:0 10px!important;
    border-radius:10px!important;
    font-size:8px!important;
  }
  #ng27 .cockpit{
    position:relative!important;
    flex:1 1 auto!important;
    min-height:0!important;
    width:100%!important;
    display:grid!important;
    grid-template-columns:96px minmax(300px,420px) 96px!important;
    justify-content:center!important;
    align-items:center!important;
    gap:20px!important;
    padding:10px 14px 12px!important;
    border-radius:28px!important;
    border:1px solid rgba(153,189,216,.18)!important;
    background:rgba(255,255,255,.44)!important;
    box-shadow:0 18px 46px rgba(62,102,139,.07),inset 0 1px 0 rgba(255,255,255,.92)!important;
  }
  #ng27 .stageWrap{
    width:100%!important;
    min-width:0!important;
    min-height:0!important;
    display:flex!important;
    flex-direction:column!important;
    align-items:center!important;
    justify-content:center!important;
  }
  #ng27 .stage.r916,
  #ng27.expanded .stage.r916{
    width:clamp(300px,calc((100dvh - 190px) * .5625),420px)!important;
    max-width:420px!important;
    min-width:0!important;
    aspect-ratio:9/16!important;
    border-radius:24px!important;
    overflow:hidden!important;
    background:linear-gradient(180deg,#111D28 0%,#08111A 100%)!important;
    border:1px solid rgba(126,189,223,.28)!important;
    box-shadow:0 18px 48px rgba(38,72,104,.20),inset 0 1px 0 rgba(255,255,255,.08)!important;
  }
  #ng27 video{background:#0B141D!important}
  #ng27 .rail,
  #ng27.expanded .rail{
    width:96px!important;
    gap:8px!important;
    align-self:center!important;
  }
  #ng27 .railBtn,
  #ng27.expanded .railBtn{
    width:82px!important;
    height:64px!important;
    min-width:82px!important;
    min-height:64px!important;
    padding:0 6px!important;
    border-radius:16px!important;
    border:1px solid rgba(151,187,216,.30)!important;
    background:rgba(255,255,255,.88)!important;
    box-shadow:0 8px 20px rgba(71,110,148,.09),inset 0 1px 0 rgba(255,255,255,.98)!important;
  }
  #ng27 .railBtn .ico,
  #ng27.expanded .railBtn .ico{width:23px!important;height:23px!important}
  #ng27 .railBtn span,
  #ng27.expanded .railBtn span{
    font-size:9px!important;
    line-height:1!important;
    letter-spacing:.06em!important;
  }
  #ng27 .timeline,
  #ng27.expanded .timeline{
    width:100%!important;
    max-width:420px!important;
    margin:10px auto 0!important;
    padding:8px 10px!important;
    border-radius:16px!important;
    border:1px solid rgba(151,187,216,.23)!important;
    background:rgba(255,255,255,.76)!important;
    box-shadow:0 9px 24px rgba(72,110,148,.07),inset 0 1px 0 rgba(255,255,255,.95)!important;
  }
  #ng27 .tlMeta{font-size:9px!important;margin-bottom:5px!important}
  #ng27 .track{height:28px!important}
  #ng27 .trimRow{font-size:9px!important;margin-top:6px!important}
  #ng27 .gsfGuide{display:none!important}
  #ng27 .drawer{
    left:12px!important;
    right:12px!important;
    bottom:12px!important;
    max-height:64%!important;
    overflow:auto!important;
    border-radius:18px!important;
  }
  #ng27 .captionPreview{
    width:84%!important;
    max-width:84%!important;
    font-size:clamp(24px,2.15vw,34px)!important;
  }
  #ng27 .footNote{
    flex:0 0 auto!important;
    margin-top:4px!important;
    font-size:8px!important;
    color:#7B90A4!important;
  }
}
@media (min-width:821px) and (max-height:700px){
  #ng27{min-height:580px!important;padding-top:6px!important}
  #ng27 .cockpit{padding-top:6px!important;padding-bottom:7px!important}
  #ng27 .stage.r916,
  #ng27.expanded .stage.r916{width:clamp(260px,calc((100dvh - 165px) * .5625),330px)!important}
  #ng27 .railBtn,
  #ng27.expanded .railBtn{height:56px!important;min-height:56px!important}
  #ng27 .timeline,
  #ng27.expanded .timeline{margin-top:6px!important;padding:6px 8px!important}
}
/* END V305 DESKTOP EDITOR CLEANUP */
'''


def main():
    if not EDITOR.is_file() or not EMBED.is_file():
        raise RuntimeError('V305 required Editor files missing')

    editor = EDITOR.read_text(encoding='utf-8')
    if MARK not in editor:
        if '</style>' not in editor:
            raise RuntimeError('V305 Editor style anchor missing')
        editor = editor.replace('</style>', CSS + '\n</style>', 1)

    editor, count = re.subn(
        r'data-editor-build="[^"]+"',
        'data-editor-build="2027.6-v305"',
        editor,
        count=1,
    )
    if count != 1:
        raise RuntimeError('V305 Editor build marker anchor missing')
    EDITOR.write_text(editor, encoding='utf-8')

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

    print('V305 desktop Editor cleanup: PASS', flush=True)


if __name__ == '__main__':
    main()
