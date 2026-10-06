#!/usr/bin/env python3
from pathlib import Path

HOME = Path('/app/web/home_v154_component/index.html')
EMBED = Path('/app/web/home_v154_embed.py')

MARKER = '/* V294 HOME DESKTOP REALIGN */'
END_MARKER = '/* END V294 HOME DESKTOP REALIGN */'

CSS = r'''
/* V294 HOME DESKTOP REALIGN */
/*
   V274 accidentally made the desktop CTA row and Game Bar inherit phone-scale
   width. V279 then left the murals and ad rails oversized around that tiny
   center. Restore the approved desktop balance while keeping the compact
   uploader, current palette, global type scale and mobile layout untouched.
*/
@media (min-width:761px){
  #home154{
    --gsf-desk-ring:clamp(204px,min(18.5vw,27vh),282px)!important;
    --gsf-desk-content:clamp(620px,59vw,790px)!important;
    --gsf-desk-card-h:clamp(110px,13.8vh,126px)!important;
    --gsf-desk-nav-h:clamp(52px,6.8vh,60px)!important;
    overflow:hidden!important;
  }

  #home154 #view{
    row-gap:clamp(3px,.55vh,6px)!important;
  }

  #home154 .stage{
    min-height:0!important;
    padding:0 0 2px!important;
  }

  #home154 .rings{
    width:var(--gsf-desk-ring)!important;
    height:var(--gsf-desk-ring)!important;
    top:-9px!important;
  }

  #home154 .features{
    width:var(--gsf-desk-content)!important;
    min-width:0!important;
    grid-template-columns:repeat(3,minmax(0,1fr))!important;
    gap:clamp(16px,1.35vw,22px)!important;
    margin:-2px auto 5px!important;
    transform:translateY(-8px)!important;
    align-items:stretch!important;
  }

  #home154 .feature,
  #home154 .feature.fAi,
  #home154 .feature.fEditor,
  #home154 .feature.fShort{
    width:100%!important;
    height:var(--gsf-desk-card-h)!important;
    min-height:var(--gsf-desk-card-h)!important;
    max-height:var(--gsf-desk-card-h)!important;
    padding:10px 14px!important;
    justify-content:center!important;
    border-radius:22px!important;
  }

  #home154 .featureIcon{
    width:clamp(44px,5.6vh,52px)!important;
    height:clamp(44px,5.6vh,52px)!important;
    flex:0 0 auto!important;
    margin:0 auto clamp(5px,.7vh,7px)!important;
    transform:none!important;
  }

  #home154 .featureIcon svg{
    width:clamp(25px,2vw,30px)!important;
    height:clamp(25px,2vw,30px)!important;
  }

  #home154 .feature b{
    margin-top:0!important;
    line-height:1.06!important;
  }

  #home154 .feature small{
    margin-top:4px!important;
    max-width:190px!important;
    line-height:1.16!important;
  }

  /* The Game Bar is a desktop navigation surface, not a phone-width child of
     the CTA strip. Keep it readable on 1366-class laptops. */
  #home154 .bottomNav{
    width:min(var(--gsf-desk-content),72vw)!important;
    min-width:560px!important;
    height:var(--gsf-desk-nav-h)!important;
    min-height:var(--gsf-desk-nav-h)!important;
    margin:-4px auto 4px!important;
    padding:4px 10px!important;
  }

  #home154 .navItem svg{
    width:clamp(20px,2.7vh,24px)!important;
    height:clamp(20px,2.7vh,24px)!important;
  }

  /* Pull the two handwritten guides back toward the uploader and undo the
     oversized V279 orbit. */
  #home154 .scribble.left,
  #home154[data-mural-state="uploading"] .scribble.left,
  #home154[data-mural-state="ready"] .scribble.left,
  #home154[data-mural-state^="focus-"] .scribble.left{
    left:calc(50% - (var(--gsf-desk-ring) / 2) - clamp(220px,17vw,265px))!important;
    right:auto!important;
    top:clamp(92px,14.5vh,132px)!important;
    width:clamp(190px,15.5vw,260px)!important;
    font-size:clamp(20px,1.7vw,28px)!important;
    line-height:1.04!important;
    text-align:right!important;
    transform:rotate(-7deg)!important;
  }

  #home154 .scribble.right,
  #home154[data-mural-state="uploading"] .scribble.right,
  #home154[data-mural-state="ready"] .scribble.right,
  #home154[data-mural-state^="focus-"] .scribble.right{
    right:calc(50% - (var(--gsf-desk-ring) / 2) - clamp(220px,17vw,265px))!important;
    left:auto!important;
    top:clamp(92px,14.5vh,132px)!important;
    width:clamp(190px,15.5vw,260px)!important;
    font-size:clamp(20px,1.7vw,28px)!important;
    line-height:1.04!important;
    text-align:left!important;
    transform:rotate(6deg)!important;
  }

  #home154 .muralAmbient,
  #home154[data-mural-state="uploading"] .muralAmbient,
  #home154[data-mural-state="ready"] .muralAmbient,
  #home154[data-mural-state^="focus-"] .muralAmbient{
    left:50%!important;
    right:auto!important;
    top:auto!important;
    bottom:clamp(18px,2.7vh,30px)!important;
    width:clamp(235px,20vw,315px)!important;
    max-width:none!important;
    font-size:clamp(17px,1.4vw,22px)!important;
    line-height:1.03!important;
    text-align:center!important;
    transform:translateX(-50%) rotate(-3deg)!important;
  }

  /* V279 made the ad columns dominate short desktop screens. Preserve both
     slots, but return them to supporting proportions. */
  #home154 .sideAd{
    height:clamp(220px,35vh,310px)!important;
    width:clamp(104px,8.4vw,136px)!important;
  }
}
/* END V294 HOME DESKTOP REALIGN */
'''


def patch_home():
    text = HOME.read_text(encoding='utf-8')
    if MARKER in text:
        print('V294 Home desktop realign already applied:', HOME, flush=True)
        return
    anchor = '</style>'
    if anchor not in text:
        raise RuntimeError('V294 Home style anchor missing')
    text = text.replace(anchor, CSS + '\n' + anchor, 1)
    HOME.write_text(text, encoding='utf-8')
    print('V294 Home desktop realign applied:', HOME, flush=True)


def patch_embed():
    text = EMBED.read_text(encoding='utf-8')
    if 'gsf_home_v154_live_294' in text:
        print('V294 Home component cache already bumped:', EMBED, flush=True)
        return
    old = '"gsf_home_v154_live_284"'
    if old not in text:
        raise RuntimeError('V294 Home component cache anchor missing')
    text = text.replace(old, '"gsf_home_v154_live_294"', 1)
    EMBED.write_text(text, encoding='utf-8')
    print('V294 Home component cache bumped:', EMBED, flush=True)


if __name__ == '__main__':
    for path in (HOME, EMBED):
        if not path.is_file():
            raise RuntimeError('V294 required file missing: ' + str(path))
    patch_home()
    patch_embed()
