import ast
import re
from pathlib import Path
import streamlit

from gsf_desktop_shell_v407 import build_desktop_shell_html

index=Path(streamlit.__file__).resolve().parent/"static"/"index.html"
if not index.is_file():
    raise RuntimeError(f"Streamlit index not found: {index}")

s=index.read_text(encoding="utf-8")
# Install lifecycle synchronously in the parent before React or any component
# iframe. Component execution order is not a lifecycle/bootstrap guarantee.
navigation_marker='id="gsf-navigation-lifecycle"'
navigation=(Path(__file__).parent/"gsf_navigation_lifecycle.js").read_text(encoding="utf-8")
# Canonical app literals are the controller source, copied verbatim into the
# top realm. They are data in Streamlit, never transient component iframes.
app_source=(Path(__file__).parent.parent/"app.py").read_text(encoding="utf-8")
selectors={"SHELL":"body","SOCIAL":"#gsf-social-overlay-v159","EDITOR":"#gsf-editor-overlay-v220","AI":"#gsf-ai-overlay-v221","FOOTER348":"#gsf-global-footer","FOOTER350":"#gsf-global-footer","FOOTER351":"#gsf-global-footer","NOTIFICATIONS":"body"}
controllers={}
for node in ast.walk(ast.parse(app_source)):
    if not isinstance(node,ast.Assign) or not isinstance(node.value,ast.Constant):continue
    for target in node.targets:
        if isinstance(target,ast.Name) and target.id.startswith("_GSF_PARENT_"):
            controllers[target.id.removeprefix("_GSF_PARENT_")]=node.value.value
if controllers.keys()!=selectors.keys():raise RuntimeError("incomplete parent controllers")
mounts=[]
for name,selector in selectors.items():
    scripts=re.findall(r"<script[^>]*>([\s\S]*?)</script>",controllers[name])
    if not scripts:raise RuntimeError("empty parent controller: "+name)
    mounts.append("{selector:"+repr(selector)+",node:null,mount:()=>{"+"\n".join(scripts)+"}}")
bootstrap="""
(() => {
 const controllers=[CONTROLLERS];
 const mount=()=>{
   for(const entry of controllers){
     const node=document.querySelector(entry.selector);
     if(node&&node!==entry.node){entry.node=node;entry.mount();}
   }
 };
 new MutationObserver(mount).observe(document.documentElement,{childList:true,subtree:true});
 mount();
})();
""".replace("CONTROLLERS",",\n".join(mounts))
navigation_script='<script '+navigation_marker+'>'+navigation+bootstrap+'</script>'
if navigation_marker in s:
    start=s.index('<script '+navigation_marker)
    end=s.index('</script>',start)+len('</script>')
    s=s[:start]+navigation_script+s[end:]
else:
    s=s.replace("</head>",navigation_script+'\n</head>',1)
index.write_text(s,encoding="utf-8")

marker='id="gsf-adsense-bridge"'
if marker in s:
    print("V105.7/V407 browser bridge already installed:",index)
    raise SystemExit(0)

# V407 reuses the same Streamlit top-level browser bridge as AdSense. This is
# intentional: desktop is only a browser frame around the existing mobile app,
# so no second Streamlit application or duplicated page tree is created.
shell=build_desktop_shell_html()
style_start=shell.index('<style id="gsf-desktop-mobile-shell-v407">')
style_end=shell.index('</style>',style_start)+len('</style>')
v407_style=shell[style_start:style_end]

script=r'''
<script id="gsf-adsense-bridge">
(function(){
  if(window.__GSF_ADSENSE_BRIDGE__) return;
  window.__GSF_ADSENSE_BRIDGE__=true;

  var loader=null;
  function validClient(v){ return /^ca-pub-\d{10,20}$/.test(v||""); }
  function validSlot(v){ return /^\d{5,20}$/.test(v||""); }

  function loadAdsense(client){
    if(loader) return loader;
    loader=new Promise(function(resolve,reject){
      var existing=document.querySelector('script[data-gsf-adsense-loader="1"]');
      if(existing){
        if(existing.dataset.loaded==="1") return resolve();
        existing.addEventListener("load",resolve,{once:true});
        existing.addEventListener("error",reject,{once:true});
        return;
      }
      var script=document.createElement("script");
      script.async=true;
      script.crossOrigin="anonymous";
      script.dataset.gsfAdsenseLoader="1";
      script.src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client="+encodeURIComponent(client);
      script.addEventListener("load",function(){script.dataset.loaded="1";resolve();},{once:true});
      script.addEventListener("error",reject,{once:true});
      document.head.appendChild(script);
    });
    return loader;
  }

  function mount(node){
    if(!node || node.dataset.gsfAdMounted==="1") return;
    var client=node.dataset.adClient||"";
    var slot=node.dataset.adSlot||"";
    if(!validClient(client) || !validSlot(slot)) return;

    var host=node.querySelector(".gsf-v1057-ad-mount");
    if(!host) return;
    if(host.querySelector("ins.adsbygoogle")){
      node.dataset.gsfAdMounted="1";
      return;
    }

    var ins=document.createElement("ins");
    ins.className="adsbygoogle";
    ins.style.display="block";
    ins.setAttribute("data-ad-client",client);
    ins.setAttribute("data-ad-slot",slot);
    ins.setAttribute("data-ad-format","auto");
    ins.setAttribute("data-full-width-responsive","true");
    host.replaceChildren(ins);
    node.dataset.gsfAdMounted="1";

    loadAdsense(client).then(function(){
      try{
        (window.adsbygoogle=window.adsbygoogle||[]).push({});
      }catch(err){
        node.dataset.gsfAdMounted="0";
      }
    }).catch(function(){
      node.dataset.gsfAdMounted="0";
    });
  }

  function ensureRail(id,sideClass){
    var rail=document.getElementById(id);
    if(!rail){
      rail=document.createElement("aside");
      rail.id=id;
      rail.className="gsf-desktop-ad-rail "+sideClass;
      rail.setAttribute("aria-label",sideClass.indexOf("left")>=0?"Pubblicità sinistra":"Pubblicità destra");
      var content=document.createElement("div");
      content.className="gsf-desktop-ad-content";
      rail.appendChild(content);
      document.body.appendChild(rail);
    }
    return rail;
  }

  function createRail(id,sideClass,source){
    if(!source) return null;
    var client=source.dataset.adClient||"";
    var slot=source.dataset.adSlot||"";
    if(!validClient(client) || !validSlot(slot)) return null;

    var rail=ensureRail(id,sideClass);
    var content=rail.querySelector(".gsf-desktop-ad-content");
    var ad=content && content.querySelector(".gsf-v407-rail-ad");
    var changed=!ad || ad.dataset.adClient!==client || ad.dataset.adSlot!==slot;
    if(changed){
      ad=document.createElement("div");
      ad.className="gsf-v1057-ad gsf-v1057-live gsf-v407-rail-ad";
      ad.dataset.adClient=client;
      ad.dataset.adSlot=slot;
      ad.dataset.gsfPlacement=id;
      var host=document.createElement("div");
      host.className="gsf-v1057-ad-mount";
      host.setAttribute("aria-label","Annuncio Google");
      ad.appendChild(host);
      content.replaceChildren(ad);
    }
    return ad;
  }

  function createPreviewRail(id,sideClass,label){
    var rail=ensureRail(id,sideClass);
    var content=rail.querySelector(".gsf-desktop-ad-content");
    if(content.querySelector(".gsf-desktop-ad-placeholder")) return rail;

    var placeholder=document.createElement("div");
    placeholder.className="gsf-desktop-ad-placeholder";
    var kicker=document.createElement("span");
    kicker.className="gsf-desktop-ad-kicker";
    kicker.textContent="AD";
    var title=document.createElement("strong");
    title.textContent="SPAZIO PUBBLICITARIO";
    var side=document.createElement("small");
    side.textContent="RAIL "+label;
    placeholder.append(kicker,title,side);
    content.replaceChildren(placeholder);
    return rail;
  }

  function removeDesktopRails(){
    ["gsf-desktop-ad-left","gsf-desktop-ad-right"].forEach(function(id){
      var rail=document.getElementById(id);
      if(rail) rail.remove();
    });
  }

  function syncDesktopRails(){
    var liveSources=Array.from(document.querySelectorAll(
      ".gsf-v1057-live[data-ad-client][data-ad-slot]:not(.gsf-v407-rail-ad)"
    ));
    if(liveSources.length){
      var left=createRail("gsf-desktop-ad-left","gsf-desktop-ad-left",liveSources[0]);
      var right=createRail("gsf-desktop-ad-right","gsf-desktop-ad-right",liveSources[1]||liveSources[0]);
      mount(left);
      mount(right);
      return;
    }

    var previewSources=Array.from(document.querySelectorAll(
      ".gsf-v1057-ad:not(.gsf-v1057-live)"
    )).filter(function(node){
      return getComputedStyle(node).display!=="none";
    });
    if(previewSources.length){
      createPreviewRail("gsf-desktop-ad-left","gsf-desktop-ad-left","SINISTRA");
      createPreviewRail("gsf-desktop-ad-right","gsf-desktop-ad-right","DESTRA");
      return;
    }

    removeDesktopRails();
  }

  function scan(){
    document.querySelectorAll(".gsf-v1057-live[data-ad-client][data-ad-slot]").forEach(mount);
    syncDesktopRails();
  }

  function boot(){
    scan();
    var observer=new MutationObserver(scan);
    observer.observe(document.body,{childList:true,subtree:true});
  }

  if(document.readyState==="loading"){
    document.addEventListener("DOMContentLoaded",boot,{once:true});
  }else{
    boot();
  }
})();
</script>
'''

needle="</head>"
if needle not in s:
    raise RuntimeError("Streamlit </head> not found")
s=s.replace(needle,v407_style+"\n"+script+"\n"+needle,1)
index.write_text(s,encoding="utf-8")
print("V105.7 AdSense + V407 desktop mobile shell bridge installed:",index)
