#!/usr/bin/env python3
from pathlib import Path
import re
import sys

STYLE_ID = 'v313MobileProfileFit'
STYLE = r'''<style id="v313MobileProfileFit">
/* V313: mobile Profile must fit in one viewport. Social rows stay intact. */
@media(max-width:767px){
  #hub .view[data-view="profile"] .profileReferenceScroll{
    height:100%!important;min-height:0!important;box-sizing:border-box!important;
    display:grid!important;grid-template-rows:34px 136px 124px minmax(0,1fr)!important;
    gap:6px!important;overflow-y:hidden!important;overflow-x:hidden!important;
    padding:2px 2px 88px!important;
  }
  #hub .profileReferenceBrand{min-height:34px!important;height:34px!important;padding:2px 10px 4px!important;box-sizing:border-box!important}
  #hub .profileReferenceCard{margin:0!important}

  /* Profile: same controls and actions, much less vertical air. */
  #hub .profileReferenceEdit{min-height:0!important;height:136px!important;box-sizing:border-box!important;padding:8px 10px!important;grid-template-columns:92px minmax(0,1fr)!important;gap:9px!important;align-items:center!important}
  #hub .profileRefPhotoCol{gap:5px!important}
  #hub .profileRefAvatar{width:68px!important;height:68px!important;border-width:3px!important;font-size:20px!important}
  #hub .profileRefPhotoBtn{min-width:84px!important;min-height:27px!important;height:27px!important;border-radius:11px!important;gap:5px!important;padding:0 7px!important;font-size:9.5px!important}
  #hub .profileRefMain{column-gap:7px!important;row-gap:2px!important;align-items:end!important}
  #hub .profileRefTitle{font-size:20px!important;line-height:1!important}
  #hub .profileRefSubtitle{margin-top:2px!important;font-size:10px!important;line-height:1.08!important}
  #hub .profileRefField{margin-top:2px!important}
  #hub .profileRefField label{margin:0 0 2px!important;font-size:9.5px!important;line-height:1!important}
  #hub .profileRefInputWrap{height:34px!important;border-radius:11px!important;grid-template-columns:minmax(0,1fr) 28px!important;padding:0 6px 0 10px!important}
  #hub .profileRefInputWrap input{font-size:13.5px!important}
  #hub .profileRefPencil{font-size:15px!important}
  #hub .profileRefSave{min-width:112px!important;height:30px!important;border-radius:11px!important;font-size:10.5px!important;gap:5px!important;box-shadow:0 5px 12px rgba(42,126,235,.16)!important}

  /* Subscription: preserve plan, copy and CTA while collapsing the card. */
  #hub .profilePlanRef{min-height:0!important;height:124px!important;box-sizing:border-box!important;padding:6px 10px!important;grid-template-columns:42px minmax(0,1fr) auto!important;column-gap:8px!important;row-gap:3px!important;align-items:center!important}
  #hub .profilePlanRef .profileRefSectionIcon{width:38px!important;height:38px!important;border-radius:12px!important;font-size:17px!important}
  #hub .profilePlanRef .profileRefSectionText h2{font-size:19px!important;line-height:1!important}
  #hub .profilePlanRef .profileRefSectionText p{margin-top:2px!important;font-size:9.5px!important;line-height:1.08!important}
  #hub .profilePlanRef .profileRefChevron{font-size:20px!important}
  #hub .profilePlanBody{grid-column:2/4!important;grid-template-columns:auto minmax(0,1fr)!important;gap:7px!important;align-items:center!important}
  #hub .profilePlanPill{min-width:58px!important;height:25px!important;border-radius:9px!important;padding:0 8px!important;font-size:10px!important}
  #hub .profilePlanCopy{font-size:9.5px!important;line-height:1.12!important}
  #hub .profilePlanCta{grid-column:2/4!important;height:28px!important;border-radius:10px!important;font-size:10.5px!important;gap:5px!important}

  /* Social section is intentionally not compacted: all providers and hit areas remain. */
  #hub .profileSocialRef{min-height:0!important;height:100%!important;box-sizing:border-box!important;overflow:hidden!important}
}

@media(max-width:767px) and (max-height:760px){
  #hub .view[data-view="profile"] .profileReferenceScroll{grid-template-rows:30px 126px 116px minmax(0,1fr)!important;gap:4px!important;padding-bottom:82px!important}
  #hub .profileReferenceBrand{min-height:30px!important;height:30px!important;padding-top:0!important;padding-bottom:2px!important}
  #hub .profileReferenceEdit{height:126px!important;padding-top:6px!important;padding-bottom:6px!important}
  #hub .profileRefAvatar{width:62px!important;height:62px!important}
  #hub .profileRefPhotoBtn{min-height:25px!important;height:25px!important}
  #hub .profilePlanRef{height:116px!important;padding-top:4px!important;padding-bottom:4px!important}
}
</style>'''


def patch_text(text: str) -> str:
    if 'V311 APPROVED CREATOR REFERENCE' not in text:
        raise RuntimeError('V313 requires the normalized V311 Creator Hub')
    for marker in ('profileReferenceEdit', 'profilePlanRef', 'profileSocialRefRow'):
        if marker not in text:
            raise RuntimeError(f'V313 missing Creator Hub anchor: {marker}')

    # Consume the newline we own along with the previous V313 block. Without
    # this, every restart leaves one extra blank line and breaks idempotence.
    pattern = re.compile(r'<style id="' + re.escape(STYLE_ID) + r'">.*?</style>\n?', re.DOTALL)
    cleaned = pattern.sub('', text)
    if '</head>' not in cleaned:
        raise RuntimeError('V313 Creator Hub </head> anchor missing')
    return cleaned.replace('</head>', STYLE + '\n</head>', 1)


def main() -> None:
    hub = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path('/app/web/creator_hub_v156_component/index.html')
    if not hub.is_file():
        raise SystemExit(f'V313 Hub missing: {hub}')
    before = hub.read_text(encoding='utf-8')
    after = patch_text(before)
    hub.write_text(after, encoding='utf-8')
    print('V313 mobile Profile fit applied: profile=136px plan=124px socials=preserved changed=', before != after, flush=True)


if __name__ == '__main__':
    main()
