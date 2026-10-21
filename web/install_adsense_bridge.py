import ast
import json
import re
from pathlib import Path
import streamlit


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
surfaces={}
surface_ids={"SOCIAL":"gsf-social-overlay-v159","HUB":"gsf-creator-hub-live-v160","EDITOR":"gsf-editor-overlay-v220","AI":"gsf-ai-overlay-v221"}
for node in ast.walk(ast.parse(app_source)):
    if not isinstance(node,ast.Assign) or not isinstance(node.value,ast.Constant):continue
    for target in node.targets:
        if isinstance(target,ast.Name) and target.id.startswith("_GSF_PARENT_"):
            controllers[target.id.removeprefix("_GSF_PARENT_")]=node.value.value
        if isinstance(target,ast.Name) and target.id.startswith("_GSF_SURFACE_"):
            surfaces[target.id.removeprefix("_GSF_SURFACE_")]=node.value.value
if surfaces.keys()!=surface_ids.keys():raise RuntimeError("incomplete persistent surfaces")
if controllers.keys()!=selectors.keys():raise RuntimeError("incomplete parent controllers")
mounts=[]
for name,selector in selectors.items():
    scripts=re.findall(r"<script[^>]*>([\s\S]*?)</script>",controllers[name])
    if not scripts:raise RuntimeError("empty parent controller: "+name)
    mounts.append("{selector:"+repr(selector)+",node:null,mount:()=>{"+"\n".join(scripts)+"}}")
# Generate the initial client from its sole canonical source, without importing
# the companion server or installing a second notification implementation.
client_tree=ast.parse((Path(__file__).parent/"direct_upload_server.py").read_text(encoding="utf-8"))
client_function=next(node for node in client_tree.body if isinstance(node,ast.FunctionDef) and node.name=="_push_client_bytes")
client_namespace={}
exec(compile(ast.Module(body=[client_function],type_ignores=[]),"<canonical-notification-client>","exec"),client_namespace)
notification_client=client_namespace["_push_client_bytes"]().decode("utf-8").replace("</script","<\\/script")
bootstrap="""
(() => {
 const controllers=[CONTROLLERS];
 const surfaces=SURFACE_MARKUP;
 const installNotifications=()=>{NOTIFICATION_CLIENT};
 const mount=()=>{
   if(!document.body)return;
   if(!window.GSFNotify)installNotifications();
   for(const [id,html] of surfaces){
     if(!document.getElementById(id))document.body.insertAdjacentHTML("beforeend",html);
   }
   for(const entry of controllers){
     const node=document.querySelector(entry.selector);
     if(node&&node!==entry.node){entry.node=node;entry.mount();}
   }
 };
 new MutationObserver(mount).observe(document.documentElement,{childList:true,subtree:true});
 mount();
})();
""".replace("CONTROLLERS",",\n".join(mounts)).replace("SURFACE_MARKUP",json.dumps([[surface_ids[name],html] for name,html in surfaces.items()])).replace("NOTIFICATION_CLIENT",notification_client)
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
    print("V105.7 browser bridge already installed:",index)
    raise SystemExit(0)

# GSF_MOBILE_ONLY_V419: GSF is phone-only (desktop gets /__gsf_mobile_gate at the
# edge), so the old desktop frame and its two ad rails are no longer installed.
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

  function scan(){
    document.querySelectorAll(".gsf-v1057-live[data-ad-client][data-ad-slot]").forEach(mount);
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
s=s.replace(needle,script+"\n"+needle,1)
index.write_text(s,encoding="utf-8")
print("V105.7 AdSense bridge installed:",index)
