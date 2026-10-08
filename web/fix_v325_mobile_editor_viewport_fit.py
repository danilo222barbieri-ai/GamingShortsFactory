#!/usr/bin/env python3
from pathlib import Path
import re
import sys

STYLE_ID='v325MobileEditorViewportFit'
STYLE=r'''<style id="v325MobileEditorViewportFit">
/* V325: kill the legacy V295 100%-height centered stage on mobile.
   The player is top-aligned, rails stay inside it, timeline stays on it,
   and the two real workflow actions live immediately below. Desktop untouched. */
@media(max-width:760px){
  #ng27{height:100%!important;min-height:0!important;max-height:100%!important;overflow:hidden!important;padding:0 6px 2px!important}
  #ng27 .shell{width:100%!important;height:100%!important;min-height:0!important;max-height:100%!important;display:flex!important;flex-direction:column!important;justify-content:flex-start!important;align-items:stretch!important;overflow:hidden!important;padding:0!important;margin:0!important}

  /* The outer GSF page already says Game Editor. Remove the legacy inner title/spacer. */
  #ng27 .topline{display:none!important;flex:0 0 0!important;min-height:0!important;height:0!important;padding:0!important;margin:0!important;overflow:hidden!important}
  #ng27 .gsfGuide,#ng27 .footNote{display:none!important}

  /* V295 used a full-height flex stageWrap centered vertically. That caused the huge blank band. */
  #ng27 .cockpit,#ng27.expanded .cockpit{
    position:relative!important;
    flex:0 0 auto!important;
    width:min(100%,340px)!important;
    max-width:min(340px,calc((100dvh - 154px)*.5625))!important;
    height:auto!important;min-height:0!important;
    margin:0 auto!important;padding:0!important;
    display:grid!important;grid-template-columns:minmax(0,1fr)!important;grid-template-rows:auto auto!important;
    gap:7px!important;align-items:start!important;align-content:start!important;justify-items:stretch!important;
    overflow:visible!important;
  }
  #ng27 .stageWrap{
    grid-column:1!important;grid-row:1!important;
    position:relative!important;
    width:100%!important;height:auto!important;min-height:0!important;max-height:none!important;
    margin:0!important;padding:0!important;
    display:block!important;align-items:initial!important;justify-content:initial!important;
    overflow:visible!important;
  }
  #ng27 .stage.r916,#ng27.expanded .stage.r916{
    display:block!important;position:relative!important;
    width:100%!important;max-width:none!important;height:auto!important;max-height:none!important;
    aspect-ratio:9/16!important;margin:0!important;border-radius:21px!important;overflow:hidden!important;
  }

  /* Rails are absolute against the same player-width cockpit, never outside the phone. */
  #ng27 .cockpit>.rail{
    position:absolute!important;top:calc((100% - 55px)/2)!important;z-index:90!important;
    width:auto!important;height:auto!important;margin:0!important;padding:0!important;
    display:flex!important;flex-direction:column!important;justify-content:center!important;gap:7px!important;
    transform:translateY(-50%)!important;pointer-events:none!important;
  }
  #ng27 .cockpit>.rail:first-child{left:7px!important;right:auto!important}
  #ng27 .cockpit>.rail:nth-of-type(2),#ng27 .cockpit>.rail:nth-of-type(3){right:7px!important;left:auto!important}
  #ng27 .cockpit>.rail .railBtn{pointer-events:auto!important}

  /* Timeline is attached to the bottom edge of the actual 9:16 frame, not the component viewport. */
  #ng27 .timeline,#ng27.expanded .timeline{
    position:absolute!important;z-index:72!important;
    left:8px!important;right:8px!important;bottom:8px!important;top:auto!important;
    width:auto!important;max-width:none!important;height:auto!important;
    margin:0!important;transform:none!important;
  }

  /* V324 moves this node after stageWrap; V325 gives it a dedicated row below the frame. */
  #ng27 .cockpit>.v323EditorActions{grid-column:1!important;grid-row:2!important;position:relative!important;z-index:80!important;width:100%!important;min-width:0!important;margin:0!important;padding:0!important;display:grid!important;grid-template-columns:minmax(0,1fr) minmax(0,1fr)!important;gap:7px!important}
  #ng27 .cockpit>.v323EditorActions .v323EditorAction{width:100%!important;min-width:0!important;min-height:48px!important;padding:7px 8px!important;font-size:9px!important;line-height:1.05!important;white-space:normal!important}

  /* FULL stays inside the frame and never changes the normal-flow geometry. */
  #ng27 #zoomEditorBtn.v323InsidePlayer{top:8px!important;right:8px!important}
}
@media(max-width:390px) and (max-height:760px){
  #ng27 .cockpit,#ng27.expanded .cockpit{width:min(100%,330px)!important;max-width:min(330px,calc((100dvh - 136px)*.5625))!important;gap:6px!important}
  #ng27 .cockpit>.rail{top:calc((100% - 50px)/2)!important;gap:5px!important}
  #ng27 .cockpit>.rail .railBtn{width:42px!important;height:42px!important;min-width:42px!important;min-height:42px!important}
  #ng27 .cockpit>.v323EditorActions{gap:6px!important}
  #ng27 .cockpit>.v323EditorActions .v323EditorAction{min-height:44px!important;font-size:8.5px!important}
  #ng27 .timeline,#ng27.expanded .timeline{left:6px!important;right:6px!important;bottom:6px!important;padding:5px 7px 6px!important}
}
</style>'''

def _clean(text:str)->str:
    return re.sub(r'<style id="'+re.escape(STYLE_ID)+r'">.*?</style>\n?','',text,count=1,flags=re.DOTALL)

def patch_text(text:str)->str:
    if f'id="{STYLE_ID}"' in text:
        return text
    for marker in ('id="ng27"','class="stageWrap"','class="timeline"','id="v323EditorActions"','V324_EDITOR_ACTION_PLACEMENT'):
        if marker not in text:
            raise RuntimeError('V325 editor anchor missing: '+marker)
    out=_clean(text)
    if '</head>' not in out:
        raise RuntimeError('V325 editor </head> missing')
    return out.replace('</head>',STYLE+'\n</head>',1)

def main()->None:
    path=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app/web/editor_2027_component/index.html')
    if not path.is_file():
        raise SystemExit('V325 editor target missing: '+str(path))
    before=path.read_text(encoding='utf-8')
    after=patch_text(before)
    path.write_text(after,encoding='utf-8')
    print('V325 mobile editor viewport fit applied changed=',before!=after,flush=True)

if __name__=='__main__':
    main()
