#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path('/app/web')
HOME = ROOT / 'home_v154_component' / 'index.html'
EMBED = ROOT / 'home_v154_embed.py'
MARKER = '/* V306 APPROVED HOME VISUAL LOCK */'

CSS = r'''
/* V306 APPROVED HOME VISUAL LOCK
   Visual-only lock. This intentionally changes no layout, routes, upload logic,
   mural geometry or responsive sizing. It restores the approved pale GSF skin
   after runtime rebuilds so desktop/mobile cannot drift to older colors. */
#home154{
  background:
    radial-gradient(circle at 9% 7%,rgba(126,214,255,.16),transparent 24%),
    radial-gradient(circle at 91% 8%,rgba(127,236,197,.14),transparent 25%),
    linear-gradient(180deg,#FEFFFF 0%,#FBFDFF 54%,#F7FCFF 100%)!important;
  filter:none!important;
  opacity:1!important;
}
#home154:before{
  background:
    radial-gradient(circle at 23% 44%,rgba(111,211,255,.05),transparent 31%),
    radial-gradient(circle at 77% 52%,rgba(91,226,178,.05),transparent 31%)!important;
  opacity:1!important;
  filter:none!important;
}

#home154 .rings{
  background:
    radial-gradient(circle at 36% 27%,rgba(255,255,255,.995) 0%,rgba(246,252,255,.985) 34%,rgba(238,249,255,.965) 61%,rgba(232,251,246,.955) 100%) padding-box,
    linear-gradient(102deg,rgba(109,195,244,.68) 0%,rgba(124,207,249,.48) 44%,rgba(132,221,214,.36) 66%,rgba(113,229,192,.42) 100%) border-box!important;
  border:1.35px solid transparent!important;
  box-shadow:-18px 0 48px rgba(89,198,247,.18),20px 7px 52px rgba(92,225,182,.14),inset 0 0 0 1px rgba(255,255,255,.86),0 16px 42px rgba(70,126,166,.07)!important;
}
#home154 .rings:before{
  border:1px solid rgba(103,202,242,.24)!important;
  background:radial-gradient(circle at 34% 46%,rgba(112,208,249,.06),transparent 58%),radial-gradient(circle at 70% 52%,rgba(107,230,192,.065),transparent 60%)!important;
  -webkit-mask:none!important;
  mask:none!important;
  box-shadow:none!important;
  opacity:.74!important;
}
#home154 .rings:after{
  border:1px solid rgba(113,220,196,.15)!important;
  background:radial-gradient(circle at 34% 46%,rgba(110,205,249,.04),transparent 61%),radial-gradient(circle at 70% 52%,rgba(104,229,190,.05),transparent 62%)!important;
  -webkit-mask:none!important;
  mask:none!important;
  box-shadow:none!important;
  opacity:.52!important;
}
#home154 .circle{background:#FFF!important}
#home154 .circle .icon{color:#6099E2!important}
#home154 .circle strong{color:#0D2A66!important;text-shadow:none!important}

#home154 .feature,
#home154 .feature.fAi,
#home154 .feature.fEditor,
#home154 .feature.fShort{
  background:rgba(255,255,255,.74)!important;
  border:1px solid rgba(150,184,214,.23)!important;
  box-shadow:0 10px 26px rgba(62,107,150,.075),0 1px 2px rgba(54,91,126,.035),inset 0 1px 0 rgba(255,255,255,.98)!important;
  -webkit-backdrop-filter:blur(16px)!important;
  backdrop-filter:blur(16px)!important;
}
#home154 .featureIcon{
  border:0!important;
  border-radius:50%!important;
  box-shadow:inset 0 0 0 1px rgba(255,255,255,.52),0 10px 26px rgba(85,124,159,.08)!important;
}
#home154 .feature.fAi .featureIcon{background:#D8E9FF!important;color:#1875E6!important}
#home154 .feature.fEditor .featureIcon{background:#CFF4DD!important;color:#078F61!important}
#home154 .feature.fShort .featureIcon{background:#FFE9A8!important;color:#D68000!important}
#home154 .feature b{color:#0D2A66!important;text-shadow:none!important}
#home154 .feature small{color:#7185A6!important;text-shadow:none!important}

#home154 .bottomNav{
  background:rgba(255,255,255,.93)!important;
  border:1px solid rgba(139,181,218,.27)!important;
  box-shadow:0 9px 24px rgba(59,104,148,.085),0 0 0 3px rgba(226,243,255,.24),inset 0 1px 0 #fff!important;
  -webkit-backdrop-filter:blur(22px)!important;
  backdrop-filter:blur(22px)!important;
}
#home154 .navItem{color:#8192AA!important;background:transparent!important;text-shadow:none!important}
#home154 .navItem svg{
  color:currentColor!important;
  background:linear-gradient(145deg,#F9FCFF,#EDF5FC)!important;
  border:1px solid rgba(150,184,215,.24)!important;
  box-shadow:none!important;
}
#home154 .navItem.active{color:#4F93D7!important;background:rgba(219,241,255,.70)!important}
#home154 .navItem.active svg{color:#4F93D7!important;background:linear-gradient(145deg,#E8F5FF,#D8EBFF)!important}
#home154 .navItem.active:after{background:#4F93D7!important}

#home154 .scribble,
#home154 .scribble .padSketch,
#home154 .muralAmbient{color:#637DA8!important}

#home154 .siteFooter{
  color:#7D90AD!important;
  background:transparent!important;
  border-top:1px solid rgba(150,184,214,.16)!important;
  box-shadow:none!important;
}
#home154 .footerBrand{color:#7D90AD!important}
#home154 .footLinks button{color:#6983A4!important}
#home154 .footerSocialLink{
  background:rgba(255,255,255,.90)!important;
  border:1px solid rgba(150,183,213,.24)!important;
  box-shadow:0 5px 13px rgba(65,105,145,.08)!important;
}
/* END V306 APPROVED HOME VISUAL LOCK */
'''.strip()


def patch_home():
    text = HOME.read_text(encoding='utf-8')
    if MARKER not in text:
        if '</style>' not in text:
            raise RuntimeError('V306 Home style anchor missing')
        text = text.replace('</style>', CSS + '\n</style>', 1)
        HOME.write_text(text, encoding='utf-8')
        print('V306 approved Home palette restored:', HOME, flush=True)
    else:
        print('V306 approved Home palette already present:', HOME, flush=True)


def patch_embed():
    text = EMBED.read_text(encoding='utf-8')
    if '"gsf_home_v154_live_306"' in text:
        print('V306 Home cache already active:', EMBED, flush=True)
        return
    text, count = re.subn(
        r'"gsf_home_v154_live_\d+"',
        '"gsf_home_v154_live_306"',
        text,
        count=1,
    )
    if count != 1:
        raise RuntimeError('V306 Home component cache anchor missing')
    EMBED.write_text(text, encoding='utf-8')
    print('V306 Home component cache bumped:', EMBED, flush=True)


if __name__ == '__main__':
    for path in (HOME, EMBED):
        if not path.is_file():
            raise RuntimeError('V306 required file missing: ' + str(path))
    patch_home()
    patch_embed()
