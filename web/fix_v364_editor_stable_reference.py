#!/usr/bin/env python3
from pathlib import Path
import re
import sys

MARK='V364_EDITOR_STABLE_REFERENCE'

STYLE=r'''<!-- V364_EDITOR_STABLE_REFERENCE -->
<style id="v364EditorStableReference">
/* V364: approved mobile cockpit, but geometry is CSS-only. No resize/mutation
   observer is allowed to continuously rewrite the player dimensions. */
@media (max-width:760px){
  #ng27.v326Mobile{
    width:100%!important;height:100%!important;min-height:0!important;max-height:100%!important;
    box-sizing:border-box!important;margin:0!important;padding:4px 6px 96px!important;overflow:hidden!important;
    background:radial-gradient(circle at 50% 8%,rgba(207,238,251,.96),transparent 34%),radial-gradient(circle at 12% 54%,rgba(219,246,255,.72),transparent 32%),linear-gradient(180deg,#FBFEFF 0%,#F2FAFE 100%)!important;
  }
  #ng27.v326Mobile .shell{
    width:100%!important;height:100%!important;min-height:0!important;max-width:460px!important;margin:0 auto!important;padding:0!important;
    display:block!important;overflow:hidden!important;background:transparent!important;
  }
  #ng27.v326Mobile .topline,#ng27.v326Mobile .gsfGuide,#ng27.v326Mobile .footNote{display:none!important}
  #ng27.v326Mobile .cockpit,#ng27.v326Mobile.expanded .cockpit{
    width:100%!important;max-width:460px!important;height:100%!important;min-height:0!important;margin:0 auto!important;padding:0 2px!important;
    display:grid!important;grid-template-columns:minmax(0,1fr)!important;grid-template-rows:minmax(0,1fr) auto auto!important;
    gap:6px!important;align-items:stretch!important;align-content:stretch!important;justify-items:stretch!important;overflow:hidden!important;
  }
  #ng27.v326Mobile .stageWrap{
    grid-column:1!important;grid-row:1!important;position:relative!important;width:clamp(220px,66vw,286px)!important;max-width:calc(100% - 8px)!important;
    height:auto!important;min-height:0!important;margin:0 auto!important;padding:0!important;align-self:start!important;justify-self:center!important;overflow:visible!important;
    transition:none!important;
  }
  #ng27.v326Mobile .stage.r916,#ng27.v326Mobile.expanded .stage.r916{
    position:relative!important;width:100%!important;max-width:none!important;height:auto!important;aspect-ratio:9/16!important;margin:0!important;
    border-radius:22px!important;border:1px solid rgba(126,207,240,.52)!important;overflow:hidden!important;
    background:linear-gradient(180deg,#dff4fd,#f5fbff)!important;box-shadow:0 12px 30px rgba(43,98,139,.15),0 0 0 4px rgba(255,255,255,.48)!important;
    transition:none!important;
  }
  #ng27.v326Mobile .stage video,#ng27.v326Mobile .stage #videoBg{transition:none!important}
  #ng27.v326Mobile .v325PlayerMeta{display:none!important}
  #ng27.v326Mobile .v325PlaybackDock{display:none!important}
  #ng27.v326Mobile .v326LeftDock{left:8px!important}
  #ng27.v326Mobile .v326RightDock{right:8px!important}
  #ng27.v326Mobile .v326ToolDock{gap:6px!important;transition:none!important}
  #ng27.v326Mobile .v326ToolDock .railBtn{
    width:44px!important;height:52px!important;min-width:44px!important;min-height:52px!important;border-radius:15px!important;
    border:1px solid rgba(255,255,255,.72)!important;background:linear-gradient(145deg,rgba(29,54,81,.68),rgba(49,76,105,.54))!important;color:#fff!important;
    -webkit-backdrop-filter:blur(15px) saturate(1.12)!important;backdrop-filter:blur(15px) saturate(1.12)!important;
    box-shadow:0 7px 18px rgba(10,27,44,.20),inset 0 1px 0 rgba(255,255,255,.26)!important;transition:none!important;
  }
  #ng27.v326Mobile .v326ToolDock .railBtn .ico{width:19px!important;height:19px!important;color:#fff!important}
  #ng27.v326Mobile .v326ToolDock .railBtn span{font-size:6.8px!important;line-height:1!important;color:#fff!important;font-weight:950!important}
  #ng27.v326Mobile .v326Meta{top:9px!important;left:9px!important;right:9px!important}
  #ng27.v326Mobile .v326Ratio{margin-left:auto!important;margin-right:44px!important}
  #ng27.v326Mobile .v326Time,#ng27.v326Mobile .v326Ratio{height:29px!important;padding:0 9px!important;border-radius:12px!important;font-size:8.4px!important}
  #ng27.v326Mobile #zoomEditorBtn{
    display:flex!important;position:absolute!important;top:9px!important;right:9px!important;z-index:104!important;width:38px!important;height:38px!important;
    min-width:38px!important;min-height:38px!important;padding:0!important;border-radius:12px!important;opacity:1!important;pointer-events:auto!important;overflow:visible!important;
    border:1px solid rgba(255,255,255,.68)!important;background:rgba(24,48,74,.64)!important;color:#fff!important;transition:none!important;
  }
  #ng27.v326Mobile #zoomEditorBtn .ico{width:18px!important;height:18px!important;margin:auto!important;color:#fff!important}
  #ng27.v326Mobile #zoomEditorBtn span{display:none!important}
  #ng27.v326Mobile .v326PlaybackDock{bottom:18px!important;gap:10px!important;transition:none!important}
  #ng27.v326Mobile #playBtn{width:52px!important;height:52px!important;min-width:52px!important;min-height:52px!important;background:linear-gradient(145deg,#57BCFC,#377CE8)!important;box-shadow:0 8px 22px rgba(17,50,94,.32),inset 0 1px 0 rgba(255,255,255,.42)!important;transition:none!important}
  #ng27.v326Mobile .v326Skip{font-size:22px!important}
  #ng27.v326Mobile .cockpit>.v323EditorActions{
    grid-column:1!important;grid-row:2!important;width:100%!important;max-width:none!important;min-height:44px!important;margin:0!important;padding:0!important;
    display:grid!important;grid-template-columns:minmax(0,1fr) minmax(0,1fr)!important;gap:6px!important;transition:none!important;
  }
  #ng27.v326Mobile .cockpit>.v323EditorActions .v323EditorAction{min-height:44px!important;height:44px!important;border-radius:15px!important;font-size:9px!important;line-height:1!important;font-weight:950!important;transition:none!important}
  #ng27.v326Mobile .cockpit>.v323EditorActions .v323EditorAction.primary{background:linear-gradient(135deg,#55B8FA,#3E83EC)!important;color:#fff!important}
  #ng27.v326Mobile .cockpit>.v323EditorActions .v323EditorAction.secondary{background:rgba(255,255,255,.92)!important;color:#123B7A!important}
  #ng27.v326Mobile .cockpit>.timeline{
    grid-column:1!important;grid-row:3!important;width:100%!important;max-width:none!important;min-height:0!important;margin:0!important;padding:7px 8px 6px!important;
    border-radius:16px!important;background:rgba(255,255,255,.76)!important;border:1px solid rgba(151,187,216,.24)!important;
    box-shadow:0 7px 18px rgba(79,118,157,.07),inset 0 1px 0 rgba(255,255,255,.84)!important;transform:none!important;transition:none!important;
  }
  #ng27.v326Mobile .cockpit>.timeline .tlMeta{margin:0 1px 5px!important;font-size:7.5px!important}
  #ng27.v326Mobile .cockpit>.timeline .track{height:36px!important}
  #ng27.v326Mobile .cockpit>.timeline .trimRow{margin-top:3px!important;font-size:7px!important}
  #ng27.v326Mobile .drawer{z-index:180!important;max-height:min(48%,360px)!important;overflow-y:auto!important;overflow-x:hidden!important;border-radius:18px!important;box-shadow:0 14px 34px rgba(36,75,112,.18)!important}
}
</style>'''

FRAME_RE=re.compile(r"function\s+setFrameHeight\(height\)\s*\{\s*const\s+h=Math\.max\(320,Number\(height\)\|\|720\);\s*sendMessage\(SET_FRAME_HEIGHT,\{height:h\}\);\s*\}",re.S)
NEW_FRAME='''let lastSentFrameHeight=0;
 function setFrameHeight(height){
   const h=Math.max(320,Math.round(Number(height)||720));
   if(Math.abs(h-lastSentFrameHeight)<3)return;
   lastSentFrameHeight=h;
   sendMessage(SET_FRAME_HEIGHT,{height:h});
 }'''

FIT_RE=re.compile(r"function\s+fitEditorViewport\(\)\s*\{\s*try\{\s*const\s+pw=Math\.max\(320,Number\(window\.parent\.innerWidth\|\|window\.innerWidth\|\|1920\)\);\s*if\(pw<=820\)\{setFrameHeight\(Math\.max\(720,Math\.ceil\(document\.documentElement\.scrollHeight\|\|720\)\)\);return\}\s*const\s+ph=Math\.max\(600,Number\(window\.parent\.innerHeight\|\|window\.innerHeight\|\|900\)\);\s*setFrameHeight\(Math\.max\(600,Math\.min\(1080,Math\.floor\(ph\)\)\)\);\s*\}catch\(e\)\{setFrameHeight\(900\)\}\s*\}",re.S)
NEW_FIT='''function fitEditorViewport(){
   try{
     const pw=Math.max(320,Number(window.parent.innerWidth||window.innerWidth||1920));
     if(pw<=820){
       const sh=Math.max(560,Number((window.screen&&window.screen.height)||0)||Number(window.parent.innerHeight||window.innerHeight||720));
       setFrameHeight(Math.max(560,Math.min(820,Math.floor(sh-110))));
       return;
     }
     const ph=Math.max(600,Number(window.parent.innerHeight||window.innerHeight||900));
     setFrameHeight(Math.max(600,Math.min(1080,Math.floor(ph))));
   }catch(e){setFrameHeight(720)}
 }'''

def _replace_fallback(text:str)->str:
    pat=re.compile(r"window\.setTimeout\(\(\)=>\{\s*if\(!hostVideoUrl\)\{(?P<body>.*?)\}\s*\},80\);",re.S)
    m=pat.search(text)
    if not m:
        raise RuntimeError('V364 editor fallback loader anchor missing')
    body=m.group('body').replace("hostVideoUrl='/editor-media/current?ts='+Date.now();","hostVideoUrl='/editor-media/current';")
    repl="window.setTimeout(()=>{\n   if(!hostVideoUrl){"+body+"}\n },900);"
    return text[:m.start()]+repl+text[m.end():]


def patch_text(text:str)->str:
    if MARK in text:
        return text
    required=('id="ng27"','id="v326MobileEditorExact"','id="stage"','id="zoomEditorBtn"','id="v323EditorActions"','data-panel="frame"','data-panel="caption"','data-panel="look"','data-panel="audio"','data-panel="vision"')
    for anchor in required:
        if anchor not in text:
            raise RuntimeError('V364 missing editor anchor: '+anchor)
    text,n=FRAME_RE.subn(NEW_FRAME,text,count=1)
    if n!=1:
        raise RuntimeError('V364 frame-height anchor missing')
    text,n=FIT_RE.subn(NEW_FIT,text,count=1)
    if n!=1:
        raise RuntimeError('V364 viewport-fit anchor missing')
    text=_replace_fallback(text)
    if '</head>' not in text:
        raise RuntimeError('V364 editor </head> missing')
    return text.replace('</head>',STYLE+'\n</head>',1)


def main():
    path=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app/web/editor_2027_component/index.html')
    if not path.is_file():
        raise SystemExit('V364 editor target missing: '+str(path))
    before=path.read_text(encoding='utf-8')
    after=patch_text(before)
    path.write_text(after,encoding='utf-8')
    print('V364 stable mobile Editor reference applied', 'changed=',before!=after, flush=True)

if __name__=='__main__':
    main()
