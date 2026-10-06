#!/usr/bin/env python3
# Isolated regression for the V297 desktop AI grid collapse.
from fix_v297_1_ai_grid_hotfix import repair_text

OLD = "const movable=[...root.children].filter(el=>el.classList.contains('top')||el.classList.contains('panel'));"
NEW = "const movable=[...root.children].filter(el=>el.classList.contains('journeySteps')||el.classList.contains('top')||el.classList.contains('panel'));"

sample = '''<!doctype html><html><body>
<main id="ai221"><div class="journeySteps">steps</div><div class="top">top</div><section class="panel">panel</section></main>
<script>'''+OLD+'''</script></body></html>'''

fixed = repair_text(sample)
assert NEW in fixed, "V297 AI hotfix must move journeySteps into v297AiMain"
assert OLD not in fixed, "broken V297 movable selector must be removed"
assert fixed.count(NEW) == 1, "hotfix must be idempotent and produce one corrected selector"
assert repair_text(fixed) == fixed, "hotfix must be idempotent"
print("V297.1 AI grid-collapse regression: PASS")
