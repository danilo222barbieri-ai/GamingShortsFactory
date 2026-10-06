#!/usr/bin/env python3
from pathlib import Path
import sys

AI = Path(sys.argv[1] if len(sys.argv) > 1 else "/app/web/ai_v221_component/index.html")

OLD = "const movable=[...root.children].filter(el=>el.classList.contains('top')||el.classList.contains('panel'));"
NEW = "const movable=[...root.children].filter(el=>el.classList.contains('journeySteps')||el.classList.contains('top')||el.classList.contains('panel'));"


def repair_text(text: str) -> str:
    if NEW in text:
        return text
    if OLD not in text:
        raise RuntimeError("V297.1 AI movable selector anchor missing")
    return text.replace(OLD, NEW, 1)


def main() -> None:
    if not AI.is_file():
        raise RuntimeError(f"V297.1 AI component missing: {AI}")
    before = AI.read_text(encoding="utf-8")
    after = repair_text(before)
    AI.write_text(after, encoding="utf-8")
    print("V297.1 AI grid-collapse hotfix applied:", AI, "changed=", after != before, flush=True)


if __name__ == "__main__":
    main()
