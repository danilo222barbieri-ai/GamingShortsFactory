from pathlib import Path
import streamlit

index=Path(streamlit.__file__).resolve().parent/"static"/"index.html"
if not index.is_file():
    raise RuntimeError(f"Streamlit index not found: {index}")

s=index.read_text(encoding="utf-8")
marker='id="gsf-adsense-bridge"'
if marker in s:
    print("V105.7 AdSense bridge already installed:",index)
    raise SystemExit(0)

script=r'''
<script id="gsf-adsense-bridge">
(function(){
  if(window.__GSF_ADSENSE_BRIDGE__) return;
  window.__GSF_ADSENSE_BRIDGE__=true;

  var loader=null;
  function validClient(v){ return /^ca-pub-\\d{10,20}$/.test(v||""); }
  function validSlot(v){ return /^\\d{5,20}$/.test(v||""); }

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
