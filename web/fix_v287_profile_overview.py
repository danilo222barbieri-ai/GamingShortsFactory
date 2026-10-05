import re
from pathlib import Path

HUB = Path('/app/web/creator_hub_v156_component/index.html')
APP = Path('/app/GamingShortsFactory_V154_STRUCTURAL_HOME.py')

CSS = '''
/* V287 PROFILE OVERVIEW
   Real account summary cards inside Profile, optimized for mobile and desktop. */
#hub .profileOverviewGrid{display:grid!important;grid-template-columns:repeat(4,minmax(0,1fr))!important;gap:clamp(8px,1vw,12px)!important;margin:clamp(10px,1.5vh,16px) 0 0!important}
#hub .profileOverviewCard{border:1px solid rgba(143,181,216,.26)!important;border-radius:18px!important;background:linear-gradient(145deg,rgba(255,255,255,.98),rgba(241,248,255,.92))!important;min-height:92px!important;padding:clamp(12px,1.4vw,17px)!important;text-align:left!important;color:var(--ink)!important;cursor:pointer!important;box-shadow:0 10px 24px rgba(61,104,145,.055)!important}
#hub .profileOverviewCard small{display:block!important;color:#7C90A7!important;font-size:clamp(10px,.72vw,11.5px)!important;font-weight:850!important;line-height:1.2!important}
#hub .profileOverviewValue{display:block!important;margin-top:5px!important;font-size:clamp(24px,2vw,32px)!important;line-height:1!important;font-weight:950!important;letter-spacing:-.04em!important}
#hub .profileOverviewHint{display:block!important;margin-top:7px!important;color:#8798AD!important;font-size:clamp(9.5px,.66vw,10.5px)!important;font-weight:750!important}
#hub .profileOverviewActions{display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:clamp(8px,1vw,12px)!important;margin-top:clamp(9px,1.2vh,13px)!important}
#hub .profileOverviewAction{min-height:52px!important;display:flex!important;align-items:center!important;justify-content:space-between!important;gap:12px!important;border:1px solid rgba(143,181,216,.24)!important;border-radius:16px!important;padding:11px 14px!important;background:linear-gradient(145deg,rgba(234,246,255,.94),rgba(229,248,240,.88))!important;color:#3E7197!important;font-size:clamp(11px,.82vw,13px)!important;font-weight:900!important;cursor:pointer!important;text-align:left!important}
#hub .profileOverviewAction span:last-child{color:#7890A7!important;font-size:clamp(10px,.72vw,11.5px)!important;font-weight:850!important}
#hub .profileOnlyScroller .logoutProfile{margin-top:clamp(12px,1.6vh,18px)!important}
@media(max-width:760px){#hub .profileOnlyScroller{overflow:auto!important}#hub .profileOnlyMural{margin:14px 0 4px!important}#hub .profileOverviewGrid{grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:8px!important}#hub .profileOverviewCard{min-height:88px!important;padding:12px!important;border-radius:16px!important}#hub .profileOverviewCard small{font-size:10px!important}#hub .profileOverviewValue{font-size:26px!important}#hub .profileOverviewHint{font-size:9.5px!important}#hub .profileOverviewActions{grid-template-columns:1fr!important;gap:7px!important;margin-top:8px!important}#hub .profileOverviewAction{min-height:48px!important;padding:10px 12px!important;font-size:11px!important;border-radius:15px!important}}
/* END V287 PROFILE OVERVIEW */
'''

OVERVIEW_HTML = '''      <div class="profileMural profileOnlyMural" aria-hidden="true">Questo è il tuo spazio,<br>fallo tuo</div>
      <div class="profileOverviewGrid" aria-label="Panoramica profilo">
       <button class="profileOverviewCard" type="button" data-profile-overview="shorts"><small>SHORTS CREATI</small><b class="profileOverviewValue" id="profileOverviewShorts">0</b><span class="profileOverviewHint">Apri I miei Shorts</span></button>
       <button class="profileOverviewCard" type="button" data-profile-overview="drafts"><small>BOZZE</small><b class="profileOverviewValue" id="profileOverviewDrafts">0</b><span class="profileOverviewHint">Riprendi i progetti</span></button>
       <button class="profileOverviewCard" type="button" data-profile-overview="subscription"><small>IL TUO PIANO</small><b class="profileOverviewValue" id="profileOverviewPlan">FREE</b><span class="profileOverviewHint">Vedi abbonamento</span></button>
       <button class="profileOverviewCard" type="button" data-profile-overview="social"><small>SOCIAL COLLEGATI</small><b class="profileOverviewValue" id="profileOverviewSocial">0/5</b><span class="profileOverviewHint">Gestisci account</span></button>
      </div>
      <div class="profileOverviewActions">
       <button class="profileOverviewAction" type="button" data-profile-overview="subscription"><span>Gestisci il tuo abbonamento</span><span id="profileOverviewPlanMeta">FREE ›</span></button>
       <button class="profileOverviewAction" type="button" data-profile-overview="social"><span>Account collegati</span><span id="profileOverviewSocialMeta">0 di 5 ›</span></button>
      </div>
      <button class="logoutProfile" id="logoutProfile" type="button">Disconnetti dal Creator Hub</button>'''

RENDER_BINDINGS = '''   const povShorts=$("#profileOverviewShorts");if(povShorts)povShorts.textContent=String(u.shorts||0);
   const povDrafts=$("#profileOverviewDrafts");if(povDrafts)povDrafts.textContent=String(u.drafts||0);
   const profilePlan=String(a.plan||"FREE").toUpperCase();
   const povPlan=$("#profileOverviewPlan");if(povPlan)povPlan.textContent=profilePlan;
   const povSocial=$("#profileOverviewSocial");if(povSocial)povSocial.textContent=connectedCount+"/5";
   const povPlanMeta=$("#profileOverviewPlanMeta");if(povPlanMeta)povPlanMeta.textContent=profilePlan+" ›";
   const povSocialMeta=$("#profileOverviewSocialMeta");if(povSocialMeta)povSocialMeta.textContent=connectedCount+" di 5 ›";
'''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f'V287: anchor missing for {label}')
    return text.replace(old, new, 1)


def patch_hub() -> None:
    text = HUB.read_text(encoding='utf-8')
    before = text
    if 'V287 PROFILE OVERVIEW' not in text:
        text = replace_once(text, '</style>', CSS + '\n</style>', 'profile overview CSS')
    if 'id="profileOverviewShorts"' not in text:
        pattern = re.compile(r'\s*<div class="profileMural profileOnlyMural" aria-hidden="true">Questo è il tuo spazio,<br>fallo tuo</div>\s*<button class="logoutProfile" id="logoutProfile" type="button">Disconnetti dal Creator Hub</button>')
        text, count = pattern.subn('\n' + OVERVIEW_HTML, text, count=1)
        if count != 1:
            raise RuntimeError('V287: anchor missing for profile overview HTML')
    if 'const povShorts=$("#profileOverviewShorts")' not in text:
        anchor = '   const connectedCount=Number(st.social||0);\n'
        text = replace_once(text, anchor, anchor + RENDER_BINDINGS, 'profile overview state bindings')
    if '$$("[data-profile-overview]").forEach' not in text:
        anchor = '$$("[data-connect]").forEach(b=>b.onclick=()=>connectSocial(b.dataset.connect));'
        routed = '$$("[data-profile-overview]").forEach(b=>b.onclick=()=>openView(b.dataset.profileOverview));\n ' + anchor
        text = replace_once(text, anchor, routed, 'profile overview routing')
    HUB.write_text(text, encoding='utf-8')
    print('V287 Creator Hub profile overview applied:', HUB, 'changed=', text != before, flush=True)


def patch_shell() -> None:
    if not APP.is_file():
        return
    text = APP.read_text(encoding='utf-8')
    before = text
    text = text.replace('/creator-hub-v156/?v=286', '/creator-hub-v156/?v=287')
    if '/creator-hub-v156/?v=287' not in text:
        raise RuntimeError('V287: Creator Hub iframe cache marker missing')
    APP.write_text(text, encoding='utf-8')
    print('V287 Creator Hub cache bumped:', APP, 'changed=', text != before, flush=True)


if __name__ == '__main__':
    patch_hub()
    patch_shell()
