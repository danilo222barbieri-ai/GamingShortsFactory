#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path('/app')
HUB = ROOT / 'web/creator_hub_v156_component/index.html'
SERVER = ROOT / 'web/direct_upload_server.py'
APP = ROOT / 'GamingShortsFactory_V154_STRUCTURAL_HOME.py'

HUB_MARK = '/* V304 PROJECT FOLDER DETAILS */'
SERVER_MARK = '# V304 PROJECT FOLDER DETAILS'

CSS = r'''
/* V304 PROJECT FOLDER DETAILS */
#hub[data-v300-layout="hub"] .projectEntry{
  width:100%!important;border:1px solid rgba(143,181,216,.22)!important;border-radius:17px!important;
  background:linear-gradient(145deg,#fff,#F5FAFF)!important;color:#173A58!important;
  padding:13px 14px!important;margin:0 0 8px!important;display:grid!important;
  grid-template-columns:minmax(0,1fr) auto!important;align-items:center!important;gap:12px!important;
  text-align:left!important;cursor:pointer!important;box-shadow:0 8px 22px rgba(61,104,145,.055)!important;
}
#hub[data-v300-layout="hub"] .projectEntry:hover{transform:translateY(-1px)!important;box-shadow:0 11px 26px rgba(61,104,145,.08)!important}
#hub[data-v300-layout="hub"] .projectEntryMain b{display:block!important;font-size:clamp(13px,1vw,15px)!important;line-height:1.12!important}
#hub[data-v300-layout="hub"] .projectEntryMain span{display:block!important;margin-top:4px!important;color:#8498AD!important;font-size:clamp(10px,.78vw,12px)!important;font-weight:700!important}
#hub[data-v300-layout="hub"] .projectEntryArrow{font-size:24px!important;color:#8EA8C0!important;font-weight:800!important}
#hub[data-v300-layout="hub"] .currentProjectEntry{background:linear-gradient(145deg,#F0F8FF,#F5F2FF)!important}
#hub[data-v300-layout="hub"] .projectEntryTag{display:inline-flex!important;width:max-content!important;margin-bottom:5px!important;padding:4px 7px!important;border-radius:999px!important;background:#E8F4FF!important;color:#4B83B5!important;font-size:8px!important;font-weight:950!important;letter-spacing:.05em!important}
#hub[data-v300-layout="hub"] .projectDetailBack{
  border:0!important;border-radius:12px!important;background:#EDF6FF!important;color:#4C7EA8!important;
  padding:8px 11px!important;font-size:10px!important;font-weight:900!important;cursor:pointer!important;
}
#hub[data-v300-layout="hub"] .projectDetailShell{max-width:760px!important;margin:0 auto!important;display:grid!important;gap:14px!important;padding:clamp(6px,1vh,10px)!important}
#hub[data-v300-layout="hub"] .projectDetailType{font-size:10px!important;font-weight:950!important;letter-spacing:.08em!important;color:#7990A8!important;text-transform:uppercase!important}
#hub[data-v300-layout="hub"] .projectDetailNameWrap{display:grid!important;gap:7px!important}
#hub[data-v300-layout="hub"] .projectDetailNameWrap label{font-size:10px!important;font-weight:900!important;color:#7389A0!important}
#hub[data-v300-layout="hub"] #projectDetailName{width:100%!important;border:1px solid rgba(143,181,216,.30)!important;border-radius:15px!important;padding:13px 14px!important;background:#fff!important;color:#173A58!important;font:inherit!important;font-size:15px!important;font-weight:850!important;outline:none!important}
#hub[data-v300-layout="hub"] #projectDetailMeta{padding:13px 14px!important;border:1px solid rgba(143,181,216,.18)!important;border-radius:15px!important;background:#FAFDFF!important;color:#7C91A7!important;font-size:11px!important;font-weight:750!important;line-height:1.35!important}
#hub[data-v300-layout="hub"] .projectDetailActions{display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:9px!important}
#hub[data-v300-layout="hub"] .projectDetailAction{min-height:48px!important;border:0!important;border-radius:15px!important;background:#E9F5FF!important;color:#3E7BAA!important;font-size:11px!important;font-weight:950!important;cursor:pointer!important}
#hub[data-v300-layout="hub"] .projectDetailAction.primary{background:linear-gradient(145deg,#DFF3FF,#DFF8EE)!important;color:#2F7190!important}
#hub[data-v300-layout="hub"] .projectDetailAction.danger{background:#FFF0F2!important;color:#A75566!important}
#hub[data-v300-layout="hub"] .projectSectionHead{margin-bottom:9px!important}
#hub[data-v300-layout="hub"] #projectRows:empty{display:none!important}
@media(max-width:760px){
  #hub[data-v300-layout="hub"] .view[data-view="projects"] .folderScroller{overflow:auto!important;padding-bottom:8px!important}
  #hub[data-v300-layout="hub"] .projectEntry{padding:12px!important;border-radius:16px!important;margin-bottom:7px!important}
  #hub[data-v300-layout="hub"] .projectEntryMain b{font-size:13px!important}
  #hub[data-v300-layout="hub"] .projectEntryMain span{font-size:10.5px!important}
  #hub[data-v300-layout="hub"] .projectEntryArrow{font-size:22px!important}
  #hub[data-v300-layout="hub"] .projectDetailShell{padding:2px!important;gap:11px!important}
  #hub[data-v300-layout="hub"] .projectDetailBack{font-size:10px!important;padding:7px 10px!important}
  #hub[data-v300-layout="hub"] #projectDetailName{font-size:14px!important;padding:12px!important}
  #hub[data-v300-layout="hub"] #projectDetailMeta{font-size:10.5px!important;padding:11px 12px!important}
  #hub[data-v300-layout="hub"] .projectDetailActions{grid-template-columns:1fr!important;gap:7px!important}
  #hub[data-v300-layout="hub"] .projectDetailAction{min-height:46px!important;font-size:11px!important}
}
/* END V304 PROJECT FOLDER DETAILS */
'''

DETAIL_HTML = r'''
  <section class="view" data-view="projectDetail">
   <div class="detail">
    <div class="detailHead"><button class="projectDetailBack" id="projectDetailBack" type="button">‹ Bozze</button><div class="detailHeadText"><h2 id="projectDetailTitle">Progetto</h2><p id="projectDetailSubtitle">Gestisci questo progetto.</p></div></div>
    <div class="detailCard"><div class="folderScroller">
      <div class="projectDetailShell">
       <div class="projectDetailType" id="projectDetailType">PROGETTO</div>
       <div class="projectDetailNameWrap"><label for="projectDetailName">NOME</label><input id="projectDetailName" maxlength="180" value=""></div>
       <div id="projectDetailMeta">Caricamento…</div>
       <div class="projectDetailActions">
        <button class="projectDetailAction primary" id="projectDetailOpen" type="button">Continua</button>
        <button class="projectDetailAction" id="projectDetailSave" type="button">Salva bozza</button>
        <button class="projectDetailAction" id="projectDetailRename" type="button">Rinomina</button>
        <button class="projectDetailAction danger" id="projectDetailDelete" type="button">Elimina</button>
       </div>
      </div>
    </div></div>
   </div>
  </section>

'''

JS_HELPERS = r'''
 let selectedProjectDetail={kind:"",id:""};
 function notify(title,body="",kind="success"){try{parent.GSFNotify&&parent.GSFNotify.show(title,body,kind)}catch(_e){}}
 async function postJSON(url,payload={}){
   const r=await fetch(url,{method:"POST",credentials:"same-origin",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});
   let j={};try{j=await r.json()}catch(_e){}
   if(!r.ok||!j.ok)throw new Error(j.error||"Operazione non riuscita");
   return j;
 }
 function openProjectDetail(kind,id=""){
   const isCurrent=kind==="current";
   const item=isCurrent?(state.project||{}):(Array.isArray(state.drafts)?state.drafts.find(d=>String(d.id||"")===String(id||"")):null);
   if(!item||(!isCurrent&&!item.id)){notify("Progetto non disponibile","Ricarica la pagina e riprova.","error");return}
   selectedProjectDetail={kind:isCurrent?"current":"draft",id:isCurrent?"":String(item.id||"")};
   const title=String(item.title||(isCurrent?"Progetto corrente":item.source_name)||"Progetto");
   const input=$("#projectDetailName");if(input)input.value=title;
   const type=$("#projectDetailType");if(type)type.textContent=isCurrent?"PROGETTO CORRENTE":"BOZZA SALVATA";
   const head=$("#projectDetailTitle");if(head)head.textContent=title;
   const sub=$("#projectDetailSubtitle");if(sub)sub.textContent=isCurrent?"Salva, rinomina o riprendi il progetto.":"Rinomina, elimina o continua da dove eri rimasto.";
   const meta=$("#projectDetailMeta");if(meta)meta.textContent=(isCurrent?(item.has_source?"Gameplay collegato · ":"In preparazione · "):"Bozza salvata · ")+ago(item.updated_at);
   const save=$("#projectDetailSave");if(save)save.style.display=isCurrent?"":"none";
   const open=$("#projectDetailOpen");if(open)open.textContent=isCurrent?"Apri nell'Editor":"Continua";
   openView("projectDetail");
 }
 async function renameSelectedProject(){
   const input=$("#projectDetailName"),title=String(input&&input.value||"").trim();
   if(!title){notify("Inserisci un nome","Il nome non può essere vuoto.","error");return}
   try{
     if(selectedProjectDetail.kind==="current")await postJSON("/projects/current/rename",{title});
     else await postJSON("/drafts/rename",{id:selectedProjectDetail.id,title});
     notify("Nome aggiornato");await loadState();openProjectDetail(selectedProjectDetail.kind,selectedProjectDetail.id);
   }catch(e){notify("Rinomina non riuscita",String(e.message||e),"error")}
 }
 async function saveCurrentAsDraft(){
   if(selectedProjectDetail.kind!=="current")return;
   const title=String($("#projectDetailName")&&$("#projectDetailName").value||"Progetto corrente").trim()||"Progetto corrente";
   try{await postJSON("/projects/current/save-draft",{title});notify("Bozza salvata");await loadState()}catch(e){notify("Bozza non salvata",String(e.message||e),"error")}
 }
 async function deleteSelectedProjectNow(){
   try{
     if(selectedProjectDetail.kind==="current")await postJSON("/projects/current/delete",{});
     else await postJSON("/drafts/delete-json",{id:selectedProjectDetail.id});
     notify(selectedProjectDetail.kind==="current"?"Progetto eliminato":"Bozza eliminata");
     await loadState();openView("drafts");
   }catch(e){notify("Eliminazione non riuscita",String(e.message||e),"error")}
 }
 function confirmDeleteSelectedProject(){
   const isCurrent=selectedProjectDetail.kind==="current",title=isCurrent?"Eliminare il progetto corrente?":"Eliminare questa bozza?";
   const body=isCurrent?"Le bozze già salvate e gli Shorts non verranno toccati.":"Questa cancellazione è definitiva.";
   try{if(parent.GSFNotify&&typeof parent.GSFNotify.confirm==="function"){parent.GSFNotify.confirm(title,body,{confirmText:"Elimina",cancelText:"Annulla",onConfirm:deleteSelectedProjectNow});return}}catch(_e){}
   if(confirm(title))deleteSelectedProjectNow();
 }
'''

SERVER_HELPERS = r'''

# V304 PROJECT FOLDER DETAILS
def _draft_rename(sid,draft_id,title):
    sid=_safe_id(sid); draft_id=_safe_id(draft_id); title=str(title or "").strip()[:180]
    if not sid or not draft_id or not title:
        return {}
    draft=_draft_load(sid,draft_id)
    if not isinstance(draft,dict) or not draft:
        return {}
    draft["title"]=title
    draft["updated_at"]=time.time()
    _write_json_atomic(_draft_dir(sid)/(draft_id+".json"),draft)
    if _bucket_enabled():
        _s3().put_object(
            Bucket=S3_BUCKET,Key=_draft_key(sid,draft_id),
            Body=json.dumps(draft,ensure_ascii=False,separators=(",",":")).encode("utf-8"),
            ContentType="application/json",CacheControl="no-store",
        )
    _draft_index_upsert(sid,draft)
    return _draft_summary(draft)

def _active_project_record(sid):
    sid=_safe_id(sid)
    if not sid:
        return None
    profile=_creator_account_load(sid) or {}
    account_id=_safe_id(profile.get("account_id","")) if isinstance(profile,dict) else ""
    project_root=(ROOT/"creator-projects"/account_id) if account_id else (ROOT/"sessions"/sid/"projects")
    idx_path=project_root/"index.json"
    try:
        idx=json.loads(idx_path.read_text(encoding="utf-8"))
        pid=_safe_id(idx.get("active_project_id",""))
        if not pid:
            return None
        state_path=project_root/pid/"project_state.json"
        pdata=json.loads(state_path.read_text(encoding="utf-8"))
        if not isinstance(pdata,dict):
            return None
        return {"root":project_root,"index_path":idx_path,"index":idx,"id":pid,"state_path":state_path,"data":pdata}
    except Exception:
        return None

def _active_project_rename(sid,title):
    rec=_active_project_record(sid); title=str(title or "").strip()[:180]
    if not rec or not title:
        return {}
    pdata=dict(rec["data"]); pdata["title"]=title; pdata["updated_at"]=time.time()
    _write_json_atomic(rec["state_path"],pdata)
    idx=dict(rec["index"]); idx["updated_at"]=pdata["updated_at"]; _write_json_atomic(rec["index_path"],idx)
    return {"id":rec["id"],"title":title,"updated_at":pdata["updated_at"]}

def _active_project_save_draft(sid,title=""):
    rec=_active_project_record(sid)
    if not rec:
        return {}
    pdata=dict(rec["data"]); state=dict(pdata.get("state") or {})
    source_name=str(state.get("gsf_source_name") or "Gameplay")[:160]
    wanted=str(title or pdata.get("title") or "Progetto corrente").strip()[:180] or "Progetto corrente"
    return _draft_save(sid,{"title":wanted,"source_name":source_name,"state":state})

def _active_project_delete(sid):
    rec=_active_project_record(sid)
    if not rec:
        return False
    idx=dict(rec["index"]); idx["active_project_id"]=""; idx["updated_at"]=time.time(); _write_json_atomic(rec["index_path"],idx)
    try:
        pdata=dict(rec["data"]); pdata["deleted_at"]=time.time(); pdata["active"]=False; _write_json_atomic(rec["state_path"],pdata)
    except Exception:
        pass
    return True
# END V304 PROJECT FOLDER DETAILS
'''

POST_ENDPOINTS = r'''
        if path=="/drafts/rename":
            try:
                data=_read_json(self,max_bytes=16*1024)
                row=_draft_rename(sid,data.get("id"),data.get("title"))
                _json(self,200 if row else 404,{"ok":bool(row),"draft":row,"error":"Bozza non trovata" if not row else ""})
            except Exception as exc:
                _json(self,400,{"ok":False,"error":str(exc)[:180]})
            return
        if path=="/drafts/delete-json":
            try:
                data=_read_json(self,max_bytes=16*1024)
                draft_id=_safe_id(data.get("id","")) if isinstance(data,dict) else ""
                ok=_draft_delete(sid,draft_id)
                _json(self,200 if ok else 404,{"ok":bool(ok),"id":draft_id})
            except Exception as exc:
                _json(self,400,{"ok":False,"error":str(exc)[:180]})
            return
        if path=="/projects/current/rename":
            try:
                data=_read_json(self,max_bytes=16*1024)
                row=_active_project_rename(sid,data.get("title"))
                _json(self,200 if row else 404,{"ok":bool(row),"project":row,"error":"Progetto non trovato" if not row else ""})
            except Exception as exc:
                _json(self,400,{"ok":False,"error":str(exc)[:180]})
            return
        if path=="/projects/current/save-draft":
            try:
                data=_read_json(self,max_bytes=16*1024)
                draft=_active_project_save_draft(sid,data.get("title"))
                _json(self,200 if draft else 404,{"ok":bool(draft),"id":(draft or {}).get("id"),"title":(draft or {}).get("title"),"error":"Progetto non trovato" if not draft else ""})
            except StorageQuotaError as exc:
                _json(self,409,{"ok":False,"code":"storage_limit","kind":exc.kind,"limit":exc.limit,"plan":exc.plan,"error":str(exc)})
            except Exception as exc:
                _json(self,400,{"ok":False,"error":str(exc)[:180]})
            return
        if path=="/projects/current/delete":
            try:
                ok=_active_project_delete(sid)
                _json(self,200 if ok else 404,{"ok":bool(ok),"error":"Progetto non trovato" if not ok else ""})
            except Exception as exc:
                _json(self,400,{"ok":False,"error":str(exc)[:180]})
            return

'''


def patch_hub():
    text=HUB.read_text(encoding='utf-8')
    if HUB_MARK in text:
        print('V304 Hub already applied',flush=True); return
    if '</style>' not in text:
        raise RuntimeError('V304 Hub style anchor missing')
    text=text.replace('</style>',CSS+'\n</style>',1)
    profile_anchor='  <section class="view" data-view="profile">'
    if profile_anchor not in text:
        raise RuntimeError('V304 detail insert anchor missing')
    text=text.replace(profile_anchor,DETAIL_HTML+profile_anchor,1)
    text=text.replace(' let current="dashboard";',' let current="dashboard";\n'+JS_HELPERS,1)
    whitelist='if(!["dashboard","projects","profile","live","social","subscription"].includes(view))view="dashboard";'
    if whitelist not in text:
        raise RuntimeError('V304 openView whitelist anchor missing')
    text=text.replace(whitelist,'if(!["dashboard","projects","projectDetail","profile","live","social","subscription"].includes(view))view="dashboard";',1)

    old_drafts='''   $("#draftRows").innerHTML=drafts.length?drafts.map(d=>'<div class="row"><b>'+esc(d.title||d.source_name||"Gameplay")+'</b><span class="muted hideMobile">'+(d.duration?d.duration+" sec":"Bozza")+'</span><span class="status hideMobile">'+ago(d.updated_at)+'</span><button class="action" data-resume="'+esc(d.id||"")+'">Continua</button></div>').join(""):'<div class="empty">Nessun progetto in lavorazione salvato.</div>';'''
    new_drafts='''   $("#draftRows").innerHTML=drafts.length?drafts.map(d=>'<button class="projectEntry" type="button" data-draft-open="'+esc(d.id||"")+'"><span class="projectEntryMain"><b>'+esc(d.title||d.source_name||"Gameplay")+'</b><span>Bozza salvata · '+ago(d.updated_at)+'</span></span><span class="projectEntryArrow">›</span></button>').join(""):'<div class="empty">Nessuna bozza salvata.</div>';'''
    if old_drafts not in text:
        raise RuntimeError('V304 draft render anchor missing')
    text=text.replace(old_drafts,new_drafts,1)

    old_project='''   $("#projectRows").innerHTML=p.id?'<div class="projectBox"><div class="projectInfo"><b>Progetto corrente</b><span>'+(p.has_source?"Gameplay collegato · ":"In preparazione · ")+ago(p.updated_at)+'</span></div><div class="quick"><button data-quick="ai">IA</button><button data-quick="editor">Editor</button><button data-quick="social">Social</button></div></div><div class="stats"><div class="stat"><b>'+String(st.shorts_created||0)+'</b><small>Short</small></div><div class="stat"><b>'+String(st.shorts_published||0)+'</b><small>Pubblicati</small></div><div class="stat"><b>'+String(st.drafts||0)+'</b><small>Bozze</small></div><div class="stat"><b>'+String(st.social||0)+'</b><small>Social</small></div></div>':'<div class="empty">Nessun progetto attivo recuperato.</div>';'''
    new_project='''   $("#projectRows").innerHTML=p.id?'<button class="projectEntry currentProjectEntry" type="button" data-current-open="1"><span class="projectEntryMain"><span class="projectEntryTag">CORRENTE</span><b>'+esc(p.title||"Progetto corrente")+'</b><span>'+(p.has_source?"Gameplay collegato · ":"In preparazione · ")+ago(p.updated_at)+'</span></span><span class="projectEntryArrow">›</span></button>':'';'''
    if old_project not in text:
        raise RuntimeError('V304 current project render anchor missing')
    text=text.replace(old_project,new_project,1)

    old_handlers='''   $$("[data-resume]").forEach(b=>b.onclick=()=>resumeDraft(b.dataset.resume));
   $$("[data-short-download]").forEach(b=>b.onclick=()=>{location.href="/shorts/file?id="+encodeURIComponent(b.dataset.shortDownload||"")});
   $$("[data-short-delete]").forEach(b=>b.onclick=()=>confirmDeleteShort(b.dataset.shortDelete));
   $$("[data-quick]").forEach(b=>b.onclick=()=>{if(b.dataset.quick==="social")openView("profile");else shell(b.dataset.quick)});'''
    new_handlers='''   $$("[data-draft-open]").forEach(b=>b.onclick=()=>openProjectDetail("draft",b.dataset.draftOpen));
   $$("[data-current-open]").forEach(b=>b.onclick=()=>openProjectDetail("current"));
   $$("[data-short-download]").forEach(b=>b.onclick=()=>{location.href="/shorts/file?id="+encodeURIComponent(b.dataset.shortDownload||"")});
   $$("[data-short-delete]").forEach(b=>b.onclick=()=>confirmDeleteShort(b.dataset.shortDelete));'''
    if old_handlers not in text:
        raise RuntimeError('V304 project handler anchor missing')
    text=text.replace(old_handlers,new_handlers,1)

    live_bind=''' $$("[data-live-folder]").forEach(b=>b.onclick=()=>openLiveFolder(b.dataset.liveFolder));'''
    detail_bind=''' const detailBack=$("#projectDetailBack");if(detailBack)detailBack.onclick=()=>openView("drafts");
 const detailOpen=$("#projectDetailOpen");if(detailOpen)detailOpen.onclick=()=>{if(selectedProjectDetail.kind==="current")shell("editor");else resumeDraft(selectedProjectDetail.id)};
 const detailSave=$("#projectDetailSave");if(detailSave)detailSave.onclick=saveCurrentAsDraft;
 const detailRename=$("#projectDetailRename");if(detailRename)detailRename.onclick=renameSelectedProject;
 const detailDelete=$("#projectDetailDelete");if(detailDelete)detailDelete.onclick=confirmDeleteSelectedProject;
'''+live_bind
    if live_bind not in text:
        raise RuntimeError('V304 detail bind anchor missing')
    text=text.replace(live_bind,detail_bind,1)
    HUB.write_text(text,encoding='utf-8')
    print('V304 Hub project folders applied',flush=True)


def patch_server():
    text=SERVER.read_text(encoding='utf-8')
    if SERVER_MARK in text:
        print('V304 server already applied',flush=True); return
    helper_anchor='def _short_index_path(sid):'
    if helper_anchor not in text:
        raise RuntimeError('V304 server helper anchor missing')
    text=text.replace(helper_anchor,SERVER_HELPERS+'\n'+helper_anchor,1)

    project_anchor='''                    project={
                        "id":pid,
                        "updated_at":float(pdata.get("updated_at") or idx.get("updated_at") or 0),
                        "has_source":bool((pdata.get("state") or {}).get("gsf_source_path") or (pdata.get("state") or {}).get("gsf_editor_source_path")),
                    }'''
    project_new='''                    project={
                        "id":pid,
                        "title":str(pdata.get("title") or "Progetto corrente")[:180],
                        "updated_at":float(pdata.get("updated_at") or idx.get("updated_at") or 0),
                        "has_source":bool((pdata.get("state") or {}).get("gsf_source_path") or (pdata.get("state") or {}).get("gsf_editor_source_path")),
                    }'''
    if project_anchor not in text:
        raise RuntimeError('V304 server project state anchor missing')
    text=text.replace(project_anchor,project_new,1)

    post_anchor='''        if path=="/push/subscribe":'''
    if post_anchor not in text:
        raise RuntimeError('V304 server POST anchor missing')
    text=text.replace(post_anchor,POST_ENDPOINTS+post_anchor,1)
    SERVER.write_text(text,encoding='utf-8')
    print('V304 backend project actions applied',flush=True)


def patch_cache():
    text=APP.read_text(encoding='utf-8')
    text,count=re.subn(r'/creator-hub-v156/\\?v=\\d+','/creator-hub-v156/?v=304',text)
    if count<1 and '/creator-hub-v156/?v=304' not in text:
        raise RuntimeError('V304 Creator Hub cache anchor missing')
    APP.write_text(text,encoding='utf-8')
    print('V304 Creator Hub cache key: v304',flush=True)

if __name__=='__main__':
    for path in (HUB,SERVER,APP):
        if not path.is_file():
            raise RuntimeError('V304 required file missing: '+str(path))
    patch_hub();patch_server();patch_cache()
