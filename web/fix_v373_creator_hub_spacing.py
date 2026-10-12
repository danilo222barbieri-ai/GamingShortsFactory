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
 app=Path('/app');run('fix_v380_mobile_editor_unified.py','test_v380_mobile_editor_unified.py',app);run('fix_v381_mobile_editor_compact_full.py','test_v381_mobile_editor_compact_full.py',app);run('fix_v382_mobile_editor_true_full.py','test_v382_mobile_editor_true_full.py',app);run('fix_v383_mobile_editor_position.py','test_v383_mobile_editor_position.py',app);run('fix_v384_mobile_editor_no_scroll.py','test_v384_mobile_editor_no_scroll.py',app);run('fix_v385_mobile_editor_lower.py','test_v385_mobile_editor_lower.py',app);run('fix_v386_mobile_editor_reference_lock.py','test_v386_mobile_editor_reference_lock.py',app);run('fix_v387_mobile_editor_player_visibility.py','test_v387_mobile_editor_player_visibility.py',app);run('fix_v388_mobile_editor_reference_final.py','test_v388_mobile_editor_reference_final.py',app)
if __name__=='__main__':main()
