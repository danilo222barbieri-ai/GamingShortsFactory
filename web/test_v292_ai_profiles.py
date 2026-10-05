import sys

sys.path.insert(0, "/app/web")

import game_brain_v112 as brain


def need(ok, message):
    print(("PASS: " if ok else "FAIL: ") + message)
    if not ok:
        raise AssertionError(message)


def diagnostics():
    return {
        "0.0": {
            "features": {
                "event_score": 0.20,
                "reaction": 0.95,
                "motion_burst": 0.05,
                "motion_avg": 0.05,
                "arc": 0.05,
                "setup_score": 0.05,
                "aftermath_score": 0.05,
                "moment_category": "reaction",
                "event_type": "reaction",
            }
        },
        "30.0": {
            "features": {
                "event_score": 0.20,
                "reaction": 0.05,
                "motion_burst": 0.95,
                "motion_avg": 0.95,
                "arc": 0.05,
                "setup_score": 0.05,
                "aftermath_score": 0.05,
                "moment_category": "action",
                "event_type": "impact",
            }
        },
        "60.0": {
            "features": {
                "event_score": 0.20,
                "reaction": 0.05,
                "motion_burst": 0.05,
                "motion_avg": 0.05,
                "arc": 0.95,
                "setup_score": 0.90,
                "aftermath_score": 0.90,
                "moment_category": "story",
                "event_type": "highlight",
            }
        },
    }


def top_start(profile):
    pool = [(0.50, 0.0), (0.50, 30.0), (0.50, 60.0)]
    chosen, meta = brain.rerank_moments(
        pool,
        diagnostics(),
        clip_duration=15,
        numero_clip=3,
        profile=profile,
        genre="Auto",
        events=[],
    )
    need(len(chosen) == 3, f"{profile} returns three candidates")
    starts = [round(float(x[1]), 3) for x in chosen]
    need(len(set(starts)) == 3, f"{profile} candidates are diverse/non-duplicated")
    need(meta.get("profile") == profile, f"{profile} is retained in ranking metadata")
    return starts[0]


reaction_top = top_start("reaction")
action_top = top_start("action")
director_top = top_start("director")
auto_top = top_start("auto")

need(reaction_top == 0.0, f"reaction profile favors reaction signal (got {reaction_top})")
need(action_top == 30.0, f"action profile favors motion signal (got {action_top})")
need(director_top == 60.0, f"director profile favors arc/setup/payoff (got {director_top})")
need(len({reaction_top, action_top, director_top}) == 3, "specialized engines produce distinct winners")
need(auto_top in {0.0, 30.0, 60.0}, "auto profile produces a valid ranked winner")

print("V292 AI profile differentiation and three-candidate diversity: PASS")
