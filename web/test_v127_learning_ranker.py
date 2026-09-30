from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0,"/app/web")

from feedback_learning_v127 import (
    empty_model,
    event_multiplier,
    load_model,
    save_model,
    update_model,
)

positive=empty_model()
for _ in range(20):
    positive=update_model(positive,{"event":"clutch","action":"published"})
boost=event_multiplier(positive,"clutch")
if not (1.0<boost<=1.04):
    raise SystemExit("V127 positive preference multiplier invalid: "+repr(boost))
if event_multiplier(positive,"goal")!=1.0:
    raise SystemExit("V127 unseen event should remain neutral")

negative=empty_model()
for _ in range(20):
    negative=update_model(negative,{"event":"death","action":"replaced"})
penalty=event_multiplier(negative,"death")
if not (.96<=penalty<1.0):
    raise SystemExit("V127 negative preference multiplier invalid: "+repr(penalty))

small=empty_model()
for _ in range(3):
    small=update_model(small,{"event":"goal","action":"published"})
if event_multiplier(small,"goal")!=1.0:
    raise SystemExit("V127 must not learn from fewer than four signals")

with tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp)
    path=root/"model.json"
    save_model(path,positive)
    restored=load_model(path)
    if restored.get("total_feedback")!=20:
        raise SystemExit("V127 learning model persistence failed")

brain=Path("/app/web/game_brain_v112.py").read_text(encoding="utf-8")
server=Path("/app/web/direct_upload_server.py").read_text(encoding="utf-8")

for marker in (
    "from feedback_learning_v127 import",
    "learning_mult=_learning_multiplier",
    '"engine":"game-brain-v127-learning"',
    '"learning_multiplier"',
    '"total_feedback"',
):
    if marker not in brain:
        raise SystemExit("V127 Game Brain learning marker missing: "+marker)

for marker in (
    "def _ai_learning_restore()",
    "def _ai_learning_update(row)",
    "GSF_V127_LEARNING",
    "GSF_V127_LEARNING_RESTORED",
    '_AI_LEARNING_BUCKET_KEY="ai-feedback/global/model.json"',
    "_ai_learning_restore()",
):
    if marker not in server:
        raise SystemExit("V127 server learning marker missing: "+marker)

compile(brain,"<v127-brain>","exec")
compile(server,"<v127-server>","exec")
print("V127 feedback learning ranker contracts: PASS")
