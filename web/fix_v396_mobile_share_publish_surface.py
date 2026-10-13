#!/usr/bin/env python3
from pathlib import Path
import sys

MARK='V396_MOBILE_SHARE_PUBLISH_SURFACE'

PATCH=r'''
<!-- V396_MOBILE_SHARE_PUBLISH_SURFACE -->
<style id="v396MobileSharePublishSurface">
#v396MobilePublishSurface{display:none}
@media(max-width:760px){
  #share.v396MobileMode{overflow:auto!important;padding:8px 8px 14px!important;background:linear-gradient(180deg,#fbfeff 0%,#f3fbff 100%)!important}
  #share.v396MobileMode>:not(#v396MobilePublishSurface){display:none!important}
  #v396MobilePublishSurface{display:flex!important;flex-direction:column;gap:7px;width:100%;min-height:100%;padding:0 0 6px;color:#153d69;font-family:"Avenir Next","SF Pro Display","SF Pro Text",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
  #v396MobilePublishSurface *{box-sizing:border-box}
  .v396Mural{position:relative;min-height:92px;padding:12px 18px 10px;border-radius:23px;border:1px solid rgba(99,190,230,.28);background:radial-gradient(circle at 14% 18%,rgba(130,219,255,.18),transparent 29%),radial-gradient(circle at 86% 72%,rgba(119,226,193,.13),transparent 30%),linear-gradient(180deg,rgba(255,255,255,.88),rgba(239,249,254,.76));box-shadow:0 10px 26px rgba(55,112,151,.09),inset 0 1px 0 rgba(255,255,255,.96);overflow:hidden;display:flex;align-items:center;justify-content:center;text-align:center}
  .v396Mural:before,.v396Mural:after{content:"";position:absolute;width:44px;height:19px;border-top:2px solid rgba(89,129,174,.33);border-radius:50%;pointer-events:none}.v396Mural:before{left:20px;bottom:18px;transform:rotate(-13deg)}.v396Mural:after{right:18px;top:19px;transform:rotate(165deg)}
  .v396MuralText{position:relative;z-index:1;font-family:"Segoe Print","Bradley Hand","Comic Sans MS",cursive;color:#5b78a6;font-size:21px;font-weight:600;line-height:1.05;transform:rotate(-1.5deg);text-shadow:0 1px 0 rgba(255,255,255,.75)}
  .v396MuralText small{display:block;margin-top:6px;font-family:"Avenir Next","SF Pro Text",sans-serif;font-size:8.5px;letter-spacing:.08em;text-transform:uppercase;color:#7891ad;font-weight:850;transform:rotate(1.5deg)}
  .v396Panel{border:1px solid rgba(131,176,210,.22);border-radius:18px;background:rgba(255,255,255,.79);box-shadow:0 8px 21px rgba(58,103,139,.07),inset 0 1px 0 rgba(255,255,255,.95);-webkit-backdrop-filter:blur(14px);backdrop-filter:blur(14px);padding:9px}
  .v396Label{display:flex;align-items:center;gap:6px;margin:0 2px 7px;font-size:9px;font-weight:950;letter-spacing:.08em;text-transform:uppercase;color:#2f6594}
  .v396ShareIcon{width:17px;height:17px;display:grid;place-items:center;border-radius:7px;background:#e8f5fd;color:#3688c8;font-size:10px}
  .v396Platforms{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:6px}
  .v396Platform{position:relative;min-width:0;height:58px;border:1px solid rgba(125,178,215,.23);border-radius:14px;background:linear-gradient(155deg,rgba(255,255,255,.96),rgba(237,248,253,.90));box-shadow:0 5px 13px rgba(52,100,136,.07);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;color:#28557e;font-size:7.3px;font-weight:900;cursor:pointer;padding:3px}
  .v396Platform[aria-pressed="true"]{border-color:rgba(63,153,224,.40);box-shadow:0 6px 15px rgba(46,132,198,.12),inset 0 0 0 1px rgba(79,176,235,.08)}
  .v396Platform[aria-pressed="true"]:after{content:"✓";position:absolute;right:5px;top:4px;width:12px;height:12px;border-radius:50%;display:grid;place-items:center;background:#3295ed;color:#fff;font-size:7px;font-weight:1000}
  .v396SocialMark{width:22px;height:22px;display:grid;place-items:center;font-weight:950;font-size:13px;line-height:1}.v396SocialMark.yt{color:#f0002f}.v396SocialMark.tt{color:#111}.v396SocialMark.ig{border-radius:7px;color:#fff;background:linear-gradient(145deg,#ffad33,#e73b8f 48%,#7355d9);font-size:11px}.v396SocialMark.fb{border-radius:50%;background:#287be9;color:#fff;font-size:15px}
  .v396Fields{display:grid;gap:6px}
  .v396Field{display:grid;grid-template-columns:31px 1fr;gap:7px;align-items:center;border:1px solid rgba(132,179,213,.19);border-radius:15px;background:rgba(255,255,255,.78);padding:7px 8px}
  .v396FieldIcon{width:31px;height:31px;border-radius:10px;display:grid;place-items:center;background:linear-gradient(145deg,#eef9ff,#e2f3fb);color:#2b75ac;font-size:15px;font-weight:850}
  .v396FieldBody label{display:block;margin:0 0 3px;font-size:7.5px;letter-spacing:.08em;text-transform:uppercase;color:#55789a;font-weight:950}
  .v396FieldBody input,.v396FieldBody textarea{display:block;width:100%;min-width:0;border:0;outline:0;resize:none;background:transparent;color:#183f69;padding:0;font:750 10px/1.25 "Avenir Next","SF Pro Text",sans-serif}.v396FieldBody textarea{height:26px}
  .v396FieldBody input::placeholder,.v396FieldBody textarea::placeholder{color:#93a7b9}
  .v396Settings{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:5px}
  .v396Setting{display:flex;align-items:center;justify-content:space-between;gap:5px;min-width:0;padding:7px;border:1px solid rgba(132,179,213,.18);border-radius:13px;background:rgba(249,253,255,.88)}
  .v396SettingText{min-width:0}.v396SettingText b{display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-size:7.6px;color:#315d84}.v396SettingText small{display:block;margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-size:5.9px;color:#8b9eb1}
  .v396Switch{position:relative;width:25px;height:15px;flex:0 0 auto;border:0;border-radius:99px;background:#cbd9e4;padding:0;cursor:pointer}.v396Switch:after{content:"";position:absolute;width:11px;height:11px;left:2px;top:2px;border-radius:50%;background:#fff;box-shadow:0 1px 4px rgba(27,63,91,.16);transition:.15s}.v396Switch.on{background:linear-gradient(90deg,#5fc8f0,#398ee9)}.v396Switch.on:after{left:12px}
  .v396Actions{display:grid;grid-template-columns:1fr 1fr 1.12fr;gap:6px;margin-top:1px}
  .v396Action{height:43px;border-radius:14px;border:1px solid rgba(106,170,214,.24);background:linear-gradient(150deg,#fff,#edf8fc);color:#2e6894;font-size:8.3px;font-weight:950;letter-spacing:.025em;box-shadow:0 6px 16px rgba(47,96,132,.08);cursor:pointer}.v396Action.primary{border-color:rgba(52,145,224,.40);background:linear-gradient(135deg,#67cff2 0%,#419ff0 52%,#3486e8 100%);color:#fff;box-shadow:0 8px 20px rgba(49,139,211,.20)}.v396Action:active{transform:scale(.985)}
  .v396Toast{position:fixed;left:50%;bottom:12px;z-index:9999;transform:translate(-50%,9px);opacity:0;pointer-events:none;max-width:82vw;padding:7px 10px;border-radius:99px;background:rgba(24,61,92,.89);color:#fff;font-size:7.5px;font-weight:850;text-align:center;transition:.18s}.v396Toast.show{opacity:1;transform:translate(-50%,0)}
}
</style>
<script id="v396MobileSharePublishRuntime">
(()=>{
  const share=document.getElementById('share');if(!share||window.__GSF_V396_SHARE)return;window.__GSF_V396_SHARE=true;
  const mobile=()=>window.matchMedia('(max-width:760px)').matches;
  const html=`<div id="v396MobilePublishSurface" aria-label="Crea Short">
    <section class="v396Mural"><div class="v396MuralText">Il tuo video è pronto<small>pubblicalo quando vuoi</small></div></section>
    <section class="v396Panel"><div class="v396Label"><span class="v396ShareIcon">↗</span>PUBBLICA SU</div><div class="v396Platforms">
      <button class="v396Platform" data-v396-platform="youtube" aria-pressed="true"><span class="v396SocialMark yt">▶</span><span>YouTube</span></button>
      <button class="v396Platform" data-v396-platform="tiktok" aria-pressed="true"><span class="v396SocialMark tt">♪</span><span>TikTok</span></button>
      <button class="v396Platform" data-v396-platform="instagram" aria-pressed="true"><span class="v396SocialMark ig">◎</span><span>Instagram</span></button>
      <button class="v396Platform" data-v396-platform="facebook" aria-pressed="true"><span class="v396SocialMark fb">f</span><span>Facebook</span></button>
    </div></section>
    <section class="v396Panel v396Fields">
      <div class="v396Field"><span class="v396FieldIcon">T</span><div class="v396FieldBody"><label for="v396Title">Titolo</label><input id="v396Title" maxlength="100" placeholder="Titolo del tuo Short"></div></div>
      <div class="v396Field"><span class="v396FieldIcon">▤</span><div class="v396FieldBody"><label for="v396Description">Descrizione</label><textarea id="v396Description" maxlength="500" placeholder="Descrivi il tuo momento"></textarea></div></div>
      <div class="v396Field"><span class="v396FieldIcon">#</span><div class="v396FieldBody"><label for="v396Hashtags">Hashtag</label><input id="v396Hashtags" maxlength="180" placeholder="#gaming #shorts"></div></div>
    </section>
    <section class="v396Panel"><div class="v396Label"><span class="v396ShareIcon">⚙</span>IMPOSTAZIONI</div><div class="v396Settings">
      <div class="v396Setting"><span class="v396SettingText"><b>Pubblico</b><small>Visibile a tutti</small></span><button class="v396Switch on" data-setting="public" aria-pressed="true"></button></div>
      <div class="v396Setting"><span class="v396SettingText"><b>Sottotitoli</b><small>Automatici</small></span><button class="v396Switch on" data-setting="captions" aria-pressed="true"></button></div>
      <div class="v396Setting"><span class="v396SettingText"><b>Audio</b><small>Attivo</small></span><button class="v396Switch on" data-setting="audio" aria-pressed="true"></button></div>
    </div></section>
    <div class="v396Actions"><button class="v396Action" id="v396Download">SCARICA</button><button class="v396Action" id="v396Share">CONDIVIDI</button><button class="v396Action primary" id="v396Publish">PUBBLICA ORA</button></div>
    <div class="v396Toast" id="v396Toast"></div>
  </div>`;
  share.insertAdjacentHTML('beforeend',html);share.classList.add('v396MobileMode');
  const root=document.getElementById('v396MobilePublishSurface'),toast=document.getElementById('v396Toast');
  const say=(msg)=>{if(!toast)return;toast.textContent=msg;toast.classList.add('show');clearTimeout(say.t);say.t=setTimeout(()=>toast.classList.remove('show'),1700)};
  const findByText=(selector,needle)=>[...document.querySelectorAll(selector)].find(el=>String(el.textContent||'').toLowerCase().includes(needle));
  root.querySelectorAll('.v396Platform').forEach(btn=>btn.onclick=()=>{const on=btn.getAttribute('aria-pressed')==='true';btn.setAttribute('aria-pressed',String(!on))});
  root.querySelectorAll('.v396Switch').forEach(btn=>btn.onclick=()=>{const on=btn.classList.toggle('on');btn.setAttribute('aria-pressed',String(on))});
  const meta=()=>({title:root.querySelector('#v396Title')?.value||'',description:root.querySelector('#v396Description')?.value||'',hashtags:root.querySelector('#v396Hashtags')?.value||'',settings:Object.fromEntries([...root.querySelectorAll('.v396Switch')].map(b=>[b.dataset.setting,b.getAttribute('aria-pressed')==='true']))});
  const originalDownload=()=>document.querySelector('.downloadBtn:not(#v396Download)')||findByText('button,a','scarica video');
  const findAsset=()=>{const a=document.querySelector('a[download][href],a[href*=".mp4"],a[href*="/media/"]');if(a&&a.href)return a.href;const b=originalDownload();return b?.dataset?.url||b?.dataset?.href||''};
  root.querySelector('#v396Download').onclick=()=>{const b=originalDownload();if(b){b.click();say('Download aperto');return}say('Download non ancora disponibile')};
  root.querySelector('#v396Share').onclick=async()=>{const data=meta(),url=findAsset();try{if(url&&navigator.share){let file=null;try{const r=await fetch(url);const blob=await r.blob();file=new File([blob],'gaming-short.mp4',{type:blob.type||'video/mp4'})}catch(_e){}if(file&&(!navigator.canShare||navigator.canShare({files:[file]}))){await navigator.share({title:data.title||'Gaming Shorts Factory',text:data.description||'Il mio Short',files:[file]});return}await navigator.share({title:data.title||'Gaming Shorts Factory',text:data.description||'Il mio Short',url:url||undefined});return}if(navigator.share){await navigator.share({title:data.title||'Gaming Shorts Factory',text:data.description||'Il mio Short'});return}if(url&&navigator.clipboard){await navigator.clipboard.writeText(url);say('Link copiato');return}say('Condivisione non disponibile')}catch(e){if(e&&e.name!=='AbortError')say('Condivisione non disponibile')}};
  root.querySelector('#v396Publish').onclick=()=>{const data=meta();try{window.parent.postMessage({type:'GSF_SHARE_METADATA',payload:data},window.location.origin)}catch(_e){}const selected=[...root.querySelectorAll('.v396Platform[aria-pressed="true"]')].map(b=>b.dataset.v396Platform);let fired=0;selected.forEach(name=>{const target=document.querySelector(`[data-platform="${name}"]`);if(target){target.click();fired++}});say(fired?`Apro ${fired} destinazioni`:'Seleziona almeno un social')};
  const sync=()=>share.classList.toggle('v396MobileMode',mobile());sync();window.addEventListener('resize',sync,{passive:true});
})();
</script>
'''

def patch_share(text:str)->str:
    if MARK in text:return text
    for anchor in ('V289 SHARE FINAL','data-card="youtube"','data-card="tiktok"','data-card="instagram"','data-card="facebook"','</body>'):
        if anchor not in text:raise RuntimeError('V396 Share anchor missing: '+anchor)
    return text.replace('</body>',PATCH+'\n</body>',1)

def main()->None:
    root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
    share=root/'web'/'share_v156_component'/'index.html'
    if not share.is_file():raise SystemExit('V396 Share target missing: '+str(share))
    before=share.read_text(encoding='utf-8');after=patch_share(before);share.write_text(after,encoding='utf-8')
    print('V396 mobile Share publish surface applied changed=',before!=after,flush=True)

if __name__=='__main__':main()
