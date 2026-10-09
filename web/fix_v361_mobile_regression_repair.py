#!/usr/bin/env python3
from pathlib import Path
import sys

MARK = 'V361_MOBILE_REGRESSION_REPAIR'

HUB_PATCH = r'''
<!-- V361_MOBILE_REGRESSION_REPAIR -->
<style id="v361MobileHubRepair">
@media(max-width:767px){
  /* V359 stretched the internal pages into the parent Game Bar. Restore a real
     scrollable content area and reserve the fixed shell at the bottom. */
  #hub{padding:4px 6px 0!important;grid-template-rows:minmax(0,1fr)!important;gap:0!important;overflow:hidden!important}
  #hub>.top{display:none!important}
  #hub>.stage{height:100%!important;min-height:0!important;overflow:hidden!important}
  #hub .view{height:100%!important;min-height:0!important;overflow:hidden!important}

  /* Profile: no duplicate Creator Hub brand row; cards keep their natural
     mobile size and the page scrolls internally above Game Bar/footer. */
  #hub .view[data-view="profile"] .profileReferenceScroll{
    height:100%!important;min-height:0!important;display:block!important;
    overflow-y:auto!important;overflow-x:hidden!important;-webkit-overflow-scrolling:touch!important;
    overscroll-behavior-y:contain!important;padding:10px 3px 104px!important;box-sizing:border-box!important;
  }
  #hub .profileReferenceBrand{display:none!important}
  #hub .profileReferenceCard{height:auto!important;margin:0 0 10px!important}
  #hub .profileReferenceEdit{
    min-height:188px!important;padding:14px!important;grid-template-columns:106px minmax(0,1fr)!important;
    gap:13px!important;align-items:center!important;
  }
  #hub .profileRefAvatar{width:88px!important;height:88px!important}
  #hub .profileRefPhotoBtn{min-width:98px!important;min-height:38px!important;font-size:10.5px!important}
  #hub .profileRefTitle{font-size:23px!important}
  #hub .profileRefSubtitle{font-size:11px!important;margin-top:4px!important}
  #hub .profileRefField{margin-top:5px!important}
  #hub .profileRefField label{font-size:10px!important;margin-bottom:5px!important}
  #hub .profileRefInputWrap{height:46px!important;border-radius:15px!important}
  #hub .profileRefInputWrap input{font-size:15px!important}
  #hub .profileRefSave{min-width:142px!important;height:44px!important;font-size:12px!important}
  #hub .profilePlanRef{min-height:142px!important;padding:13px 14px!important;grid-template-columns:54px minmax(0,1fr) auto!important;column-gap:10px!important;row-gap:8px!important}
  #hub .profileRefSectionIcon{width:50px!important;height:50px!important;border-radius:16px!important;font-size:21px!important}
  #hub .profileRefSectionText h2{font-size:21px!important}
  #hub .profileRefSectionText p{font-size:10.5px!important;margin-top:4px!important}
  #hub .profilePlanBody{grid-column:1/4!important;gap:9px!important}
  #hub .profilePlanPill{min-width:70px!important;height:36px!important;font-size:11px!important}
  #hub .profilePlanCopy{font-size:10px!important;line-height:1.25!important}
  #hub .profilePlanCta{grid-column:1/4!important;height:44px!important;font-size:12px!important}
  #hub .profileSocialRef{min-height:108px!important;padding:12px 14px!important}
  #hub .profileSocialRefHead{grid-template-columns:52px minmax(0,1fr)!important;gap:10px!important;margin:0!important}
  #hub .profileSocialRef .profileRefSectionIcon{width:50px!important;height:50px!important}
  #hub .view[data-view="profile"].v357SocialOpen .profileReferenceScroll{display:block!important;overflow-y:auto!important;padding:10px 3px 104px!important}
  #hub .view[data-view="profile"].v357SocialOpen .profileSocialRef{height:auto!important;min-height:430px!important;overflow:visible!important}
  #hub .view[data-view="profile"].v357SocialOpen .profileSocialRows{height:auto!important;overflow:visible!important;grid-template-rows:repeat(5,56px)!important}

  /* Projects: keep the selected collection at the top, never stretch an
     empty state over the whole viewport, and restore the bottom shell reserve. */
  #hub .view[data-view="projects"]{padding:8px 2px 0!important;box-sizing:border-box!important}
  #hub .view[data-view="projects"] .detail{height:100%!important;min-height:0!important;display:grid!important;grid-template-rows:auto minmax(0,1fr)!important;gap:8px!important;padding:0!important}
  #hub .view[data-view="projects"].v359ProjectDirect .detail{display:grid!important;padding:0!important;gap:8px!important}
  #hub .view[data-view="projects"].v359ProjectDirect .detailHead{display:flex!important;min-height:66px!important;padding:7px 10px 5px!important;align-items:flex-start!important}
  #hub .view[data-view="projects"] .detailHeadText h2{font-size:24px!important;line-height:1.02!important;margin:0!important}
  #hub .view[data-view="projects"] .detailHeadText p{font-size:11px!important;line-height:1.22!important;margin-top:5px!important}
  #hub .view[data-view="projects"] .detailCard{height:100%!important;min-height:0!important;overflow:hidden!important}
  #hub .view[data-view="projects"] .folderScroller,
  #hub .view[data-view="projects"].v359ProjectDirect .folderScroller{
    height:100%!important;min-height:0!important;display:block!important;overflow-y:auto!important;overflow-x:hidden!important;
    -webkit-overflow-scrolling:touch!important;overscroll-behavior-y:contain!important;
    padding:0 4px 104px!important;box-sizing:border-box!important;
  }
  #hub .view[data-view="projects"] .hubProjectsGuide{margin:0 0 10px!important;padding:9px 11px!important;min-height:0!important}
  #hub .view[data-view="projects"].v359ProjectDirect .v359ProjectActivePane{
    height:auto!important;min-height:0!important;display:block!important;overflow:visible!important;margin:0!important;padding:0!important;
  }
  #hub .view[data-view="projects"].v359ProjectDirect .v359ProjectActivePane #projectRows,
  #hub .view[data-view="projects"].v359ProjectDirect .v359ProjectActivePane #draftRows,
  #hub .view[data-view="projects"].v359ProjectDirect .v359ProjectActivePane #shortRows{
    height:auto!important;min-height:0!important;max-height:none!important;overflow:visible!important;
  }
  #hub .view[data-view="projects"].v359ProjectDirect .v359ProjectActivePane #draftRows>.empty,
  #hub .view[data-view="projects"].v359ProjectDirect .v359ProjectActivePane #shortRows>.empty{
    width:100%!important;height:auto!important;min-height:220px!important;margin:0 0 10px!important;
    display:grid!important;place-content:center!important;padding:24px 18px!important;box-sizing:border-box!important;
  }

  /* Live: preserve the Twitch/YouTube folder hierarchy but stop using each
     provider as half of the entire viewport. */
  #hub .view[data-view="live"]{height:100%!important;min-height:0!important;padding:10px 2px 0!important;overflow:hidden!important;box-sizing:border-box!important}
  #hub .view[data-view="live"] .detail,
  #hub .view[data-view="live"] .detailCard{height:100%!important;min-height:0!important;overflow:hidden!important}
  #hub .view[data-view="live"] .folderScroller{
    height:100%!important;min-height:0!important;display:block!important;overflow-y:auto!important;overflow-x:hidden!important;
    -webkit-overflow-scrolling:touch!important;overscroll-behavior-y:contain!important;padding:0 2px 104px!important;box-sizing:border-box!important;
  }
  #hub .v357LiveRoot{height:auto!important;min-height:0!important;display:grid!important;grid-template-rows:repeat(2,148px)!important;gap:12px!important;padding:0 4px!important;align-content:start!important}
  #hub .v357LiveFolder{height:148px!important;min-height:148px!important;padding:15px!important;border-radius:25px!important;grid-template-columns:60px minmax(0,1fr) auto!important;gap:13px!important}
  #hub .v357LiveFolderIcon{width:58px!important;height:58px!important;border-radius:19px!important;font-size:23px!important}
  #hub .v357LiveFolderCopy b{font-size:22px!important;line-height:1!important}
  #hub .v357LiveFolderCopy small{font-size:11px!important;line-height:1.22!important;margin-top:5px!important}
  #hub .v357LiveFolderArrow{font-size:27px!important}
  #hub .v357LiveDetail{height:auto!important;min-height:0!important;grid-template-rows:46px auto!important;padding:0 4px 8px!important;overflow:visible!important}
  #hub .v357LiveDetailBody{height:auto!important;min-height:0!important;overflow:visible!important}
  #hub .v357LiveDetailBody .livePlatformCard{height:auto!important;min-height:0!important;overflow:visible!important}
  #hub .v357LiveDetailBody .liveMiniFolders{height:auto!important;grid-template-rows:none!important;grid-auto-rows:minmax(66px,auto)!important;overflow:visible!important}
  #hub .v357LiveDetailBody .liveMiniFolder{height:auto!important;min-height:66px!important}
}
</style>
'''

EDITOR_PATCH = r'''
<!-- V361_MOBILE_REGRESSION_REPAIR -->
<style id="v361MobileEditorRepair">
#ng27.v326Mobile.v360Reference{
  box-sizing:border-box!important;
  padding:5px 6px 96px!important;
  --v360-bottom-gap:0px!important;
}
#ng27.v326Mobile.v360Reference .shell{height:100%!important;min-height:0!important;gap:6px!important}
#ng27.v326Mobile.v360Reference .v360EditorHeader{
  min-height:50px!important;padding:7px 64px 7px 10px!important;
  grid-template-columns:minmax(0,1fr)!important;gap:0!important;
}
#ng27.v326Mobile.v360Reference .v360EditorTitle b{font-size:20px!important}
#ng27.v326Mobile.v360Reference .v360EditorTitle span{font-size:9.8px!important;margin-top:4px!important}
#ng27.v326Mobile.v360Reference .v360FullProxy{display:none!important}

/* V325 and V326 both created metadata/playback shells. Keep V326 only. */
#ng27.v326Mobile.v360Reference .v325PlayerMeta{display:none!important}
#ng27.v326Mobile.v360Reference .v325PlaybackDock{display:none!important}

/* Reuse the original real fullscreen control inside the player instead of
   adding a second header control beside the parent close button. */
#ng27.v326Mobile.v360Reference #zoomEditorBtn{
  display:flex!important;position:absolute!important;top:9px!important;right:9px!important;z-index:104!important;
  width:38px!important;height:38px!important;min-width:38px!important;min-height:38px!important;
  padding:0!important;border-radius:12px!important;opacity:1!important;pointer-events:auto!important;overflow:visible!important;
  border:1px solid rgba(255,255,255,.68)!important;background:rgba(24,48,74,.64)!important;color:#fff!important;
  -webkit-backdrop-filter:blur(13px)!important;backdrop-filter:blur(13px)!important;
}
#ng27.v326Mobile.v360Reference #zoomEditorBtn .ico{width:18px!important;height:18px!important;margin:auto!important;color:#fff!important}
#ng27.v326Mobile.v360Reference #zoomEditorBtn span{display:none!important}
#ng27.v326Mobile.v360Reference .v326Ratio{margin-right:44px!important}

#ng27.v326Mobile.v360Reference .cockpit,#ng27.v326Mobile.v360Reference.expanded .cockpit{
  height:100%!important;min-height:0!important;grid-template-rows:minmax(0,1fr) auto auto!important;gap:6px!important;overflow:hidden!important;
}
#ng27.v326Mobile.v360Reference .stageWrap{max-width:calc(100% - 8px)!important;align-self:start!important}
#ng27.v326Mobile.v360Reference .v326ToolDock{gap:6px!important}
#ng27.v326Mobile.v360Reference .v326ToolDock .railBtn{width:44px!important;height:52px!important;min-width:44px!important;min-height:52px!important;border-radius:15px!important}
#ng27.v326Mobile.v360Reference .v326ToolDock .railBtn .ico{width:19px!important;height:19px!important}
#ng27.v326Mobile.v360Reference .v326ToolDock .railBtn span{font-size:6.8px!important}
#ng27.v326Mobile.v360Reference .v326PlaybackDock{bottom:18px!important;gap:10px!important}
#ng27.v326Mobile.v360Reference #playBtn{width:52px!important;height:52px!important;min-width:52px!important;min-height:52px!important}
#ng27.v326Mobile.v360Reference .cockpit>.v323EditorActions{min-height:44px!important;gap:6px!important}
#ng27.v326Mobile.v360Reference .cockpit>.v323EditorActions .v323EditorAction{height:44px!important;min-height:44px!important;border-radius:15px!important;font-size:9px!important}
#ng27.v326Mobile.v360Reference .cockpit>.timeline{padding:7px 8px 6px!important;border-radius:16px!important}
#ng27.v326Mobile.v360Reference .cockpit>.timeline .tlMeta{margin:0 1px 5px!important;font-size:7.5px!important}
#ng27.v326Mobile.v360Reference .cockpit>.timeline .track{height:36px!important}
#ng27.v326Mobile.v360Reference .cockpit>.timeline .trimRow{margin-top:3px!important;font-size:7px!important}

@media(max-width:390px){
  #ng27.v326Mobile.v360Reference{padding:4px 5px 94px!important}
  #ng27.v326Mobile.v360Reference .v360EditorHeader{min-height:48px!important;padding-right:60px!important}
  #ng27.v326Mobile.v360Reference .v360EditorTitle b{font-size:19px!important}
  #ng27.v326Mobile.v360Reference .v360EditorTitle span{font-size:9px!important}
  #ng27.v326Mobile.v360Reference .v326ToolDock .railBtn{width:42px!important;height:49px!important;min-width:42px!important;min-height:49px!important}
  #ng27.v326Mobile.v360Reference #playBtn{width:50px!important;height:50px!important;min-width:50px!important;min-height:50px!important}
  #ng27.v326Mobile.v360Reference .cockpit>.v323EditorActions .v323EditorAction{height:42px!important;min-height:42px!important;font-size:8.5px!important}
  #ng27.v326Mobile.v360Reference .cockpit>.timeline .track{height:32px!important}
}
</style>
'''


def _append_once(text: str, prereq: str, patch: str, label: str) -> str:
    if MARK in text:
        return text
    if prereq not in text:
        raise RuntimeError(f'V361 requires {label}')
    if '</body>' not in text:
        raise RuntimeError(f'V361 {label} body anchor missing')
    return text.replace('</body>', patch + '\n</body>', 1)


def patch_hub_text(text: str) -> str:
    return _append_once(text, 'V359_CREATOR_HUB_GAMEBAR_FIT', HUB_PATCH, 'V359 Creator Hub')


def patch_editor_text(text: str) -> str:
    return _append_once(text, 'V360_MOBILE_EDITOR_REFERENCE', EDITOR_PATCH, 'V360 Game Editor')


def main() -> None:
    hub = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path('/app/web/creator_hub_v156_component/index.html')
    editor = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else Path('/app/web/editor_2027_component/index.html')
    if not hub.is_file():
        raise SystemExit('V361 Creator Hub target missing: ' + str(hub))
    if not editor.is_file():
        raise SystemExit('V361 Editor target missing: ' + str(editor))

    hb = hub.read_text(encoding='utf-8')
    eb = editor.read_text(encoding='utf-8')
    ha = patch_hub_text(hb)
    ea = patch_editor_text(eb)
    hub.write_text(ha, encoding='utf-8')
    editor.write_text(ea, encoding='utf-8')
    print('V361 mobile regression repair applied hub_changed=', hb != ha, 'editor_changed=', eb != ea, flush=True)


if __name__ == '__main__':
    main()
