#!/usr/bin/env python3
import ast
import re
from pathlib import Path

APP_SRC = Path("/app/GamingShortsFactory_V154_STRUCTURAL_HOME.py")
APP_OUT = Path("/app/GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py")
UPLOAD_SERVER = Path("/app/web/direct_upload_server.py")
HUB = Path("/app/web/creator_hub_v156_component/index.html")

PROJECT_STYLE = r"""
<style id="v311ProjectPagesReference">
/* V311 PROJECT PAGES REFERENCE */
#hub.projectsReferenceActive{grid-template-rows:minmax(0,1fr)!important;padding:8px 10px 0!important}
#hub.projectsReferenceActive>.top{display:none!important}
#hub .view[data-view="projects"]{height:100%!important;overflow:hidden!important}
#hub .view[data-view="projects"] .detail{height:100%!important;display:block!important}
#hub .view[data-view="projects"] .detailHead{display:none!important}
#hub .view[data-view="projects"] .detailCard{height:100%!important;padding:0!important;border:0!important;border-radius:0!important;background:transparent!important;box-shadow:none!important;backdrop-filter:none!important;-webkit-backdrop-filter:none!important;overflow:hidden!important}
#hub .view[data-view="projects"] .folderScroller{height:100%!important;min-height:0!important;overflow-y:auto!important;overflow-x:hidden!important;-webkit-overflow-scrolling:touch!important;padding:4px 2px 104px!important}
#hub .projectReferenceBrand{display:none;align-items:center;gap:10px;min-height:46px;padding:4px 16px 12px;color:#6f83a3;white-space:nowrap}
#hub.projectsReferenceActive .projectReferenceBrand{display:flex}
#hub .projectReferenceBrand b{font-size:13px;letter-spacing:.19em;color:#17366f;font-weight:950}
#hub .projectReferenceBrand span{font-size:13px;font-weight:750}
#hub .projectReferenceHero{display:none;grid-template-columns:126px minmax(0,1fr);gap:22px;align-items:center;margin:0 0 16px;padding:8px 18px 12px}
#hub.projectsReferenceActive .projectReferenceHero{display:grid}
#hub .projectRefHeroIcon{width:112px;height:112px;border-radius:30px;display:grid;place-items:center;background:linear-gradient(145deg,#efe7ff,#e8dcff);color:#8f48ff;font-size:46px;box-shadow:inset 0 1px 0 rgba(255,255,255,.95)}
#hub .projectReferenceHero[data-kind="shorts"] .projectRefHeroIcon{background:linear-gradient(145deg,#e4f4ff,#ddecff);color:#1686dc}
#hub .projectRefHeroTitle{margin:0;font-size:34px;line-height:1;font-weight:950;letter-spacing:-.045em;color:#0d2a66}
#hub .projectRefHeroSub{margin-top:8px;font-size:16px;line-height:1.25;font-weight:720;color:#7185a6}
#hub .projectRefHeroCount{display:inline-flex;align-items:center;gap:8px;margin-top:14px;min-height:44px;padding:0 18px;border-radius:999px;background:#e6f5ff;color:#1686dc;font-size:14px;font-weight:900}
#hub.projectsReferenceActive #projectHubCards{display:none!important}
#hub.projectsReferenceActive .projectSectionHead{display:none!important}
#hub.projectsReferenceActive #projectRows{display:none!important}
#hub.projectsReferenceActive [data-project-pane]{margin:0!important}
#hub .projectRefList{display:grid;grid-template-columns:1fr;gap:14px}
#hub .projectRefItem{position:relative;min-height:186px;padding:18px 28px 18px 18px;border:1px solid rgba(143,181,216,.18);border-radius:28px;background:rgba(255,255,255,.96);box-shadow:0 14px 34px rgba(61,104,145,.075),inset 0 1px 0 rgba(255,255,255,.99);display:grid;grid-template-columns:190px minmax(0,1fr);gap:24px;align-items:center}
#hub .projectRefThumb{width:190px;height:148px;border-radius:22px;overflow:hidden;display:flex;flex-direction:column;justify-content:flex-end;padding:14px;background:radial-gradient(circle at 72% 25%,rgba(133,213,255,.7),transparent 33%),linear-gradient(145deg,#173f73,#64aee5 58%,#8fd8bd);color:#fff;box-shadow:inset 0 0 0 1px rgba(255,255,255,.22)}
#hub .projectRefItem.short .projectRefThumb{background:radial-gradient(circle at 75% 20%,rgba(255,231,145,.5),transparent 34%),linear-gradient(145deg,#142f5f,#4d88ce 58%,#7fb6e6)}
#hub .projectRefThumbIcon{font-size:28px;line-height:1}
#hub .projectRefThumbLabel{margin-top:auto;font-size:18px;font-weight:950;letter-spacing:-.03em;text-shadow:0 2px 8px rgba(0,0,0,.22);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
#hub .projectRefBody{min-width:0}
#hub .projectRefBody h3{margin:0 38px 9px 0;font-size:24px;line-height:1.05;font-weight:950;letter-spacing:-.03em;color:#0d2a66}
#hub .projectRefMeta{display:grid;gap:7px;color:#7185a6;font-size:14px;font-weight:720}
#hub .projectRefActions{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin-top:16px}
#hub .projectRefBtn{min-height:50px;border:0;border-radius:17px;background:#edf2f8;color:#587397;font-size:14px;font-weight:900;cursor:pointer}
#hub .projectRefBtn.primary{background:linear-gradient(135deg,#68b8ff,#2683ef);color:#fff;box-shadow:0 8px 18px rgba(42,126,235,.18)}
#hub .projectRefBtn.danger{background:#fff0f2;color:#ef2d3d}
#hub .projectRefDots{position:absolute;right:18px;top:16px;border:0;background:transparent;color:#7d91af;font-size:29px;line-height:1;cursor:default}
#hub .projectRefEmpty{min-height:265px;border:2px dashed rgba(143,181,216,.24);border-radius:30px;background:rgba(255,255,255,.34);display:grid;place-items:center;text-align:center;padding:34px 24px;color:#7185a6}
#hub .projectRefEmptyIcon{width:82px;height:82px;margin:0 auto 16px;border-radius:24px;background:#eaf6ff;color:#2f8ee3;display:grid;place-items:center;font-size:34px}
#hub .projectRefEmpty b{display:block;font-size:23px;line-height:1.08;color:#0d2a66}
#hub .projectRefEmpty p{max-width:560px;margin:10px auto 0;font-size:14px;line-height:1.45;font-weight:700}
@media(max-width:520px){
 #hub.projectsReferenceActive{padding-left:6px!important;padding-right:6px!important}
 #hub .projectReferenceBrand{padding-left:10px;padding-right:10px;gap:7px}
 #hub .projectReferenceBrand b{font-size:10px;letter-spacing:.15em}
 #hub .projectReferenceBrand span{font-size:10px}
 #hub .projectReferenceHero{grid-template-columns:96px minmax(0,1fr);gap:14px;padding:6px 10px 10px;margin-bottom:10px}
 #hub .projectRefHeroIcon{width:92px;height:92px;border-radius:25px;font-size:38px}
 #hub .projectRefHeroTitle{font-size:31px}
 #hub .projectRefHeroSub{font-size:13px;margin-top:6px}
 #hub .projectRefHeroCount{min-height:40px;margin-top:11px;padding:0 14px;font-size:12px}
 #hub .projectRefList{gap:12px}
 #hub .projectRefItem{min-height:164px;padding:14px 22px 14px 14px;border-radius:24px;grid-template-columns:112px minmax(0,1fr);gap:14px}
 #hub .projectRefThumb{width:112px;height:132px;border-radius:18px;padding:10px}
 #hub .projectRefThumbIcon{font-size:23px}
 #hub .projectRefThumbLabel{font-size:14px}
 #hub .projectRefBody h3{margin-right:26px;font-size:18px;margin-bottom:7px}
 #hub .projectRefMeta{gap:5px;font-size:11.5px}
 #hub .projectRefActions{gap:7px;margin-top:11px}
 #hub .projectRefBtn{min-height:42px;border-radius:14px;font-size:10.5px;padding:0 5px}
 #hub .projectRefDots{right:10px;top:12px;font-size:25px}
 #hub .projectRefEmpty{min-height:225px;border-radius:25px;padding:28px 18px}
 #hub .projectRefEmptyIcon{width:68px;height:68px;border-radius:20px;font-size:29px}
 #hub .projectRefEmpty b{font-size:20px}
 #hub .projectRefEmpty p{font-size:12px}
}
</style>
"""

PROJECT_SCRIPT = r"""
<script id="v311ProjectPagesRuntime">
(()=>{
 const $=(q,r=document)=>r.querySelector(q), $$=(q,r=document)=>[...r.querySelectorAll(q)];
 let mode="";
 const esc=(s)=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c]));
 const notify=(title,msg="",kind="success")=>{try{parent.GSFNotify&&parent.GSFNotify.show(title,msg,kind)}catch(_e){}};
 const stamp=(v)=>{
   const n=Number(v||0); if(!n)return "Salvato";
   const d=new Date(n>1e12?n:n*1000);
   try{return "Salvato il "+d.toLocaleDateString("it-IT",{day:"2-digit",month:"short",year:"numeric"})+", "+d.toLocaleTimeString("it-IT",{hour:"2-digit",minute:"2-digit"})}catch(_e){return "Salvato"}
 };
 const sourceLabel=(s)=>{
   let x=String(s||"Gameplay").replace(/^.*[\\/]/,"").replace(/\.[a-z0-9]{2,5}$/i,"").replace(/[_-]+/g," ").trim();
   return x||"Gameplay";
 };
 const ensureChrome=()=>{
   const scroller=$('#hub .view[data-view="projects"] .folderScroller'); if(!scroller)return null;
   if(!$('#projectReferenceBrand',scroller)){
     scroller.insertAdjacentHTML("afterbegin",'<div class="projectReferenceBrand" id="projectReferenceBrand"><b>GAMING SHORTS FACTORY</b><span>|</span><span>Creator Hub</span></div><div class="projectReferenceHero" id="projectReferenceHero"><div class="projectRefHeroIcon" id="projectRefHeroIcon">▯</div><div><h2 class="projectRefHeroTitle" id="projectRefHeroTitle">Bozze</h2><div class="projectRefHeroSub" id="projectRefHeroSub"></div><div class="projectRefHeroCount" id="projectRefHeroCount"></div></div></div>');
   }
   return scroller;
 };
 const setChrome=(kind,count)=>{
   ensureChrome(); const hero=$('#projectReferenceHero'); if(hero)hero.dataset.kind=kind;
   $('#projectRefHeroIcon').textContent=kind==="drafts"?"▯":"▶";
   $('#projectRefHeroTitle').textContent=kind==="drafts"?"Bozze":"I miei Shorts";
   $('#projectRefHeroSub').textContent=kind==="drafts"?"I tuoi progetti non ancora pubblicati.":"I tuoi Shorts salvati, pronti da rivedere o pubblicare.";
   $('#projectRefHeroCount').innerHTML=(kind==="drafts"?"▱ ":"▶ ")+String(count)+" "+(kind==="drafts"?(count===1?"bozza salvata":"bozze salvate"):(count===1?"Short salvato":"Shorts salvati"));
 };
 const emptyBlock=(kind,hasRows)=>'<div class="projectRefEmpty"><div><div class="projectRefEmptyIcon">'+(kind==="drafts"?"▱":"▶")+'</div><b>'+(kind==="drafts"?(hasRows?"Nessuna altra bozza":"Nessuna bozza salvata"):(hasRows?"Nessun altro Short":"Nessuno Short salvato"))+'</b><p>'+(kind==="drafts"?"Le tue bozze appariranno qui. Puoi salvare i tuoi progetti in qualsiasi momento e riprenderli più tardi.":"I tuoi Shorts finali appariranno qui e resteranno pronti per essere scaricati o pubblicati.")+'</p></div></div>';
 async function getState(){
   const r=await fetch("/creator-hub/state",{cache:"no-store",credentials:"same-origin"}),j=await r.json();
   if(!r.ok||!j.ok)throw new Error(j.error||"Creator Hub non disponibile"); return j;
 }
 function draftCard(d){
   const id=esc(d.id||""),title=esc(d.title||d.source_name||"Gameplay"),src=esc(sourceLabel(d.source_name||"Gameplay"));
   return '<div class="projectRefItem" data-ref-draft="'+id+'"><div class="projectRefThumb"><div class="projectRefThumbIcon">🎮</div><div class="projectRefThumbLabel">'+src+'</div></div><div class="projectRefBody"><h3>'+title+'</h3><div class="projectRefMeta"><span>🎮 '+src+'</span><span>◷ '+esc(stamp(d.updated_at))+'</span></div><div class="projectRefActions"><button class="projectRefBtn primary" data-ref-action="resume" data-id="'+id+'">▶ Riprendi</button><button class="projectRefBtn" data-ref-action="rename-draft" data-id="'+id+'" data-title="'+title+'">✎ Rinomina</button><button class="projectRefBtn danger" data-ref-action="delete-draft" data-id="'+id+'">▱ Elimina</button></div></div><button class="projectRefDots" type="button">⋮</button></div>';
 }
 function shortCard(s){
   const id=esc(s.id||""),title=esc(s.title||"Short"),status=(s.published||[]).length?"Pubblicato":"Salvato";
   return '<div class="projectRefItem short" data-ref-short="'+id+'"><div class="projectRefThumb"><div class="projectRefThumbIcon">▶</div><div class="projectRefThumbLabel">SHORT</div></div><div class="projectRefBody"><h3>'+title+'</h3><div class="projectRefMeta"><span>🎮 Short finale</span><span>◷ '+esc(status)+'</span></div><div class="projectRefActions"><button class="projectRefBtn primary" data-ref-action="download-short" data-id="'+id+'">↓ Scarica</button><button class="projectRefBtn" data-ref-action="publish-short" data-id="'+id+'">↗ Pubblica</button><button class="projectRefBtn danger" data-ref-action="delete-short" data-id="'+id+'">▱ Elimina</button></div></div><button class="projectRefDots" type="button">⋮</button></div>';
 }
 async function render(kind){
   mode=kind; const hub=$('#hub'); if(hub)hub.classList.add("projectsReferenceActive");
   $$('[data-project-pane]').forEach(p=>p.style.display=p.dataset.projectPane===kind?"":"none");
   const landing=$('#projectHubCards'); if(landing)landing.style.display="none";
   try{
     const st=await getState(),rows=kind==="drafts"?(Array.isArray(st.drafts)?st.drafts:[]):(Array.isArray(st.shorts)?st.shorts:[]);
     setChrome(kind,rows.length);
     const host=kind==="drafts"?$('#draftRows'):$('#shortRows'); if(!host)return;
     host.className="projectRefList";
     host.innerHTML=rows.map(kind==="drafts"?draftCard:shortCard).join("")+emptyBlock(kind,rows.length>0);
   }catch(e){notify("Creator Hub non disponibile",String(e.message||e),"error")}
 }
 async function post(url,body){
   const r=await fetch(url,{method:"POST",credentials:"same-origin",headers:{"Content-Type":"application/json"},body:JSON.stringify(body||{})}),j=await r.json();
   if(!r.ok||!j.ok)throw new Error(j.error||"Operazione non riuscita"); return j;
 }
 async function act(btn){
   const a=btn.dataset.refAction,id=btn.dataset.id||"";
   try{
     if(a==="resume"){const h=window.GSFHubV304||{};if(h.resumeDraft)h.resumeDraft(id);return}
     if(a==="rename-draft"){const current=btn.dataset.title||"Bozza",title=prompt("Rinomina bozza",current);if(title===null)return;const clean=title.trim();if(!clean)return;await post("/creator-hub/draft/rename",{id,title:clean});notify("Nome aggiornato");return render("drafts")}
     if(a==="delete-draft"){if(!confirm("Eliminare questa bozza?"))return;await post("/creator-hub/draft/delete",{id});notify("Bozza eliminata");return render("drafts")}
     if(a==="download-short"){location.href="/shorts/file?id="+encodeURIComponent(id);return}
     if(a==="publish-short"){const h=window.GSFHubV304||{};if(h.shell)h.shell("social");return}
     if(a==="delete-short"){if(!confirm("Eliminare questo Short?"))return;await post("/shorts/delete",{id});notify("Short eliminato");return render("shorts")}
   }catch(e){notify("Operazione non riuscita",String(e.message||e),"error")}
 }
 function clear(){
   mode=""; const hub=$('#hub'); if(hub)hub.classList.remove("projectsReferenceActive");
 }
 document.addEventListener("click",e=>{
   const action=e.target.closest("[data-ref-action]"); if(action){e.preventDefault();e.stopPropagation();act(action);return}
   const dest=e.target.closest("[data-project-dest]"); if(dest)setTimeout(()=>render(dest.dataset.projectDest),0);
   const folder=e.target.closest('[data-folder="projects"]'); if(folder)setTimeout(clear,0);
 });
 window.addEventListener("message",e=>{
   if(!e.data||e.data.type!=="GSF_HUB_FOCUS")return;
   const s=String(e.data.section||"");
   if(s==="drafts"||s==="shorts")setTimeout(()=>render(s),0);
   else if(s==="projects"||s==="dashboard")setTimeout(clear,0);
 });
 ensureChrome();
})();
</script>
"""

def _apply_project_reference():
    if not HUB.is_file() or not APP_SRC.is_file():
        return
    text = HUB.read_text(encoding="utf-8")
    if 'id="v311ProjectPagesReference"' not in text:
        if "</head>" not in text or "</body>" not in text:
            raise RuntimeError("V311 project reference anchors missing")
        text = text.replace("</head>", PROJECT_STYLE + "\n</head>", 1)
        text = text.replace("</body>", PROJECT_SCRIPT + "\n</body>", 1)
        HUB.write_text(text, encoding="utf-8")
    shell = APP_SRC.read_text(encoding="utf-8")
    target = "/creator-hub-v156/?v=3115&ui=projects-ref-1"
    if target not in shell:
        shell, count = re.subn(r'/creator-hub-v156/\?v=[^"\'\s]+', target, shell)
        if count:
            compile(shell, str(APP_SRC), "exec")
            APP_SRC.write_text(shell, encoding="utf-8")
    print("V311 project pages reference applied", flush=True)

_apply_project_reference()

# 1) Keep bucket materialization intentionally narrow on the 1 GB web service.
upload_src = UPLOAD_SERVER.read_text(encoding="utf-8")
old_materialize = """def _materialize_concurrency():
    try:
        value=int(os.environ.get("GSF_MATERIALIZE_CONCURRENCY","6") or 6)
    except Exception:
        value=6
    return max(1,min(8,value))
"""
new_materialize = """def _materialize_concurrency():
    try:
        value=int(os.environ.get("GSF_MATERIALIZE_CONCURRENCY","1") or 1)
    except Exception:
        value=1
    return max(1,min(2,value))
"""
if new_materialize not in upload_src:
    if old_materialize not in upload_src:
        raise RuntimeError("V293 materialization concurrency block not found")
    upload_src = upload_src.replace(old_materialize, new_materialize, 1)
    compile(upload_src, str(UPLOAD_SERVER), "exec")
    UPLOAD_SERVER.write_text(upload_src, encoding="utf-8")


# 2) Serialize the real final FFmpeg execution across Streamlit sessions.
# Later GSF versions may wrap subprocess.run in a helper, so anchor on the
# established render result variable `r` plus the command object `cmd` instead
# of depending on a specific callable name.
s = APP_SRC.read_text(encoding="utf-8")
tree = ast.parse(s)
core = next(
    (node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "_gsf_render_core"),
    None,
)
if core is None:
    raise RuntimeError("V293 _gsf_render_core missing")


def is_render_run(assign):
    if not isinstance(assign, ast.Assign):
        return False
    if not any(isinstance(target, ast.Name) and target.id == "r" for target in assign.targets):
        return False
    call = assign.value
    if not isinstance(call, ast.Call):
        return False
    return any(isinstance(node, ast.Name) and node.id == "cmd" for node in ast.walk(call))


render_assigns = [node for node in ast.walk(core) if is_render_run(node)]
if len(render_assigns) != 1:
    candidates = []
    for node in ast.walk(core):
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "r" for target in node.targets
        ):
            candidates.append(ast.unparse(node)[:500])
    raise RuntimeError(
        f"V293 expected one final r=<call using cmd>, found {len(render_assigns)}; "
        f"r_candidates={candidates}"
    )
render_assign = render_assigns[0]

parents = {}
for parent in ast.walk(core):
    for child in ast.iter_child_nodes(parent):
        parents[child] = parent
parent = parents.get(render_assign)
if parent is None or not hasattr(parent, "body") or render_assign not in parent.body:
    raise RuntimeError("V293 render execution parent body missing")

with_node = ast.With(
    items=[
        ast.withitem(
            context_expr=ast.Call(
                func=ast.Name(id="_gsf_render_slot_v293", ctx=ast.Load()),
                args=[ast.Constant(value="final")],
                keywords=[],
            ),
            optional_vars=None,
        )
    ],
    body=[render_assign],
    type_comment=None,
)
ast.copy_location(with_node, render_assign)
idx = parent.body.index(render_assign)
parent.body[idx] = with_node
ast.fix_missing_locations(core)
new_core = ast.unparse(core)

lines = s.splitlines(keepends=True)
s = "".join(lines[: core.lineno - 1]) + new_core.rstrip() + "\n\n" + "".join(lines[core.end_lineno :])

header = """# V293 RENDER MEMORY GUARD\nfrom web.render_gate_v293 import render_slot as _gsf_render_slot_v293\nGSF_FINAL_RENDER_SLOTS=max(1,min(2,int(__import__("os").environ.get("GSF_FINAL_RENDER_SLOTS","1") or 1)))\n"""
if "# V293 RENDER MEMORY GUARD" not in s:
    s = header + s

compile(s, str(APP_OUT), "exec")
APP_OUT.write_text(s, encoding="utf-8")
print(
    "V293 render memory guard applied:",
    APP_OUT,
    "materialize_default=1 materialize_cap=2 final_render_slots_default=1",
    flush=True,
)
