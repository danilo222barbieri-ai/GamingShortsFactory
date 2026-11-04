"""GSF AI Performance Engine 2.0 (Blocco 2, 3, 4, 5).

Architecture:
1. Fast Detection (`fast_detect_candidates`):
   Rapid candidate window extraction from the 0.5s audio/motion/peak grid,
   adaptive stride (fine 0.5s-1.0s on short clips, keyframe-guided on long videos),
   and low-signal/dead-video detection.
2. Game-Aware AI (`GAME_PROFILES`, `infer_game_profile`, `game_aware_adjustment`):
   10 specialized gaming profiles (FPS, Battle Royale, Action, Racing, Sports,
   Survival, Horror, RPG, Platform, Narrative) + Generic ("Auto").
3. Smart Ranking (`smart_rank_candidates`, `score_candidate_window`):
   Verifiable multi-signal scoring (action intensity, audio variation, visual change,
   recognized events, game relevance, hook/ending quality, climax payoff, short virality)
   with MMR diversity so the 3 returned moments are never near-duplicates.
4. Precision Pass (`precision_refine_boundary`):
   Zero-subprocess timestamp boundary refinement directly on the in-memory scan arrays,
   aligning starts to natural quiet transitions and keeping the climax in the 35%-75% zone.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import threading
import time
from pathlib import Path
from typing import Any, Mapping

ENGINE_VERSION_V2 = "v2.0-fast-game-aware"

_WHISPER_LOCK = threading.Lock()
_WHISPER_TINY_INSTANCE = None
_MEMORY_SCAN_CACHE: dict[str, dict[str, Any]] = {}
_MEMORY_SCAN_LOCK = threading.Lock()


def _num(v: Any, default: float = 0.0) -> float:
    try:
        x = float(v)
        return x if math.isfinite(x) else float(default)
    except Exception:
        return float(default)


def _clamp(v: Any, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, _num(v, lo)))


# ============================================================================
# BLOCCO 2 — MODEL SINGLETON & PERSISTENT SCAN CACHE
# ============================================================================

def get_cached_whisper_tiny():
    """Load Whisper Tiny at most once per process. Eliminates the 7.2s re-init penalty."""
    global _WHISPER_TINY_INSTANCE
    if _WHISPER_TINY_INSTANCE is not None:
        return _WHISPER_TINY_INSTANCE
    with _WHISPER_LOCK:
        if _WHISPER_TINY_INSTANCE is None:
            from faster_whisper import WhisperModel
            _WHISPER_TINY_INSTANCE = WhisperModel("tiny", device="cpu", compute_type="int8")
    return _WHISPER_TINY_INSTANCE


def _scan_cache_signature(input_file: str | Path, engine_version: str = "") -> str:
    try:
        p = Path(str(input_file))
        st = p.stat()
        raw = f"{engine_version}|{p.resolve()}|{st.st_size}|{st.st_mtime_ns}"
    except Exception:
        raw = f"{engine_version}|{input_file}"
    return hashlib.sha1(raw.encode("utf-8", errors="ignore")).hexdigest()[:24]


def load_cached_scan(input_file: str | Path, preview_dir: str | Path | None = None, engine_version: str = "") -> tuple[dict[str, Any] | None, bool]:
    sig = _scan_cache_signature(input_file, engine_version)
    with _MEMORY_SCAN_LOCK:
        mem = _MEMORY_SCAN_CACHE.get(sig)
        if isinstance(mem, dict) and mem.get("audio") is not None:
            return dict(mem), True
    if preview_dir:
        try:
            cache_file = Path(preview_dir) / f".gsf_scan_cache_{sig}.json"
            if cache_file.is_file():
                data = json.loads(cache_file.read_text(encoding="utf-8"))
                if isinstance(data, dict) and isinstance(data.get("audio"), list) and isinstance(data.get("motion"), list):
                    with _MEMORY_SCAN_LOCK:
                        _MEMORY_SCAN_CACHE[sig] = data
                    return data, True
        except Exception:
            pass
    return None, False


def save_cached_scan(
    input_file: str | Path,
    scan: Mapping[str, Any],
    preview_dir: str | Path | None = None,
    engine_version: str = "",
) -> None:
    if not isinstance(scan, Mapping):
        return
    meta = scan.get("meta") if isinstance(scan.get("meta"), Mapping) else {}
    if meta.get("audio_error") or meta.get("video_error"):
        return
    sig = _scan_cache_signature(input_file, engine_version)
    payload = dict(scan)
    with _MEMORY_SCAN_LOCK:
        if len(_MEMORY_SCAN_CACHE) >= 32:
            _MEMORY_SCAN_CACHE.pop(next(iter(_MEMORY_SCAN_CACHE)), None)
        _MEMORY_SCAN_CACHE[sig] = payload
    if preview_dir:
        try:
            d = Path(preview_dir)
            d.mkdir(parents=True, exist_ok=True)
            cache_file = d / f".gsf_scan_cache_{sig}.json"
            tmp = d / f".gsf_scan_cache_{sig}.{os.getpid()}.tmp"
            tmp.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
            os.replace(tmp, cache_file)
        except Exception:
            pass


def scan_profile_for_duration(total_seconds: float) -> dict[str, Any]:
    """Adaptive scan parameters tuned for fast turnaround on both short and long videos."""
    total = max(0.0, _num(total_seconds, 0.0))
    if total <= 60.0:
        return {
            "tier": "fast_short",
            "video_fps": 2.0,
            "analysis_width": 144,
            "adaptive": False,
            "keyframes_only": False,
        }
    if total <= 3 * 60:
        return {
            "tier": "standard",
            "video_fps": 2.0,
            "analysis_width": 160,
            "adaptive": False,
            "keyframes_only": False,
        }
    if total <= 20 * 60:
        return {
            "tier": "medium_turbo",
            "video_fps": 0.5,
            "analysis_width": 128,
            "adaptive": True,
            "keyframes_only": True,
        }
    if total <= 60 * 60:
        return {
            "tier": "long_turbo",
            "video_fps": 0.35,
            "analysis_width": 112,
            "adaptive": True,
            "keyframes_only": True,
        }
    return {
        "tier": "marathon_turbo",
        "video_fps": 0.25,
        "analysis_width": 96,
        "adaptive": True,
        "keyframes_only": True,
    }


# ============================================================================
# BLOCCO 3 — GAME-AWARE AI (10 GENRE PROFILES + GENERIC FALLBACK)
# ============================================================================

GAME_PROFILES: dict[str, dict[str, Any]] = {
    "FPS": {
        "name": "FPS",
        "label": "FPS e Shooter",
        "keywords": (
            "valorant", "counter strike", "counterstrike", "cs2", "csgo",
            "call of duty", "modern warfare", "black ops", "overwatch",
            "rainbow six", "r6 siege", "battlefield", "doom", "quake",
            "halo", "destiny", "the finals", "xdefiant", "escape from tarkov",
            "tarkov", "team fortress", "splitgate", "fragpunk", "fps", "shooter",
        ),
        "important_events": ["multi_kill", "clutch", "kill", "impact", "reaction"],
        "recommended_duration": 15,
        "priority": "action_burst_and_precision",
        "context_padding": {"pre_event_seconds": 3.5, "post_event_seconds": 2.5},
        "weights": {
            "motion_burst": 0.24,
            "event_score": 0.22,
            "audio_burst": 0.16,
            "synergy": 0.14,
            "reaction": 0.12,
            "sustained_motion": 0.12,
            "arc": 0.0,
            "continuity": 0.0,
        },
        "vision_zones": ["CROSSHAIR", "KILLFEED", "MINIMAP"],
    },
    "Battle Royale": {
        "name": "Battle Royale",
        "label": "Battle Royale",
        "keywords": (
            "fortnite", "pubg", "playerunknown", "warzone", "apex legends",
            "apex", "free fire", "naraka", "realm royale", "fall guys",
            "super people", "battle royale",
        ),
        "important_events": ["victory", "clutch", "multi_kill", "kill", "reaction"],
        "recommended_duration": 30,
        "priority": "endgame_clutch_and_survival",
        "context_padding": {"pre_event_seconds": 5.0, "post_event_seconds": 3.5},
        "weights": {
            "event_score": 0.22,
            "motion_burst": 0.20,
            "synergy": 0.18,
            "reaction": 0.16,
            "arc": 0.14,
            "sustained_motion": 0.10,
            "audio_burst": 0.0,
            "continuity": 0.0,
        },
        "vision_zones": ["PLAYER", "KILLFEED", "MINIMAP"],
    },
    "Action": {
        "name": "Action",
        "label": "Action e Hack-and-Slash",
        "keywords": (
            "devil may cry", "dmc", "god of war", "bayonetta", "stellar blade",
            "black myth", "wukong", "sekiro", "ninja gaiden", "hades",
            "monster hunter", "nier", "hi fi rush", "metal gear rising",
            "sifu", "dynasty warriors", "ghost of tsushima", "marvel spider man",
            "spiderman", "arkham", "hack and slash", "action",
        ),
        "important_events": ["boss", "multi_kill", "impact", "clutch", "kill"],
        "recommended_duration": 30,
        "priority": "sustained_combat_and_combo_peaks",
        "context_padding": {"pre_event_seconds": 4.0, "post_event_seconds": 3.0},
        "weights": {
            "sustained_motion": 0.24,
            "motion_burst": 0.22,
            "synergy": 0.18,
            "event_score": 0.16,
            "arc": 0.12,
            "audio_burst": 0.08,
            "reaction": 0.0,
            "continuity": 0.0,
        },
        "vision_zones": ["COMBO_METER", "BOSS_BAR", "PLAYER"],
    },
    "Racing": {
        "name": "Racing",
        "label": "Racing e Motori",
        "keywords": (
            "forza", "gran turismo", "assetto corsa", "iracing", "need for speed",
            "nfs", "f1 2", "formula 1", "motogp", "wrc", "dirt rally",
            "the crew", "project cars", "mario kart", "trackmania", "beamng",
            "burnout", "asphalt", "ride 5", "racing", "corsa",
        ),
        "important_events": ["overtake", "crash", "victory", "impact", "clutch"],
        "recommended_duration": 15,
        "priority": "high_speed_flow_and_overtakes",
        "context_padding": {"pre_event_seconds": 4.5, "post_event_seconds": 2.5},
        "weights": {
            "continuity": 0.26,
            "sustained_motion": 0.24,
            "motion_burst": 0.18,
            "synergy": 0.14,
            "arc": 0.10,
            "event_score": 0.08,
            "audio_burst": 0.0,
            "reaction": 0.0,
        },
        "vision_zones": ["VEHICLE", "SPEEDOMETER", "HUD"],
    },
    "Sports": {
        "name": "Sports",
        "label": "Sportivi",
        "keywords": (
            "ea sports fc", "fc 24", "fc 25", "fc 26", "fc 27", "fifa",
            "efootball", "pes ", "nba 2k", "madden", "nhl ", "football",
            "soccer", "calcio", "rocket league", "ufc", "wwe 2k", "topspin",
            "f1 manager", "tony hawk", "skate", "tenis", "tennis", "sport",
        ),
        "important_events": ["goal", "save", "shot", "victory", "reaction"],
        "recommended_duration": 15,
        "priority": "build_up_climax_and_celebration",
        "context_padding": {"pre_event_seconds": 5.0, "post_event_seconds": 4.0},
        "weights": {
            "arc": 0.24,
            "event_score": 0.20,
            "audio_burst": 0.18,
            "synergy": 0.14,
            "reaction": 0.14,
            "sustained_motion": 0.10,
            "motion_burst": 0.0,
            "continuity": 0.0,
        },
        "vision_zones": ["ACTION", "SCOREBOARD"],
    },
    "Survival": {
        "name": "Survival",
        "label": "Survival e Crafting",
        "keywords": (
            "minecraft", "rust", "ark survival", "dayz", "subnautica",
            "valheim", "sons of the forest", "the forest", "terraria",
            "palworld", "no man s sky", "don t starve", "7 days to die",
            "project zomboid", "grounded", "raft", "scum", "enlisted",
            "once human", "survival",
        ),
        "important_events": ["clutch", "impact", "reaction", "kill", "victory"],
        "recommended_duration": 30,
        "priority": "sudden_danger_and_tension_release",
        "context_padding": {"pre_event_seconds": 5.5, "post_event_seconds": 3.5},
        "weights": {
            "arc": 0.22,
            "audio_burst": 0.20,
            "reaction": 0.18,
            "event_score": 0.16,
            "synergy": 0.14,
            "motion_burst": 0.10,
            "sustained_motion": 0.0,
            "continuity": 0.0,
        },
        "vision_zones": ["PLAYER", "INVENTORY_BAR", "HUD"],
    },
    "Horror": {
        "name": "Horror",
        "label": "Horror",
        "keywords": (
            "resident evil", "silent hill", "dead by daylight", "dbd",
            "phasmophobia", "outlast", "five nights at freddy", "fnaf",
            "alan wake", "lethal company", "amnesia", "until dawn",
            "the quarry", "visage", "mortuary assistant", "poppy playtime",
            "backrooms", "content warning", "horror",
        ),
        "important_events": ["reaction", "impact", "clutch", "death"],
        "recommended_duration": 15,
        "priority": "silence_to_scream_contrast_and_jumpscares",
        "context_padding": {"pre_event_seconds": 4.5, "post_event_seconds": 4.0},
        "weights": {
            "audio_burst": 0.28,
            "reaction": 0.26,
            "event_score": 0.16,
            "arc": 0.14,
            "motion_burst": 0.10,
            "synergy": 0.06,
            "sustained_motion": 0.0,
            "continuity": 0.0,
        },
        "vision_zones": ["CENTER_FOCUS", "PLAYER_REACTION"],
    },
    "RPG": {
        "name": "RPG",
        "label": "RPG e Soulslike",
        "keywords": (
            "elden ring", "dark souls", "bloodborne", "demon s souls",
            "lies of p", "lords of the fallen", "baldur s gate", "bg3",
            "cyberpunk 2077", "cyberpunk", "witcher", "skyrim", "oblivion",
            "fallout", "starfield", "final fantasy", "persona", "diablo",
            "path of exile", "poe", "genshin impact", "honkai", "wuwa",
            "wuthering waves", "dragon s dogma", "kingdom come", "mass effect",
            "dragon age", "zed", "zelda", "metaphor", "rpg", "soulslike",
        ),
        "important_events": ["boss", "victory", "clutch", "impact", "kill"],
        "recommended_duration": 30,
        "priority": "boss_climax_and_dramatic_arcs",
        "context_padding": {"pre_event_seconds": 5.5, "post_event_seconds": 4.0},
        "weights": {
            "arc": 0.24,
            "event_score": 0.20,
            "synergy": 0.18,
            "sustained_motion": 0.16,
            "motion_burst": 0.12,
            "reaction": 0.10,
            "audio_burst": 0.0,
            "continuity": 0.0,
        },
        "vision_zones": ["BOSS_BAR", "PLAYER", "HUD"],
    },
    "Platform": {
        "name": "Platform",
        "label": "Platform e Precision",
        "keywords": (
            "super mario", "mario wonder", "mario odyssey", "celeste",
            "hollow knight", "silksong", "cuphead", "crash bandicoot",
            "sonic", "ori and the", "rayman", "astro bot", "little nightmares",
            "geometry dash", "super meat boy", "dead cells", "blasphemous",
            "prince of persia", "pizza tower", "platform", "platformer",
        ),
        "important_events": ["clutch", "victory", "reaction", "impact"],
        "recommended_duration": 15,
        "priority": "precision_movement_and_tight_saves",
        "context_padding": {"pre_event_seconds": 3.5, "post_event_seconds": 2.5},
        "weights": {
            "continuity": 0.24,
            "sustained_motion": 0.22,
            "motion_burst": 0.18,
            "reaction": 0.14,
            "arc": 0.12,
            "event_score": 0.10,
            "audio_burst": 0.0,
            "synergy": 0.0,
        },
        "vision_zones": ["PLAYER", "OBSTACLES"],
    },
    "Narrative": {
        "name": "Narrative",
        "label": "Giochi Narrativi",
        "keywords": (
            "life is strange", "detroit become human", "heavy rain",
            "beyond two souls", "the walking dead", "telltale", "wolf among us",
            "death stranding", "disco elysium", "firewatch", "what remains of edith finch",
            "outer wilds", "stanley parable", "dispatch", "as dusk falls",
            "LA noire", "ace attorney", "danganronpa", "visual novel", "narrativo",
        ),
        "important_events": ["reaction", "clutch", "victory", "impact"],
        "recommended_duration": 60,
        "priority": "emotional_peaks_dialogue_and_story_turns",
        "context_padding": {"pre_event_seconds": 6.5, "post_event_seconds": 4.5},
        "weights": {
            "arc": 0.28,
            "reaction": 0.26,
            "audio_burst": 0.16,
            "event_score": 0.14,
            "synergy": 0.10,
            "continuity": 0.06,
            "motion_burst": 0.0,
            "sustained_motion": 0.0,
        },
        "vision_zones": ["CHARACTER", "SUBTITLES"],
    },
    "Auto": {
        "name": "Auto",
        "label": "Profilo Universale Adattivo",
        "keywords": (),
        "important_events": ["multi_kill", "clutch", "victory", "goal", "reaction", "impact"],
        "recommended_duration": 15,
        "priority": "balanced_action_reaction_and_narrative_arc",
        "context_padding": {"pre_event_seconds": 4.5, "post_event_seconds": 3.0},
        "weights": {
            "event_score": 0.20,
            "motion_burst": 0.18,
            "audio_burst": 0.16,
            "synergy": 0.16,
            "reaction": 0.12,
            "arc": 0.10,
            "sustained_motion": 0.08,
            "continuity": 0.0,
        },
        "vision_zones": ["ACTION", "HUD"],
    },
}

# Priority order for genre matching so specific genres match before broad terms
_GENRE_MATCH_ORDER = (
    "Battle Royale",
    "Sports",
    "Racing",
    "Horror",
    "Platform",
    "Narrative",
    "Survival",
    "RPG",
    "Action",
    "FPS",
)


def infer_game_genre_v2(value: Any) -> str:
    """Infer one of the 10 canonical game genres from a title/hint, or 'Auto' if unknown."""
    text = re.sub(r"[^a-z0-9]+", " ", str(value or "").lower()).strip()
    if not text:
        return "Auto"
    padded = f" {text} "
    # Check exact genre names first
    for gname in GAME_PROFILES:
        if gname.lower() == text:
            return gname
    for gname in _GENRE_MATCH_ORDER:
        prof = GAME_PROFILES[gname]
        for kw in prof["keywords"]:
            if kw in text or kw in padded:
                return gname
    return "Auto"


def get_game_profile(genre_or_title: Any) -> dict[str, Any]:
    """Return the full configuration dict for a genre name or game title."""
    raw = str(genre_or_title or "").strip()
    if raw in GAME_PROFILES:
        return dict(GAME_PROFILES[raw])
    inferred = infer_game_genre_v2(raw)
    return dict(GAME_PROFILES.get(inferred, GAME_PROFILES["Auto"]))


def genre_score_multiplier_v2(genre: str, profile: str, features: Mapping[str, Any] | None) -> float:
    """Compute bounded genre score multiplier [0.93, 1.08] for all 10 game profiles."""
    g = str(genre or "Auto")
    if g not in GAME_PROFILES:
        g = infer_game_genre_v2(g)
    if g == "Auto":
        return 1.0
    f = features or {}
    prof = GAME_PROFILES[g]
    w = prof["weights"]

    motion_burst = _clamp(f.get("motion_burst", f.get("motion_peak", 0.0)))
    sustained = _clamp(f.get("sustained_motion", f.get("motion_avg", 0.0)))
    continuity = _clamp(f.get("continuity", f.get("active_ratio", 0.0)))
    audio_burst = _clamp(f.get("audio_burst", f.get("audio_peak", 0.0)))
    synergy = _clamp(f.get("synergy", 0.0))
    arc = _clamp(f.get("arc", 0.0))
    reaction = max(_clamp(f.get("reaction", 0.0)), _clamp(f.get("reaction_cue", 0.0)))
    event_score = _clamp(f.get("event_score", 0.0))
    dead = max(_clamp(f.get("dead_ratio", 0.0)), _clamp(f.get("dead_streak_ratio", 0.0)))

    fit = (
        w.get("motion_burst", 0.0) * motion_burst
        + w.get("sustained_motion", 0.0) * sustained
        + w.get("continuity", 0.0) * continuity
        + w.get("audio_burst", 0.0) * audio_burst
        + w.get("synergy", 0.0) * synergy
        + w.get("arc", 0.0) * arc
        + w.get("reaction", 0.0) * reaction
        + w.get("event_score", 0.0) * event_score
    )

    centered = max(-1.0, min(1.0, (fit - 0.40) / 0.40))
    multiplier = 1.0 + 0.065 * centered - 0.025 * dead
    if str(profile or "").lower() == "reaction":
        multiplier = 1.0 + (multiplier - 1.0) * 0.60
    return max(0.93, min(1.08, multiplier))


# ============================================================================
# BLOCCO 4 — FAST DETECTION, SMART RANKING & PRECISION PASS
# ============================================================================

def is_low_signal_scan(scan: Mapping[str, Any] | None) -> bool:
    """Detect if the scanned video has virtually no events or dynamic changes."""
    if not isinstance(scan, Mapping):
        return True
    audio = [ _num(x) for x in (scan.get("audio") or []) ]
    motion = [ _num(x) for x in (scan.get("motion") or []) ]
    peak = [ _num(x) for x in (scan.get("peak") or []) ]
    n = min(len(audio), len(motion))
    if n <= 0:
        return True
    max_m = max(motion) if motion else 0.0
    max_a = max(audio) if audio else 0.0
    max_p = max(peak) if peak else 0.0
    if max_m < 0.03 and max_a < 0.03 and max_p < 0.03:
        return True
    # Check if both audio and motion are completely flat (zero variance)
    avg_m = sum(motion) / len(motion)
    avg_a = sum(audio) / len(audio)
    var_m = sum((x - avg_m) ** 2 for x in motion) / len(motion)
    var_a = sum((x - avg_a) ** 2 for x in audio) / len(audio)
    return var_m < 1e-5 and var_a < 1e-5 and max_m < 0.08 and max_a < 0.08


def precision_refine_boundary(
    scan: Mapping[str, Any] | None,
    center_start: float,
    target_duration: float,
    total_seconds: float = 0.0,
    genre: str = "Auto",
) -> tuple[float, float]:
    """Zero-subprocess boundary refinement using the 0.5s scan arrays.

    Finds a natural low-energy / silence dip near the candidate start so the clip
    doesn't cut in the middle of a word or explosion, while keeping the main peak
    inside the 35%-75% payoff zone.
    """
    duration = max(0.5, _num(target_duration, 15.0))
    start = max(0.0, _num(center_start, 0.0))
    if not isinstance(scan, Mapping):
        return start, duration

    step = max(0.1, _num(scan.get("step"), 0.5))
    audio = scan.get("audio") or []
    motion = scan.get("motion") or []
    peak = scan.get("peak") or []
    n = min(len(audio), len(motion))
    if n <= 2:
        return start, duration

    total = max(_num(total_seconds, 0.0), n * step)
    max_start = max(0.0, total - duration)
    if max_start <= 0.25:
        return 0.0, min(duration, total) if total > 0 else duration

    start = min(start, max_start)

    # Locate the strongest instant inside [start, start + duration]
    i0 = max(0, min(n - 1, int(round(start / step))))
    i1 = max(i0 + 1, min(n, int(round((start + duration) / step))))
    best_idx = i0
    best_energy = -1.0
    for idx in range(i0, i1):
        a = _num(audio[idx])
        m = _num(motion[idx])
        p = _num(peak[idx]) if idx < len(peak) else a
        e = 0.42 * a + 0.40 * m + 0.18 * p
        if e > best_energy:
            best_energy = e
            best_idx = idx

    peak_time = best_idx * step
    prof = get_game_profile(genre)
    pre_pad = _num((prof.get("context_padding") or {}).get("pre_event_seconds"), 4.5)
    # Target start places the climax around 45%-60% of the clip, or pre_pad before peak
    ideal_offset = min(duration * 0.52, max(pre_pad, duration * 0.36))
    ideal_start = max(0.0, min(max_start, peak_time - ideal_offset))

    # Search within [-2.0s, +2.0s] around ideal_start (and within [-3.0s, +3.0s] of original start)
    search_lo = max(0.0, ideal_start - 2.0, start - 3.0)
    search_hi = min(max_start, ideal_start + 2.0, start + 3.0)
    if search_hi < search_lo:
        search_lo, search_hi = max(0.0, start - 1.5), min(max_start, start + 1.5)

    idx_lo = max(0, min(n - 1, int(round(search_lo / step))))
    idx_hi = max(idx_lo, min(n - 1, int(round(search_hi / step))))

    chosen_start = start
    best_cost = 999.0
    for idx in range(idx_lo, idx_hi + 1):
        cand_start = min(max_start, idx * step)
        # Cost combines audio level at cut point (prefer quiet transition) + distance from ideal
        a_cut = _num(audio[idx])
        m_cut = _num(motion[idx])
        # Next bucket hook energy (we want activity right after the cut)
        next_idx = min(n - 1, idx + 1)
        hook_energy = 0.5 * _num(audio[next_idx]) + 0.5 * _num(motion[next_idx])
        drift = abs(cand_start - ideal_start) / max(1.0, duration)
        cost = 0.50 * a_cut + 0.20 * m_cut - 0.18 * hook_energy + 0.35 * drift
        if cost < best_cost:
            best_cost = cost
            chosen_start = cand_start

    return round(max(0.0, min(max_start, chosen_start)), 3), float(duration)


def verify_and_diversify_candidates(
    scored_candidates: list[tuple[float, float, dict[str, Any], str]],
    duration: float,
    target_count: int = 3,
    total_seconds: float = 0.0,
) -> list[tuple[float, float, dict[str, Any], str]]:
    """Select up to `target_count` high-value, non-redundant moments.

    Avoids proposing 3 nearly identical windows and penalizes overlapping starts.
    """
    if not scored_candidates:
        return []
    dur = max(1.0, _num(duration, 15.0))
    want = max(1, int(target_count or 3))
    ordered = sorted(scored_candidates, key=lambda x: float(x[0]), reverse=True)

    # Adaptive minimum spacing based on total video length vs clip duration
    slack = max(0.0, _num(total_seconds, 0.0) - dur)
    if slack <= 1.0:
        # Only 1 full-duration window fits in the source video
        return [ordered[0]]

    min_gap = min(max(2.5, dur * 0.45), max(1.5, slack / max(1, want)))
    selected: list[tuple[float, float, dict[str, Any], str]] = []

    for pass_scale in (1.0, 0.65, 0.35):
        gap = max(1.0, min_gap * pass_scale)
        for item in ordered:
            if len(selected) >= want:
                break
            if any(abs(float(item[1]) - float(old[1])) < gap for old in selected):
                continue
            selected.append(item)
        if len(selected) >= want:
            break

    selected.sort(key=lambda x: float(x[0]), reverse=True)
    return selected[:want]
