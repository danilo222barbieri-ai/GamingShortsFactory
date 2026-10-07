#!/usr/bin/env python3
from pathlib import Path

HOME = Path('/app/web/home_v154_component/index.html')
EMBED = Path('/app/web/home_v154_embed.py')

MARKER = '/* V301 HOME DESK REBALANCE */'

CSS = r'''
/* V301 HOME DESK REBALANCE
   Desktop-only visual reset: restore a strong uploader hierarchy, widen the
   central composition, move the two handwritten guides outward/upward and
   remove the redundant ambient mural between uploader and CTA cards.
   Mobile is intentionally untouched. */
@media (min-width:761px){
  #home154{
    --gsf-desk-ring:clamp(270px,min(23vw,36vh),360px)!important;
    --gsf-desk-content:clamp(740px,68vw,940px)!important;
    --gsf-desk-card-h:clamp(112px,14.5vh,132px)!important;
    --gsf-desk-nav-h:clamp(56px,7.2vh,64px)!important;
    padding-left:clamp(34px,3.8vw,72px)!important;
    padding-right:clamp(34px,3.8vw,72px)!important;
    overflow:hidden!important;
  }

  #home154 #view{
    row-gap:clamp(3px,.45vh,6px)!important;
  }

  #home154 .stage{
    min-height:0!important;
    padding:clamp(2px,.45vh,6px) 0 0!important;
    overflow:visible!important;
  }

  #home154 .rings{
    width:var(--gsf-desk-ring)!important;
    height:var(--gsf-desk-ring)!important;
    min-width:var(--gsf-desk-ring)!important;
    min-height:var(--gsf-desk-ring)!important;
    top:clamp(-14px,-1.2vh,-7px)!important;
  }

  /* The two guide murals now orbit the hero instead of crowding it. */
  #home154 .scribble.left,
  #home154[data-mural-state="uploading"] .scribble.left,
  #home154[data-mural-state="ready"] .scribble.left,
  #home154[data-mural-state^="focus-"] .scribble.left{
    left:clamp(34px,4.6vw,86px)!important;
    right:auto!important;
    top:clamp(54px,8.2vh,82px)!important;
    width:clamp(210px,16vw,280px)!important;
    max-width:none!important;
    font-size:clamp(21px,1.65vw,28px)!important;
    line-height:1.03!important;
    text-align:right!important;
    transform:rotate(-6deg)!important;
  }

  #home154 .scribble.right,
  #home154[data-mural-state="uploading"] .scribble.right,
  #home154[data-mural-state="ready"] .scribble.right,
  #home154[data-mural-state^="focus-"] .scribble.right{
    right:clamp(34px,4.6vw,86px)!important;
    left:auto!important;
    top:clamp(54px,8.2vh,82px)!important;
    width:clamp(210px,16vw,280px)!important;
    max-width:none!important;
    font-size:clamp(21px,1.65vw,28px)!important;
    line-height:1.03!important;
    text-align:left!important;
    transform:rotate(5deg)!important;
  }

  /* Redundant third mural removed only on desktop. */
  #home154 .muralAmbient{display:none!important}

  /* CTA row uses the width a desktop actually has; equal cards, no squeezed center. */
  #home154 .features{
    width:min(var(--gsf-desk-content),calc(100vw - 300px))!important;
    min-width:0!important;
    grid-template-columns:repeat(3,minmax(0,1fr))!important;
    gap:clamp(16px,1.35vw,24px)!important;
    margin:clamp(-4px,-.35vh,-1px) auto clamp(6px,.85vh,10px)!important;
    transform:none!important;
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
    padding:clamp(10px,1.2vh,13px) clamp(14px,1.15vw,18px)!important;
    border-radius:24px!important;
    justify-content:center!important;
  }

  #home154 .featureIcon{
    width:clamp(46px,5.7vh,54px)!important;
    height:clamp(46px,5.7vh,54px)!important;
    margin:0 auto clamp(5px,.7vh,8px)!important;
    flex:0 0 auto!important;
  }

  #home154 .feature b{font-size:clamp(14px,1.05vw,17px)!important;line-height:1.05!important}
  #home154 .feature small{font-size:clamp(9px,.72vw,11px)!important;line-height:1.18!important;max-width:210px!important}

  /* Game Bar follows the CTA width, so the whole lower composition reads as one system. */
  #home154 .bottomNav{
    width:min(var(--gsf-desk-content),calc(100vw - 360px))!important;
    min-width:620px!important;
    height:var(--gsf-desk-nav-h)!important;
    min-height:var(--gsf-desk-nav-h)!important;
    margin:0 auto clamp(5px,.7vh,8px)!important;
    padding:5px 12px!important;
  }

  #home154 .navItem{font-size:clamp(8px,.62vw,10px)!important}
  #home154 .navItem svg{width:clamp(20px,2.65vh,24px)!important;height:clamp(20px,2.65vh,24px)!important}

  /* Ads stay secondary to the hero instead of stretching the page visually. */
  #home154 .sideAd{
    width:clamp(104px,7.7vw,132px)!important;
    height:clamp(250px,37vh,340px)!important;
  }

  #home154 .siteFooter{
    margin-top:0!important;
    padding-top:clamp(5px,.65vh,8px)!important;
  }
}
/* END V301 HOME DESK REBALANCE */
'''


def patch_home():
    text = HOME.read_text(encoding='utf-8')
    if MARKER in text:
        print('V301 Home desk rebalance already applied:', HOME, flush=True)
        return
    if '</style>' not in text:
        raise RuntimeError('V301 Home style anchor missing')
    text = text.replace('</style>', CSS + '\n</style>', 1)
    HOME.write_text(text, encoding='utf-8')
    print('V301 Home desk rebalance applied:', HOME, flush=True)


def patch_embed():
    text = EMBED.read_text(encoding='utf-8')
    if 'gsf_home_v154_live_301' in text:
        print('V301 Home cache already applied:', EMBED, flush=True)
        return
    import re
    text, count = re.subn(r'"gsf_home_v154_live_\d+"', '"gsf_home_v154_live_301"', text, count=1)
    if count != 1:
        raise RuntimeError('V301 Home component cache anchor missing')
    EMBED.write_text(text, encoding='utf-8')
    print('V301 Home component cache bumped:', EMBED, flush=True)


if __name__ == '__main__':
    for path in (HOME, EMBED):
        if not path.is_file():
            raise RuntimeError('V301 required file missing: ' + str(path))
    patch_home()
    patch_embed()
