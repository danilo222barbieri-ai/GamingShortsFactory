#!/usr/bin/env python3
from pathlib import Path
import re
import sys

STYLE_ID='v315MobileHomeLowerFlow'
STYLE=r'''<style id="v315MobileHomeLowerFlow">
/* V315: lower the mobile Home composition without changing its approved skin. */
@media(max-width:760px){
  #home154{--gsf-home-lower-shift:clamp(14px,2.5vh,22px)!important}

  /* Lower only the upload core + central handwritten line. Upper side murals stay where they are. */
  #home154 .rings{
    top:var(--gsf-home-lower-shift)!important;
  }
  #home154 .muralAmbient,
  #home154[data-mural-state="uploading"] .muralAmbient,
  #home154[data-mural-state="ready"] .muralAmbient,
  #home154[data-mural-state^="focus-"] .muralAmbient{
    top:auto!important;
    bottom:calc(1px - var(--gsf-home-lower-shift))!important;
  }

  /* Follow the uploader downward with the three action cards and Game Bar. */
  #home154 .features{
    position:relative!important;
    top:var(--gsf-home-lower-shift)!important;
  }
  #home154 .bottomNav{
    position:relative!important;
    top:var(--gsf-home-lower-shift)!important;
    margin-bottom:12px!important;
  }
  #home154 .siteFooter{margin-top:0!important}
}

@media(max-width:760px) and (max-height:760px){
  #home154{--gsf-home-lower-shift:12px!important}
  #home154 .bottomNav{margin-bottom:9px!important}
}
</style>'''


def patch_text(text:str)->str:
    for marker in ('id="home154"','class="rings"','class="features"','class="bottomNav"','class="siteFooter"','class="muralAmbient muralGuide"'):
        if marker not in text:
            raise RuntimeError(f'V315 missing Home anchor: {marker}')
    pattern=re.compile(r'\s*<style id="'+re.escape(STYLE_ID)+r'">.*?</style>\s*',re.DOTALL)
    cleaned=pattern.sub('',text)
    if '</head>' not in cleaned:
        raise RuntimeError('V315 Home </head> anchor missing')
    return cleaned.replace('</head>','\n'+STYLE+'\n</head>',1)


def main()->None:
    home=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app/web/home_v154_component/index.html')
    if not home.is_file():
        raise SystemExit(f'V315 Home missing: {home}')
    before=home.read_text(encoding='utf-8')
    after=patch_text(before)
    home.write_text(after,encoding='utf-8')
    print('V315 mobile Home lower flow applied changed=',before!=after,flush=True)

if __name__=='__main__':
    main()
