from pathlib import Path
import re

SHARE=Path('/app/web/share_v156_component/index.html')
APP=Path('/app/GamingShortsFactory_V154_STRUCTURAL_HOME.py')


def once(text,old,new,label):
    if old not in text:
        raise RuntimeError('V290 anchor missing: '+label)
    return text.replace(old,new,1)


def patch_share():
    s=SHARE.read_text(encoding='utf-8')
    before=s
    if 'V290 SOCIAL PUBLISH BRIDGE' not in s:
        s=once(
            s,
            'btn.textContent=(yes?"Apri ":"Collega ")+names[key]+(yes?" ↗":"");',
            'btn.textContent=(yes?"Pubblica su ":"Collega ")+names[key]+(yes?" →":"");',
            'connected social CTA copy',
        )
        old=''' document.querySelectorAll("[data-platform]").forEach(b=>b.onclick=()=>{\n   const key=b.dataset.platform,connected=!!(state.social||{})[key];\n   if(key==="facebook"){\n     setGuide("facebook");\n     window.open("https://www.facebook.com/","_blank","noopener,noreferrer");\n     return;\n   }\n   setGuide(connected?key:"connect");\n   setTimeout(()=>parentClick([key]),connected?180:650);\n });'''
        new=''' document.querySelectorAll("[data-platform]").forEach(b=>b.onclick=()=>{\n   const key=b.dataset.platform,connected=!!(state.social||{})[key];\n   if(key==="facebook"){\n     setGuide("facebook");\n     window.open("https://www.facebook.com/","_blank","noopener,noreferrer");\n     return;\n   }\n   if(!connected){\n     setGuide("connect");\n     window.open("/social-connect","_blank","noopener,noreferrer");\n     toast("Collega "+names[key]+", poi torna qui");\n     return;\n   }\n   setGuide(key);\n   b.disabled=true;b.dataset.oldText=b.textContent;b.textContent="Pubblicazione…";\n   try{parent.postMessage({type:"GSF_SOCIAL_PUBLISH",platform:key},location.origin)}catch(e){b.disabled=false;b.textContent=b.dataset.oldText||("Pubblica su "+names[key])}\n });'''
        s=once(s,old,new,'share platform handler')
        old=''' window.addEventListener("message",e=>{\n   if(e.origin!==location.origin||!e.data||e.data.type!=="GSF_SHARE_FOCUS")return;\n   const key=String(e.data.platform||"");\n   if(!key)return;'''
        new=''' window.addEventListener("message",e=>{\n   if(e.origin!==location.origin||!e.data)return;\n   if(e.data.type==="GSF_SOCIAL_RESULT"){\n     const key=String(e.data.platform||"");\n     const btn=document.querySelector('[data-platform="'+key+'"]');\n     if(btn){btn.disabled=false;btn.textContent=(e.data.ok?"Pubblicato su ":"Riprova su ")+(names[key]||key)+(e.data.ok?" ✓":"");}\n     toast(String(e.data.message||(e.data.ok?"Pubblicazione completata":"Pubblicazione non riuscita")));\n     if(e.data.ok)setTimeout(load,700);\n     return;\n   }\n   if(e.data.type!=="GSF_SHARE_FOCUS")return;\n   const key=String(e.data.platform||"");\n   if(!key)return;'''
        s=once(s,old,new,'share result listener')
        s=once(
            s,
            ' load();\n /* V159 regression compatibility only;',
            ' window.addEventListener("focus",()=>setTimeout(load,250));\n load();\n /* V290 SOCIAL PUBLISH BRIDGE */\n /* V159 regression compatibility only;',
            'share focus refresh marker',
        )
    SHARE.write_text(s,encoding='utf-8')
    print('V290 share bridge applied:',s!=before,flush=True)


def patch_app():
    s=APP.read_text(encoding='utf-8')
    before=s
    if 'V290 SOCIAL PUBLISH BRIDGE' not in s:
        start=s.find('# V159 — Social/Share')
        end=s.find('# V160 —',start)
        if start<0 or end<0:
            raise RuntimeError('V290 social shell boundaries missing')
        seg=s[start:end]
        seg=once(
            seg,
            "      const frame=o.querySelector('iframe');\n",
            "      const frame=o.querySelector('iframe');\n      const OPEN_KEY='gsf_social_overlay_open_v290';\n      const PUBLISH_KEY='gsf_social_publish_pending_v290';\n",
            'social storage keys',
        )
        seg=once(
            seg,
            "        o.setAttribute('aria-hidden','false');\n        if(platform)setTimeout(()=>{try{frame.contentWindow.postMessage({type:'GSF_SHARE_FOCUS',platform},location.origin)}catch(e){}},90);\n",
            "        o.setAttribute('aria-hidden','false');\n        try{sessionStorage.setItem(OPEN_KEY,'1')}catch(e){}\n        if(platform)setTimeout(()=>{try{frame.contentWindow.postMessage({type:'GSF_SHARE_FOCUS',platform},location.origin)}catch(e){}},90);\n",
            'persist social open',
        )
        old_close="""      const close=()=>{\n        o.classList.remove('is-open');\n        o.style.opacity='0';o.style.visibility='hidden';o.style.pointerEvents='none';\n        o.setAttribute('aria-hidden','true');\n      };\n"""
        new_close="""      const close=()=>{\n        o.classList.remove('is-open');\n        o.style.opacity='0';o.style.visibility='hidden';o.style.pointerEvents='none';\n        o.setAttribute('aria-hidden','true');\n        try{sessionStorage.setItem(OPEN_KEY,'0');sessionStorage.removeItem(PUBLISH_KEY)}catch(e){}\n      };\n      const clickExact=(label)=>{\n        const wanted=String(label||'').trim().toLowerCase();\n        const nodes=[...document.querySelectorAll('button,[role=button]')].filter(x=>!x.closest('#gsf-social-overlay-v159'));\n        const el=nodes.find(x=>(x.innerText||x.textContent||'').trim().toLowerCase()===wanted);\n        if(el){el.click();return true}return false;\n      };\n      const sendResult=(platform,ok,message)=>{\n        setTimeout(()=>{try{frame.contentWindow.postMessage({type:'GSF_SOCIAL_RESULT',platform,ok:!!ok,message:String(message||'')},location.origin)}catch(e){}},500);\n      };\n      const publishPending=()=>{\n        let raw='';try{raw=sessionStorage.getItem(PUBLISH_KEY)||''}catch(e){}\n        if(!raw)return true;\n        const parts=raw.split(':'),phase=parts[0],platform=parts[1]||'',started=Number(parts[2]||Date.now());\n        if(Date.now()-started>240000){try{sessionStorage.removeItem(PUBLISH_KEY)}catch(e){};sendResult(platform,false,'Tempo di pubblicazione scaduto. Riprova.');return true}\n        const labels={youtube:'YouTube',tiktok:'TikTok',instagram:'Instagram'};\n        if(phase==='select'){\n          if(clickExact(labels[platform])){try{sessionStorage.setItem(PUBLISH_KEY,'confirm:'+platform+':'+started)}catch(e){};return true}\n          return false;\n        }\n        if(phase==='confirm'){\n          if(clickExact('PUBBLICA')){try{sessionStorage.setItem(PUBLISH_KEY,'result:'+platform+':'+started)}catch(e){};return true}\n          return false;\n        }\n        if(phase==='result'){\n          const texts=[...document.querySelectorAll('[data-testid=stAlert],[role=alert],.stAlert')].map(x=>(x.innerText||x.textContent||'').trim()).filter(Boolean);\n          const p=platform.toLowerCase();\n          const msg=texts.find(t=>{const l=t.toLowerCase();return (l.includes(p)||l.includes('video pubblicato'))&&/(pubblic|errore|non riusc|privat|manca|collegat)/.test(l)});\n          if(!msg)return false;\n          const bad=/(errore|non riusc|manca|non collegat|fallit)/i.test(msg);\n          try{sessionStorage.removeItem(PUBLISH_KEY)}catch(e){}\n          sendResult(platform,!bad,msg);\n          return true;\n        }\n        return true;\n      };\n      const resumePublish=()=>{\n        let tries=0;\n        const tick=()=>{\n          let raw='';try{raw=sessionStorage.getItem(PUBLISH_KEY)||''}catch(e){}\n          if(!raw)return;\n          const phase=raw.split(':')[0];\n          const acted=publishPending();\n          tries+=1;\n          if(phase==='result'||!acted){setTimeout(tick,phase==='result'?900:180);return}\n          if(tries<30)setTimeout(tick,220);\n        };\n        setTimeout(tick,120);\n      };\n"""
        seg=once(seg,old_close,new_close,'social close + publisher')
        old_listener="""      window.addEventListener('message',e=>{\n        if(e.origin!==location.origin||!e.data||e.data.type!=='GSF_SHELL_NAV')return;\n        const t=String(e.data.target||'');\n        if(t==='social')open(String(e.data.platform||''));\n        if(t==='close'||t==='home'||t==='hub'||t==='editor'||t==='ai'||t==='account')close();\n      });\n    })();\n"""
        new_listener="""      window.addEventListener('message',e=>{\n        if(e.origin!==location.origin||!e.data)return;\n        if(e.data.type==='GSF_SOCIAL_PUBLISH'){\n          const platform=String(e.data.platform||'').toLowerCase();\n          if(!['youtube','tiktok','instagram'].includes(platform))return;\n          const stamp=Date.now();\n          try{sessionStorage.setItem(OPEN_KEY,'1');sessionStorage.setItem(PUBLISH_KEY,'select:'+platform+':'+stamp)}catch(_e){}\n          open(platform);resumePublish();return;\n        }\n        if(e.data.type!=='GSF_SHELL_NAV')return;\n        const t=String(e.data.target||'');\n        if(t==='social')open(String(e.data.platform||''));\n        if(t==='close'||t==='home'||t==='hub'||t==='editor'||t==='ai'||t==='account')close();\n      });\n      try{if(sessionStorage.getItem(OPEN_KEY)==='1'){setTimeout(()=>{open();resumePublish()},90)}}catch(e){}\n      /* V290 SOCIAL PUBLISH BRIDGE */\n    })();\n"""
        seg=once(seg,old_listener,new_listener,'social publish message listener')
        s=s[:start]+seg+s[end:]
    s=re.sub(r'/share-v156/\?v=\d+','/share-v156/?v=290',s)
    APP.write_text(s,encoding='utf-8')
    print('V290 social shell bridge applied:',s!=before,flush=True)


if __name__=='__main__':
    for p in (SHARE,APP):
        if not p.is_file():
            raise RuntimeError('V290 required file missing: '+str(p))
    patch_share();patch_app()
