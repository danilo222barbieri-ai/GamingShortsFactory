from pathlib import Path
import re

SHARE = Path('/app/web/share_v156_component/index.html')
APP = Path('/app/GamingShortsFactory_V154_STRUCTURAL_HOME.py')

CSS = r'''
/* V289 SHARE FINAL — playerless GSF publishing/download surface */
#share.gsfFinalSurface{
  position:relative;
  display:flex;
  flex-direction:column;
  gap:12px;
  min-height:100%;
  padding:clamp(16px,2.1vh,24px) clamp(16px,2.25vw,30px) clamp(16px,2vh,22px)!important;
  background:
    radial-gradient(circle at 10% 5%,rgba(104,207,255,.19),transparent 27%),
    radial-gradient(circle at 91% 8%,rgba(115,232,192,.17),transparent 27%),
    radial-gradient(circle at 52% 92%,rgba(191,225,255,.14),transparent 31%),
    linear-gradient(180deg,#FEFFFF 0%,#FAFDFF 55%,#F5FBFF 100%)!important;
}
#share.gsfFinalSurface .topline{
  position:relative;
  z-index:3;
  margin:0 2px 2px!important;
  align-items:center;
}
#share.gsfFinalSurface .titleWrap{gap:15px}
#share.gsfFinalSurface .titleIcon{
  width:58px;height:58px;border-radius:20px;
  background:linear-gradient(145deg,#E9F8FF,#DDF6EE)!important;
  color:#318DDC;
  box-shadow:inset 0 0 0 1px rgba(255,255,255,.96),0 12px 30px rgba(66,145,204,.13)!important;
}
#share.gsfFinalSurface h1{
  color:#0D2A66;
  font-size:clamp(30px,2.7vw,43px)!important;
  font-weight:900!important;
  letter-spacing:-.045em!important;
}
#share.gsfFinalSurface .subtitle{
  color:#7488A6!important;
  font-size:clamp(12px,1vw,15px)!important;
  font-weight:700!important;
}
#share.gsfFinalSurface .readyPill{
  min-width:240px;
  justify-content:flex-start;
  border-radius:20px!important;
  padding:11px 14px!important;
  background:rgba(255,255,255,.88)!important;
  border:1px solid rgba(143,181,216,.22)!important;
  box-shadow:0 10px 26px rgba(62,107,147,.07)!important;
}
#share.gsfFinalSurface .section{
  border:1px solid rgba(143,181,216,.22)!important;
  border-radius:27px!important;
  background:rgba(255,255,255,.82)!important;
  box-shadow:0 15px 40px rgba(61,104,145,.075),inset 0 1px 0 rgba(255,255,255,.98)!important;
  backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);
}
#share.gsfFinalSurface .section+.section{margin-top:0!important}
#share.gsfFinalSurface .sectionHead{margin-bottom:12px!important}
#share.gsfFinalSurface .sectionTitle{font-size:clamp(16px,1.25vw,20px)!important;color:#173873}
#share.gsfFinalSurface .step{
  width:31px;height:31px;border-radius:11px;
  background:linear-gradient(145deg,#E1F2FF,#E4F8EF)!important;
  color:#2277C6!important;
  box-shadow:inset 0 0 0 1px rgba(111,185,226,.12);
}
#share.gsfFinalSurface .quality strong{
  background:linear-gradient(145deg,#DDF7EA,#E8FBF3)!important;
  color:#168B65!important;
}
#share.gsfFinalSurface .socials{gap:clamp(10px,1vw,15px)!important}
#share.gsfFinalSurface .card{
  min-height:210px!important;
  padding:16px!important;
  border-radius:22px!important;
  background:linear-gradient(155deg,rgba(255,255,255,.98),rgba(248,252,255,.93))!important;
  border:1px solid rgba(144,181,214,.20)!important;
  box-shadow:0 8px 24px rgba(65,105,145,.055),inset 0 1px 0 #fff!important;
}
#share.gsfFinalSurface .card:hover,#share.gsfFinalSurface .card:focus-within{
  transform:translateY(-3px)!important;
  border-color:rgba(99,184,243,.36)!important;
  box-shadow:0 16px 32px rgba(65,105,145,.095),inset 0 1px 0 #fff!important;
}
#share.gsfFinalSurface .logo{width:46px;height:46px!important}
#share.gsfFinalSurface .card h3{font-size:clamp(15px,1.2vw,19px)!important;margin-top:12px!important}
#share.gsfFinalSurface .card p{font-size:clamp(10.5px,.87vw,13px)!important;line-height:1.35!important}
#share.gsfFinalSurface .cardHint{font-size:clamp(9px,.72vw,11px)!important}
#share.gsfFinalSurface .open{
  min-height:40px;
  border-radius:14px!important;
  background:linear-gradient(135deg,#78D1FA,#50A8F3)!important;
  font-size:clamp(10px,.82vw,12px)!important;
}
#share.gsfFinalSurface .open.connect{background:#EAF5FF!important;color:#52769B!important}
#share.gsfFinalSurface .downloadRow{
  grid-template-columns:minmax(270px,1fr) minmax(420px,auto)!important;
  gap:18px!important;
}
#share.gsfFinalSurface .downloadTitle h2{font-size:clamp(18px,1.45vw,23px)!important;color:#173873}
#share.gsfFinalSurface .downloadTitle p{font-size:clamp(10px,.85vw,13px)!important}
#share.gsfFinalSurface .chips{gap:6px!important}
#share.gsfFinalSurface .chip{
  padding:6px 9px!important;
  background:#EDF6FF!important;
  border:1px solid rgba(130,183,219,.12);
  color:#6884A4!important;
  font-size:clamp(8px,.65vw,10px)!important;
}
#share.gsfFinalSurface .qualityMax{
  background:linear-gradient(145deg,#DDF8EB,#E8FBF3)!important;
  color:#168B65!important;
}
#share.gsfFinalSurface .actions{gap:8px!important}
#share.gsfFinalSurface .downloadBtn{
  min-height:48px;
  padding:13px 24px!important;
  border-radius:16px!important;
  background:linear-gradient(135deg,#79D7FF,#439FF5)!important;
  box-shadow:0 11px 28px rgba(69,157,223,.22)!important;
  font-size:clamp(12px,.95vw,14px)!important;
}
#share.gsfFinalSurface .secondary{
  min-height:44px;
  background:rgba(255,255,255,.94)!important;
  border-color:rgba(143,181,214,.22)!important;
  font-size:clamp(9.5px,.75vw,11px)!important;
}
/* The final surface intentionally contains no video/player: creation is already complete. */

/* V289 SHARE MOBILE */
@media(max-width:760px){
  #share.gsfFinalSurface{
    overflow:auto!important;
    gap:9px;
    padding:12px 9px 86px!important;
  }
  #share.gsfFinalSurface .topline{align-items:flex-start!important;margin-bottom:1px!important}
  #share.gsfFinalSurface .titleWrap{gap:10px!important}
  #share.gsfFinalSurface .titleIcon{width:44px;height:44px;border-radius:15px}
  #share.gsfFinalSurface h1{font-size:25px!important;line-height:1.02!important}
  #share.gsfFinalSurface .subtitle{font-size:11.5px!important;max-width:285px}
  #share.gsfFinalSurface .readyPill{display:none!important}
  #share.gsfFinalSurface .section{padding:11px!important;border-radius:21px!important}
  #share.gsfFinalSurface .sectionHead{margin-bottom:9px!important}
  #share.gsfFinalSurface .sectionTitle{font-size:14px!important}
  #share.gsfFinalSurface .step{width:28px;height:28px;border-radius:10px}
  #share.gsfFinalSurface .quality{display:none!important}
  #share.gsfFinalSurface .socials{grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:8px!important}
  #share.gsfFinalSurface .card{min-height:164px!important;padding:11px!important;border-radius:18px!important}
  #share.gsfFinalSurface .logo{width:38px;height:38px!important}
  #share.gsfFinalSurface .connected{font-size:8.6px!important;padding:4px 6px!important}
  #share.gsfFinalSurface .card h3{font-size:13.5px!important;margin:9px 0 4px!important}
  #share.gsfFinalSurface .card p{font-size:9.8px!important;min-height:32px!important}
  #share.gsfFinalSurface .cardHint{display:none!important}
  #share.gsfFinalSurface .open{min-height:36px;font-size:9.6px!important}
  #share.gsfFinalSurface .downloadRow{grid-template-columns:1fr!important;gap:10px!important}
  #share.gsfFinalSurface .downloadTitle h2{font-size:17.5px!important}
  #share.gsfFinalSurface .downloadTitle p{font-size:10.5px!important}
  #share.gsfFinalSurface .actions{display:grid!important;grid-template-columns:1fr 1fr!important;width:100%}
  #share.gsfFinalSurface .downloadBtn{grid-column:1/-1!important;width:100%;min-height:49px;font-size:12.5px!important}
  #share.gsfFinalSurface .secondary{width:100%;min-height:40px;font-size:9.8px!important}
  #share.gsfFinalSurface #muralSocial{font-size:12px!important}
}
@media(max-width:390px){
  #share.gsfFinalSurface .socials{grid-template-columns:1fr!important}
  #share.gsfFinalSurface .card{min-height:140px!important}
}
/* END V289 SHARE FINAL */
'''


def replace_once(text, old, new, label):
    if old not in text:
        raise RuntimeError(f'V289 anchor missing: {label}')
    return text.replace(old, new, 1)


def patch_share():
    text = SHARE.read_text(encoding='utf-8')
    before = text
    if 'V289 SHARE FINAL' not in text:
        text = replace_once(text, '</style>', CSS + '\n</style>', 'share CSS')
        text = replace_once(text, '<main id="share">', '<main id="share" class="gsfFinalSurface">', 'share surface class')
        text = replace_once(text, '<section class="section">', '<section class="section gsfFinalGrid">', 'final social grid')
        text = replace_once(text, '<h2>Scarica sul dispositivo</h2>', '<h2>Scarica il tuo Short</h2>', 'download heading')
        text = replace_once(
            text,
            '<span class="chip">AAC</span></div>',
            '<span class="chip">AAC</span><span class="chip qualityMax">✓ Qualità massima</span></div>',
            'quality max chip',
        )
    SHARE.write_text(text, encoding='utf-8')
    print('V289 Share Final applied:', SHARE, 'changed=', text != before, flush=True)


def patch_app():
    text = APP.read_text(encoding='utf-8')
    before = text
    text, count = re.subn(r'/share-v156/\?v=\d+', '/share-v156/?v=289', text)
    if count < 1 and '/share-v156/?v=289' not in text:
        raise RuntimeError('V289 share iframe cache anchor missing')
    APP.write_text(text, encoding='utf-8')
    print('V289 Share cache bumped:', APP, 'changed=', text != before, flush=True)


if __name__ == '__main__':
    for path in (SHARE, APP):
        if not path.is_file():
            raise RuntimeError('V289 required file missing: ' + str(path))
    patch_share()
    patch_app()
