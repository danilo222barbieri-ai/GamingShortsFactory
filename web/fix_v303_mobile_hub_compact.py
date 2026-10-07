#!/usr/bin/env python3
from pathlib import Path

HUB = Path('/app/web/creator_hub_v156_component/index.html')
text = HUB.read_text(encoding='utf-8')

MARK = '/* V303 MOBILE HUB COMPACT */'
if MARK in text:
    print('V303 mobile Hub already applied')
    raise SystemExit(0)

css = r'''
/* V303 MOBILE HUB COMPACT */
.profileMobilePlan{display:none}
@media(max-width:760px){
  #hub[data-v300-layout="hub"] .view[data-view="dashboard"] .dashboard{
    grid-template-rows:auto minmax(0,1fr)!important;
    gap:6px!important;
  }
  #hub[data-v300-layout="hub"] .view[data-view="dashboard"] .hubMural{
    display:none!important;
  }
  #hub[data-v300-layout="hub"] .view[data-view="dashboard"] .folder[data-folder="subscription"]{
    display:none!important;
  }
  #hub[data-v300-layout="hub"] .view[data-view="dashboard"] .folders{
    grid-template-rows:repeat(4,minmax(0,1fr))!important;
    gap:6px!important;
    min-height:0!important;
  }
  #hub[data-v300-layout="hub"] .view[data-view="profile"] .profileOnlyMural{
    display:none!important;
  }
  #hub[data-v300-layout="hub"] .view[data-view="profile"] .profileMobilePlan{
    display:block!important;
    margin:9px 0 0!important;
    padding-top:9px!important;
    border-top:1px solid rgba(143,181,216,.16)!important;
  }
  #hub[data-v300-layout="hub"] .view[data-view="profile"] .profileOnlyScroller{
    overflow:auto!important;
    padding-bottom:2px!important;
  }
  #hub[data-v300-layout="hub"] .view[data-view="profile"] .profileMobilePlan .planRow{
    min-height:56px!important;
    padding:9px 10px!important;
    border-radius:14px!important;
  }
  #hub[data-v300-layout="hub"] .view[data-view="profile"] .profileMobilePlan .planBtn{
    font-size:9.5px!important;
    padding:7px 8px!important;
  }
  #hub[data-v300-layout="hub"] .view[data-view="profile"] .logoutProfile{
    margin-top:9px!important;
  }
}
/* END V303 MOBILE HUB COMPACT */
'''

text = text.replace('</style>', css + '\n</style>', 1)

anchor = '''      <div class="profileMural profileOnlyMural" aria-hidden="true">Questo è il tuo spazio,<br>fallo tuo</div>'''
mobile_plan = '''      <div class="profileGroup profilePlanGroup profileMobilePlan" aria-label="Abbonamento">
       <div class="profileGroupTitle">ABBONAMENTO</div>
       <div class="planRow"><div><b id="mobileProfilePlanName">FREE</b><span id="mobileProfilePlanText">Piano attuale</span></div><button class="planBtn" type="button" disabled>Gestione piano in arrivo</button></div>
      </div>
'''
if anchor not in text:
    raise SystemExit('V303: profile mural anchor not found')
text = text.replace(anchor, mobile_plan + anchor, 1)

render_anchor = '''   const ppt=$("#profilePlanText");if(ppt)ppt.textContent=a.connected?"Piano collegato al tuo account":"Collega un account per gestire il piano";'''
render_add = '''   const ppt=$("#profilePlanText");if(ppt)ppt.textContent=a.connected?"Piano collegato al tuo account":"Collega un account per gestire il piano";
   const mpn=$("#mobileProfilePlanName");if(mpn)mpn.textContent=String(a.plan||"FREE").toUpperCase();
   const mpt=$("#mobileProfilePlanText");if(mpt)mpt.textContent=a.connected?"Piano collegato al tuo account":"Collega un account per gestire il piano";'''
if render_anchor not in text:
    raise SystemExit('V303: plan render anchor not found')
text = text.replace(render_anchor, render_add, 1)

HUB.write_text(text, encoding='utf-8')
print('V303 mobile Creator Hub compact: applied')
