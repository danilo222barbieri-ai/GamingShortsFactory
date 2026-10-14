#!/usr/bin/env python3
from pathlib import Path
import re
import sys

MARK='V403_CREATOR_HUB_SIMPLIFIED'

PATCH=r'''
<!-- V403_CREATOR_HUB_SIMPLIFIED -->
<style id="v403CreatorHubSimplified">
/* Main Hub: keep the existing language, remove one whole decision layer. */
#hub .view[data-view="dashboard"] .folder[data-folder="subscription"]{display:none!important}
#hub .view[data-view="dashboard"] .folders{
  grid-template-rows:repeat(4,minmax(0,1fr))!important;
}
#hub .view[data-view="dashboard"] .hubMural{
  opacity:.78!important;
  transform:rotate(-2deg)!important;
}
#hub .view[data-view="dashboard"] .folder p{
  max-width:620px!important;
}

/* Profile owns the plan entry now: one place for account + subscription. */
#hub .v403PlanShortcut{
  width:100%;margin:16px 0 10px;padding:13px 14px;border:1px solid rgba(143,181,216,.22);
  border-radius:16px;background:linear-gradient(145deg,rgba(239,248,255,.92),rgba(244,251,248,.92));
  color:#55738f;display:flex;align-items:center;justify-content:space-between;gap:12px;
  text-align:left;font-weight:850;cursor:pointer;box-shadow:none;
}
#hub .v403PlanShortcut span{display:grid;gap:2px}
#hub .v403PlanShortcut b{font-size:13px;color:#244f77}
#hub .v403PlanShortcut small{font-size:10.5px;color:#8195aa;font-weight:750}
#hub .v403PlanShortcut i{font-style:normal;font-size:21px;color:#9ab0c2}

/* Projects: one obvious action per item, everything destructive stays secondary. */
#hub #draftRows,#hub #shortRows{gap:8px!important}
#hub #draftRows .row,#hub #shortRows .row{
  position:relative!important;display:grid!important;
  grid-template-columns:minmax(0,1fr) auto auto!important;
  grid-template-rows:auto auto!important;gap:3px 8px!important;
  min-height:66px!important;padding:10px 10px 10px 13px!important;
  border:1px solid rgba(143,181,216,.20)!important;border-radius:16px!important;
  background:rgba(255,255,255,.96)!important;
}
#hub #draftRows .row>b,#hub #shortRows .row>b{
  grid-column:1!important;grid-row:1!important;align-self:end!important;
  min-width:0!important;overflow:hidden!important;text-overflow:ellipsis!important;white-space:nowrap!important;
  font-size:13px!important;color:#234d75!important;
}
#hub #draftRows .row .muted,#hub #shortRows .row .muted{display:none!important}
#hub #draftRows .row .status,#hub #shortRows .row .status{
  display:block!important;grid-column:1!important;grid-row:2!important;align-self:start!important;
  font-size:10px!important;color:#7d91a7!important;font-weight:750!important;
}
#hub .v403Primary{
  grid-column:2!important;grid-row:1/3!important;align-self:center!important;
  min-width:90px!important;padding:9px 12px!important;border-radius:11px!important;
  background:#e8f5ff!important;color:#347fb9!important;font-size:10.5px!important;font-weight:950!important;
}
#hub .v403ProjectMenu{
  grid-column:3!important;grid-row:1/3!important;align-self:center!important;position:relative!important;
}
#hub .v403ProjectMenuButton{
  width:36px;height:36px;border:1px solid rgba(143,181,216,.22);border-radius:11px;
  background:#f8fbfd;color:#6885a0;font-size:18px;font-weight:900;line-height:1;cursor:pointer;
}
#hub .v403ProjectMenuPanel{
  display:none;position:absolute;right:0;top:42px;z-index:20;min-width:142px;padding:5px;
  border:1px solid rgba(143,181,216,.24);border-radius:12px;background:rgba(255,255,255,.98);
  box-shadow:0 14px 36px rgba(55,91,125,.16);
}
#hub .v403ProjectMenu.open .v403ProjectMenuPanel{display:grid;gap:3px}
#hub .v403ProjectMenuPanel button{
  width:100%;border:0;border-radius:9px;background:transparent;padding:9px 10px;text-align:left;
  color:#57748f;font-size:10.5px;font-weight:850;cursor:pointer;
}
#hub .v403ProjectMenuPanel button:hover{background:#f0f7fc}
#hub .v403ProjectMenuPanel button.danger{color:#b65663}
#hub #shortRows .row>.action.danger{display:none!important}

@media(max-width:760px){
  #hub .view[data-view="dashboard"] .folders{grid-template-rows:repeat(4,minmax(0,1fr))!important}
  #hub .view[data-view="dashboard"] .folder{padding:11px 13px!important}
  #hub .view[data-view="dashboard"] .hubMural{font-size:20px!important;padding:3px 4px 4px!important}
  #hub #draftRows .row,#hub #shortRows .row{min-height:62px!important;padding:9px 8px 9px 11px!important}
  #hub .v403Primary{min-width:82px!important;padding:8px 9px!important;font-size:10px!important}
  #hub .v403ProjectMenuButton{width:34px;height:34px!important}
  #hub .v403PlanShortcut{margin-top:12px!important;padding:11px 12px!important}
}
</style>
<script id="v403CreatorHubSimplifiedRuntime">
(()=>{
  const hub=document.getElementById('hub');
  if(!hub)return;
  const q=(sel,root=hub)=>root.querySelector(sel);
  const qa=(sel,root=hub)=>Array.from(root.querySelectorAll(sel));

  function simplifyDashboard(){
    const profile=q('.view[data-view="dashboard"] .folder[data-folder="profile"]');
    if(profile){
      const title=q('h2',profile),copy=q('p',profile);
      if(title)title.textContent='Profilo e piano';
      if(copy)copy.textContent='Account, foto e abbonamento.';
    }
    const projects=q('.view[data-view="dashboard"] .folder[data-folder="projects"]');
    if(projects){
      const title=q('h2',projects),copy=q('p',projects);
      if(title)title.textContent='Progetti';
      if(copy)copy.textContent='Bozze e Shorts, senza confusione.';
    }
    const subscription=q('.view[data-view="dashboard"] .folder[data-folder="subscription"]');
    if(subscription)subscription.setAttribute('aria-hidden','true');
  }

  function ensurePlanShortcut(){
    const scroller=q('.view[data-view="profile"] .profileOnlyScroller');
    if(!scroller||q('#v403PlanShortcut',scroller))return;
    const logout=q('.logoutProfile',scroller);
    const btn=document.createElement('button');
    btn.type='button';btn.id='v403PlanShortcut';btn.className='v403PlanShortcut';
    const plan=(q('#profilePlanName')?.textContent||q('#planBadge')?.textContent||'FREE').trim();
    btn.innerHTML='<span><b>Piano '+plan+'</b><small>Abbonamento e vantaggi</small></span><i>›</i>';
    btn.addEventListener('click',()=>q('.view[data-view="dashboard"] .folder[data-folder="subscription"]')?.click());
    if(logout)scroller.insertBefore(btn,logout);else scroller.appendChild(btn);
  }

  function closeMenus(except){
    qa('.v403ProjectMenu.open').forEach(menu=>{if(menu!==except)menu.classList.remove('open')});
  }

  async function deleteDraft(id){
    if(!id)return;
    const ask=()=>confirm('Eliminare questa bozza?');
    let accepted=false;
    try{
      if(parent.GSFNotify&&typeof parent.GSFNotify.confirm==='function'){
        parent.GSFNotify.confirm('Eliminare questa bozza?','La bozza verrà rimossa dal Creator Hub.',{
          confirmText:'Elimina',cancelText:'Annulla',onConfirm:()=>deleteDraftNow(id)
        });
        return;
      }
    }catch(_e){}
    accepted=ask();if(accepted)await deleteDraftNow(id);
  }

  async function deleteDraftNow(id){
    try{
      await fetch('/drafts/delete?id='+encodeURIComponent(id),{credentials:'same-origin',redirect:'follow',cache:'no-store'});
      location.reload();
    }catch(err){
      try{parent.GSFNotify&&parent.GSFNotify.show('Bozza non eliminata',String(err?.message||err),'error')}catch(_e){}
    }
  }

  function menuFor(row,kind,id,deleteButton){
    let menu=q('.v403ProjectMenu',row);if(menu)return menu;
    menu=document.createElement('div');menu.className='v403ProjectMenu';
    const trigger=document.createElement('button');trigger.type='button';trigger.className='v403ProjectMenuButton';
    trigger.setAttribute('aria-label','Altre azioni');trigger.setAttribute('aria-expanded','false');trigger.textContent='•••';
    const panel=document.createElement('div');panel.className='v403ProjectMenuPanel';
    if(kind==='draft'){
      const del=document.createElement('button');del.type='button';del.className='danger';del.textContent='Elimina';
      del.addEventListener('click',(ev)=>{ev.stopPropagation();menu.classList.remove('open');deleteDraft(id)});
      panel.appendChild(del);
    }else if(deleteButton){
      deleteButton.classList.add('danger');deleteButton.textContent='Elimina';deleteButton.style.display='block';
      panel.appendChild(deleteButton);
    }
    trigger.addEventListener('click',(ev)=>{
      ev.stopPropagation();const willOpen=!menu.classList.contains('open');closeMenus(menu);
      menu.classList.toggle('open',willOpen);trigger.setAttribute('aria-expanded',willOpen?'true':'false');
    });
    menu.append(trigger,panel);row.appendChild(menu);return menu;
  }

  function enhanceDraftRow(row){
    if(row.dataset.v403Simple==='1')return;
    const primary=q('[data-resume]',row);if(!primary)return;
    row.dataset.v403Simple='1';row.classList.add('v403ProjectRow');
    primary.textContent='RIPRENDI';primary.classList.add('v403Primary');
    const status=q('.status',row);if(status&&!status.textContent.includes('✓ Salvata'))status.textContent='✓ Salvata · '+status.textContent.trim();
    menuFor(row,'draft',primary.dataset.resume||'',null);
  }

  function enhanceShortRow(row){
    if(row.dataset.v403Simple==='1')return;
    const primary=q('[data-short-download]',row);if(!primary)return;
    row.dataset.v403Simple='1';row.classList.add('v403ProjectRow');
    primary.textContent='SCARICA';primary.classList.add('v403Primary');
    const status=q('.status',row);if(status&&status.textContent.trim()==='Salvato')status.textContent='✓ Salvato';
    const deleteButton=q('[data-short-delete]',row);
    menuFor(row,'short',primary.dataset.shortDownload||'',deleteButton);
  }

  function enhanceRows(){
    qa('#draftRows .row').forEach(enhanceDraftRow);
    qa('#shortRows .row').forEach(enhanceShortRow);
  }

  simplifyDashboard();ensurePlanShortcut();enhanceRows();
  document.addEventListener('click',()=>closeMenus(null));
  const observer=new MutationObserver(()=>{simplifyDashboard();ensurePlanShortcut();enhanceRows()});
  ['#draftRows','#shortRows','.view[data-view="profile"]'].forEach(sel=>{const node=q(sel);if(node)observer.observe(node,{subtree:true,childList:true})});
})();
</script>
'''

def patch_text(text:str)->str:
    if MARK in text:
        return text
    if not re.search(r'<main\b[^>]*\bid=["\']hub["\'][^>]*>', text, flags=re.I):
        raise RuntimeError('V403 requires Creator Hub component baseline')
    if 'data-folder="projects"' not in text or 'data-folder="subscription"' not in text:
        raise RuntimeError('V403 requires modular Creator Hub folders')
    if '</body>' not in text:
        raise RuntimeError('V403 Creator Hub body anchor missing')
    return text.replace('</body>',PATCH+'\n</body>',1)

def main()->None:
    path=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app/web/creator_hub_v156_component/index.html')
    if not path.is_file():
        raise SystemExit('V403 Creator Hub target missing: '+str(path))
    before=path.read_text(encoding='utf-8')
    after=patch_text(before)
    path.write_text(after,encoding='utf-8')
    print('V403 Creator Hub simplified applied changed=',before!=after,flush=True)

if __name__=='__main__':
    main()
