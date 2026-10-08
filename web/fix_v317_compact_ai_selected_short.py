#!/usr/bin/env python3
from pathlib import Path
import re
import sys

STYLE_ID = "v317AiCompactSelectedShort"

STYLE = r'''<style id="v317AiCompactSelectedShort">
/* V317: compact mobile AI flow + dedicated selected-short page. */
#ai221 .v317EmptyResults,#ai221 .selectedShortPage{display:none}
@media(max-width:760px){
  #ai221{height:100dvh!important;min-height:0!important;overflow:hidden!important;padding:8px 7px 10px!important}
  #ai221 .top{display:grid!important;grid-template-columns:minmax(0,1fr) auto!important;gap:7px!important;margin:0 0 7px!important;align-items:start!important}
  #ai221 .title{gap:8px!important;align-items:center!important}
  #ai221 .titleIcon{width:42px!important;height:42px!important;border-radius:14px!important}
  #ai221 h1{font-size:22px!important;line-height:1!important}
  #ai221 .subtitle{margin-top:4px!important;font-size:10px!important;line-height:1.15!important;max-width:250px!important}
  #ai221 .duration{padding:4px!important;border-radius:15px!important}
  #ai221 .duration button{padding:7px 9px!important;font-size:10px!important}
  #ai221>.panel:first-of-type{padding:8px!important;border-radius:20px!important;margin:0!important}
  #ai221>.panel:first-of-type .panelHead{display:none!important}
  #ai221 .engines{grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:6px!important}
  #ai221 .engine{min-height:104px!important;padding:8px!important;border-radius:16px!important;display:grid!important;grid-template-rows:auto auto auto!important;align-content:start!important}
  #ai221 .engineTop{margin-bottom:4px!important}
  #ai221 .engineIcon{width:34px!important;height:34px!important;border-radius:50%!important;font-size:16px!important}
  #ai221 .check{width:24px!important;height:24px!important;border-radius:50%!important}
  #ai221 .engine h3{font-size:12.5px!important;line-height:1.08!important;margin:2px 0 3px!important}
  #ai221 .engine p{font-size:9.2px!important;line-height:1.15!important;display:-webkit-box!important;-webkit-line-clamp:2!important;-webkit-box-orient:vertical!important;overflow:hidden!important}
  #ai221 .tags,#ai221 .selectBtn{display:none!important}
  #ai221 .actionRow{margin-top:7px!important;display:grid!important;grid-template-columns:1fr!important;gap:5px!important}
  #ai221 .status{display:block!important;text-align:center!important;font-size:9.2px!important;line-height:1.1!important}
  #ai221.hasGameplay .status{display:none!important}
  #ai221 .create{width:100%!important;min-height:44px!important;border-radius:15px!important;padding:10px 12px!important;font-size:10.5px!important}
  #ai221>.panel:nth-of-type(2){margin-top:7px!important;padding:8px!important;border-radius:20px!important;min-height:0!important}
  #ai221>.panel:nth-of-type(2) .panelHead{display:flex!important;margin:0 0 6px!important}
  #ai221>.panel:nth-of-type(2) .panelTitle{font-size:12.5px!important}
  #ai221>.panel:nth-of-type(2) .panelHint{display:none!important}
  #ai221 .moments{display:block!important;min-height:74px!important}
  #ai221:not(.hasResults) .moment{display:none!important}
  #ai221.hasResults .v317EmptyResults{display:none!important}
  #ai221:not(.hasResults) .v317EmptyResults{display:flex!important;min-height:74px!important;align-items:center!important;justify-content:center!important;text-align:center!important;padding:12px!important;border:1px solid rgba(143,181,216,.20)!important;border-radius:16px!important;background:linear-gradient(145deg,rgba(240,249,255,.96),rgba(244,251,248,.94))!important;color:#7e92aa!important;font-size:10px!important;font-weight:800!important}
  #ai221.hasResults .moments{display:grid!important;grid-template-columns:1fr!important;gap:6px!important}
  #ai221 .moment{min-height:66px!important;width:100%!important;grid-template-columns:92px minmax(0,1fr) 28px!important;grid-template-rows:auto auto!important;align-items:center!important;column-gap:9px!important;row-gap:2px!important;padding:5px!important;border-radius:15px!important}
  #ai221 .moment .thumb{grid-column:1!important;grid-row:1/3!important;width:92px!important;height:56px!important;border-radius:12px!important}
  #ai221 .moment>b{grid-column:2!important;grid-row:1!important;margin:0!important;align-self:end!important;font-size:11px!important;line-height:1.05!important}
  #ai221 .momentMeta{grid-column:2!important;grid-row:2!important;align-self:start!important;color:#7185a6!important;font-size:8.8px!important;line-height:1.15!important;font-weight:750!important}
  #ai221 .momentChevron{grid-column:3!important;grid-row:1/3!important;display:grid!important;place-items:center!important;width:26px!important;height:26px!important;border-radius:50%!important;background:#f0f6fb!important;color:#6e88a7!important;font-size:18px!important;font-weight:800!important}
  #ai221 .rank{width:21px!important;height:21px!important;font-size:8.5px!important}
  #ai221 .moment .play{width:28px!important;height:28px!important;font-size:10px!important}
  #ai221 .momentNextActions,#ai221 .momentFullscreen{display:none!important}
  #ai221 .selectedShortPage{position:fixed!important;inset:0!important;z-index:12000!important;box-sizing:border-box!important;overflow:hidden!important;padding:8px 8px 10px!important;background:radial-gradient(circle at 8% 6%,rgba(126,214,255,.18),transparent 25%),radial-gradient(circle at 92% 7%,rgba(127,236,197,.15),transparent 26%),linear-gradient(180deg,#FCFEFF 0%,#F8FCFF 60%,#F4FAFF 100%)!important}
  #ai221 .selectedShortPage.open{display:grid!important;grid-template-rows:auto auto minmax(0,1fr) auto auto!important;gap:7px!important}
  #ai221 .selectedBack{justify-self:start!important;border:0!important;background:transparent!important;color:#3e93db!important;font-size:10.5px!important;font-weight:900!important;padding:2px 4px!important}
  #ai221 .selectedHead{display:flex!important;align-items:center!important;gap:9px!important}
  #ai221 .selectedHeadIcon{width:40px!important;height:40px!important;border-radius:14px!important;display:grid!important;place-items:center!important;background:linear-gradient(145deg,#e6f6ff,#d9f0ff)!important;color:#2e8fe3!important;font-size:19px!important;font-weight:900!important}
  #ai221 .selectedHead h2{margin:0!important;font-size:22px!important;line-height:1!important;color:#0d2a66!important}
  #ai221 .selectedHead p{margin:3px 0 0!important;font-size:9.5px!important;color:#7185a6!important;font-weight:750!important}
  #ai221 .selectedBody{min-height:0!important;display:grid!important;grid-template-columns:minmax(0,44%) minmax(0,56%)!important;gap:8px!important;overflow:hidden!important}
  #ai221 .selectedPreviewWrap{min-height:0!important;display:flex!important;align-items:center!important;justify-content:center!important}
  #ai221 .selectedPreview{display:block!important;width:min(100%,210px)!important;max-height:100%!important;aspect-ratio:9/16!important;object-fit:cover!important;background:#06111e!important;border-radius:18px!important;border:2px solid rgba(98,189,239,.55)!important;box-shadow:0 10px 24px rgba(69,157,223,.14)!important}
  #ai221 .selectedDetails{min-height:0!important;overflow:hidden!important;border:1px solid rgba(143,181,216,.20)!important;border-radius:18px!important;background:rgba(255,255,255,.93)!important;padding:8px!important;box-shadow:0 10px 24px rgba(61,104,145,.055)!important}
  #ai221 .selectedDetailsTitle{font-size:12px!important;font-weight:950!important;margin:0 0 6px!important;color:#0d2a66!important}
  #ai221 .selectedDetailRow{display:grid!important;grid-template-columns:58px minmax(0,1fr)!important;gap:6px!important;padding:4px 0!important;border-bottom:1px solid rgba(143,181,216,.13)!important}
  #ai221 .selectedDetailRow:last-child{border-bottom:0!important}
  #ai221 .selectedDetailRow span:first-child{font-size:8px!important;color:#8798ae!important;font-weight:850!important}
  #ai221 .selectedDetailRow span:last-child{font-size:8.8px!important;color:#18376f!important;font-weight:750!important;line-height:1.15!important;word-break:break-word!important}
  #ai221 .selectedTags{display:flex!important;flex-wrap:wrap!important;gap:3px!important}
  #ai221 .selectedTags i{font-style:normal!important;padding:3px 5px!important;border-radius:999px!important;background:#eaf5ff!important;color:#217ec7!important;font-size:7.6px!important;font-weight:850!important}
  #ai221 .selectedPrimary{display:grid!important;grid-template-columns:1fr 1fr!important;gap:7px!important}
  #ai221 .selectedAction{min-height:42px!important;border:0!important;border-radius:14px!important;font-size:10px!important;font-weight:900!important;cursor:pointer!important}
  #ai221 .selectedAction.editor{background:linear-gradient(145deg,#ddf6ea,#cff0dd)!important;color:#24765b!important}
  #ai221 .selectedAction.publish{background:linear-gradient(135deg,#77d3fb,#4ea7f3)!important;color:#fff!important}
  #ai221 .selectedAnother{min-height:36px!important;border:1px solid rgba(105,170,220,.24)!important;border-radius:13px!important;background:rgba(255,255,255,.85)!important;color:#2f84cc!important;font-size:9.5px!important;font-weight:900!important}
}
@media(max-width:390px) and (max-height:760px){
  #ai221 h1{font-size:19.5px!important}#ai221 .titleIcon{width:38px!important;height:38px!important}
  #ai221 .engine{min-height:96px!important;padding:7px!important}#ai221 .engine p{font-size:8.7px!important}
  #ai221 .create{min-height:40px!important}#ai221 .moment{min-height:60px!important}#ai221 .moment .thumb{height:50px!important}
  #ai221 .selectedShortPage.open{gap:5px!important}#ai221 .selectedHead h2{font-size:19px!important}#ai221 .selectedHead p{font-size:8.8px!important}
  #ai221 .selectedBody{grid-template-columns:42% 58%!important;gap:6px!important}#ai221 .selectedDetails{padding:6px!important}
  #ai221 .selectedDetailRow{padding:3px 0!important}#ai221 .selectedAction{min-height:38px!important;font-size:9.5px!important}#ai221 .selectedAnother{min-height:32px!important}
}
</style>'''

EMPTY_RESULTS = '<div class="v317EmptyResults" id="v317EmptyResults">🎮 I tuoi momenti appariranno qui dopo l’analisi.</div>'
SELECTED_PAGE = r'''
 <section class="selectedShortPage" id="selectedShortPage" aria-hidden="true" aria-label="Short selezionato">
  <button class="selectedBack" id="selectedBack" type="button">← Torna ai momenti</button>
  <div class="selectedHead"><div class="selectedHeadIcon">✦</div><div><h2>Short selezionato</h2><p>Anteprima e dati pronti in automatico.</p></div></div>
  <div class="selectedBody">
   <div class="selectedPreviewWrap"><video class="selectedPreview" id="selectedShortVideo" controls playsinline preload="metadata"></video></div>
   <div class="selectedDetails">
    <div class="selectedDetailsTitle">Dettagli pronti</div>
    <div class="selectedDetailRow"><span>Titolo</span><span id="selectedTitle">—</span></div>
    <div class="selectedDetailRow"><span>Descrizione</span><span id="selectedDescription">—</span></div>
    <div class="selectedDetailRow"><span>Hashtag</span><span class="selectedTags" id="selectedHashtags"></span></div>
    <div class="selectedDetailRow"><span>Durata</span><span id="selectedDuration">—</span></div>
    <div class="selectedDetailRow"><span>Motore</span><span id="selectedEngine">—</span></div>
    <div class="selectedDetailRow"><span>Timecode</span><span id="selectedTimecode">—</span></div>
   </div>
  </div>
  <div class="selectedPrimary">
   <button class="selectedAction editor" id="selectedEdit" type="button">✎ Modifica in Editor</button>
   <button class="selectedAction publish" id="selectedPublish" type="button">↥ Vai alla pubblicazione</button>
  </div>
  <button class="selectedAnother" id="selectedAnother" type="button">↻ Scegli un altro momento</button>
 </section>
'''
JS = r'''
 function v317EngineLabel(name){return ({auto:"Automatico",best:"Momento migliore",action:"Più azione",reaction:"Reazioni"})[name]||"Automatico";}
 function v317Seconds(v){const n=Number(v);if(!Number.isFinite(n)||n<0)return null;const m=Math.floor(n/60),s=Math.round(n%60);return (m?String(m).padStart(2,"0")+":":"")+String(s).padStart(2,"0");}
 function v317MomentMeta(d,i){
  const start=Number(d.start_seconds??d.start??d.inPoint??d.start_time),end=Number(d.end_seconds??d.end??d.outPoint??d.end_time);let tc="";if(Number.isFinite(start)&&Number.isFinite(end)&&end>=start)tc=v317Seconds(start)+"–"+v317Seconds(end);
  const title=String(d.title||d.name||d.label||("Momento "+(i+1))),description=String(d.description||d.reason||d.caption||"Momento scelto dall’IA, pronto per il tuo Short.");let tags=d.hashtags||d.tags||[];if(typeof tags==="string")tags=tags.split(/[,\s]+/).filter(Boolean);
  if(!Array.isArray(tags)||!tags.length){const extra=state.engine==="reaction"?"#reaction":state.engine==="action"?"#action":state.engine==="best"?"#clutch":"#gaming";tags=["#gaming","#shorts",extra];}
  tags=tags.slice(0,4).map(x=>String(x).startsWith("#")?String(x):("#"+String(x)));const duration=Number(d.duration||d.duration_seconds||state.duration)||state.duration||15;return {title,description,tags,duration,tc:tc||"Clip pronta",engine:v317EngineLabel(state.engine)};
 }
 function v317SyncResults(){const root=document.getElementById("ai221"),rows=Array.isArray(state.previews)?state.previews.slice(0,3):[];if(root){root.classList.toggle("hasResults",rows.some(d=>d&&(d.video||d.cover)));root.classList.toggle("hasGameplay",!!state.loaded)}document.querySelectorAll(".moment").forEach((card,i)=>{let meta=card.querySelector(".momentMeta"),chev=card.querySelector(".momentChevron");if(!meta){meta=document.createElement("span");meta.className="momentMeta";card.appendChild(meta)}if(!chev){chev=document.createElement("span");chev.className="momentChevron";chev.textContent="›";card.appendChild(chev)}const d=rows[i]||{},m=v317MomentMeta(d,i),b=card.querySelector("b");if(b)b.textContent=m.title;meta.textContent=d&&(d.video||d.cover)?((m.tc==="Clip pronta"?"Pronto":m.tc)+" · "+m.duration+"s"):""})}
 function v317SetText(id,value){const el=document.getElementById(id);if(el)el.textContent=value}
 function openSelectedShort(index){const rows=Array.isArray(state.previews)?state.previews.slice(0,3):[],i=Math.max(0,Math.min(2,Number(index)||0)),d=rows[i]||{};if(!d.video&&!d.cover)return;state.selectedMoment=i;const page=document.getElementById("selectedShortPage"),video=document.getElementById("selectedShortVideo");if(!page||!video)return;const m=v317MomentMeta(d,i);video.poster=d.cover||"";if(d.video&&video.getAttribute("src")!==d.video){video.setAttribute("src",d.video);video.load()}v317SetText("selectedTitle",m.title);v317SetText("selectedDescription",m.description);v317SetText("selectedDuration",m.duration+"s");v317SetText("selectedEngine",m.engine);v317SetText("selectedTimecode",m.tc);const tags=document.getElementById("selectedHashtags");if(tags){tags.innerHTML="";m.tags.forEach(t=>{const x=document.createElement("i");x.textContent=t;tags.appendChild(x)})}page.classList.add("open");page.setAttribute("aria-hidden","false");const play=video.play();if(play&&play.catch)play.catch(()=>{})}
 function closeSelectedShort(){const page=document.getElementById("selectedShortPage"),video=document.getElementById("selectedShortVideo");if(video)try{video.pause()}catch(_e){};if(page){page.classList.remove("open");page.setAttribute("aria-hidden","true")}}
'''
CLICK_OLD = r'''document.querySelectorAll(".moment").forEach(card=>card.addEventListener("click",()=>{
  const index=Number(card.dataset.index)||0;
  if(window.matchMedia("(max-width:760px)").matches){
   if(typeof selectMoment==="function")selectMoment(index,true);else send("preview",{index});
   openMomentPreview(index);
   return;
  }
  if(typeof selectMoment==="function")selectMoment(index,true);else send("preview",{index});
 }));'''
CLICK_NEW = CLICK_OLD.replace('openMomentPreview(index);','openSelectedShort(index);')
BINDINGS = r'''
 const selectedBack=document.getElementById("selectedBack"),selectedAnother=document.getElementById("selectedAnother"),selectedEdit=document.getElementById("selectedEdit"),selectedPublish=document.getElementById("selectedPublish");
 if(selectedBack)selectedBack.addEventListener("click",closeSelectedShort);if(selectedAnother)selectedAnother.addEventListener("click",closeSelectedShort);
 if(selectedEdit)selectedEdit.addEventListener("click",()=>{if(state.selectedMoment<0)return;send("open_editor",{index:state.selectedMoment,duration:state.duration,engine:state.engine})});
 if(selectedPublish)selectedPublish.addEventListener("click",()=>{if(state.selectedMoment<0)return;send("create_short",{index:state.selectedMoment,duration:state.duration,engine:state.engine})});
'''
SHORT_COPY={"Quattro modi diversi di leggere il gameplay. Il cervello è lo stesso, cambia ciò che cerchiamo.":"Scegli come l’IA deve leggere il tuo gameplay.","Lascia decidere alla nostra IA quali momenti meritano davvero.":"L’IA sceglie i momenti migliori.","Cerca il picco più forte: clutch, vittorie e giocate che restano.":"Cerca il picco più forte.","Predilige ritmo, impatti, esplosioni e gameplay ad alta intensità.":"Privilegia ritmo e intensità.","Segue voce, emozioni, errori epici e momenti spontanei.":"Segue emozioni e voce."}

def _clean(text:str)->str:
    text=re.sub(r'<style id="'+re.escape(STYLE_ID)+r'">.*?</style>\n?','',text,count=1,flags=re.DOTALL);text=re.sub(r'\n?\s*<div class="v317EmptyResults" id="v317EmptyResults">.*?</div>','',text,count=1,flags=re.DOTALL);text=re.sub(r'\n?\s*<section class="selectedShortPage" id="selectedShortPage".*?</section>','',text,count=1,flags=re.DOTALL);return text

def patch_text(text:str)->str:
    if 'V308 MOBILE AI FLOW' not in text:raise RuntimeError('V317 requires V308 mobile AI flow first')
    if STYLE_ID in text:return text
    out=_clean(text)
    for old,new in SHORT_COPY.items():out=out.replace(old,new,1)
    if '</head>' not in out:raise RuntimeError('V317 </head> anchor missing')
    out=out.replace('</head>',STYLE+'\n</head>',1)
    anchor='<div class="moments">'
    if anchor not in out:raise RuntimeError('V317 moments anchor missing')
    out=out.replace(anchor,EMPTY_RESULTS+'\n  '+anchor,1)
    anchor='</main>\n<script>'
    if anchor not in out:raise RuntimeError('V317 main/script anchor missing')
    out=out.replace(anchor,SELECTED_PAGE+'\n</main>\n<script>',1)
    anchor=' function sync(){'
    if anchor not in out:raise RuntimeError('V317 sync anchor missing')
    out=out.replace(anchor,JS+'\n function sync(){\n  v317SyncResults();',1)
    if CLICK_OLD not in out:raise RuntimeError('V317 V308 moment click anchor missing')
    out=out.replace(CLICK_OLD,CLICK_NEW,1)
    create_anchor='create.addEventListener("click",()=>{if(!state.loaded)return;guide("creating");status.textContent="L’IA sta cercando i momenti migliori…";send("create",{engine:state.engine,duration:state.duration})});'
    if create_anchor not in out:raise RuntimeError('V317 create handler anchor missing')
    return out.replace(create_anchor,create_anchor+'\n'+BINDINGS,1)

def main()->None:
    target=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app/web/ai_v221_component/index.html')
    if not target.is_file():raise SystemExit(f'V317 AI component missing: {target}')
    before=target.read_text(encoding='utf-8');after=patch_text(before);target.write_text(after,encoding='utf-8');print('V317 compact AI + selected short page applied changed=',before!=after,flush=True)

if __name__=='__main__':main()
