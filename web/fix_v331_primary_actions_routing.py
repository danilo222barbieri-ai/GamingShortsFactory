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

      if(!D.getElementById('gsf-v331-primary-actions-style')){
        const style=D.createElement('style');
        style.id='gsf-v331-primary-actions-style';
        style.textContent=`
          #gsf-short-overlay-v331{
            position:fixed;inset:0;z-index:2147483654;
            display:flex;align-items:center;justify-content:center;
            padding:44px 14px 118px;
            background:
              radial-gradient(circle at 12% 8%,rgba(111,209,255,.15),transparent 24%),
              radial-gradient(circle at 88% 10%,rgba(106,229,185,.13),transparent 25%),
              linear-gradient(180deg,#FEFFFF 0%,#F8FCFF 100%);
            opacity:0;visibility:hidden;pointer-events:none;
            transition:opacity .18s ease,visibility .18s ease;
          }
          #gsf-short-overlay-v331.is-open{opacity:1;visibility:visible;pointer-events:auto}
          #gsf-short-overlay-v331 .v331ShortShell{
            position:relative;width:min(680px,calc(100vw - 28px));height:100%;min-height:0;
            display:grid;grid-template-rows:auto 1fr auto;gap:10px;
            border:1px solid rgba(150,184,214,.24);border-radius:24px;
            background:rgba(255,255,255,.86);box-shadow:0 22px 58px rgba(49,94,135,.12);
            overflow:hidden;padding:14px;
          }
          #gsf-short-overlay-v331 .v331ShortHead{display:flex;align-items:flex-start;justify-content:space-between;gap:10px}
          #gsf-short-overlay-v331 .v331ShortHead h2{margin:0;color:#0D2A66;font:900 22px/1.05 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
          #gsf-short-overlay-v331 .v331ShortHead p{margin:4px 0 0;color:#7185A6;font:700 10px/1.25 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
          #gsf-short-overlay-v331 .v331ShortClose{width:32px;height:32px;flex:0 0 32px;border-radius:11px;border:1px solid rgba(150,184,214,.26);background:#fff;color:#6C81A1;font-size:20px;line-height:1}
          #gsf-short-overlay-v331 .v331ShortStage{min-height:0;display:flex;align-items:center;justify-content:center;overflow:hidden}
          #gsf-short-overlay-v331 .v331Preview{
            position:relative;height:min(100%,470px);aspect-ratio:9/16;max-width:78%;
            border-radius:20px;border:1px solid rgba(112,187,230,.30);overflow:hidden;
            background:linear-gradient(155deg,#EFF8FF,#F7FFFC);box-shadow:0 16px 40px rgba(56,108,151,.10);
            display:grid;place-items:center;color:#6F88A8;text-align:center;padding:18px;
          }
          #gsf-short-overlay-v331 .v331Preview video{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;background:#000}
          #gsf-short-overlay-v331 .v331PreviewText{font:800 11px/1.25 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;letter-spacing:.02em}
          #gsf-short-overlay-v331 .v331PreviewText span{font-weight:700;font-size:9px;color:#7C91AC}
          #gsf-short-overlay-v331 .v331Actions{display:grid;grid-template-columns:1.15fr 1fr 1fr;gap:7px}
          #gsf-short-overlay-v331 .v331Actions button{min-height:44px;border-radius:14px;border:1px solid rgba(146,182,213,.26);background:#F7FBFF;color:#56718F;font:900 9px/1.1 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;padding:7px 8px}
          #gsf-short-overlay-v331 .v331Actions .primary{background:#DDEFFF;color:#136FCF;border-color:rgba(92,157,218,.28)}
          #gsf-short-overlay-v331 .v331Status{position:absolute;left:14px;right:14px;bottom:66px;text-align:center;color:#6E86A5;font:800 9px/1.2 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;pointer-events:none}
          @media(max-width:760px){
            #gsf-short-overlay-v331{padding:34px 10px calc(112px + env(safe-area-inset-bottom))}
            #gsf-short-overlay-v331 .v331ShortShell{width:100%;border-radius:21px;padding:11px;gap:8px}
            #gsf-short-overlay-v331 .v331ShortHead h2{font-size:20px}
            #gsf-short-overlay-v331 .v331Preview{height:min(100%,420px);max-width:74%}
            #gsf-short-overlay-v331 .v331Actions{grid-template-columns:1fr 1fr 1fr;gap:5px}
            #gsf-short-overlay-v331 .v331Actions button{min-height:42px;font-size:8px;padding:6px 4px}
          }
        `;
        D.head.appendChild(style);
      }

      const hideOverlay=(o)=>{
        if(!o)return;
        o.classList.remove('is-open');
        o.style.opacity='0';o.style.visibility='hidden';o.style.pointerEvents='none';
        o.setAttribute('aria-hidden','true');
      };
      const closeCompeting=(keep)=>{
        ['gsf-social-overlay-v159','gsf-creator-hub-live-v160','gsf-editor-overlay-v220','gsf-ai-overlay-v221','gsf-account-overlay-v223','gsf-short-overlay-v331']
          .forEach(id=>{if(id!==keep)hideOverlay(D.getElementById(id))});
      };

      const v331OpenEditor=(attempt=0)=>{
        const o=D.getElementById('gsf-editor-overlay-v220');
        if(!o){if(attempt<20)P.setTimeout(()=>v331OpenEditor(attempt+1),45+attempt*18);return false}
        const f=o.querySelector('iframe.gsf-editor-frame,iframe[title="Game Editor"]');
        if(f&&f.dataset.loaded!=='1'){
          f.src='/editor-live/?v=331';
          f.dataset.src='/editor-live/';
          f.dataset.loaded='1';
        }
        closeCompeting('gsf-editor-overlay-v220');
        o.classList.add('is-open');
        o.style.opacity='1';o.style.visibility='visible';o.style.pointerEvents='auto';
        o.setAttribute('aria-hidden','false');
        try{P.sessionStorage.setItem(EDITOR_KEY,'1');P.sessionStorage.setItem(SHORT_KEY,'0')}catch(_e){}
        return true;
      };

      const ensureShortSurface=()=>{
        let o=D.getElementById('gsf-short-overlay-v331');
        if(o)return o;
        o=D.createElement('section');
        o.id='gsf-short-overlay-v331';o.setAttribute('aria-hidden','true');
        o.innerHTML=`
          <div class="v331ShortShell" role="dialog" aria-modal="false" aria-label="Crea Short">
            <div class="v331ShortHead"><div><h2>Crea Short</h2><p>La tua scelta finale resta nel progetto finché non decidi di crearla.</p></div><button class="v331ShortClose" type="button" aria-label="Chiudi">×</button></div>
            <div class="v331ShortStage"><div class="v331Preview"><div class="v331PreviewText">ANTEPRIMA 9:16<br><span>Carica o scegli un gameplay per vedere qui il tuo Short.</span></div><video playsinline controls preload="metadata" hidden></video></div></div>
            <div class="v331Actions"><button class="primary v331Create" type="button">CREA SHORT</button><button class="v331Editor" type="button">GAME EDITOR</button><button class="v331Draft" type="button">SALVA BOZZA</button></div>
            <div class="v331Status" aria-live="polite"></div>
          </div>`;
        D.body.appendChild(o);
        const status=o.querySelector('.v331Status');
        const setStatus=(txt)=>{if(status)status.textContent=String(txt||'')};
        o.querySelector('.v331ShortClose').addEventListener('click',()=>{
          hideOverlay(o);try{P.sessionStorage.setItem(SHORT_KEY,'0')}catch(_e){}
        });
        o.querySelector('.v331Editor').addEventListener('click',()=>{
          hideOverlay(o);try{P.sessionStorage.setItem(SHORT_KEY,'0')}catch(_e){}
          P.postMessage({type:'GSF_SHELL_NAV',target:'editor'},P.location.origin);
          v331OpenEditor();
        });
        o.querySelector('.v331Create').addEventListener('click',()=>{
          let b=D.querySelector('.st-key-gsf-major-create-short button,.st-key-create_final_short_v54 button');
          if(!b){
            b=[...D.querySelectorAll('button,[role="button"]')].find(x=>{
              const t=String(x.innerText||x.textContent||'').trim().toLowerCase();
              return t==='crea short'||t.includes('crea short finale')||t.includes('crea il tuo short');
            });
          }
          if(!b){setStatus('Carica un gameplay prima di creare lo Short.');return}
          if(b.disabled||b.getAttribute('aria-disabled')==='true'){setStatus('Il gameplay non è ancora pronto per il render.');return}
          setStatus('Creazione Short…');
          b.click();
        });
        o.querySelector('.v331Draft').addEventListener('click',async()=>{
          setStatus('Salvataggio…');
          try{
            const r=await P.fetch('/drafts/save-current',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json'},body:'{}'});
            const j=await r.json().catch(()=>({}));
            setStatus(r.ok&&j&&j.ok?'Bozza salvata.':(j&&j.error)||'Nessuna modifica da salvare.');
          }catch(_e){setStatus('Salvataggio non riuscito. Riprova.')}
        });
        const v=o.querySelector('video');
        if(v){
          v.src='/editor-media/current?v=331';
          v.addEventListener('loadedmetadata',()=>{v.hidden=false;const t=o.querySelector('.v331PreviewText');if(t)t.style.display='none'},{once:true});
          v.addEventListener('error',()=>{v.hidden=true},{once:true});
        }
        return o;
      };

      const v331OpenShort=()=>{
        const o=ensureShortSurface();
        closeCompeting('gsf-short-overlay-v331');
        o.classList.add('is-open');
        o.style.opacity='1';o.style.visibility='visible';o.style.pointerEvents='auto';
        o.setAttribute('aria-hidden','false');
        try{P.sessionStorage.setItem(SHORT_KEY,'1');P.sessionStorage.setItem(EDITOR_KEY,'0')}catch(_e){}
        return true;
      };

      P.addEventListener('message',(e)=>{
        if(e.origin!==P.location.origin||!e.data||e.data.type!=='GSF_SHELL_NAV')return;
        const target=String(e.data.target||'');
        if(target==='editor'){v331OpenEditor();return}
        if(target==='short'){v331OpenShort();return}
        if(target==='home'||target==='close'||target==='hub'||target==='ai'||target==='social'||target==='account'){
          const s=D.getElementById('gsf-short-overlay-v331');if(s)hideOverlay(s);
          try{P.sessionStorage.setItem(SHORT_KEY,'0')}catch(_e){}
        }
      },true);
      try{if(P.sessionStorage.getItem(SHORT_KEY)==='1')P.setTimeout(v331OpenShort,70)}catch(_e){}
    })(window.parent);
    </script></div>
    """, height=0)
'''


def patch_home(text:str)->str:
    patterns=[
        'if(action==="short"){const opened=parentClick(["crea short","crea short finale","crea il tuo short"]);if(!opened)shellNav("short");value({event:"create_short",duration,engine});}',
        'if(action==="short"){parentClick(["crea short","crea short finale","crea il tuo short"]);value({event:"create_short",duration,engine});}',
    ]
    replaced=False
    for old in patterns:
        if old in text:
            text=text.replace(old,'if(action==="short"){shellNav("short");value({event:"create_short",duration,engine});}',1)
            replaced=True
            break
    if not replaced and 'if(action==="short"){shellNav("short")' not in text:
        raise RuntimeError('V331 Home Short action anchor missing')

    marker='/* GSF_V331_EDITOR_DIRECT_LOAD */'
    if marker not in text:
        anchor='const panel=doc.getElementById(ids[target]);\n       handled=show(panel);'
        if anchor not in text:
            raise RuntimeError('V331 Home editor panel anchor missing')
        inject='''const panel=doc.getElementById(ids[target]);\n       /* GSF_V331_EDITOR_DIRECT_LOAD */\n       if(target==="editor"&&panel){\n         const ef=panel.querySelector('iframe.gsf-editor-frame,iframe[title="Game Editor"]');\n         if(ef&&ef.dataset.loaded!=="1"){ef.src='/editor-live/?v=331';ef.dataset.src='/editor-live/';ef.dataset.loaded='1';}\n       }\n       handled=show(panel);'''
        text=text.replace(anchor,inject,1)
    return text


def main():
    if not HOME.is_file(): raise SystemExit('V331 Home missing')
    if not APP.is_file(): raise SystemExit('V331 shell missing')
    home_before=HOME.read_text(encoding='utf-8')
    home_after=patch_home(home_before)
    HOME.write_text(home_after,encoding='utf-8')

    app_text=APP.read_text(encoding='utf-8')
    changed=False
    if MARK not in app_text:
        app_text=app_text.rstrip()+"\n\n"+SHELL_BLOCK+"\n"
        compile(app_text,str(APP),'exec')
        APP.write_text(app_text,encoding='utf-8')
        changed=True
    print('V331 primary actions routing applied home_changed=',home_before!=home_after,'shell_changed=',changed,flush=True)

if __name__=='__main__': main()
