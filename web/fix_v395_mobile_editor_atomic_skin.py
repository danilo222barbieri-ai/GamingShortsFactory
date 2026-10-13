#!/usr/bin/env python3
from pathlib import Path
import sys

MARK='V395_MOBILE_EDITOR_ATOMIC_SKIN'

EDITOR_PATCH=r'''
<!-- V395_MOBILE_EDITOR_ATOMIC_SKIN -->
<style id="v395MobileEditorAtomicSkin">
@media(max-width:760px){
  #ng27{
    --v395-ink:#24557b;
    --v395-blue:#2f92ea;
    --v395-cyan:#63d8f2;
    --v395-glass:rgba(248,253,255,.88);
    --v395-line:rgba(76,165,216,.28);
  }
  #ng27 .stage.r916,#ng27.expanded .stage.r916{
    border:1px solid rgba(74,190,232,.48)!important;
    border-radius:25px!important;
    background:linear-gradient(180deg,#ddf5fc 0%,#edf9fd 58%,#f8fdff 100%)!important;
    box-shadow:0 12px 30px rgba(31,99,145,.16),inset 0 1px 0 rgba(255,255,255,.92)!important;
    isolation:isolate!important;
  }
  #ng27 .stage.r916:before,#ng27.expanded .stage.r916:before{
    content:""!important;position:absolute!important;inset:7px!important;z-index:165!important;pointer-events:none!important;
    border:0!important;border-radius:19px!important;opacity:.72!important;
    background:
      linear-gradient(90deg,var(--v395-cyan),var(--v395-cyan)) left top/14px 1px no-repeat,
      linear-gradient(180deg,var(--v395-cyan),var(--v395-cyan)) left top/1px 14px no-repeat,
      linear-gradient(90deg,var(--v395-cyan),var(--v395-cyan)) right top/14px 1px no-repeat,
      linear-gradient(180deg,var(--v395-cyan),var(--v395-cyan)) right top/1px 14px no-repeat,
      linear-gradient(90deg,var(--v395-cyan),var(--v395-cyan)) left bottom/14px 1px no-repeat,
      linear-gradient(180deg,var(--v395-cyan),var(--v395-cyan)) left bottom/1px 14px no-repeat,
      linear-gradient(90deg,var(--v395-cyan),var(--v395-cyan)) right bottom/14px 1px no-repeat,
      linear-gradient(180deg,var(--v395-cyan),var(--v395-cyan)) right bottom/1px 14px no-repeat!important;
    box-shadow:none!important;
  }
  #ng27 .stage.r916:after,#ng27.expanded .stage.r916:after{display:none!important}
  #ng27 .stage video,#ng27 .stage #videoBg,#ng27 .v393PosterFrame{border-radius:24px!important}

  #ng27 .v389UndoRedo #undoBtn,#ng27 .v389UndoRedo #redoBtn,
  #ng27 .v389TrimBtn,#ng27 .v389RatioBtn,#ng27 #zoomEditorBtn{
    height:32px!important;min-height:32px!important;border-radius:10px!important;
    border:1px solid var(--v395-line)!important;
    background:linear-gradient(160deg,rgba(255,255,255,.96),rgba(222,243,251,.88))!important;
    color:var(--v395-ink)!important;
    box-shadow:0 4px 12px rgba(35,93,133,.12),inset 0 1px 0 rgba(255,255,255,.96)!important;
    -webkit-backdrop-filter:blur(12px) saturate(1.12)!important;backdrop-filter:blur(12px) saturate(1.12)!important;
  }
  #ng27 .v389UndoRedo #undoBtn,#ng27 .v389UndoRedo #redoBtn{width:30px!important;min-width:30px!important}
  #ng27 .v389TrimBtn{width:58px!important;font-size:6.3px!important;letter-spacing:.01em!important}
  #ng27 .v389RatioBtn{width:36px!important;min-width:36px!important}
  #ng27 #zoomEditorBtn{width:34px!important;min-width:34px!important}
  #ng27 .v389UndoRedo .ico,#ng27 #zoomEditorBtn .ico{
    width:16px!important;height:16px!important;color:var(--v395-ink)!important;stroke-width:2.15!important;
    filter:drop-shadow(0 1px 2px rgba(38,97,138,.12))!important;
  }

  #ng27 .v389ToolDock{gap:8px!important}
  #ng27 .v389ToolDock .railBtn{
    position:relative!important;overflow:hidden!important;
    width:46px!important;height:54px!important;min-width:46px!important;min-height:54px!important;
    border-radius:15px!important;border:1px solid rgba(84,169,220,.30)!important;
    background:linear-gradient(155deg,rgba(255,255,255,.94),rgba(215,240,250,.84))!important;
    color:var(--v395-ink)!important;
    box-shadow:0 7px 17px rgba(35,94,136,.13),inset 0 1px 0 rgba(255,255,255,.96)!important;
    -webkit-backdrop-filter:blur(13px) saturate(1.12)!important;backdrop-filter:blur(13px) saturate(1.12)!important;
  }
  #ng27 .v389ToolDock .railBtn:before{
    content:""!important;position:absolute!important;left:8px!important;top:7px!important;width:9px!important;height:2px!important;
    border-radius:99px!important;background:linear-gradient(90deg,var(--v395-cyan),var(--v395-blue))!important;opacity:.9!important;
    box-shadow:0 0 7px rgba(73,190,237,.28)!important;
  }
  #ng27 .v389ToolDock .railBtn .ico{
    width:19px!important;height:19px!important;color:var(--v395-ink)!important;stroke-width:2.05!important;
    filter:drop-shadow(0 1px 2px rgba(35,86,124,.12))!important;
  }
  #ng27 .v389ToolDock .railBtn span{
    margin-top:2px!important;font-size:6.35px!important;letter-spacing:.035em!important;font-weight:950!important;color:var(--v395-ink)!important;
  }
  #ng27 .v389ToolDock .railBtn.active{
    background:linear-gradient(155deg,rgba(221,249,255,.98),rgba(176,226,248,.94))!important;
    border-color:rgba(62,165,224,.46)!important;
    box-shadow:0 8px 20px rgba(42,126,184,.18),inset 0 1px 0 rgba(255,255,255,.96)!important;
  }
  #ng27 .v389ToolDock .railBtn.active .ico,#ng27 .v389ToolDock .railBtn.active span{color:#1f6f9f!important}
  #ng27 .v389RightDock .railBtn[data-panel="vision"]{
    border-color:rgba(73,161,227,.42)!important;
    background:linear-gradient(155deg,rgba(245,253,255,.98),rgba(205,237,251,.94))!important;
    box-shadow:0 8px 21px rgba(38,130,198,.17),0 0 16px rgba(80,205,241,.10),inset 0 1px 0 rgba(255,255,255,.98)!important;
  }
  #ng27 .v389RightDock .railBtn[data-panel="vision"]:before{
    width:14px!important;background:linear-gradient(90deg,#68e2f2,#4d9ff2)!important;
  }

  #ng27 .v393TransportGlass{
    left:10px!important;right:10px!important;bottom:8px!important;height:72px!important;
    border:1px solid rgba(93,170,214,.22)!important;border-radius:17px!important;
    background:linear-gradient(155deg,rgba(250,254,255,.84),rgba(219,240,249,.74))!important;
    box-shadow:0 7px 18px rgba(42,98,137,.10),inset 0 1px 0 rgba(255,255,255,.90)!important;
  }
  #ng27 .v393TransportGlass:before{
    content:""!important;position:absolute!important;left:18px!important;right:18px!important;top:0!important;height:1px!important;
    background:linear-gradient(90deg,transparent,rgba(92,211,242,.72),transparent)!important;
  }
  #ng27 .v389PlaybackDock{bottom:25px!important}
  #ng27 .v389PlaybackDock #playBtn{
    width:60px!important;height:60px!important;min-width:60px!important;min-height:60px!important;
    border:1px solid rgba(255,255,255,.94)!important;
    background:radial-gradient(circle at 32% 25%,#73dbf6 0%,#46a9f3 43%,#2f82e8 100%)!important;
    box-shadow:0 9px 22px rgba(41,126,205,.26),0 0 0 2px rgba(255,255,255,.30)!important;
  }
  #ng27 .v389PlaybackDock #playBtn .ico{width:27px!important;height:27px!important;stroke-width:2!important}
  #ng27 .v389PlayerProgress{left:19px!important;right:19px!important;bottom:11px!important;color:var(--v395-ink)!important}
  #ng27 .v389ProgressTrack{height:4px!important;background:rgba(54,105,144,.22)!important;box-shadow:inset 0 1px 2px rgba(27,67,96,.08)!important}
  #ng27 .v389ProgressFill{background:linear-gradient(90deg,#62d7f0,#3797ec)!important}
  #ng27 .v389ProgressKnob{width:9px!important;height:9px!important;box-shadow:0 2px 6px rgba(30,78,111,.18)!important}
  #ng27 .v389ProgressNow,#ng27 .v389ProgressEnd{font-size:6.7px!important;letter-spacing:.01em!important}

  #ng27 .v391EditorActions{margin-top:7px!important}
  #ng27 .v393ChangeShort{
    margin:-3px auto 14px!important;
    height:27px!important;min-height:27px!important;
    border-radius:11px!important;
    border:1px solid rgba(89,164,211,.22)!important;
    background:linear-gradient(145deg,rgba(255,255,255,.94),rgba(233,247,252,.88))!important;
    color:#347cae!important;
    box-shadow:0 4px 12px rgba(44,94,132,.07),inset 0 1px 0 rgba(255,255,255,.92)!important;
  }

  #ng27.gsfFullscreen .stage.r916:before,#ng27.gsfFullscreenFallback .stage.r916:before,
  #ng27:fullscreen .stage.r916:before,#ng27:-webkit-full-screen .stage.r916:before{inset:10px!important}
}
</style>
'''

def patch_editor(text:str)->str:
    if MARK in text:
        return text
    for anchor in ('V394_MOBILE_EDITOR_FOOTER_RESTORE','v393ChangeShort','v393TransportGlass','</body>'):
        if anchor not in text:
            raise RuntimeError('V395 Editor anchor missing: '+anchor)
    return text.replace('</body>',EDITOR_PATCH+'\n</body>',1)

def main()->None:
    root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
    editor=root/'web'/'editor_2027_component'/'index.html'
    if not editor.is_file():
        raise SystemExit('V395 editor target missing: '+str(editor))
    before=editor.read_text(encoding='utf-8')
    after=patch_editor(before)
    editor.write_text(after,encoding='utf-8')
    print('V395 mobile Editor atomic skin applied changed=',before!=after,flush=True)

if __name__=='__main__':
    main()
