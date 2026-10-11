#!/usr/bin/env python3
from pathlib import Path
import sys

MARK='V331_PRIMARY_ACTIONS_ROUTING'
ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
HOME=ROOT/'web/home_v154_component/index.html'
APP=ROOT/'GamingShortsFactory_V154_STRUCTURAL_HOME.py'

SHELL_BLOCK=r'''
# V331_PRIMARY_ACTIONS_ROUTING — one canonical browser route for Editor + Crea Short.
if GSF_WEB_MODE:
    st.html(r"""
    <div style="display:none!important"><script>
    ((P)=>{
      if(P.__GSF_V331_PRIMARY_ACTIONS_ROUTING)return;
      P.__GSF_V331_PRIMARY_ACTIONS_ROUTING=true;
      const D=P.document;
      const EDITOR_KEY='gsf_editor_overlay_open_v223';
      const SHORT_KEY='gsf_short_overlay_open_v331';
      const hideOverlay=(o)=>{if(!o)return;o.classList.remove('is-open');o.style.opacity='0';o.style.visibility='hidden';o.style.pointerEvents='none';o.setAttribute('aria-hidden','true')};
      const closeCompeting=(keep)=>['gsf-social-overlay-v159','gsf-creator-hub-live-v160','gsf-editor-overlay-v220','gsf-ai-overlay-v221','gsf-account-overlay-v223','gsf-short-overlay-v331'].forEach(id=>{if(id!==keep)hideOverlay(D.getElementById(id))});
      const v331OpenEditor=(attempt=0)=>{const o=D.getElementById('gsf-editor-overlay-v220');if(!o){if(attempt<20)P.setTimeout(()=>v331OpenEditor(attempt+1),45+attempt*18);return false}const f=o.querySelector('iframe.gsf-editor-frame,iframe[title="Game Editor"]');if(f&&f.dataset.loaded!=='1'){f.src='/editor-live/?v=331';f.dataset.src='/editor-live/';f.dataset.loaded='1'}closeCompeting('gsf-editor-overlay-v220');o.classList.add('is-open');o.style.opacity='1';o.style.visibility='visible';o.style.pointerEvents='auto';o.setAttribute('aria-hidden','false');try{P.sessionStorage.setItem(EDITOR_KEY,'1');P.sessionStorage.setItem(SHORT_KEY,'0')}catch(_e){}return true};
      const ensureShortSurface=()=>{let o=D.getElementById('gsf-short-overlay-v331');if(o)return o;o=D.createElement('section');o.id='gsf-short-overlay-v331';o.setAttribute('aria-hidden','true');o.innerHTML=`<div class="v331ShortShell" role="dialog" aria-label="Crea Short"><button class="v331ShortClose" type="button">×</button><div class="v331Preview"><video playsinline controls preload="metadata"></video></div><div class="v331Actions"><button class="primary v331Create" type="button">CREA SHORT</button><button class="v331Editor" type="button">GAME EDITOR</button><button class="v331Draft" type="button">SALVA BOZZA</button></div></div>`;D.body.appendChild(o);o.querySelector('.v331ShortClose').onclick=()=>hideOverlay(o);o.querySelector('.v331Editor').onclick=()=>{hideOverlay(o);P.postMessage({type:'GSF_SHELL_NAV',target:'editor'},P.location.origin);v331OpenEditor()};return o};
      const v331OpenShort=()=>{const o=ensureShortSurface();closeCompeting('gsf-short-overlay-v331');o.classList.add('is-open');o.style.opacity='1';o.style.visibility='visible';o.style.pointerEvents='auto';o.setAttribute('aria-hidden','false');return true};
      P.addEventListener('message',(e)=>{if(e.origin!==P.location.origin||!e.data||e.data.type!=='GSF_SHELL_NAV')return;const target=String(e.data.target||'');if(target==='editor'){v331OpenEditor();return}if(target==='short'){v331OpenShort();return}},true);
    })(window.parent);
    </script></div>
    """, height=0)
'''

# V337_RESTART_SAFE_V331

def patch_home(text:str)->str:
    patterns=[
        'if(action==="short"){const opened=parentClick(["crea short","crea short finale","crea il tuo short"]);if(!opened)shellNav("short");value({event:"create_short",duration,engine});}',
        'if(action==="short"){parentClick(["crea short","crea short finale","crea il tuo short"]);value({event:"create_short",duration,engine});}',
    ]
    for old in patterns:
        if old in text:
            text=text.replace(old,'if(action==="short"){shellNav("short");value({event:"create_short",duration,engine});}',1)
            break

    marker='/* GSF_V331_EDITOR_DIRECT_LOAD */'
    if marker not in text:
        anchor='const panel=doc.getElementById(ids[target]);\n       handled=show(panel);'
        if anchor in text:
            inject='''const panel=doc.getElementById(ids[target]);\n       /* GSF_V331_EDITOR_DIRECT_LOAD */\n       if(target==="editor"&&panel){\n         const ef=panel.querySelector('iframe.gsf-editor-frame,iframe[title="Game Editor"]');\n         if(ef&&ef.dataset.loaded!=="1"){ef.src='/editor-live/?v=331';ef.dataset.src='/editor-live/';ef.dataset.loaded='1';}\n       }\n       handled=show(panel);'''
            text=text.replace(anchor,inject,1)
        else:
            # V343+ owns navigation globally. The old Home-local editor route was
            # intentionally removed, so V331 must become a no-op instead of
            # aborting startup on every restart/deploy.
            print('V331 restart-safe: Home-local editor route retired by canonical shell',flush=True)
    return text

def main():
    if not HOME.is_file(): raise SystemExit('V331 Home missing')
    if not APP.is_file(): raise SystemExit('V331 shell missing')
    home_before=HOME.read_text(encoding='utf-8');home_after=patch_home(home_before);HOME.write_text(home_after,encoding='utf-8')
    app_text=APP.read_text(encoding='utf-8');changed=False
    if MARK not in app_text:
        app_text=app_text.rstrip()+"\n\n"+SHELL_BLOCK+"\n";compile(app_text,str(APP),'exec');APP.write_text(app_text,encoding='utf-8');changed=True
    print('V331 primary actions routing applied home_changed=',home_before!=home_after,'shell_changed=',changed,flush=True)
if __name__=='__main__': main()
