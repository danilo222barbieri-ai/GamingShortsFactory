#!/usr/bin/env python3
"""V405 presentation over the real V396 publication actions, baked once."""
from pathlib import Path
import sys

MARK = 'V405_PUBLISH_SHORT_LIVE'
PATCH = r'''
<!-- V405_PUBLISH_SHORT_LIVE -->
<style>
#v396MobilePublishSurface{display:flex!important;flex-direction:column;gap:12px;align-items:center;text-align:center}
#v396MobilePublishSurface>.v396Mural,#v396MobilePublishSurface>.v396Actions{display:none!important}
.v405Title{margin:6px 0;font-size:clamp(26px,6vw,38px);line-height:1.05;color:#0d2a66;letter-spacing:-.04em}
.v405Preview{display:block;width:min(280px,70vw);max-height:52dvh;border-radius:23px;background:#07101d;object-fit:contain}
.v405Actions{display:grid;grid-template-columns:1fr 1fr;gap:8px;width:100%;max-width:520px}
.v405Actions button{border:1px solid rgba(143,181,216,.24);border-radius:16px;padding:13px;background:#fff;color:#28557e;font:inherit;font-weight:850;cursor:pointer}
.v405Actions .primary{grid-column:1/-1;background:#55aaf2;color:#fff;border:0}
.v405Actions button:disabled{opacity:.45;cursor:not-allowed}
.v405Sheet{position:fixed;inset:0;z-index:10000;display:none;align-items:flex-end;justify-content:center;background:rgba(20,40,65,.18);padding:10px}
.v405Sheet.open{display:flex}.v405Panel{width:min(560px,100%);max-height:85dvh;overflow:auto;border-radius:25px;background:#fff;padding:16px;text-align:left;display:grid;gap:10px}
.v405Close{justify-self:end;border:0;background:#edf6fd;border-radius:10px;padding:8px 14px;color:#28557e}
.v405Feedback{min-height:18px;color:#7185a6;font-size:12px}
</style>
<script id="v405PublishLive">
(()=>{
 const root=document.getElementById('v396MobilePublishSurface');if(!root||root.dataset.v405Live)return;root.dataset.v405Live='1';
 const title=document.createElement('h1');title.className='v405Title';title.textContent='Il tuo Short è pronto';root.prepend(title);
 const video=document.createElement('video');video.className='v405Preview';video.controls=true;video.playsInline=true;video.preload='metadata';video.hidden=true;title.after(video);
 const note=document.createElement('div');note.className='v405Feedback';note.setAttribute('role','status');root.append(note);
 const sheet=document.createElement('section');sheet.className='v405Sheet';sheet.id='v405PublishSheet';sheet.setAttribute('role','dialog');sheet.setAttribute('aria-label','Pubblica il tuo Short');sheet.setAttribute('aria-modal','true');sheet.setAttribute('aria-hidden','true');
 const panel=document.createElement('div');panel.className='v405Panel';const close=document.createElement('button');close.className='v405Close';close.textContent='Chiudi';panel.append(close);sheet.append(panel);root.append(sheet);
 [...root.querySelectorAll(':scope > .v396Panel')].forEach(el=>panel.append(el));
 const originalPublish=root.querySelector('#v396Publish');if(originalPublish)panel.append(originalPublish);
 const actions=document.createElement('div');actions.className='v405Actions';
 function button(label,action,handler){const b=document.createElement('button');b.type='button';b.dataset.action=action;b.textContent=label;b.onclick=handler;actions.append(b);return b}
 button('Modifica','edit',()=>parent.postMessage({type:'GSF_SHELL_NAV',target:'editor'},location.origin));
 const save=button('Salva','save',async()=>{save.disabled=true;try{const r=await fetch('/drafts/save-current',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json'},body:'{}'});const j=await r.json();if(!r.ok||!j.ok)throw new Error(j.error||'Salvataggio non riuscito');note.textContent='Salvato nei tuoi Progetti'}catch(e){note.textContent=e.message||'Salvataggio non riuscito'}finally{save.disabled=false}});
 const publish=button('PUBBLICA','publish',()=>{sheet.classList.add('open');sheet.setAttribute('aria-hidden','false');publish.setAttribute('aria-expanded','true');close.focus()});publish.className='primary';publish.setAttribute('aria-controls',sheet.id);publish.setAttribute('aria-expanded','false');
 const download=button('Scarica','download',()=>root.querySelector('#v396Download')?.click());
 root.insertBefore(actions,note);
 const hide=()=>{sheet.classList.remove('open');sheet.setAttribute('aria-hidden','true');publish.setAttribute('aria-expanded','false');publish.focus()};close.onclick=hide;sheet.onclick=e=>{if(e.target===sheet)hide()};document.addEventListener('keydown',e=>{if(e.key==='Escape'&&sheet.classList.contains('open'))hide()});
 async function sync(){try{const r=await fetch('/share/state',{cache:'no-store',credentials:'same-origin'});const state=await r.json();const ready=r.ok&&state.ok&&state.ready;publish.disabled=!ready;download.disabled=!ready;if(ready&&video.dataset.revision!==String(state.revision||'')){video.dataset.revision=String(state.revision||'');video.src='/share/final?revision='+encodeURIComponent(video.dataset.revision);video.hidden=false}if(!ready){delete video.dataset.revision;video.removeAttribute('src');video.hidden=true;title.textContent='Preparo il tuo Short'}else title.textContent='Il tuo Short è pronto'}catch(e){publish.disabled=true;download.disabled=true}}
 sync();setInterval(sync,2500);
})();
</script>
'''

def patch_text(text):
    if MARK in text:return text
    if 'V396_MOBILE_SHARE_PUBLISH_SURFACE' not in text or '</body>' not in text:
        raise RuntimeError('V405 requires the materialized real publication surface')
    return text.replace('</body>',PATCH+'\n</body>',1)

if __name__ == '__main__':
    root=Path(sys.argv[1] if len(sys.argv)>1 else '/app')
    path=root/'web/share_v156_component/index.html'
    path.write_text(patch_text(path.read_text(encoding='utf-8')),encoding='utf-8')
    print('V405 live publication surface: PASS')

