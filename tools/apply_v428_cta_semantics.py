from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def replace_once(path: str, old: str, new: str) -> None:
    file = ROOT / path
    text = file.read_text(encoding='utf-8')
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{path}: expected 1 match, found {count}')
    file.write_text(text.replace(old, new, 1), encoding='utf-8')

replace_once(
    'web/ai_v221_component/index.html',
    'data-alive-next="create_short publish"',
    'data-alive-next="create_short"',
)
replace_once(
    'tests/test_mobile_polish_v428.py',
    '    assert ">Pubblica</button>" not in page\n',
    '    assert ">Pubblica</button>" not in page\n    assert \'data-alive-next="create_short publish"\' not in page\n    assert \'data-alive-next="create_short"\' in page\n',
)
print('V428 CTA semantics cleaned')
