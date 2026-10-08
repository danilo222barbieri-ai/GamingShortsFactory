#!/usr/bin/env python3
from pathlib import Path
import re
import sys

STYLE_ID='v320AiMobileStability'
STYLE=r'''<style id="v320AiMobileStability">
/* V320: mobile AI stability + use the empty lower viewport for results. */
@media(max-width:760px){
  #ai221{
    display:flex!important;
    flex-direction:column!important;
    min-height:0!important;
    padding-bottom:96px!important;
  }
  #ai221>.top{flex:0 0 auto!important}
  #ai221>.panel:not(:has(.moments)){flex:0 0 auto!important}
  #ai221>.panel:has(.moments){
    flex:1 1 0!important;
    min-height:0!important;
    display:flex!important;
    flex-direction:column!important;
    overflow:hidden!important;
  }
  #ai221>.panel:has(.moments) .panelHead{flex:0 0 auto!important}
  #ai221>.panel:has(.moments) .moments{flex:1 1 auto!important;min-height:0!important}
  #ai221:not(.hasResults) .v317EmptyResults{flex:1 1 auto!important;min-height:150px!important}
  #ai221.hasResults .moments{
    display:grid!important;
    grid-template-columns:1fr!important;
    grid-template-rows:repeat(3,minmax(0,1fr))!important;
    align-content:stretch!important;
  }
  #ai221.hasResults .moment{height:100%!important;min-height:0!important}
  #ai221.v320Recovering .status{display:block!important;color:#2d83c7!important;font-weight:850!important}
}
@media(max-width:760px) and (max-height:760px){
  #ai221{padding-bottom:84px!important}
  #ai221:not(.hasResults) .v317EmptyResults{min-height:118px!important}
}
</style>'''

JS=r'''
 /* V320 MOBILE AI STABILITY */
 const V320_SELECTED_KEY="GSF_AI_SELECTED_SHORT_V320";
 function v320AssertAiRoute(){
   try{parent.postMessage({type:"GSF_SHELL_NAV",target:"ai"},location.origin)}catch(_e){}
 }
 function v320RequestState(){
   v320AssertAiRoute();
   try{send("ready")}catch(_e){}
 }
 function v320Delay(ms){return new Promise(resolve=>setTimeout(resolve,ms))}
 async function v320StartAnalysis(){
   const root=document.getElementById("ai221");
   v320AssertAiRoute();
   if(!state.loaded){
     if(root)root.classList.add("v320Recovering");
     if(status)status.textContent="Recupero il gameplay del progetto…";
     for(let attempt=0;attempt<5&&!state.loaded;attempt++){
       v320RequestState();
       await v320Delay(240);
     }
     if(root)root.classList.remove("v320Recovering");
   }
   if(!state.loaded){
     if(typeof v319Fail==="function")v319Fail("Nessun gameplay attivo. Torna alla Home, caricalo e poi riapri Crea con IA.");
     else if(status)status.textContent="Nessun gameplay attivo. Torna alla Home e caricalo.";
     return;
   }
   v319StartAnalysis();
 }
 function v320RememberSelected(index){
   try{sessionStorage.setItem(V320_SELECTED_KEY,String(index))}catch(_e){}
 }
 function v320ForgetSelected(){
   try{sessionStorage.removeItem(V320_SELECTED_KEY)}catch(_e){}
 }
 function v320RestoreSelected(){
   const page=document.getElementById("selectedShortPage");
   if(!page||page.classList.contains("open"))return;
   let raw=null;
   try{raw=sessionStorage.getItem(V320_SELECTED_KEY)}catch(_e){}
   if(raw===null)return;
   const index=Number(raw);
   const rows=Array.isArray(state.previews)?state.previews:[];
   if(!Number.isInteger(index)||index<0||index>2||!rows[index]||(!rows[index].video&&!rows[index].cover))return;
   openSelectedShort(index);
 }
 setTimeout(v320RequestState,80);
 setTimeout(v320RequestState,420);
 setTimeout(v320RequestState,1000);
 setInterval(v320RestoreSelected,350);
'''

def _clean(text:str)->str:
    text=re.sub(r'<style id="'+re.escape(STYLE_ID)+r'">.*?</style>\n?','',text,count=1,flags=re.DOTALL)
    text=re.sub(r'\n?\s*/\* V320 MOBILE AI STABILITY \*/.*?setInterval\(v320RestoreSelected,350\);\n?','',text,count=1,flags=re.DOTALL)
    return text

def patch_text(text:str)->str:
    if STYLE_ID in text and 'V320 MOBILE AI STABILITY' in text and 'create.addEventListener("click",v320StartAnalysis);' in text and 'function v320AssertAiRoute()' in text and '#ai221>.panel:has(.moments){' in text:
        return text
    if 'v317AiCompactSelectedShort' not in text:
        raise RuntimeError('V320 requires V317 compact AI flow')
    if 'v319AiResultsBridgeStyle' not in text or 'function v319StartAnalysis()' not in text:
        raise RuntimeError('V320 requires V319 AI result bridge')
    out=_clean(text)
    if '</head>' not in out:
        raise RuntimeError('V320 AI </head> anchor missing')
    out=out.replace('</head>',STYLE+'\n</head>',1)

    out=out.replace('create.disabled=!!on||!state.loaded;','create.disabled=!!on;')
    out=out.replace('create.disabled=!state.loaded;','create.disabled=false;')

    open_anchor='page.classList.add("open");page.setAttribute("aria-hidden","false");'
    if open_anchor not in out:
        raise RuntimeError('V320 selected short open anchor missing')
    out=out.replace(open_anchor,open_anchor+'v320RememberSelected(i);video.setAttribute("playsinline","");video.setAttribute("webkit-playsinline","");',1)

    autoplay='const play=video.play();if(play&&play.catch)play.catch(()=>{})'
    if autoplay not in out:
        raise RuntimeError('V320 selected short autoplay anchor missing')
    out=out.replace(autoplay,'try{video.currentTime=0}catch(_e){}',1)

    close_anchor='if(page){page.classList.remove("open");page.setAttribute("aria-hidden","true")}}'
    if close_anchor not in out:
        raise RuntimeError('V320 selected short close anchor missing')
    out=out.replace(close_anchor,'if(page){page.classList.remove("open");page.setAttribute("aria-hidden","true")}v320ForgetSelected()}',1)

    handler='create.addEventListener("click",v319StartAnalysis);'
    if handler not in out:
        raise RuntimeError('V320 V319 create handler anchor missing')
    out=out.replace(handler,JS+'\n create.addEventListener("click",v320StartAnalysis);',1)
    return out

def main()->None:
    path=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app/web/ai_v221_component/index.html')
    if not path.is_file():
        raise SystemExit(f'V320 AI target missing: {path}')
    before=path.read_text(encoding='utf-8')
    after=patch_text(before)
    path.write_text(after,encoding='utf-8')
    print('V320 mobile AI stability applied changed=',before!=after,flush=True)

if __name__=='__main__':
    main()
