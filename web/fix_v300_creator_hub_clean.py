#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path('/app')
HUB = ROOT / 'web/creator_hub_v156_component/index.html'
APP = ROOT / 'GamingShortsFactory_V154_STRUCTURAL_HOME.py'

CSS = r'''
/* V300 CREATOR HUB CLEAN REBUILD */
#hub[data-v300-layout="hub"]{
  width:100%!important;
  height:100dvh!important;
  max-width:1920px!important;
  margin:0 auto!important;
  padding:clamp(10px,1.4vh,16px) clamp(14px,1.7vw,26px)!important;
  display:grid!important;
  grid-template-rows:minmax(0,1fr)!important;
  gap:0!important;
  overflow:hidden!important;
  background:
    radial-gradient(circle at 9% 8%,rgba(126,214,255,.18),transparent 25%),
    radial-gradient(circle at 92% 9%,rgba(127,236,197,.15),transparent 26%),
    linear-gradient(180deg,#FEFFFF 0%,#F9FDFF 54%,#F4FAFF 100%)!important;
}
#hub[data-v300-layout="hub"]>.top{display:none!important}
#hub[data-v300-layout="hub"]>.stage{height:100%!important;min-height:0!important;overflow:hidden!important}
#hub[data-v300-layout="hub"] .view{inset:0!important}
#hub[data-v300-layout="hub"] .view[data-view="dashboard"] .dashboard{
  height:100%!important;
  min-height:0!important;
  display:grid!important;
  grid-template-rows:auto auto minmax(0,1fr)!important;
  gap:clamp(10px,1.25vh,15px)!important;
}
#hub[data-v300-layout="hub"] .profileCard{
  min-height:124px!important;
  padding:clamp(14px,1.7vh,19px) clamp(16px,1.5vw,24px)!important;
  grid-template-columns:auto minmax(0,1fr) auto!important;
  gap:clamp(13px,1.15vw,18px)!important;
  border:1px solid rgba(143,181,216,.22)!important;
  border-radius:28px!important;
  background:linear-gradient(135deg,rgba(255,255,255,.96),rgba(235,248,255,.90) 58%,rgba(240,251,247,.88))!important;
  box-shadow:0 16px 38px rgba(61,104,145,.085),inset 0 1px 0 #fff!important;
}
#hub[data-v300-layout="hub"] .profileCard .avatar{
  width:72px!important;height:72px!important;border-radius:22px!important;
  font-size:24px!important;box-shadow:0 9px 24px rgba(72,137,190,.11)!important;
}
#hub[data-v300-layout="hub"] .profileName{font-size:clamp(21px,1.65vw,27px)!important;line-height:1!important}
#hub[data-v300-layout="hub"] .profileMeta{font-size:clamp(10.8px,.82vw,12.5px)!important;margin-top:5px!important}
#hub[data-v300-layout="hub"] .badges{margin-top:7px!important;gap:6px!important}
#hub[data-v300-layout="hub"] .badge{font-size:9px!important;padding:5px 8px!important}
#hub[data-v300-layout="hub"] .profileSocials{margin-top:7px!important;gap:6px!important}
#hub[data-v300-layout="hub"] .profileSocials .socialDot{
  width:30px!important;height:30px!important;border-radius:10px!important;font-size:10px!important;
}
#hub[data-v300-layout="hub"] .profileAction{
  min-width:116px!important;min-height:42px!important;border-radius:14px!important;
  font-size:10.5px!important;background:linear-gradient(145deg,#E6F5FF,#EBF2FF)!important;
  color:#397BC0!important;box-shadow:0 8px 20px rgba(74,134,187,.08)!important;
}
#hub[data-v300-layout="hub"] .hubMural{
  margin:0!important;padding:1px 10px 3px!important;
  font-size:clamp(22px,1.75vw,29px)!important;line-height:1.02!important;
  text-align:center!important;color:#657FA8!important;transform:rotate(-2.2deg)!important;
}
#hub[data-v300-layout="hub"] .view[data-view="dashboard"] .folders{
  width:100%!important;height:100%!important;min-height:0!important;
  display:grid!important;grid-template-columns:repeat(5,minmax(0,1fr))!important;
  grid-template-rows:minmax(0,1fr)!important;gap:clamp(10px,1vw,15px)!important;
  border:0!important;border-radius:0!important;background:transparent!important;overflow:visible!important;
}
#hub[data-v300-layout="hub"] .view[data-view="dashboard"] .folder,
#hub[data-v300-layout="hub"] .view[data-view="dashboard"] .folder[data-folder]{
  min-width:0!important;min-height:0!important;height:100%!important;
  padding:clamp(15px,1.8vh,21px)!important;
  display:flex!important;flex-direction:column!important;justify-content:flex-start!important;align-items:stretch!important;
  border:1px solid rgba(143,181,216,.22)!important;border-radius:25px!important;
  background:rgba(255,255,255,.90)!important;
  box-shadow:0 14px 34px rgba(61,104,145,.075),inset 0 1px 0 #fff!important;
  backdrop-filter:blur(16px)!important;-webkit-backdrop-filter:blur(16px)!important;
  transition:transform .22s ease,box-shadow .22s ease,border-color .22s ease!important;
}
#hub[data-v300-layout="hub"] .view[data-view="dashboard"] .folder:hover,
#hub[data-v300-layout="hub"] .view[data-view="dashboard"] .folder:focus-visible{
  transform:translateY(-3px)!important;border-color:rgba(104,173,221,.38)!important;
  box-shadow:0 18px 40px rgba(61,104,145,.11),inset 0 1px 0 #fff!important;
}
#hub[data-v300-layout="hub"] .folder>div:first-child{display:block!important}
#hub[data-v300-layout="hub"] .folderTop{display:flex!important;align-items:center!important;justify-content:space-between!important;gap:8px!important}
#hub[data-v300-layout="hub"] .folderIcon{
  width:52px!important;height:52px!important;border-radius:17px!important;display:grid!important;place-items:center!important;
  font-size:20px!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.92)!important;
}
#hub[data-v300-layout="hub"] .folder[data-folder="profile"] .folderIcon{background:linear-gradient(145deg,#E3F3FF,#D7EBFF)!important;color:#397FC8!important}
#hub[data-v300-layout="hub"] .folder[data-folder="projects"] .folderIcon{background:linear-gradient(145deg,#EEE8FF,#E3DCFF)!important;color:#735DD1!important}
#hub[data-v300-layout="hub"] .folder[data-folder="live"] .folderIcon{background:linear-gradient(145deg,#F0E9FF,#E7DEFF)!important;color:#9146FF!important}
#hub[data-v300-layout="hub"] .folder[data-folder="social"] .folderIcon{background:linear-gradient(145deg,#DDF8EB,#D4F1E2)!important;color:#168B65!important}
#hub[data-v300-layout="hub"] .folder[data-folder="subscription"] .folderIcon{background:linear-gradient(145deg,#FFF2D4,#FFE8B8)!important;color:#B87916!important}
#hub[data-v300-layout="hub"] .folderArrow{font-size:26px!important;color:#91A9C0!important}
#hub[data-v300-layout="hub"] .folder h2{margin:18px 0 7px!important;font-size:clamp(16px,1.25vw,20px)!important;line-height:1.03!important}
#hub[data-v300-layout="hub"] .folder p{margin:0!important;font-size:clamp(10px,.76vw,12px)!important;line-height:1.32!important;color:#758AA3!important}
#hub[data-v300-layout="hub"] .folderFoot{display:block!important;margin-top:auto!important;padding-top:14px!important;font-size:9px!important;color:#8195AA!important}

#hub[data-v300-layout="hub"] .detail{height:100%!important;min-height:0!important;display:grid!important;grid-template-rows:auto minmax(0,1fr)!important;gap:10px!important}
#hub[data-v300-layout="hub"] .detailHead{min-height:52px!important;padding:0 4px!important}
#hub[data-v300-layout="hub"] .detailHeadText h2{font-size:clamp(22px,1.65vw,28px)!important}
#hub[data-v300-layout="hub"] .detailHeadText p{font-size:11px!important;margin-top:4px!important}
#hub[data-v300-layout="hub"] .detailCard{
  height:100%!important;min-height:0!important;padding:clamp(13px,1.5vh,18px)!important;border-radius:26px!important;
  border:1px solid rgba(143,181,216,.22)!important;background:rgba(255,255,255,.88)!important;
  box-shadow:0 14px 34px rgba(61,104,145,.07),inset 0 1px 0 #fff!important;
}
#hub[data-v300-layout="hub"] .view .backBtn{display:none!important}

#hub[data-v300-layout="hub"] .v300ProfileOverview{
  display:grid!important;grid-template-columns:repeat(4,minmax(0,1fr))!important;gap:10px!important;
  margin:12px 0 2px!important;
}
#hub[data-v300-layout="hub"] .v300ProfileStat{
  min-height:82px!important;padding:12px 13px!important;border:1px solid rgba(143,181,216,.20)!important;
  border-radius:17px!important;background:linear-gradient(145deg,#FFFFFF,#F3F9FF)!important;color:#163E73!important;
  text-align:left!important;cursor:pointer!important;box-shadow:0 8px 20px rgba(61,104,145,.055)!important;
}
#hub[data-v300-layout="hub"] .v300ProfileStat b{display:block!important;font-size:clamp(18px,1.4vw,24px)!important;line-height:1!important}
#hub[data-v300-layout="hub"] .v300ProfileStat span{display:block!important;margin-top:7px!important;font-size:10px!important;color:#7D90A8!important;font-weight:800!important}
#hub[data-v300-layout="hub"] .profileOnlyMural{margin:clamp(13px,2vh,22px) 0 8px!important;font-size:clamp(19px,1.5vw,25px)!important}
#hub[data-v300-layout="hub"] .profileOnlyScroller{overflow:hidden!important}
#hub[data-v300-layout="hub"] .logoutProfile{margin-top:auto!important}

@media(max-width:760px){
  #hub[data-v300-layout="hub"]{padding:7px 6px 6px!important}
  #hub[data-v300-layout="hub"] .view[data-view="dashboard"] .dashboard{gap:7px!important}
  #hub[data-v300-layout="hub"] .profileCard{
    min-height:91px!important;padding:8px 9px!important;grid-template-columns:auto minmax(0,1fr)!important;gap:9px!important;border-radius:20px!important;
  }
  #hub[data-v300-layout="hub"] .profileCard .avatar{width:48px!important;height:48px!important;border-radius:15px!important;font-size:17px!important}
  #hub[data-v300-layout="hub"] .profileName{font-size:17px!important}
  #hub[data-v300-layout="hub"] .profileMeta{font-size:9.5px!important;margin-top:3px!important}
  #hub[data-v300-layout="hub"] .badge{font-size:7.8px!important;padding:3px 5px!important}
  #hub[data-v300-layout="hub"] .profileSocials{margin-top:4px!important;gap:4px!important}
  #hub[data-v300-layout="hub"] .profileSocials .socialDot{width:24px!important;height:24px!important;border-radius:8px!important}
  #hub[data-v300-layout="hub"] .profileAction{display:none!important}
  #hub[data-v300-layout="hub"] .hubMural{font-size:clamp(18px,5vw,22px)!important;padding:0 4px 2px!important}
  #hub[data-v300-layout="hub"] .view[data-view="dashboard"] .folders{
    grid-template-columns:1fr!important;grid-template-rows:repeat(5,minmax(0,1fr))!important;gap:6px!important;overflow:hidden!important;
  }
  #hub[data-v300-layout="hub"] .view[data-view="dashboard"] .folder,
  #hub[data-v300-layout="hub"] .view[data-view="dashboard"] .folder[data-folder]{
    min-height:0!important;padding:8px 10px!important;border-radius:18px!important;
    display:grid!important;grid-template-columns:auto minmax(0,1fr) auto!important;grid-template-rows:auto auto!important;
    column-gap:10px!important;row-gap:1px!important;align-items:center!important;
  }
  #hub[data-v300-layout="hub"] .folder>div:first-child,#hub[data-v300-layout="hub"] .folderTop{display:contents!important}
  #hub[data-v300-layout="hub"] .folderIcon{grid-column:1!important;grid-row:1/3!important;width:39px!important;height:39px!important;border-radius:12px!important;font-size:15px!important}
  #hub[data-v300-layout="hub"] .folderArrow{grid-column:3!important;grid-row:1/3!important;font-size:21px!important}
  #hub[data-v300-layout="hub"] .folder h2{grid-column:2!important;grid-row:1!important;margin:0!important;font-size:14px!important;align-self:end!important}
  #hub[data-v300-layout="hub"] .folder p{grid-column:2!important;grid-row:2!important;margin:0!important;font-size:8.8px!important;line-height:1.18!important;align-self:start!important}
  #hub[data-v300-layout="hub"] .folderFoot{display:none!important}
  #hub[data-v300-layout="hub"] .detail{gap:6px!important}
  #hub[data-v300-layout="hub"] .detailHead{min-height:42px!important}
  #hub[data-v300-layout="hub"] .detailHeadText h2{font-size:18px!important}
  #hub[data-v300-layout="hub"] .detailHeadText p{font-size:9.5px!important}
  #hub[data-v300-layout="hub"] .detailCard{padding:8px!important;border-radius:19px!important}
  #hub[data-v300-layout="hub"] .v300ProfileOverview{grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:6px!important;margin:8px 0 2px!important}
  #hub[data-v300-layout="hub"] .v300ProfileStat{min-height:58px!important;padding:8px 9px!important;border-radius:13px!important}
  #hub[data-v300-layout="hub"] .v300ProfileStat b{font-size:17px!important}
  #hub[data-v300-layout="hub"] .v300ProfileStat span{font-size:8.5px!important;margin-top:4px!important}
  #hub[data-v300-layout="hub"] .profileOnlyMural{font-size:17px!important;margin:7px 0 4px!important}
}
/* END V300 CREATOR HUB CLEAN REBUILD */
'''

OVERVIEW = '''
      <div class="v300ProfileOverview" aria-label="Panoramica account">
       <button class="v300ProfileStat" type="button" data-v300-focus="shorts"><b id="v300ShortsCount">0</b><span>Shorts creati</span></button>
       <button class="v300ProfileStat" type="button" data-v300-focus="drafts"><b id="v300DraftsCount">0</b><span>Bozze</span></button>
       <button class="v300ProfileStat" type="button" data-v300-focus="subscription"><b id="v300PlanName">FREE</b><span>Piano</span></button>
       <button class="v300ProfileStat" type="button" data-v300-focus="social"><b id="v300SocialCount">0</b><span>Social collegati</span></button>
      </div>
'''

JS = r'''
<script id="v300HubRuntime">
(()=>{
 const root=document.getElementById('hub'); if(!root)return;
 const text=(q,fallback='0')=>{const el=root.querySelector(q);return el?String(el.textContent||fallback).trim():fallback};
 const sync=()=>{
   const shorts=root.querySelector('#v300ShortsCount'),drafts=root.querySelector('#v300DraftsCount'),plan=root.querySelector('#v300PlanName'),social=root.querySelector('#v300SocialCount');
   if(shorts)shorts.textContent=text('#shortProjectCount','0');
   if(drafts)drafts.textContent=text('#draftProjectCount','0');
   if(plan)plan.textContent=text('#profilePlanName','FREE');
   if(social)social.textContent=String(root.querySelectorAll('.socialCard.connected').length);
 };
 root.querySelectorAll('[data-v300-focus]').forEach(btn=>btn.addEventListener('click',()=>{
   window.postMessage({type:'GSF_HUB_FOCUS',section:btn.dataset.v300Focus},location.origin);
 }));
 const observer=new MutationObserver(sync);
 observer.observe(root,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:['class']});
 sync();setTimeout(sync,350);
})();
</script>
'''


def strip_v297_hub(text: str) -> str:
    text = text.replace(' data-v297-layout="hub"', '')
    text = re.sub(r'\n?/\* V297 DESK REBUILD — HUB \*/.*?/\* END V297 DESK REBUILD — HUB \*/\n?', '\n', text, flags=re.S)
    text = re.sub(r'\n?<script id="v297HubRuntime">.*?</script>\n?', '\n', text, flags=re.S)
    return text


def patch_hub():
    text = HUB.read_text(encoding='utf-8')
    text = strip_v297_hub(text)
    if 'V300 CREATOR HUB CLEAN REBUILD' in text:
        print('V300 Creator Hub already applied', flush=True)
        return
    if '<main id="hub">' not in text:
        raise RuntimeError('V300 Hub root anchor missing')
    text = text.replace('<main id="hub">', '<main id="hub" data-v300-layout="hub">', 1)
    text = text.replace('<h2>Le mie live</h2>', '<h2>Live</h2>', 1)
    profile_anchor = '      <div class="profileMural profileOnlyMural" aria-hidden="true">Questo è il tuo spazio,<br>fallo tuo</div>'
    if profile_anchor not in text:
        raise RuntimeError('V300 profile overview anchor missing')
    text = text.replace(profile_anchor, OVERVIEW + profile_anchor, 1)
    style_pos = text.rfind('</style>')
    if style_pos < 0:
        raise RuntimeError('V300 style anchor missing')
    text = text[:style_pos] + CSS + '\n' + text[style_pos:]
    if '</body>' not in text:
        raise RuntimeError('V300 body anchor missing')
    text = text.replace('</body>', JS + '\n</body>', 1)
    HUB.write_text(text, encoding='utf-8')
    print('V300 Creator Hub clean rebuild applied:', HUB, flush=True)


def patch_cache():
    text = APP.read_text(encoding='utf-8')
    text, count = re.subn(r'/creator-hub-v156/\?v=\d+', '/creator-hub-v156/?v=300', text)
    if count < 1 and '/creator-hub-v156/?v=300' not in text:
        raise RuntimeError('V300 Creator Hub cache anchor missing')
    APP.write_text(text, encoding='utf-8')
    print('V300 Creator Hub cache key: v300', flush=True)


if __name__ == '__main__':
    for path in (HUB, APP):
        if not path.is_file():
            raise RuntimeError('V300 required file missing: ' + str(path))
    patch_hub()
    patch_cache()
