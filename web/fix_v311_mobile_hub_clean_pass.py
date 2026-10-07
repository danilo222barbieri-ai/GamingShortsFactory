#!/usr/bin/env python3
from pathlib import Path
import re
import sys

DEFAULT_HUB = Path('/app/web/creator_hub_v156_component/index.html')
DEFAULT_APP = Path('/app/GamingShortsFactory_V154_STRUCTURAL_HOME.py')
CACHE_KEY = '3114'

# V311.4 is the authoritative Creator Hub mobile source. It rewrites the served
# Hub after the historical patches have run, so the user-facing DOM contains the
# approved three-card dashboard and the shell contains one four-item Game Bar.
STYLE = r'''
<style id="v311HubForce">
/* V311 MOBILE HUB CLEAN PASS */
/* V311 SOURCE NORMALIZED */
/* V311 APPROVED CREATOR REFERENCE */
html,body{overflow:hidden!important}
#hub{height:100dvh!important;min-height:0!important;overflow:hidden!important;padding:8px 10px 6px!important;box-sizing:border-box!important}
#hub .stage{height:100%!important;min-height:0!important;overflow:hidden!important}

/* Approved dashboard: creator summary + Profile / Projects / Live. */
#hub .view[data-view="dashboard"]{height:100%!important;overflow:hidden!important}
#hub .view[data-view="dashboard"] .dashboard{
  height:100%!important;min-height:0!important;box-sizing:border-box!important;
  display:grid!important;grid-template-rows:136px minmax(0,1fr)!important;
  gap:12px!important;padding:0 0 94px!important;align-content:stretch!important;
}
#hub .view[data-view="dashboard"] .profileCard{
  min-height:136px!important;height:136px!important;padding:14px 16px!important;
  border:1px solid rgba(143,181,216,.22)!important;border-radius:28px!important;
  background:linear-gradient(135deg,rgba(255,255,255,.96),rgba(234,248,255,.91) 55%,rgba(235,251,244,.89))!important;
  box-shadow:0 14px 34px rgba(61,104,145,.075),inset 0 1px 0 rgba(255,255,255,.99)!important;
  grid-template-columns:auto minmax(0,1fr)!important;gap:15px!important;align-items:center!important;
}
#hub .view[data-view="dashboard"] .profileCard .avatar{
  width:76px!important;height:76px!important;border-radius:50%!important;font-size:24px!important;
  border:3px solid rgba(255,255,255,.96)!important;box-shadow:0 5px 18px rgba(40,154,224,.18)!important;
}
#hub .view[data-view="dashboard"] .profileName{font-size:22px!important;line-height:1!important;letter-spacing:-.025em!important}
#hub .view[data-view="dashboard"] .profileMeta{font-size:13px!important;line-height:1.2!important;margin-top:5px!important}
#hub .view[data-view="dashboard"] .badges{margin-top:8px!important;gap:7px!important}
#hub .view[data-view="dashboard"] .badge{font-size:10px!important;padding:5px 9px!important;border-radius:12px!important}
#hub .view[data-view="dashboard"] .profileSocials{margin-top:8px!important;gap:7px!important}
#hub .view[data-view="dashboard"] .profileSocials .socialDot{width:32px!important;height:32px!important;border-radius:11px!important;font-size:13px!important}
#hub .view[data-view="dashboard"] .profileAction{display:none!important}
#hub .view[data-view="dashboard"] .folders{
  width:100%!important;height:100%!important;min-height:0!important;display:grid!important;
  grid-template-columns:1fr!important;grid-template-rows:repeat(3,minmax(0,1fr))!important;
  gap:12px!important;align-content:stretch!important;overflow:hidden!important;
  border:0!important;border-radius:0!important;background:transparent!important;box-shadow:none!important;
}
#hub .view[data-view="dashboard"] .folder,
#hub .view[data-view="dashboard"] .folder[data-folder]{
  position:relative!important;width:100%!important;height:100%!important;min-height:0!important;margin:0!important;
  padding:15px 18px!important;border:1px solid rgba(143,181,216,.19)!important;border-radius:26px!important;
  background:rgba(255,255,255,.95)!important;box-shadow:0 12px 28px rgba(61,104,145,.07),inset 0 1px 0 rgba(255,255,255,.99)!important;
  display:grid!important;grid-template-columns:auto minmax(0,1fr) auto!important;grid-template-rows:auto auto!important;
  column-gap:16px!important;row-gap:3px!important;align-items:center!important;text-align:left!important;
}
#hub .view[data-view="dashboard"] .folder::after{display:none!important}
#hub .view[data-view="dashboard"] .folder>div:first-child,
#hub .view[data-view="dashboard"] .folderTop{display:contents!important}
#hub .view[data-view="dashboard"] .folderIcon{
  grid-column:1!important;grid-row:1/3!important;width:58px!important;height:58px!important;border-radius:20px!important;
  font-size:22px!important;align-self:center!important;display:grid!important;place-items:center!important;
}
#hub .view[data-view="dashboard"] .folderArrow{grid-column:3!important;grid-row:1/3!important;font-size:30px!important;align-self:center!important;color:#7f98b6!important}
#hub .view[data-view="dashboard"] .folder h2{grid-column:2!important;grid-row:1!important;margin:0!important;font-size:22px!important;line-height:1.02!important;align-self:end!important;letter-spacing:-.025em!important}
#hub .view[data-view="dashboard"] .folder p{grid-column:2!important;grid-row:2!important;margin:0!important;font-size:12.5px!important;line-height:1.18!important;align-self:start!important;color:#7589a2!important}
#hub .view[data-view="dashboard"] .folderFoot{display:none!important}

/* Profile: edit block plus only Abbonamento and Social collegati. */
#hub .view[data-view="profile"] .profileOnlyMural{display:none!important}
#hub .view[data-view="profile"] .profileOnlyScroller{overflow-y:auto!important;overflow-x:hidden!important;padding-bottom:104px!important}
#hub .view[data-view="profile"] .profileOverviewGrid{display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:10px!important;margin:12px 0 0!important}
#hub .view[data-view="profile"] .profileOverviewCard{display:flex!important;flex-direction:column!important;align-items:flex-start!important;justify-content:flex-start!important;min-height:118px!important;padding:14px!important;border-radius:20px!important}
#hub .view[data-view="profile"] .profileOverviewValue{margin-top:8px!important}
#hub .view[data-view="profile"] .profileOverviewHint{margin-top:auto!important;padding-top:9px!important}

/* Projects: first show two destinations, then the selected collection. */
#hub .view[data-view="projects"] .folderScroller{overflow-y:auto!important;overflow-x:hidden!important;padding-bottom:104px!important}
#hub #projectHubCards{display:grid;grid-template-columns:1fr;gap:12px;margin:2px 0 12px}
#hub .projectHubCard{min-height:118px;padding:16px 18px;border:1px solid rgba(143,181,216,.20);border-radius:24px;background:rgba(255,255,255,.96);box-shadow:0 10px 26px rgba(61,104,145,.065);display:grid;grid-template-columns:56px minmax(0,1fr) auto;gap:14px;align-items:center;text-align:left;color:var(--ink);cursor:pointer}
#hub .projectHubIcon{width:56px;height:56px;border-radius:18px;display:grid;place-items:center;background:linear-gradient(145deg,#e7f6ff,#eef0ff);font-size:21px;color:#318fd8}
#hub .projectHubCard b{display:block;font-size:20px;line-height:1.05}
#hub .projectHubCard small{display:block;margin-top:5px;font-size:11.5px;line-height:1.25;color:#7b8da4;font-weight:750}
#hub .projectHubCard i{font-style:normal;font-size:28px;color:#8198b4}

/* Live: Twitch and YouTube each own a direct section. */
#hub .view[data-view="live"] .folderScroller{overflow-y:auto!important;overflow-x:hidden!important;padding-bottom:104px!important}
#hub .view[data-view="live"] .livePane[data-live-pane="twitch"],
#hub .view[data-view="live"] .livePane[data-live-pane="youtube"]{display:block!important}
#hub .view[data-view="live"] .livePane[data-live-pane="youtube"]{margin-top:16px!important;padding-top:14px!important;border-top:1px solid rgba(143,181,216,.22)!important}
#hub .view[data-view="live"] .livePaneTitle{font-size:18px!important;margin:4px 4px 8px!important}
#hub .view[data-view="live"] .liveMiniFolders{display:grid!important;grid-template-columns:1fr!important;gap:8px!important}
#hub .view[data-view="live"] .liveMiniFolder{min-height:66px!important;padding:10px 11px!important;border-radius:17px!important}
/* END V311 MOBILE HUB CLEAN PASS */
</style>
'''

PROJECT_LANDING = '''      <div id="projectHubCards" aria-label="I miei progetti">
       <button class="projectHubCard" type="button" data-project-dest="shorts"><span class="projectHubIcon">▣</span><span><b>I miei Shorts</b><small>Short finali, pronti da rivedere e condividere.</small></span><i>›</i></button>
       <button class="projectHubCard" type="button" data-project-dest="drafts"><span class="projectHubIcon">□</span><span><b>Bozze</b><small>Progetti salvati da riprendere quando vuoi.</small></span><i>›</i></button>
      </div>
'''

YOUTUBE_NEW = '''<div class="livePane" data-live-pane="youtube">
       <div class="livePaneTitle">YouTube</div>
       <div class="liveMiniFolders youtubeLiveFolders">
        <div class="liveMiniFolder"><span>▶</span><div><b>Le tue live</b><small>Dirette YouTube salvate nel Creator Hub</small></div><i>›</i></div>
        <div class="liveMiniFolder"><span>▣</span><div><b>VOD</b><small>Replay completi delle live YouTube</small></div><i>›</i></div>
        <div class="liveMiniFolder"><span>✦</span><div><b>Highlights</b><small>Short e momenti estratti da YouTube</small></div><i>›</i></div>
       </div>
      </div>'''

RUNTIME = r'''
<script id="v311HubRuntime">
(()=>{
  document.documentElement.dataset.gsfHubVersion='3114';
  const $=(q)=>document.querySelector(q), $$=(q)=>[...document.querySelectorAll(q)];
  const showProjectLanding=()=>{
    const landing=$('#projectHubCards'); if(!landing)return;
    landing.style.display='grid';
    $$('[data-project-pane]').forEach((p)=>p.style.display='none');
    const title=$('#projectsViewTitle'), sub=$('#projectsViewSubtitle');
    if(title)title.textContent='I miei progetti';
    if(sub)sub.textContent='I miei Shorts e Bozze, nello stesso posto.';
  };
  const openProjectDest=(dest)=>{
    const landing=$('#projectHubCards'); if(landing)landing.style.display='none';
    $$('[data-project-pane]').forEach((p)=>p.style.display=p.dataset.projectPane===dest?'':'none');
    const title=$('#projectsViewTitle'), sub=$('#projectsViewSubtitle');
    if(title)title.textContent=dest==='shorts'?'I miei Shorts':'Bozze';
    if(sub)sub.textContent=dest==='shorts'?'Tutti gli Shorts completati e salvati nel Creator Hub.':'Progetti salvati da riprendere quando vuoi.';
  };
  const bind=()=>{
    $$('[data-project-dest]').forEach((b)=>{b.onclick=()=>openProjectDest(b.dataset.projectDest)});
    const projectFolder=$('[data-folder="projects"]');
    if(projectFolder)projectFolder.addEventListener('click',()=>setTimeout(showProjectLanding,0));
  };
  window.addEventListener('message',(e)=>{
    if(!e.data||e.data.type!=='GSF_HUB_FOCUS')return;
    if(String(e.data.section||'')==='projects')setTimeout(showProjectLanding,0);
  });
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',bind,{once:true});else bind();
})();
</script>
'''


def _strip_old_v311(text: str) -> str:
    text = re.sub(r'\s*<style id="v311HubForce">.*?</style>\s*(?=</head>)','\n',text,count=1,flags=re.DOTALL)
    text = re.sub(r'\s*<script id="v311HubRuntime">.*?</script>\s*(?=</body>)','\n',text,count=1,flags=re.DOTALL)
    return text


def _remove_profile_mobile_plan(text: str) -> str:
    token = '<div class="profileGroup profilePlanGroup profileMobilePlan"'
    start = text.find(token)
    if start < 0: return text
    line_start = text.rfind('\n',0,start)+1
    anchors=[text.find('<div class="profileMural profileOnlyMural"',start),text.find('<div class="profileOverviewGrid"',start)]
    anchors=[p for p in anchors if p>=0]
    if not anchors: raise RuntimeError('V311: profile mobile plan end anchor missing')
    return text[:line_start]+text[min(anchors):]


def _remove_profile_overview_actions(text: str) -> str:
    token='<div class="profileOverviewActions">'
    start=text.find(token)
    if start<0:return text
    line_start=text.rfind('\n',0,start)+1
    end=text.find('<button class="logoutProfile"',start)
    if end<0:raise RuntimeError('V311: profile overview actions end anchor missing')
    return text[:line_start]+text[end:]


def _remove_live_root(text: str) -> str:
    token='<div class="liveRootFolders">'
    start=text.find(token)
    if start<0:return text
    line_start=text.rfind('\n',0,start)+1
    end=text.find('<div class="livePane',start)
    if end<0:raise RuntimeError('V311: live root end anchor missing')
    return text[:line_start]+text[end:]


def _remove_dashboard_folder(text: str, name: str) -> str:
    return re.sub(r'^\s*<button class="folder" data-folder="'+re.escape(name)+r'">.*?</button>\s*$','',text,count=1,flags=re.MULTILINE)


def _remove_profile_card(text: str, name: str) -> str:
    return re.sub(r'^\s*<button class="profileOverviewCard"[^>]*data-profile-overview="'+re.escape(name)+r'".*?</button>\s*$','',text,count=1,flags=re.MULTILINE)


def _normalize_structure(text: str) -> str:
    # Dashboard: exactly Profile, Projects, Live.
    text=re.sub(r'^\s*<div class="hubMural">.*?</div>\s*$','',text,count=1,flags=re.MULTILINE)
    text=_remove_dashboard_folder(text,'social')
    text=_remove_dashboard_folder(text,'subscription')
    text=text.replace('<h2>Le mie live</h2>','<h2>Live</h2>',1)

    # Profile owns account/personal settings only: plan + social.
    text=_remove_profile_mobile_plan(text)
    text=_remove_profile_overview_actions(text)
    text=_remove_profile_card(text,'shorts')
    text=_remove_profile_card(text,'drafts')

    # Projects starts from a two-folder landing.
    if 'id="projectHubCards"' not in text:
        anchor='''    <div class="detailCard"><div class="folderScroller">\n      <div class="projectSection" data-project-pane="drafts">'''
        if anchor not in text: raise RuntimeError('V311: Projects landing anchor missing')
        text=text.replace(anchor,'    <div class="detailCard"><div class="folderScroller">\n'+PROJECT_LANDING+'      <div class="projectSection" data-project-pane="drafts">',1)

    # Bozze: no current-project / four-stat strip.
    text=re.sub(r'^[ \t]*\$\("#projectRows"\)\.innerHTML=.*?;\s*$','   $("#projectRows").innerHTML="";',text,count=1,flags=re.MULTILINE)

    # Live: direct Twitch + YouTube sections.
    text=_remove_live_root(text)
    text=re.sub(r'^\s*<div class="livePane" data-live-pane="highlights">.*?</div></div>\s*$','',text,count=1,flags=re.MULTILINE)
    if 'youtubeLiveFolders' not in text:
        text,count=re.subn(r'^\s*<div class="livePane" data-live-pane="youtube">.*?</div></div>\s*$',YOUTUBE_NEW,text,count=1,flags=re.MULTILINE)
        if count!=1:raise RuntimeError('V311: YouTube Live pane anchor missing')
    return text


def patch_hub_text(text: str) -> str:
    if ('V311 APPROVED CREATOR REFERENCE' in text and 'id="v311HubForce"' in text and 'id="v311HubRuntime"' in text and "gsfHubVersion='3114'" in text and 'youtubeLiveFolders' in text and 'id="projectHubCards"' in text):
        return text
    text=_strip_old_v311(text)
    text=_normalize_structure(text)
    if '</head>' not in text:raise RuntimeError('V311: head anchor missing')
    if '</body>' not in text:raise RuntimeError('V311: body anchor missing')
    text=text.replace('</head>',STYLE+'\n</head>',1)
    text=text.replace('</body>',RUNTIME+'\n</body>',1)
    return text


def _page_nav_button_pattern(active: str) -> re.Pattern:
    return re.compile(r'<button class="gsf-page-nav-item"(?=[^>]*data-active="'+re.escape(active)+r'")[^>]*>.*?</button>',re.DOTALL)


def _replace_gamebar(text: str) -> str:
    # Already normalized.
    if ('data-section="projects" data-active="projects"' in text and '<span>Progetti</span>' in text and '<span>I miei Shorts</span>' not in text and '<span>Bozze</span>' not in text and 'data-target="hub" data-section="dashboard" data-active="home"' in text):
        return text

    home_pat=_page_nav_button_pattern('home')
    m=home_pat.search(text)
    if m:
        home=m.group(0)
        home=re.sub(r'\sdata-section="[^"]*"','',home)
        home=re.sub(r'data-target="[^"]*"','data-target="hub"',home,count=1)
        home=home.replace('data-active="home"','data-section="dashboard" data-active="home"',1)
        text=home_pat.sub(home,text,count=1)
    else:
        # The production shell guaranteed by V286/V302 can have no page-level
        # Home button at all. Build Home from the real Hub button instead of
        # aborting startup, then let the normal pass reduce the bar to 4 items.
        hub_pat=_page_nav_button_pattern('hub')
        hub_match=hub_pat.search(text)
        if not hub_match:raise RuntimeError('V311: global Hub Game Bar button missing')
        home=hub_match.group(0)
        home=home.replace('data-active="hub"','data-active="home"',1)
        home=re.sub(r'\sdata-section="[^"]*"','',home)
        home=re.sub(r'data-target="[^"]*"','data-target="hub"',home,count=1)
        home=home.replace('data-active="home"','data-section="dashboard" data-active="home"',1)
        home=re.sub(r'<span>.*?</span>','<span>Home</span>',home,count=1,flags=re.DOTALL)
        text=text[:hub_match.start()]+home+'\n'+text[hub_match.start():]

    shorts_pat=_page_nav_button_pattern('shorts')
    text,count=shorts_pat.subn('',text,count=1)
    if count!=1:raise RuntimeError('V311: global Shorts Game Bar button missing')

    drafts_pat=_page_nav_button_pattern('drafts')
    m=drafts_pat.search(text)
    if not m:raise RuntimeError('V311: global Bozze Game Bar button missing')
    projects=m.group(0).replace('data-section="drafts"','data-section="projects"',1).replace('data-active="drafts"','data-active="projects"',1).replace('<span>Bozze</span>','<span>Progetti</span>',1)
    text=drafts_pat.sub(projects,text,count=1)

    if "activeKey==='projects'" not in text:
        anchor="else if(activeKey==='live') active=(lastTarget==='hub'&&lastSection==='live');"
        if anchor not in text:raise RuntimeError('V311: global Game Bar active-state anchor missing')
        text=text.replace(anchor,"else if(activeKey==='projects') active=(lastTarget==='hub'&&lastSection==='projects');\n"+anchor,1)

    text=re.sub(
        r"else if\(target==='hub'\) active=\(lastTarget==='hub'&&lastSection!=='drafts'&&lastSection!=='shorts'&&lastSection!=='live'\);",
        "else if(target==='hub') active=(lastTarget==='hub'&&(lastSection==='dashboard'||!lastSection));",
        text,count=1,
    )
    text=re.sub(r'grid-template-columns\s*:\s*repeat\(5\s*,\s*minmax\(0\s*,\s*1fr\)\)', 'grid-template-columns:repeat(4,minmax(0,1fr))', text)
    return text


def patch_shell_text(text: str) -> str:
    text=_replace_gamebar(text)
    target=f'/creator-hub-v156/?v={CACHE_KEY}'
    if target not in text:
        text,count=re.subn(r'/creator-hub-v156/\?v=[^"\'&\s]+',target,text)
        if count<1:raise RuntimeError('V311: Creator Hub shell cache anchor missing')
    return text


def main():
    hub=Path(sys.argv[1]) if len(sys.argv)>1 else DEFAULT_HUB
    app=Path(sys.argv[2]) if len(sys.argv)>2 else DEFAULT_APP
    if not hub.is_file():raise SystemExit(f'V311 target missing: {hub}')
    if not app.is_file():raise SystemExit(f'V311 shell missing: {app}')

    before=hub.read_text(encoding='utf-8')
    after=patch_hub_text(before)
    hub.write_text(after,encoding='utf-8')

    shell_before=app.read_text(encoding='utf-8')
    shell_after=patch_shell_text(shell_before)
    compile(shell_after,str(app),'exec')
    app.write_text(shell_after,encoding='utf-8')

    print('V311 Creator Hub approved reference applied:',hub,'changed=',before!=after,flush=True)
    print('V311 four-item Game Bar + cache key:','v='+CACHE_KEY,'changed=',shell_before!=shell_after,flush=True)


if __name__=='__main__':
    main()
