#!/usr/bin/env python3
from pathlib import Path
import sys

MARK = 'V365_CREATOR_HUB_BOOTSTRAP_FIX'

REPLACEMENT_GROUPS = (
    (
        ('$("[data-view]").forEach', '$$("[data-view]").forEach'),
        ("$('[data-view]').forEach", "$$('[data-view]').forEach"),
    ),
    (
        ('$("[data-project-pane]").forEach', '$$("[data-project-pane]").forEach'),
        ("$('[data-project-pane]').forEach", "$$('[data-project-pane]').forEach"),
    ),
    (
        ('$(".socialDot").forEach', '$$(".socialDot").forEach'),
        ("$('.socialDot').forEach", "$$('.socialDot').forEach"),
    ),
)


def patch_text(text: str) -> str:
    for variants in REPLACEMENT_GROUPS:
        found = False
        for bad, good in variants:
            bad_count = text.count(bad)
            good_count = text.count(good)
            if bad_count:
                if bad_count != 1:
                    raise RuntimeError(f'V365 expected exactly one broken collection call: {bad} (found {bad_count})')
                text = text.replace(bad, good, 1)
                found = True
            elif good_count:
                found = True
        if not found:
            raise RuntimeError('V365 Creator Hub bootstrap collection anchor missing')

    if 'GSF_HUB_FOCUS' not in text:
        raise RuntimeError('V365 Creator Hub focus bridge missing')
    if 'openView("dashboard");loadState();' not in text and "openView('dashboard');loadState();" not in text:
        raise RuntimeError('V365 Creator Hub bootstrap tail missing')

    if MARK not in text:
        if '</body>' not in text:
            raise RuntimeError('V365 Creator Hub body anchor missing')
        text = text.replace('</body>', f'<!-- {MARK} -->\n</body>', 1)
    return text


def main() -> None:
    path = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path('/app/web/creator_hub_v156_component/index.html')
    if not path.is_file():
        raise SystemExit('V365 Creator Hub target missing: ' + str(path))
    before = path.read_text(encoding='utf-8')
    after = patch_text(before)
    path.write_text(after, encoding='utf-8')
    print('V365 Creator Hub bootstrap fixed changed=', before != after, flush=True)


if __name__ == '__main__':
    main()
