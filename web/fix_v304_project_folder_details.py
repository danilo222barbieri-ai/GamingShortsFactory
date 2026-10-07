#!/usr/bin/env python3
from pathlib import Path
import re

ROOT=Path('/app')
HUB=ROOT/'web/creator_hub_v156_component/index.html'
SERVER=ROOT/'web/direct_upload_server.py'
APP=ROOT/'GamingShortsFactory_V154_STRUCTURAL_HOME.py'
MARK='/* V304 PROJECT FOLDER DETAILS */'

CSS=r'''
/* V304 PROJECT FOLDER DETAILS */
#hub .view[data-view="projects"] .stats{display:none!important}
#hub .view[data-view="projects"] .projectSection{margin:0!important}
#hub .view[data-view="projects"] .projectSection + .projectSection{margin-top:14px!important}
.hubProjectCard{
 width:100%;border:1px solid rgba(143,181,216,.24);border-radius:18px;background:#fff;
 display:grid;grid-template-columns:auto minmax(0,1fr) auto;align-items:center;gap:12px;
 padding:13px 14px;color:#173A70;text-align:left;cursor:pointer;
 box-shadow:0 8px 20px rgba(61,104,145,.05);margin:0 0 8px;
}
.hubProjectCard:hover{border-color:rgba(80,157,218,.42);box-shadow:0 11px 24px rgba(61,104,145,.08)}
.hubProjectIcon{width:43px;height:43px;border-radius:14px;display:grid;place-items:center;background:#EAF5FF;color:#458FD0;font-weight:950;font-size:17px}
.currentProjectCard .hubProjectIcon{background:#E7F5FF;color:#347FC2}
.draftProjectCard .hubProjectIcon{background:#F0EAFF;color:#765CD5}
.hubProjectCopy{min-width:0;display:block}.hubProjectCopy b{display:block;font-size:13px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.hubProjectCopy small{display:block;margin-top:4px;color:#8798AE;font-size:10px;font-weight:700}.hubProjectCard i{font-style:normal;font-size:24px;color:#91A9C0}
.projectDetailOverlay{position:fixed;inset:0;z-index:80;background:rgba(236,247,255,.94);backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);display:grid;place-items:center;padding:18px}
.projectDetailOverlay[hidden]{display:none!important}.projectDetailSheet{width:min(560px,100%);border:1px solid rgba(143,181,216,.28);border-radius:26px;background:rgba(255,255,255,.97);box-shadow:0 24px 60px rgba(46,89,128,.15);padding:18px}
.projectDetailHead{display:flex;align-items:flex-start;justify-content:space-between;gap:12px}.projectDetailHead h3{margin:0;font-size:22px;line-height:1.05}.projectDetailHead p{margin:5px 0 0;color:#8294A8;font-size:11px;font-weight:700}.projectDetailClose{border:0;width:38px;height:38px;border-radius:12px;background:#EEF6FC;color:#63809D;font-size:19px;font-weight:900;cursor:pointer}
.projectDetailField{margin-top:16px}.projectDetailField label{display:block;font-size:9px;font-weight:950;letter-spacing:.08em;color:#7890A6;margin-bottom:6px}.projectDetailField input{width:100%;border:1px solid rgba(143,181,216,.30);border-radius:14px;padding:12px 13px;background:#fff;color:#173A70;font-size:14px;font-weight:850;outline:none}
.projectDetailActions{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;margin-top:14px}.projectDetailActions button{border:0;border-radius:14px;min-height:46px;padding:9px 11px;background:#E9F5FF;color:#397FC1;font-size:11px;font-weight:900;cursor:pointer}.projectDetailActions button.primary{background:linear-gradient(145deg,#DFF3FF,#DFF8EE);color:#26799A}.projectDetailActions button.danger{background:#FFF0F1;color:#A95D68}.projectDetailActions button[hidden]{display:none!important}
@media(max-width:760px){
 #hub[data-v300-layout="hub"] .view[data-view="projects"] .detailCard{padding:7px!important}
 #hub .view[data-view="projects"] .projectSectionHead{padding:4px 5px 8px!important}
 .hubProjectCard{padding:11px 12px;border-radius:17px;gap:10px;margin-bottom:7px}.hubProjectIcon{width:40px;height:40px;border-radius:13px}.hubProjectCopy b{font-size:12px}.hubProjectCopy small{font-size:9.5px}.hubProjectCard i{font-size:22px}
 .projectDetailOverlay{padding:10px;align-items:end}.projectDetailSheet{border-radius:25px 25px 18px 18px;padding:15px 14px calc(15px + env(safe-area-inset-bottom))}.projectDetailHead h3{font-size:20px}.projectDetailActions{grid-template-columns:1fr;gap:7px}.projectDetailActions button{min-height:48px;font-size:11.5px}
}
/* END V304 PROJECT FOLDER DETAILS */
'''

OVERLAY=r'''
<div class="projectDetailOverlay" id="projectDetailOverlay" hidden>
 <div class="projectDetailSheet" role="dialog" aria-modal="true" aria-labelledby="projectDetailTitle">
  <div class="projectDetailHead"><div><h3 id="projectDetailTitle">Progetto</h3><p id="projectDetailMeta">Gestisci il progetto</p></div><button class="projectDetailClose" id="projectDetailClose" type="button">×</button></div>
  <div class="projectDetailField"><label for="projectDetailName">NOME</label><input id="projectDetailName" maxlength="180"></div>
  <div class="projectDetailActions">
   <button class="primary" id="projectDetailContinue" type="button">Continua nell’Editor</button>
   <button class="primary" id="projectDetailSaveDraft" type="button">Salva bozza</button>
   <button id="projectDetailRename" type="button">Rinomina</button>
   <button class="danger" id="projectDetailDelete" type="button">Elimina</button>
  </div>
 </div>
</div>
'''

JS=r'''
 let projectDetailState={kind:"",id:""};
 function openProjectDetail(kind,id,title,meta){
   projectDetailState={kind:String(kind||""),id:String(id||"")};
   const ov=$("#projectDetailOverlay"),name=$("#projectDetailName"),ttl=$("#projectDetailTitle"),sub=$("#projectDetailMeta");
   if(!ov)return;
   if(name)name.value=String(title|| (kind==="draft"?"Bozza":"Progetto corrente"));
   if(ttl)ttl.textContent=kind==="draft"?"Bozza":"Progetto corrente";
   if(sub)sub.textContent=String(meta||"");
   const save=$("#projectDetailSaveDraft");if(save)save.hidden=kind!=="current";
   const cont=$("#projectDetailContinue");if(cont)cont.textContent=kind==="draft"?"Continua":"Apri nell’Editor";
   ov.hidden=false;
 }
 function closeProjectDetail(){const ov=$("#projectDetailOverlay");if(ov)ov.hidden=true;projectDetailState={kind:"",id:""}}
 async function projectPost(url,payload={}){
   const r=await fetch(url,{method:"POST",credentials:"same-origin",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload||{})});
   const j=await r.json().catch(()=>({ok:false,error:"Risposta non valida"}));
   if(!r.ok||!j.ok)throw new Error(j.error||"Operazione non riuscita");
   return j;
 }
 async function projectDetailRename(){
   const name=String($("#projectDetailName")?.value||"").trim();if(!name)return;
   try{
     if(projectDetailState.kind==="draft")await projectPost("/drafts/rename",{id:projectDetailState.id,title:name});
     else await projectPost("/creator-hub/project/rename",{id:projectDetailState.id,title:name});
     closeProjectDetail();await loadState();try{parent.GSFNotify&&parent.GSFNotify.show("Nome aggiornato","","success")}catch(_e){}
   }catch(e){try{parent.GSFNotify&&parent.GSFNotify.show("Rinomina non riuscita",String(e.message||e),"error")}catch(_e){}}
 }
 async function projectDetailDelete(){
   const isDraft=projectDetailState.kind==="draft";
   const message=isDraft?"Eliminare definitivamente questa bozza?":"Eliminare il progetto corrente? Le bozze e gli Shorts salvati restano intatti.";
   if(!confirm(message))return;
   try{
     if(isDraft)await projectPost("/drafts/delete-json",{id:projectDetailState.id});
     else await projectPost("/creator-hub/project/delete",{id:projectDetailState.id});
     closeProjectDetail();await loadState();try{parent.GSFNotify&&parent.GSFNotify.show(isDraft?"Bozza eliminata":"Progetto eliminato","","success")}catch(_e){}
   }catch(e){try{parent.GSFNotify&&parent.GSFNotify.show("Eliminazione non riuscita",String(e.message||e),"error")}catch(_e){}}
 }
 async function projectDetailSaveDraft(){
   const title=String($("#projectDetailName")?.value||"Progetto corrente").trim();
   try{await projectPost("/creator-hub/project/save-draft",{id:projectDetailState.id,title});closeProjectDetail();await loadState();try{parent.GSFNotify&&parent.GSFNotify.show("Bozza salvata","Puoi riprenderla quando vuoi.","success")}catch(_e){}}
   catch(e){try{parent.GSFNotify&&parent.GSFNotify.show("Bozza non salvata",String(e.message||e),"error")}catch(_e){}}
 }
 function projectDetailContinue(){if(projectDetailState.kind==="draft")resumeDraft(projectDetailState.id);else shell("editor")}
'''

SERVER_HELPERS=r'''

def _v304_active_project(sid):
    sid=_safe_id(sid)
    profile=_creator_account_load(sid) or {}
    account_id=_safe_id(profile.get("account_id","")) if isinstance(profile,dict) else ""
    root=(ROOT/"creator-projects"/account_id) if account_id else (ROOT/"sessions"/sid/"projects")
    idx_path=root/"index.json"
    try: idx=json.loads(idx_path.read_text(encoding="utf-8"))
    except Exception: idx={}
    pid=_safe_id(idx.get("active_project_id",""))
    if not pid:return root,idx_path,idx,"",None,{}
    ppath=root/pid/"project_state.json"
    try:pdata=json.loads(ppath.read_text(encoding="utf-8"))
    except Exception:pdata={}
    return root,idx_path,idx,pid,ppath,pdata if isinstance(pdata,dict) else {}

def _v304_draft_rename(sid,draft_id,title):
    draft=_draft_load(sid,draft_id)
    if not draft:raise RuntimeError("Bozza non trovata")
    title=str(title or "").strip()[:180]
    if not title:raise ValueError("Inserisci un nome")
    draft["title"]=title;draft["updated_at"]=time.time()
    path=_draft_dir(sid)/(_safe_id(draft_id)+".json")
    _write_json_atomic(path,draft)
    if _bucket_enabled():
        _s3().put_object(Bucket=S3_BUCKET,Key=_draft_key(sid,draft_id),Body=json.dumps(draft,ensure_ascii=False,separators=(",",":")).encode("utf-8"),ContentType="application/json",CacheControl="no-store")
    _draft_index_upsert(sid,draft)
    return _draft_summary(draft)

def _v304_project_rename(sid,project_id,title):
    root,idx_path,idx,pid,ppath,pdata=_v304_active_project(sid)
    if not pid or (project_id and _safe_id(project_id)!=pid) or ppath is None:raise RuntimeError("Progetto corrente non trovato")
    title=str(title or "").strip()[:180]
    if not title:raise ValueError("Inserisci un nome")
    state=dict(pdata.get("state") or {})
    state["gsf_project_title"]=title
    pdata["state"]=state;pdata["title"]=title;pdata["updated_at"]=time.time()
    _write_json_atomic(ppath,pdata)
    idx["updated_at"]=time.time();_write_json_atomic(idx_path,idx)
    return {"id":pid,"title":title}

def _v304_project_save_draft(sid,project_id,title):
    _root,_idx_path,_idx,pid,_ppath,pdata=_v304_active_project(sid)
    if not pid or (project_id and _safe_id(project_id)!=pid):raise RuntimeError("Progetto corrente non trovato")
    state=dict(pdata.get("state") or {})
    if not state:raise RuntimeError("Progetto vuoto")
    source_name=str(state.get("gsf_source_name") or "Gameplay")[:160]
    draft=_draft_save(sid,{"title":str(title or pdata.get("title") or "Progetto corrente")[:180],"source_name":source_name,"state":state})
    return draft

def _v304_project_delete(sid,project_id):
    import shutil
    root,idx_path,idx,pid,_ppath,_pdata=_v304_active_project(sid)
    if not pid or (project_id and _safe_id(project_id)!=pid):raise RuntimeError("Progetto corrente non trovato")
    shutil.rmtree(root/pid,ignore_errors=True)
    idx["active_project_id"]="";idx["updated_at"]=time.time()
    if isinstance(idx.get("projects"),list):idx["projects"]=[x for x in idx["projects"] if _safe_id((x or {}).get("id",""))!=pid]
    idx_path.parent.mkdir(parents=True,exist_ok=True);_write_json_atomic(idx_path,idx)
    session_root=ROOT/"sessions"/_safe_id(sid)
    for name in ("session_state.json","draft_resume.json"):
        try:(session_root/name).unlink(missing_ok=True)
        except Exception:pass
    try:(session_root/"media"/".direct_upload_ready.json").unlink(missing_ok=True)
    except Exception:pass
    return True
'''

SERVER_ROUTES=r'''
        if path=="/drafts/rename":
            try:
                data=_read_json(self,max_bytes=16*1024); row=_v304_draft_rename(sid,_safe_id(data.get("id","")),data.get("title")); _json(self,200,{"ok":True,"draft":row})
            except Exception as exc:_json(self,400,{"ok":False,"error":str(exc)[:180]})
            return
        if path=="/drafts/delete-json":
            try:
                data=_read_json(self,max_bytes=16*1024); did=_safe_id(data.get("id","")); ok=_draft_delete(sid,did); _json(self,200 if ok else 404,{"ok":bool(ok),"id":did})
            except Exception as exc:_json(self,400,{"ok":False,"error":str(exc)[:180]})
            return
        if path=="/creator-hub/project/rename":
            try:
                data=_read_json(self,max_bytes=16*1024); row=_v304_project_rename(sid,_safe_id(data.get("id","")),data.get("title")); _json(self,200,{"ok":True,"project":row})
            except Exception as exc:_json(self,400,{"ok":False,"error":str(exc)[:180]})
            return
        if path=="/creator-hub/project/save-draft":
            try:
                data=_read_json(self,max_bytes=16*1024); draft=_v304_project_save_draft(sid,_safe_id(data.get("id","")),data.get("title")); _json(self,200,{"ok":True,"id":draft.get("id"),"title":draft.get("title")})
            except StorageQuotaError as exc:_json(self,409,{"ok":False,"code":"storage_limit","limit":exc.limit,"error":str(exc)})
            except Exception as exc:_json(self,400,{"ok":False,"error":str(exc)[:180]})
            return
        if path=="/creator-hub/project/delete":
            try:
                data=_read_json(self,max_bytes=16*1024); ok=_v304_project_delete(sid,_safe_id(data.get("id",""))); _json(self,200,{"ok":bool(ok)})
            except Exception as exc:_json(self,400,{"ok":False,"error":str(exc)[:180]})
            return

'''

def patch_hub():
    text=HUB.read_text(encoding='utf-8')
    if MARK in text:return
    text=text.replace('</style>',CSS+'\n</style>',1)
    text=text.replace('</main>',OVERLAY+'\n</main>',1)
    anchor=' function render(){'
    if anchor not in text:raise RuntimeError('V304 render anchor missing')
    text=text.replace(anchor,JS+'\n'+anchor,1)
    start='   const drafts=Array.isArray(state.drafts)?state.drafts:[];'
    end='   $$("[data-short-download]").forEach'
    a=text.find(start);b=text.find(end,a)
    if a<0 or b<0:raise RuntimeError('V304 project render block missing')
    block=r'''   const drafts=Array.isArray(state.drafts)?state.drafts:[];
   $("#draftRows").innerHTML=drafts.length?drafts.map(d=>'<button class="hubProjectCard draftProjectCard" type="button" data-open-draft="'+esc(d.id||"")+'" data-project-title="'+esc(d.title||d.source_name||"Bozza")+'"><span class="hubProjectIcon">▢</span><span class="hubProjectCopy"><b>'+esc(d.title||d.source_name||"Bozza")+'</b><small>'+ago(d.updated_at)+' · Tocca per aprire</small></span><i>›</i></button>').join(""):'<div class="empty">Nessuna bozza salvata.</div>';

   const p=state.project||{};
   $("#projectRows").innerHTML=p.id?'<button class="hubProjectCard currentProjectCard" type="button" data-open-current="'+esc(p.id||"")+'" data-project-title="'+esc(p.title||"Progetto corrente")+'"><span class="hubProjectIcon">▣</span><span class="hubProjectCopy"><b>'+esc(p.title||"Progetto corrente")+'</b><small>'+(p.has_source?"Gameplay collegato":"In preparazione")+' · '+ago(p.updated_at)+'</small></span><i>›</i></button>':'<div class="empty">Nessun progetto corrente.</div>';

   $$("[data-open-draft]").forEach(b=>b.onclick=()=>openProjectDetail("draft",b.dataset.openDraft,b.dataset.projectTitle||"Bozza","Bozza salvata · pronta da riprendere"));
   $$("[data-open-current]").forEach(b=>b.onclick=()=>openProjectDetail("current",b.dataset.openCurrent,b.dataset.projectTitle||"Progetto corrente","Workspace corrente · puoi salvarlo come bozza"));
'''
    text=text[:a]+block+text[b:]
    hook=' const saveBtn=$("#saveProfileBtn");if(saveBtn)saveBtn.onclick=saveProfile;'
    bind=''' const detailClose=$("#projectDetailClose");if(detailClose)detailClose.onclick=closeProjectDetail;
 const detailRename=$("#projectDetailRename");if(detailRename)detailRename.onclick=projectDetailRename;
 const detailDelete=$("#projectDetailDelete");if(detailDelete)detailDelete.onclick=projectDetailDelete;
 const detailSave=$("#projectDetailSaveDraft");if(detailSave)detailSave.onclick=projectDetailSaveDraft;
 const detailContinue=$("#projectDetailContinue");if(detailContinue)detailContinue.onclick=projectDetailContinue;
 const detailOverlay=$("#projectDetailOverlay");if(detailOverlay)detailOverlay.onclick=e=>{if(e.target===detailOverlay)closeProjectDetail()};
'''
    if hook not in text:raise RuntimeError('V304 event hook missing')
    text=text.replace(hook,bind+hook,1)
    HUB.write_text(text,encoding='utf-8')

def patch_server():
    text=SERVER.read_text(encoding='utf-8')
    if '_v304_active_project' not in text:
        anchor='def _short_index_path(sid):'
        if anchor not in text:raise RuntimeError('V304 server helper anchor missing')
        text=text.replace(anchor,SERVER_HELPERS+'\n'+anchor,1)
    old='''                    project={
                        "id":pid,
                        "updated_at":float(pdata.get("updated_at") or idx.get("updated_at") or 0),
                        "has_source":bool((pdata.get("state") or {}).get("gsf_source_path") or (pdata.get("state") or {}).get("gsf_editor_source_path")),
                    }'''
    new='''                    project={
                        "id":pid,
                        "title":str(pdata.get("title") or (pdata.get("state") or {}).get("gsf_project_title") or (pdata.get("state") or {}).get("gsf_source_name") or "Progetto corrente")[:120],
                        "updated_at":float(pdata.get("updated_at") or idx.get("updated_at") or 0),
                        "has_source":bool((pdata.get("state") or {}).get("gsf_source_path") or (pdata.get("state") or {}).get("gsf_editor_source_path")),
                    }'''
    if old in text:text=text.replace(old,new,1)
    elif '"title":str(pdata.get("title")' not in text:raise RuntimeError('V304 project state anchor missing')
    route_anchor='        if path=="/drafts/save-current":\n'
    if '/creator-hub/project/save-draft' not in text:
        if route_anchor not in text:raise RuntimeError('V304 POST route anchor missing')
        text=text.replace(route_anchor,SERVER_ROUTES+route_anchor,1)
    SERVER.write_text(text,encoding='utf-8')

def patch_cache():
    text=APP.read_text(encoding='utf-8')
    text,count=re.subn(r'/creator-hub-v156/\?v=\d+','/creator-hub-v156/?v=304',text)
    if count<1 and '/creator-hub-v156/?v=304' not in text:raise RuntimeError('V304 cache anchor missing')
    APP.write_text(text,encoding='utf-8')

patch_hub();patch_server();patch_cache();print('V304 project folder details: applied',flush=True)
