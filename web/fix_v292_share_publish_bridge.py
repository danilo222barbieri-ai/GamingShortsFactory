#!/usr/bin/env python3
from pathlib import Path
import sys

MARKER='GSF_V292_SHARE_PUBLISH_INTENT'

def main():
    target=Path(sys.argv[1] if len(sys.argv)>1 else '/app/web/share_v156_component/index.html')
    if not target.exists():
        local=Path(__file__).with_name('share_v156_component')/'index.html'
        target=local if local.exists() else target
    text=target.read_text(encoding='utf-8')
    if MARKER in text:
        print('V292 share publish bridge already applied:',target)
        return

    parent_anchor=' const parentClick=(words)=>{try{const d=parent.document,els=[...d.querySelectorAll("button,a,[role=button]")].filter(x=>!x.closest("#gsf-social-overlay-v159"));const e=els.find(x=>words.some(w=>(x.innerText||x.textContent||"").toLowerCase().includes(w)));if(e){e.click();return true}}catch(e){}return false};\n'
    if parent_anchor not in text:
        raise SystemExit('V292 share parentClick anchor missing')

    bridge=r''' /* GSF_V292_SHARE_PUBLISH_INTENT */
 const PUBLISH_INTENT_KEY="gsf_share_publish_v292";
 const clearPublishIntent=()=>{try{sessionStorage.removeItem(PUBLISH_INTENT_KEY)}catch(_e){}};
 const readPublishIntent=()=>{try{const v=JSON.parse(sessionStorage.getItem(PUBLISH_INTENT_KEY)||"null");return v&&v.platform?v:null}catch(_e){return null}};
 const savePublishIntent=(platform)=>{try{sessionStorage.setItem(PUBLISH_INTENT_KEY,JSON.stringify({platform:String(platform||""),at:Date.now()}))}catch(_e){}};
 const publishCandidate=(platform)=>{
   try{
     const d=parent.document,key=String(platform||"").toLowerCase();
     const els=[...d.querySelectorAll("button,a,[role=button]")].filter(el=>{
       if(el.closest("#gsf-social-overlay-v159"))return false;
       const s=parent.getComputedStyle?parent.getComputedStyle(el):null;
       if(s&&(s.display==="none"||s.visibility==="hidden"))return false;
       const t=(el.innerText||el.textContent||"").trim().toLowerCase();
       return t.includes("pubblica")||t.includes("publish");
     });
     for(const el of els){
       const own=(el.innerText||el.textContent||"").toLowerCase();
       if(own.includes(key)){clearPublishIntent();el.click();return true}
       let node=el.parentElement,depth=0;
       while(node&&depth++<5&&node!==d.body){
         const txt=(node.innerText||node.textContent||"").toLowerCase();
         if(txt.includes(key)){clearPublishIntent();el.click();return true}
         node=node.parentElement;
       }
     }
   }catch(_e){}
   return false;
 };
 const resumePublishIntent=()=>{
   const intent=readPublishIntent();
   if(!intent)return;
   if(!intent.at||Date.now()-Number(intent.at)>20000){clearPublishIntent();return}
   let tries=0;
   const tick=()=>{
     const current=readPublishIntent();
     if(!current)return;
     if(publishCandidate(current.platform))return;
     if(++tries>=50){clearPublishIntent();return}
     setTimeout(tick,300);
   };
   setTimeout(tick,500);
 };
 const armPublish=(platform)=>{savePublishIntent(platform);setTimeout(resumePublishIntent,650)};
'''
    text=text.replace(parent_anchor,parent_anchor+bridge,1)

    copy_old='btn.textContent=(yes?"Apri ":"Collega ")+names[key]+(yes?" ↗":"");'
    copy_new='btn.textContent=(yes?"Pubblica su ":"Collega ")+names[key]+(yes?" →":"");'
    if copy_old not in text:
        raise SystemExit('V292 connected social CTA anchor missing')
    text=text.replace(copy_old,copy_new,1)

    click_old='   setGuide(connected?key:"connect");\n   setTimeout(()=>parentClick([key]),connected?180:650);'
    click_new='   setGuide(connected?key:"connect");\n   if(connected){armPublish(key);setTimeout(()=>parentClick([key]),180)}\n   else setTimeout(()=>parentClick([key]),650);'
    if click_old not in text:
        raise SystemExit('V292 social click anchor missing')
    text=text.replace(click_old,click_new,1)

    load_old=' load();\n /* V159 regression compatibility only; no visible player exists:'
    load_new=' load();\n resumePublishIntent();\n /* V159 regression compatibility only; no visible player exists:'
    if load_old not in text:
        raise SystemExit('V292 share load anchor missing')
    text=text.replace(load_old,load_new,1)

    target.write_text(text,encoding='utf-8')
    print('V292 share direct-publish resume bridge applied:',target)

if __name__=='__main__':
    main()
