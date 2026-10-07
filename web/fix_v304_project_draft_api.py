#!/usr/bin/env python3
from pathlib import Path

SERVER = Path('/app/web/direct_upload_server.py')
text = SERVER.read_text(encoding='utf-8')
MARK = '# V304 PROJECT + DRAFT DETAIL API'
if MARK in text:
    print('V304 project/draft API already applied', flush=True)
    raise SystemExit(0)

if 'import shutil\n' not in text:
    anchor = 'import secrets\nimport html\n'
    if anchor not in text:
        raise SystemExit('V304 API: import anchor missing')
    text = text.replace(anchor, 'import secrets\nimport shutil\nimport html\n', 1)

helper_anchor = 'def _short_index_path(sid):\n'
if helper_anchor not in text:
    raise SystemExit('V304 API: helper anchor missing')
helpers = r'''# V304 PROJECT + DRAFT DETAIL API

def _v304_clean_title(value, fallback="Progetto"):
    value=re.sub(r"\s+"," ",str(value or "").strip())[:180]
    return value or fallback

def _draft_rename(sid,draft_id,title):
    sid=_safe_id(sid); draft_id=_safe_id(draft_id)
    if not sid or not draft_id:
        return {}
    draft=_draft_load(sid,draft_id)
    if not isinstance(draft,dict) or not draft.get("id"):
        return {}
    draft["title"]=_v304_clean_title(title,"Bozza")
    draft["updated_at"]=time.time()
    path=_draft_dir(sid)/(draft_id+".json")
    _write_json_atomic(path,draft)
    if _bucket_enabled():
        try:
            _s3().put_object(
                Bucket=S3_BUCKET,Key=_draft_key(sid,draft_id),
                Body=json.dumps(draft,ensure_ascii=False,separators=(",",":")).encode("utf-8"),
                ContentType="application/json",CacheControl="no-store",
            )
        except Exception as exc:
            print("GSF_DRAFT_RENAME_BUCKET_WARN",sid,draft_id,repr(str(exc))[:180],flush=True)
    _draft_index_upsert(sid,draft)
    print("GSF_DRAFT_RENAMED",sid,draft_id,draft["title"],flush=True)
    return _draft_summary(draft)

def _current_project_record(sid):
    sid=_safe_id(sid)
    if not sid:
        return None,{},"",{}
    profile=_creator_account_load(sid) or {}
    account_id=_safe_id(profile.get("account_id","")) if isinstance(profile,dict) else ""
    root=(ROOT/"creator-projects"/account_id) if account_id else (ROOT/"sessions"/sid/"projects")
    idx_path=root/"index.json"
    try:
        idx=json.loads(idx_path.read_text(encoding="utf-8"))
        if not isinstance(idx,dict): idx={}
    except Exception:
        idx={}
    pid=_safe_id(idx.get("active_project_id",""))
    if not pid:
        return root,idx,"",{}
    try:
        pdata=json.loads((root/pid/"project_state.json").read_text(encoding="utf-8"))
        if not isinstance(pdata,dict): pdata={}
    except Exception:
        pdata={}
    return root,idx,pid,pdata

def _current_project_rename(sid,title):
    root,idx,pid,pdata=_current_project_record(sid)
    if not pid or not pdata:
        return {}
    clean=_v304_clean_title(title,"Progetto corrente")
    pdata["title"]=clean
    pdata["updated_at"]=time.time()
    _write_json_atomic(root/pid/"project_state.json",pdata)
    idx["active_project_title"]=clean
    idx["updated_at"]=time.time()
    _write_json_atomic(root/"index.json",idx)
    print("GSF_PROJECT_RENAMED",_safe_id(sid),pid,clean,flush=True)
    return {"id":pid,"title":clean,"updated_at":pdata["updated_at"]}

def _current_project_save_draft(sid,title=""):
    root,idx,pid,pdata=_current_project_record(sid)
    if not pid or not pdata:
        return {}
    state=pdata.get("state") if isinstance(pdata.get("state"),dict) else {}
    source_name=str(state.get("gsf_source_name") or state.get("source_name") or "Gameplay")[:160]
    desired=_v304_clean_title(title or pdata.get("title") or idx.get("active_project_title"),"Bozza · "+source_name)
    draft=_draft_save(sid,{"title":desired,"source_name":source_name,"state":state})
    print("GSF_PROJECT_SAVED_AS_DRAFT",_safe_id(sid),pid,draft.get("id",""),flush=True)
    return _draft_summary(draft)

def _current_project_delete(sid):
    root,idx,pid,pdata=_current_project_record(sid)
    if not pid:
        return False
    try:
        shutil.rmtree(root/pid,ignore_errors=True)
    except Exception:
        pass
    idx["active_project_id"]=""
    idx.pop("active_project_title",None)
    idx["updated_at"]=time.time()
    for key in ("projects","items"):
        if isinstance(idx.get(key),list):
            idx[key]=[row for row in idx[key] if _safe_id((row or {}).get("id","") if isinstance(row,dict) else row)!=pid]
    root.mkdir(parents=True,exist_ok=True)
    _write_json_atomic(root/"index.json",idx)
    print("GSF_PROJECT_DELETED",_safe_id(sid),pid,flush=True)
    return True

'''
text = text.replace(helper_anchor, helpers + helper_anchor, 1)

project_field = '                        "has_source":bool((pdata.get("state") or {}).get("gsf_source_path") or (pdata.get("state") or {}).get("gsf_editor_source_path")),\n'
if project_field not in text:
    raise SystemExit('V304 API: Creator Hub project field anchor missing')
text = text.replace(
    project_field,
    project_field + '                        "title":str(pdata.get("title") or idx.get("active_project_title") or "Progetto corrente")[:180],\n',
    1,
)

post_anchor = '        if path=="/drafts/save":\n'
if post_anchor not in text:
    raise SystemExit('V304 API: POST route anchor missing')
routes = r'''        # V304 project/draft detail actions.
        if path=="/creator-hub/draft/rename":
            try:
                data=_read_json(self,max_bytes=32768)
                row=_draft_rename(sid,data.get("id"),data.get("title"))
                if not row:
                    _json(self,404,{"ok":False,"error":"Bozza non trovata"})
                else:
                    _json(self,200,{"ok":True,"draft":row})
            except Exception as exc:
                _json(self,400,{"ok":False,"error":str(exc)[:180]})
            return
        if path=="/creator-hub/draft/delete":
            try:
                data=_read_json(self,max_bytes=32768)
                did=_safe_id(data.get("id",""))
                ok=_draft_delete(sid,did) if did else False
                _json(self,200 if ok else 404,{"ok":bool(ok)})
            except Exception as exc:
                _json(self,400,{"ok":False,"error":str(exc)[:180]})
            return
        if path=="/creator-hub/project/rename":
            try:
                data=_read_json(self,max_bytes=32768)
                row=_current_project_rename(sid,data.get("title"))
                if not row:
                    _json(self,404,{"ok":False,"error":"Progetto corrente non trovato"})
                else:
                    _json(self,200,{"ok":True,"project":row})
            except Exception as exc:
                _json(self,400,{"ok":False,"error":str(exc)[:180]})
            return
        if path=="/creator-hub/project/save-draft":
            try:
                data=_read_json(self,max_bytes=32768)
                row=_current_project_save_draft(sid,data.get("title"))
                if not row:
                    _json(self,404,{"ok":False,"error":"Progetto corrente non trovato"})
                else:
                    _json(self,200,{"ok":True,"draft":row})
            except StorageQuotaError as exc:
                _json(self,409,{"ok":False,"code":"storage_limit","kind":exc.kind,"limit":exc.limit,"plan":exc.plan,"error":str(exc)})
            except Exception as exc:
                _json(self,400,{"ok":False,"error":str(exc)[:180]})
            return
        if path=="/creator-hub/project/delete":
            try:
                ok=_current_project_delete(sid)
                _json(self,200 if ok else 404,{"ok":bool(ok)})
            except Exception as exc:
                _json(self,400,{"ok":False,"error":str(exc)[:180]})
            return
'''
text = text.replace(post_anchor, routes + post_anchor, 1)

SERVER.write_text(text, encoding='utf-8')
print('V304 project/draft API applied', flush=True)
