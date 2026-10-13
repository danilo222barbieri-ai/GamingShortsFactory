#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys
MARK='V373_CREATOR_HUB_HEADER_BREATH'
PATCH=r'''<!-- V373_CREATOR_HUB_HEADER_BREATH --><style id="v373CreatorHubHeaderBreath">@media(max-width:767px){#hub>.stage>.view{top:16px!important;bottom:0!important;height:auto!important}#hub .view[data-view="projects"].v373DraftsOnly #shortRows{display:none!important}}</style><script id="v373CreatorHubHeaderBreathRuntime">(()=>{const hub=document.getElementById('hub');const view=hub&&hub.querySelector('.view[data-view="projects"]');if(!view)return;const sync=()=>{const title=String(view.querySelector('#projectsViewTitle')?.textContent||'').trim().toLowerCase();view.classList.toggle('v373DraftsOnly',title==='bozze')};sync();try{new MutationObserver(sync).observe(view,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:['class','style']})}catch(_e){}})();</script>'''
def patch_text(text:str)->str:
 if MARK in text:return text
 if '</body>' not in text:raise RuntimeError('V373 Creator Hub body anchor missing')
 return text.replace('</body>',PATCH+'\n</body>',1)
def run(name,test,*args):
 here=Path(__file__).resolve().parent;f=here/name;t=here/test
 if not f.is_file() or not t.is_file():raise RuntimeError(name+' continuation missing')
 subprocess.run([sys.executable,str(f),*map(str,args)],check=True);subprocess.run([sys.executable,str(t),*map(str,args)],check=True)
def main()->None:
 path=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app/web/creator_hub_v156_component/index.html')
 if not path.is_file():raise SystemExit('V373 Creator Hub target missing: '+str(path))
 before=path.read_text(encoding='utf-8');after=patch_text(before);path.write_text(after,encoding='utf-8');print('V373 Creator Hub header breath + drafts cleanup applied changed=',before!=after,flush=True)
 run('fix_v374_creator_hub_spacing_live.py','test_v374_creator_hub_spacing_live.py',path)
 ai=Path('/app/web/ai_v221_component/index.html');run('fix_v375_ai_header_breath.py','test_v375_ai_header_breath.py',ai)
 app=Path('/app');here=Path(__file__).resolve().parent
 fix389=here/'fix_v389_mobile_editor_bounded_reset.py';clean390=here/'fix_v390_mobile_editor_owner_cleanup.py';test389=here/'test_v389_mobile_editor_bounded_reset.py';fix391=here/'fix_v391_mobile_editor_top_actions.py';test391=here/'test_v391_mobile_editor_top_actions.py';fix392=here/'fix_v392_mobile_editor_premium_skin.py';test392=here/'test_v392_mobile_editor_premium_skin.py'
 for f in (fix389,clean390,test389,fix391,test391,fix392,test392):
  if not f.is_file():raise RuntimeError(f.name+' continuation missing')
 subprocess.run([sys.executable,str(fix389),str(app)],check=True)
 subprocess.run([sys.executable,str(clean390),str(app)],check=True)
 subprocess.run([sys.executable,str(test389),str(app)],check=True)
 subprocess.run([sys.executable,str(fix391),str(app)],check=True)
 subprocess.run([sys.executable,str(test391),str(app)],check=True)
 subprocess.run([sys.executable,str(fix392),str(app)],check=True)
 subprocess.run([sys.executable,str(test392),str(app)],check=True)
if __name__=='__main__':main()
