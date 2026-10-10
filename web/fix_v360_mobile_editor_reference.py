#!/usr/bin/env python3
from pathlib import Path
import re
import sys

MARK = 'V360_MOBILE_EDITOR_REFERENCE'

PATCH = r'''
<!-- V360_MOBILE_EDITOR_REFERENCE -->
<!-- GSF_V361_EDITOR_REPAIR -->
<!-- GSF_V364_EDITOR_STABLE_NOSCROLL -->
<style id="v360MobileEditorReference">
/* V364: compact approved mobile Editor. Geometry is CSS-owned and stable:
   no resize observer, no mutation observer, no JS-written player width. */
@media(max-width:760px){
  html,body{
    width:100%!important;height:100%!important;min-height:0!important;margin:0!important;padding:0!important;
    overflow:hidden!important;overscroll-behavior:none!important;
  }
  #ng27.v326Mobile{
    width:100%!important;height:100%!important;min-height:0!important;max-height:100%!important;
    box-sizing:border-box!important;margin:0!important;padding:4px 6px 88px!important;overflow:hidden!important;
    background:radial-gradient(circle at 50% 8%,rgba(207,238,251,.96),transparent 34%),radial-gradient(circle at 12% 54%,rgba(219,246,255,.72),transparent 32%),linear-gradient(180deg,#FBFEFF 0%,#F2FAFE 100%)!important;
  }
  #ng27.v326Mobile .shell{
    width:100%!important;height:100%!important;min-height:0!important;max-width:460px!important;
    margin:0 auto!important;padding:0!important;overflow:hidden!important;background:transparent!important;display:block!important;
  }
  #ng27.v326Mobile .topline,#ng27.v326Mobile .gsfGuide,#ng27.v326Mobile .footNote{display:none!important}
  #ng27.v326Mobile .cockpit,#ng27.v326Mobile.expanded .cockpit{
    width:100%!important;max-width:460px!important;height:100%!important;min-height:0!important;margin:0 auto!important;padding:0 2px!important;
    display:grid!important;grid-template-columns:minmax(0,1fr)!important;grid-template-rows:minmax(0,1fr) auto auto!important;
    gap:4px!important;align-items:stretch!important;align-content:stretch!important;justify-items:stretch!important;overflow:hidden!important;
  }
  /* Compact default: the user can open FULL for precision work. */
  #ng27.v326Mobile .stageWrap{
    grid-column:1!important;grid-row:1!important;position:relative!important;
    width:clamp(188px,52vw,200px)!important;max-width:calc(100% - 8px)!important;height:auto!important;min-height:0!important;
    margin:0 auto!important;padding:0!important;align-self:start!important;justify-self:center!important;overflow:visible!important;transition:none!important;
  }
  #ng27.v326Mobile .stage.r916,#ng27.v326Mobile.expanded .stage.r916{
    position:relative!important;width:100%!important;max-width:none!important;height:auto!important;aspect-ratio:9/16!important;margin:0!important;
    border-radius:20px!important;border:1px solid rgba(126,207,240,.52)!important;overflow:hidden!important;
    background:linear-gradient(180deg,#dff4fd,#f5fbff)!important;
    box-shadow:0 10px 26px rgba(43,98,139,.14),0 0 0 3px rgba(255,255,255,.46)!important;transition:none!important;
  }
  #ng27.v326Mobile .stage video,#ng27.v326Mobile .stage #videoBg{transition:none!important}

  /* V326 is the only visible control shell. */
  #ng27.v326Mobile .v325PlayerMeta{display:none!important}
  #ng27.v326Mobile .v325PlaybackDock{display:none!important}
  #ng27.v326Mobile .v326LeftDock{left:7px!important}
  #ng27.v326Mobile .v326RightDock{right:7px!important}
  #ng27.v326Mobile .v326ToolDock{gap:5px!important;transition:none!important}
  #ng27.v326Mobile .v326ToolDock .railBtn{
    width:40px!important;height:48px!important;min-width:40px!important;min-height:48px!important;border-radius:14px!important;
    border:1px solid rgba(255,255,255,.72)!important;background:linear-gradient(145deg,rgba(29,54,81,.68),rgba(49,76,105,.54))!important;color:#fff!important;
    -webkit-backdrop-filter:blur(14px) saturate(1.10)!important;backdrop-filter:blur(14px) saturate(1.10)!important;
    box-shadow:0 6px 16px rgba(10,27,44,.19),inset 0 1px 0 rgba(255,255,255,.25)!important;transition:none!important;
  }
  #ng27.v326Mobile .v326ToolDock .railBtn .ico{width:17px!important;height:17px!important;color:#fff!important}
  #ng27.v326Mobile .v326ToolDock .railBtn span{font-size:6.1px!important;line-height:1!important;color:#fff!important;font-weight:950!important}

  #ng27.v326Mobile .v326Meta{top:7px!important;left:7px!important;right:7px!important}
  #ng27.v326Mobile .v326Ratio{margin-left:auto!important;margin-right:40px!important}
  #ng27.v326Mobile .v326Time,#ng27.v326Mobile .v326Ratio{height:26px!important;padding:0 7px!important;border-radius:11px!important;font-size:7.6px!important}
  #ng27.v326Mobile #zoomEditorBtn{
    display:flex!important;position:absolute!important;top:7px!important;right:7px!important;z-index:104!important;
    width:34px!important;height:34px!important;min-width:34px!important;min-height:34px!important;padding:0!important;border-radius:11px!important;
    opacity:1!important;pointer-events:auto!important;overflow:visible!important;border:1px solid rgba(255,255,255,.68)!important;
    background:rgba(24,48,74,.64)!important;color:#fff!important;-webkit-backdrop-filter:blur(12px)!important;backdrop-filter:blur(12px)!important;transition:none!important;
  }
  #ng27.v326Mobile #zoomEditorBtn .ico{width:16px!important;height:16px!important;margin:auto!important;color:#fff!important}
  #ng27.v326Mobile #zoomEditorBtn span{display:none!important}

  #ng27.v326Mobile .v326PlaybackDock{bottom:14px!important;gap:8px!important;transition:none!important}
  #ng27.v326Mobile #playBtn{
    width:46px!important;height:46px!important;min-width:46px!important;min-height:46px!important;
    background:linear-gradient(145deg,#57BCFC,#377CE8)!important;box-shadow:0 7px 19px rgba(17,50,94,.30),inset 0 1px 0 rgba(255,255,255,.40)!important;transition:none!important;
  }
  #ng27.v326Mobile .v326Skip{font-size:20px!important}

  #ng27.v326Mobile .cockpit>.v323EditorActions{
    grid-column:1!important;grid-row:2!important;width:100%!important;max-width:none!important;min-height:40px!important;margin:0!important;padding:0!important;
    display:grid!important;grid-template-columns:minmax(0,1fr) minmax(0,1fr)!important;gap:5px!important;transition:none!important;
  }
  #ng27.v326Mobile .cockpit>.v323EditorActions .v323EditorAction{
    height:40px!important;min-height:40px!important;padding:6px 8px!important;border-radius:14px!important;font-size:8.3px!important;line-height:1!important;font-weight:950!important;transition:none!important;
  }
  #ng27.v326Mobile .cockpit>.v323EditorActions .v323EditorAction.primary{background:linear-gradient(135deg,#55B8FA,#3E83EC)!important;color:#fff!important}
  #ng27.v326Mobile .cockpit>.v323EditorActions .v323EditorAction.secondary{background:rgba(255,255,255,.92)!important;color:#123B7A!important}

  #ng27.v326Mobile .cockpit>.timeline{
    grid-column:1!important;grid-row:3!important;width:100%!important;max-width:none!important;min-height:0!important;margin:0!important;padding:5px 7px 4px!important;
    border-radius:14px!important;background:rgba(255,255,255,.76)!important;border:1px solid rgba(151,187,216,.24)!important;
    box-shadow:0 6px 16px rgba(79,118,157,.06),inset 0 1px 0 rgba(255,255,255,.84)!important;transform:none!important;transition:none!important;
  }
  #ng27.v326Mobile .cockpit>.timeline .tlMeta{margin:0 1px 3px!important;font-size:6.8px!important}
  #ng27.v326Mobile .cockpit>.timeline .track{height:28px!important}
  #ng27.v326Mobile .cockpit>.timeline .trimRow{margin-top:2px!important;font-size:6.4px!important}
  #ng27.v326Mobile .drawer{
    z-index:180!important;max-height:min(52%,330px)!important;overflow-y:auto!important;overflow-x:hidden!important;
    border-radius:17px!important;box-shadow:0 14px 34px rgba(36,75,112,.18)!important;
  }

  /* FULL is intentionally larger; normal mode remains compact and no-scroll. */
  #ng27.v326Mobile.gsfFullscreen,#ng27.v326Mobile:fullscreen,#ng27.v326Mobile:-webkit-full-screen{padding:8px!important}
  #ng27.v326Mobile.gsfFullscreen .stageWrap,#ng27.v326Mobile:fullscreen .stageWrap,#ng27.v326Mobile:-webkit-full-screen .stageWrap{
    width:min(78vw,360px,calc((100dvh - 126px)*9/16))!important;max-width:calc(100% - 16px)!important;
  }
}
</style>
'''

FRAME_RE = re.compile(
    r"function\s+setFrameHeight\(height\)\s*\{\s*const\s+h=Math\.max\(320,Number\(height\)\|\|720\);\s*sendMessage\(SET_FRAME_HEIGHT,\{height:h\}\);\s*\}",
    re.S,
)
NEW_FRAME = '''let lastSentFrameHeight=0;
 function setFrameHeight(height){
   let h=Math.max(320,Math.round(Number(height)||720));
   try{
     const pw=Math.max(320,Number(window.parent.innerWidth||window.innerWidth||1920));
     if(pw<=820){
       const sh=Math.max(560,Number((window.screen&&window.screen.height)||0)||Number(window.parent.innerHeight||window.innerHeight||720));
       const mobileCap=Math.max(520,Math.min(820,Math.floor(sh-110)));
       h=Math.min(h,mobileCap);
     }
   }catch(e){}
   if(Math.abs(h-lastSentFrameHeight)<3)return;
   lastSentFrameHeight=h;
   sendMessage(SET_FRAME_HEIGHT,{height:h});
 }'''

FIT_RE = re.compile(
    r"function\s+fitEditorViewport\(\)\s*\{\s*try\{\s*const\s+pw=Math\.max\(320,Number\(window\.parent\.innerWidth\|\|window\.innerWidth\|\|1920\)\);\s*if\(pw<=820\)\{setFrameHeight\(Math\.max\(720,Math\.ceil\(document\.documentElement\.scrollHeight\|\|720\)\)\);return\}\s*const\s+ph=Math\.max\(600,Number\(window\.parent\.innerHeight\|\|window\.innerHeight\|\|900\)\);\s*setFrameHeight\(Math\.max\(600,Math\.min\(1080,Math\.floor\(ph\)\)\)\);\s*\}catch\(e\)\{setFrameHeight\(900\)\}\s*\}",
    re.S,
)
FIT_RE_V325 = re.compile(
    r"function\s+fitEditorViewport\(\)\s*\{\s*try\{\s*const\s+pw=Math\.max\(320,Number\(window\.parent\.innerWidth\|\|window\.innerWidth\|\|1920\)\);\s*if\(pw<=820\)\{const\s+ph=Math\.max\(560,Number\(window\.parent\.innerHeight\|\|window\.innerHeight\|\|760\)\);setFrameHeight\(Math\.max\(500,Math\.min\(710,Math\.floor\(ph-145\)\)\)\);return\}\s*const\s+ph=Math\.max\(600,Number\(window\.parent\.innerHeight\|\|window\.innerHeight\|\|900\)\);\s*setFrameHeight\(Math\.max\(600,Math\.min\(1080,Math\.floor\(ph\)\)\)\);\s*\}catch\(e\)\{setFrameHeight\(900\)\}\s*\}",
    re.S,
)
NEW_FIT = '''function fitEditorViewport(){
   try{
     const pw=Math.max(320,Number(window.parent.innerWidth||window.innerWidth||1920));
     const ph=Math.max(560,Number(window.parent.innerHeight||window.innerHeight||720));
     if(pw<=820){setFrameHeight(ph);return}
     setFrameHeight(Math.max(600,Math.min(1080,Math.floor(ph))));
   }catch(e){setFrameHeight(720)}
 }'''

FALLBACK_RE = re.compile(
    r"window\.setTimeout\(\(\)=>\{\s*if\(!hostVideoUrl\)\{(?P<body>.*?)\}\s*\},80\);",
    re.S,
)


def _stabilize_frame_sizing(text: str) -> str:
    text, n = FRAME_RE.subn(NEW_FRAME, text, count=1)
    if n != 1:
        raise RuntimeError('V364 frame-height anchor missing')
    text, n = FIT_RE.subn(NEW_FIT, text, count=1)
    if n != 1:
        text, n = FIT_RE_V325.subn(NEW_FIT, text, count=1)
    if n != 1:
        raise RuntimeError('V364 viewport-fit anchor missing')
    return text


def _stabilize_fallback_source(text: str) -> str:
    match = FALLBACK_RE.search(text)
    if not match:
        raise RuntimeError('V364 editor fallback loader anchor missing')
    body = match.group('body').replace(
        "hostVideoUrl='/editor-media/current?ts='+Date.now();",
        "hostVideoUrl='/editor-media/current';",
    )
    replacement = "window.setTimeout(()=>{\n   if(!hostVideoUrl){" + body + "}\n },900);"
    return text[:match.start()] + replacement + text[match.end():]


def patch_text(text: str) -> str:
    if MARK in text:
        return text
    required = (
        'id="ng27"',
        'id="v326MobileEditorExact"',
        'id="v323EditorActions"',
        'id="zoomEditorBtn"',
        'id="stage"',
        'data-panel="frame"',
        'data-panel="caption"',
        'data-panel="look"',
        'data-panel="audio"',
        'data-panel="vision"',
    )
    for anchor in required:
        if anchor not in text:
            raise RuntimeError('V360 missing editor anchor: ' + anchor)
    text = _stabilize_frame_sizing(text)
    text = _stabilize_fallback_source(text)
    if '</body>' not in text:
        raise RuntimeError('V360 editor body anchor missing')
    return text.replace('</body>', PATCH + '\n</body>', 1)


def main() -> None:
    path = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path('/app/web/editor_2027_component/index.html')
    if not path.is_file():
        raise SystemExit('V360 editor target missing: ' + str(path))
    before = path.read_text(encoding='utf-8')
    after = patch_text(before)
    path.write_text(after, encoding='utf-8')
    print('V364 compact no-scroll Editor stabilization applied', 'changed=', before != after, flush=True)


if __name__ == '__main__':
    main()
