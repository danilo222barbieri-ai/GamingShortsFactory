#!/usr/bin/env python3
from pathlib import Path
import re
import sys

MARK = 'V365_CREATOR_HUB_BOOTSTRAP_FIX'
COLLECTION_SELECTORS = ('[data-view]', '[data-project-pane]', '.socialDot')


def broken_pattern(selector: str) -> re.Pattern[str]:
    return re.compile(
        r'(?<!\$)\$\((?P<q>["\'])' + re.escape(selector) + r'(?P=q)\)\.forEach'
    )


def healthy_pattern(selector: str) -> re.Pattern[str]:
    return re.compile(
        r'\$\$\((?P<q>["\'])' + re.escape(selector) + r'(?P=q)\)\.forEach'
    )


def patch_text(text: str) -> str:
    for selector in COLLECTION_SELECTORS:
        bad = broken_pattern(selector)
        text, repaired = bad.subn(
            lambda m: '$$(' + m.group('q') + selector + m.group('q') + ').forEach',
            text,
        )
        if bad.search(text):
            raise RuntimeError(f'V365 broken Creator Hub collection call remains: {selector}')
        if not healthy_pattern(selector).search(text):
            raise RuntimeError(f'V365 Creator Hub collection anchor missing after repair: {selector}')
        if repaired:
            print(f'V365 repaired {selector} collection calls={repaired}', flush=True)

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
