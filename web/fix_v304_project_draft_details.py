#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path('/app')
HUB = ROOT / 'web/creator_hub_v156_component/index.html'
APP = ROOT / 'GamingShortsFactory_V154_STRUCTURAL_HOME.py'
text = HUB.read_text(encoding='utf-8')
MARK = '/* V304 PROJECT + DRAFT DETAILS */'
if MARK in text:
    print('V304 project/draft details already applied', flush=True)
    raise SystemExit(0)

css = r'''
/* V304 PROJECT + DRAFT DETAILS */
#hub[data-v300-layout="hub"] .view[data-view="projects"] #projectRows .projectBox,
#hub[data-v300-layout="hub"] .view[data-view="projects"] #draftRows .row{
  cursor:pointer;
  transition:transform .16s ease,border-color .16s ease,box-shadow .16s ease;
}
#hub[data-v300-layout="hub"] .view[data-view="projects"] #projectRows .projectBox:hover,
#hub[data-v300-layout="hub"] .view[data-view="projects"] #draftRows .row:hover{
  transform:translateY(-1px);
  border-color:rgba(83,157,217,.34);
  box-shadow:0 8px 20px rgba(61,104,145,.06);
}
#hub[data-v300-layout="hub"] .v304ItemDetail{
  height:100%;min-height:0;display:none;overflow:auto;
  padding:2px 1px 4px;
}
#hub[data-v300-layout="hub"] .v304ItemDetail.active{display:flex;flex-direction:column}
#hub[data-v300-layout="hub"] .v304DetailTop{display:flex;align-items:center;gap:10px;margin-bottom:12px}
#hub[data-v300-layout="hub"] .v304DetailBack{
  border:0;border-radius:12px;padding:8px 11px;background:#EDF6FF;color:#467EA9;
  font-size:11px;font-weight:900;cursor:pointer;
}
#hub[data-v300-layout="hub"] .v304DetailEyebrow{font-size:10px;font-weight:950;letter-spacing:.08em;color:#8A9BAF}
#hub[data-v300-layout="hub"] .v304DetailCard{
  border:1px solid rgba(144,181,214,.22);border-radius:22px;background:#fff;
  padding:clamp(15px,1.7vw,22px);box-shadow:0 12px 30px rgba(61,104,145,.06);
}
#hub[data-v300-layout="hub"] .v304DetailCard h3{margin:0;font-size:clamp(20px,1.55vw,26px);line-height:1.05;color:#173A72}
#hub[data-v300-layout="hub"] .v304DetailMeta{margin-top:6px;color:#8798AE;font-size:11px;font-weight:750}
#hub[data-v300-layout="hub"] .v304Rename{margin-top:18px}
#hub[data-v300-layout="hub"] .v304Rename label{display:block;margin-bottom:6px;color:#758BA1;font-size:10px;font-weight:950;letter-spacing:.08em}
#hub[data-v300-layout="hub"] .v304RenameRow{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:8px}
#hub[data-v300-layout="hub"] .v304Rename input{
  min-width:0;border:1px solid rgba(143,181,216,.30);border-radius:13px;padding:11px 12px;
  background:#FBFDFF;color:#173A58;font:inherit;font-size:13px;font-weight:850;outline:none;
}
#hub[data-v300-layout="hub"] .v304Rename input:focus{border-color:rgba(74,155,220,.55);box-shadow:0 0 0 3px rgba(96,180,238,.10)}
#hub[data-v300-layout="hub"] .v304Btn{
  border:0;border-radius:13px;padding:10px 13px;background:#E8F5FF;color:#397FC8;
  font:inherit;font-size:11px;font-weight:950;cursor:pointer;min-height:42px;
}
#hub[data-v300-layout="hub"] .v304Btn.primary{background:linear-gradient(145deg,#DFF3FF,#DDF8EE);color:#2E7395}
#hub[data-v300-layout="hub"] .v304Btn.danger{background:#FFF0F1;color:#AA5967}
#hub[data-v300-layout="hub"] .v304Actions{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:9px;margin-top:14px}
#hub[data-v300-layout="hub"] .v304Actions[data-kind="draft"]{grid-template-columns:repeat(2,minmax(0,1fr))}
#hub[data-v300-layout="hub"] .v304SaveDraft{display:block}
#hub[data-v300-layout="hub"] .v304Actions[data-kind="draft"] .v304SaveDraft{display:none}
@media(max-width:760px){
  #hub[data-v300-layout="hub"] .v304ItemDetail{padding:0}
  #hub[data-v300-layout="hub"] .v304DetailTop{margin-bottom:8px}
  #hub[data-v300-layout="hub"] .v304DetailBack{font-size:10.5px;padding:7px 9px}
  #hub[data-v300-layout="hub"] .v304DetailCard{padding:14px 12px;border-radius:18px}
  #hub[data-v300-layout="hub"] .v304DetailCard h3{font-size:20px}
  #hub[data-v300-layout="hub"] .v304DetailMeta{font-size:10.5px}
  #hub[data-v300-layout="hub"] .v304Rename{margin-top:14px}
  #hub[data-v300-layout="hub"] .v304RenameRow{grid-template-columns:1fr;gap:7px}
  #hub[data-v300-layout="hub"] .v304Rename input{font-size:12.5px;padding:10px 11px}
  #hub[data-v300-layout="hub"] .v304Btn{font-size:11px;min-height:44px}
  #hub[data-v300-layout="hub"] .v304Actions,
  #hub[data-v300-layout="hub"] .v304Actions[data-kind="draft"]{grid-template-columns:1fr;gap:7px;margin-top:10px}
}
/* END V304 PROJECT + DRAFT DETAILS */
'''
if '</style>' not in text:
    raise SystemExit('V304 details: style anchor missing')
text = text.replace('</style>', css + '\n</style>', 1)

# Keep the existing Bozze screen intact; only show a renamed current project title.
title_anchor = '<div class="projectInfo"><b>Progetto corrente</b><span>'
title_repl = '<div class="projectInfo"><b>'+"'+esc(p.title||\"Progetto corrente\")+'"+'</b><span>'
if title_anchor not in text:
    raise SystemExit('V304 details: current project title anchor missing')
text = text.replace(title_anchor, title_repl, 1)

hook_anchor = ' openView("dashboard");loadState();'
if hook_anchor not in text:
    raise SystemExit('V304 details: Hub hook anchor missing')
text = text.replace(
    hook_anchor,
    ' window.GSFHubV304={openView,loadState,resumeDraft,shell};\n openView("dashboard");loadState();',
    1,
)

runtime = r'''
<script id="v304ProjectDraftRuntime">
(()=>{
 const qs=(q,r=document)=>r.querySelector(q);
 let selected=null;
 function notify(title,msg="",kind="success"){
   try{parent.GSFNotify&&parent.GSFNotify.show(title,msg,kind)}catch(_e){}
 }
 async function jsonFetch(url,opts={}){
   const r=await fetch(url,{cache:"no-store",credentials:"same-origin",...opts});
   let j={};try{j=await r.json()}catch(_e){}
   if(!r.ok||!j.ok)throw new Error(j.error||"Operazione non riuscita");
   return j;
 }
 function host(){return qs('#hub .view[data-view="projects"] .detailCard')}
 function list(){const h=host();return h&&qs('.folderScroller',h)}
 function ensurePanel(){
   const h=host();if(!h)return null;
   let p=qs('#v304ItemDetail',h);if(p)return p;
   p=document.createElement('div');p.id='v304ItemDetail';p.className='v304ItemDetail';
   p.innerHTML=`<div class="v304DetailTop"><button type="button" class="v304DetailBack">‹ Bozze</button><span class="v304DetailEyebrow">DETTAGLIO PROGETTO</span></div>
    <div class="v304DetailCard">
      <h3 id="v304DetailTitle">Progetto</h3>
      <div class="v304DetailMeta" id="v304DetailMeta"></div>
      <div class="v304Rename"><label for="v304TitleInput">NOME</label><div class="v304RenameRow"><input id="v304TitleInput" maxlength="180"><button type="button" class="v304Btn" data-v304-action="rename">Salva nome</button></div></div>
      <div class="v304Actions" id="v304Actions" data-kind="project">
        <button type="button" class="v304Btn primary" data-v304-action="open">Apri nell'Editor</button>
        <button type="button" class="v304Btn v304SaveDraft" data-v304-action="save-draft">Salva bozza</button>
        <button type="button" class="v304Btn danger" data-v304-action="delete">Elimina</button>
      </div>
    </div>`;
   h.appendChild(p);
   qs('.v304DetailBack',p).onclick=closeDetail;
   p.addEventListener('click',e=>{const b=e.target.closest('[data-v304-action]');if(b)action(b.dataset.v304Action)});
   return p;
 }
 function showDetail(kind,id,title,meta){
   selected={kind,id:id||'',title:title||''};
   const p=ensurePanel(),l=list();if(!p||!l)return;
   l.style.display='none';p.classList.add('active');
   qs('#v304DetailTitle',p).textContent=title||(kind==='draft'?'Bozza':'Progetto corrente');
   qs('#v304TitleInput',p).value=title||(kind==='draft'?'Bozza':'Progetto corrente');
   qs('#v304DetailMeta',p).textContent=meta||'';
   const actions=qs('#v304Actions',p);actions.dataset.kind=kind;
   qs('[data-v304-action="open"]',p).textContent=kind==='draft'?'Continua':'Apri nell’Editor';
 }
 function closeDetail(){
   const p=ensurePanel(),l=list();if(p)p.classList.remove('active');if(l)l.style.display='';selected=null;
 }
 async function openCurrent(){
   try{
     const j=await jsonFetch('/creator-hub/state');const p=j.project||{};
     if(!p.id)return;
     const meta=p.has_source?'Gameplay collegato · pronto da riprendere':'In preparazione';
     showDetail('project',p.id,p.title||'Progetto corrente',meta);
   }catch(e){notify('Progetto non disponibile',String(e.message||e),'error')}
 }
 function openDraft(row){
   const resume=qs('[data-resume]',row);if(!resume)return;
   const title=(qs('b',row)||{}).textContent||'Bozza';
   showDetail('draft',resume.dataset.resume,title,'Bozza salvata · puoi rinominarla, eliminarla o riprenderla.');
 }
 async function action(name){
   if(!selected)return;
   const p=ensurePanel(),input=qs('#v304TitleInput',p),title=String(input&&input.value||'').trim();
   try{
     if(name==='open'){
       if(selected.kind==='draft'){
         const h=window.GSFHubV304||{};if(h.resumeDraft)h.resumeDraft(selected.id);
       }else{
         const h=window.GSFHubV304||{};if(h.shell)h.shell('editor');
       }
       return;
     }
     if(name==='rename'){
       if(!title)throw new Error('Inserisci un nome.');
       const url=selected.kind==='draft'?'/creator-hub/draft/rename':'/creator-hub/project/rename';
       await jsonFetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(selected.kind==='draft'?{id:selected.id,title}:{title})});
       selected.title=title;qs('#v304DetailTitle',p).textContent=title;
       const h=window.GSFHubV304||{};if(h.loadState)await h.loadState();
       notify('Nome aggiornato');return;
     }
     if(name==='save-draft'&&selected.kind==='project'){
       const j=await jsonFetch('/creator-hub/project/save-draft',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({title:title||selected.title||'Bozza'})});
       const h=window.GSFHubV304||{};if(h.loadState)await h.loadState();
       notify('Bozza salvata',j.draft&&j.draft.title||'');return;
     }
     if(name==='delete'){
       const deletedKind=selected.kind;
       const label=deletedKind==='draft'?'questa bozza':'il progetto corrente';
       if(!confirm('Eliminare '+label+'?'))return;
       const url=deletedKind==='draft'?'/creator-hub/draft/delete':'/creator-hub/project/delete';
       const body=deletedKind==='draft'?{id:selected.id}:{};
       await jsonFetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
       closeDetail();const h=window.GSFHubV304||{};if(h.loadState)await h.loadState();
       notify(deletedKind==='draft'?'Bozza eliminata':'Progetto eliminato');return;
     }
   }catch(e){notify('Operazione non riuscita',String(e.message||e),'error')}
 }
 document.addEventListener('click',e=>{
   if(e.target.closest('button,a,input,label'))return;
   const project=e.target.closest('#projectRows .projectBox');if(project){openCurrent();return}
   const draft=e.target.closest('#draftRows .row');if(draft){openDraft(draft)}
 });
 window.addEventListener('message',e=>{
   if(e.origin!==location.origin||!e.data||e.data.type!=='GSF_HUB_FOCUS')return;
   const s=String(e.data.section||'');if(!['drafts','projects','project'].includes(s))closeDetail();
 });
})();
</script>
'''
if '</body>' not in text:
    raise SystemExit('V304 details: body anchor missing')
text = text.replace('</body>', runtime + '\n</body>', 1)
HUB.write_text(text, encoding='utf-8')

app = APP.read_text(encoding='utf-8')
app, count = re.subn(r'/creator-hub-v156/\?v=\d+', '/creator-hub-v156/?v=304', app)
if count < 1 and '/creator-hub-v156/?v=304' not in app:
    raise SystemExit('V304 details: Creator Hub cache anchor missing')
APP.write_text(app, encoding='utf-8')
print('V304 project/draft detail UI + cache v304 applied', flush=True)
