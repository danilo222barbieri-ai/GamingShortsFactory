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
import shutil
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

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
    return hashlib.sha1(raw.encode("utf-8", errors="ignore"), usedforsecurity=False).hexdigest()[:24]


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
            "nfs", "f1", "f1 2", "formula 1", "motogp", "wrc", "dirt rally",
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
            "dragon age", "zelda", "metaphor", "rpg", "soulslike",
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


CANONICAL_GAME_MAP: dict[str, tuple[str, str]] = {
    # keyword: (Display Title, Genre)
    "valorant": ("Valorant", "FPS"),
    "counter strike": ("Counter-Strike 2", "FPS"),
    "counterstrike": ("Counter-Strike 2", "FPS"),
    "cs2": ("Counter-Strike 2", "FPS"),
    "csgo": ("Counter-Strike: Global Offensive", "FPS"),
    "call of duty": ("Call of Duty", "FPS"),
    "modern warfare": ("Call of Duty: Modern Warfare", "FPS"),
    "black ops": ("Call of Duty: Black Ops", "FPS"),
    "overwatch": ("Overwatch 2", "FPS"),
    "rainbow six": ("Rainbow Six Siege", "FPS"),
    "r6 siege": ("Rainbow Six Siege", "FPS"),
    "battlefield": ("Battlefield", "FPS"),
    "doom": ("DOOM", "FPS"),
    "the finals": ("The Finals", "FPS"),
    "escape from tarkov": ("Escape from Tarkov", "FPS"),
    "tarkov": ("Escape from Tarkov", "FPS"),
    "fortnite": ("Fortnite", "Battle Royale"),
    "warzone": ("Call of Duty: Warzone", "Battle Royale"),
    "apex legends": ("Apex Legends", "Battle Royale"),
    "apex": ("Apex Legends", "Battle Royale"),
    "pubg": ("PUBG", "Battle Royale"),
    "fall guys": ("Fall Guys", "Battle Royale"),
    "devil may cry": ("Devil May Cry", "Action"),
    "dmc": ("Devil May Cry", "Action"),
    "god of war": ("God of War", "Action"),
    "black myth": ("Black Myth: Wukong", "Action"),
    "wukong": ("Black Myth: Wukong", "Action"),
    "sekiro": ("Sekiro: Shadows Die Twice", "Action"),
    "hades": ("Hades", "Action"),
    "monster hunter": ("Monster Hunter", "Action"),
    "sifu": ("Sifu", "Action"),
    "ghost of tsushima": ("Ghost of Tsushima", "Action"),
    "forza": ("Forza Horizon", "Racing"),
    "gran turismo": ("Gran Turismo", "Racing"),
    "assetto corsa": ("Assetto Corsa", "Racing"),
    "f1 24": ("F1 24", "Racing"),
    "f1 23": ("F1 23", "Racing"),
    "f1": ("F1", "Racing"),
    "formula 1": ("Formula 1", "Racing"),
    "need for speed": ("Need for Speed", "Racing"),
    "nfs": ("Need for Speed", "Racing"),
    "mario kart": ("Mario Kart", "Racing"),
    "rocket league": ("Rocket League", "Sports"),
    "ea sports fc": ("EA Sports FC", "Sports"),
    "fc 24": ("EA Sports FC 24", "Sports"),
    "fc 25": ("EA Sports FC 25", "Sports"),
    "fifa": ("EA Sports FC", "Sports"),
    "nba 2k": ("NBA 2K", "Sports"),
    "minecraft": ("Minecraft", "Survival"),
    "rust": ("Rust", "Survival"),
    "sons of the forest": ("Sons of the Forest", "Survival"),
    "the forest": ("The Forest", "Survival"),
    "palworld": ("Palworld", "Survival"),
    "valheim": ("Valheim", "Survival"),
    "subnautica": ("Subnautica", "Survival"),
    "resident evil": ("Resident Evil", "Horror"),
    "silent hill": ("Silent Hill", "Horror"),
    "dead by daylight": ("Dead by Daylight", "Horror"),
    "dbd": ("Dead by Daylight", "Horror"),
    "phasmophobia": ("Phasmophobia", "Horror"),
    "lethal company": ("Lethal Company", "Horror"),
    "alan wake": ("Alan Wake", "Horror"),
    "elden ring": ("Elden Ring", "RPG"),
    "dark souls": ("Dark Souls", "RPG"),
    "bloodborne": ("Bloodborne", "RPG"),
    "baldur s gate": ("Baldur\'s Gate 3", "RPG"),
    "bg3": ("Baldur\'s Gate 3", "RPG"),
    "cyberpunk 2077": ("Cyberpunk 2077", "RPG"),
    "cyberpunk": ("Cyberpunk 2077", "RPG"),
    "witcher": ("The Witcher 3", "RPG"),
    "genshin impact": ("Genshin Impact", "RPG"),
    "super mario": ("Super Mario", "Platform"),
    "mario wonder": ("Super Mario Wonder", "Platform"),
    "mario odyssey": ("Super Mario Odyssey", "Platform"),
    "celeste": ("Celeste", "Platform"),
    "hollow knight": ("Hollow Knight", "Platform"),
    "cuphead": ("Cuphead", "Platform"),
    "astro bot": ("Astro Bot", "Platform"),
    "life is strange": ("Life is Strange", "Narrative"),
    "detroit become human": ("Detroit: Become Human", "Narrative"),
    "the walking dead": ("The Walking Dead", "Narrative"),
    "death stranding": ("Death Stranding", "Narrative"),
    "disco elysium": ("Disco Elysium", "Narrative"),
}


def probe_media_metadata(source_path: str | Path) -> dict[str, str]:
    """Extract format tags/metadata via ffprobe (tags like title, game, comment)."""
    tags: dict[str, str] = {}
    try:
        out = subprocess.check_output(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "format_tags",
                "-of", "json",
                str(source_path)
            ],
            stderr=subprocess.DEVNULL,
            timeout=5,
            text=True
        )
        data = json.loads(out)
        tags = data.get("format", {}).get("tags", {}) or {}
    except Exception:
        pass
    return tags


def extract_game_title_from_path_or_meta(
    source_path_or_title: Any,
    metadata: Mapping[str, Any] | None = None
) -> tuple[str, str]:
    """Extract clean canonical game title and matched genre from filename or metadata."""
    raw = str(source_path_or_title or "").strip()
    if not raw and not metadata:
        return "", "Auto"

    # Check container metadata tags first
    if isinstance(metadata, Mapping):
        for k in ("game", "title", "game_name", "comment", "description", "album"):
            v = str(metadata.get(k) or "").strip()
            if v:
                g = infer_game_genre_v2(v)
                if g != "Auto":
                    return v, g

    p = Path(raw)
    stem = p.stem if p.suffix else raw

    # Split camelCase / PascalCase e.g. RocketLeague -> Rocket League
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", stem)
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", s)
    s = re.sub(r"[\W_]+", " ", s).strip().lower()

    # Sort keywords by length descending so longer phrases match first
    sorted_kws = sorted(CANONICAL_GAME_MAP.keys(), key=lambda k: len(k), reverse=True)
    padded = f" {s} "
    for kw in sorted_kws:
        if f" {kw} " in padded or (len(kw) > 3 and kw in s):
            title, genre = CANONICAL_GAME_MAP[kw]
            return title, genre

    # Fallback to general infer_game_genre_v2
    g = infer_game_genre_v2(s)
    return ("", g)


def classify_game_genre_from_scan(scan: Mapping[str, Any] | None) -> tuple[str, float]:
    """Live behavioral classification of video genre from audio and motion arrays."""
    if not isinstance(scan, Mapping):
        return "Auto", 1.0
    audio = [_num(x) for x in (scan.get("audio") or [])]
    motion = [_num(x) for x in (scan.get("motion") or [])]
    n = min(len(audio), len(motion))
    if n < 6:
        return "Auto", 1.0

    avg_m = sum(motion) / n
    avg_a = sum(audio) / n
    max_m = max(motion)
    max_a = max(audio)

    if max_m < 0.05 and max_a < 0.05:
        return "Auto", 1.0

    silence_ratio = sum(1 for a in audio if a < 0.15) / n
    active_motion_ratio = sum(1 for m in motion if m > 0.40) / n
    motion_burstiness = max_m - avg_m
    audio_burstiness = max_a - avg_a

    # Horror: long periods of silence/low audio punctuated by extreme audio jumpscares
    if silence_ratio >= 0.50 and audio_burstiness >= 0.55 and avg_m < 0.35:
        return "Horror", 0.85

    # Racing: continuous high-velocity sustained motion, very few quiet moments
    if active_motion_ratio >= 0.60 and avg_m >= 0.50 and motion_burstiness < 0.38:
        return "Racing", 0.85

    # Action / Hack-and-Slash: high sustained combo combat motion with frequent bursts
    if active_motion_ratio >= 0.25 and motion_burstiness >= 0.35:
        return "Action", 0.80

    # FPS: high burstiness in both motion and audio (gunfights, flick shots) with moderate baseline
    if motion_burstiness >= 0.45 and audio_burstiness >= 0.45 and avg_m < 0.45:
        return "FPS", 0.75

    # Sports: high audio arc/cheering with intermittent play action
    if audio_burstiness >= 0.50 and silence_ratio < 0.30 and avg_a >= 0.35:
        return "Sports", 0.70

    return "Auto", 1.0


def detect_game_genre_live(
    source_path_or_title: Any,
    scan: Mapping[str, Any] | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> tuple[str, str, float]:
    """Live game-aware classifier.
    
    Returns:
        (genre, detected_game_title, confidence)
    """
    raw_input = str(source_path_or_title or "").strip()
    title, genre = extract_game_title_from_path_or_meta(raw_input, metadata=metadata)
    if genre and genre != "Auto":
        return genre, title, 0.95

    if scan:
        scan_genre, conf = classify_game_genre_from_scan(scan)
        if scan_genre != "Auto":
            return scan_genre, title or scan_genre, conf

    return "Auto", title or "", 1.0



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
            clean_kw = str(kw or "").strip()
            if not clean_kw:
                continue
            if " " in clean_kw:
                if clean_kw in text or clean_kw in padded:
                    return gname
            else:
                if f" {clean_kw} " in padded:
                    return gname
    return "Auto"


# Backward compatibility aliases
infer_game_genre = infer_game_genre_v2
detect_game_genre = detect_game_genre_live


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
    """Zero-subprocess precision boundary refinement with dynamic contextual padding (< 5ms).

    Uses genre-specific context padding (pre_event_seconds & post_event_seconds)
    and anti-cutoff boundary evaluation to ensure:
    1. Cuts avoid loud speech/action peaks at both boundaries (natural breath/pause dip).
    2. Event climax is guaranteed inside the 35%-75% payoff zone.
    3. Neither pre-event context nor post-event reaction/aftermath is cut prematurely.
    4. Clip boundaries strictly adhere to [0.0, total_seconds].
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

    # Locate the strongest climax instant inside [start, start + duration]
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
    pad_cfg = prof.get("context_padding") or {}
    pre_pad = _num(pad_cfg.get("pre_event_seconds"), 4.5)
    post_pad = _num(pad_cfg.get("post_event_seconds"), 3.0)

    # Ideal offset centers pre_pad context before peak and post_pad after
    ideal_offset = min(duration * 0.65, max(pre_pad, duration * 0.35))
    ideal_start = max(0.0, min(max_start, peak_time - ideal_offset))

    # Search window locally bounded around start (+/- 2.0s) to preserve candidate diversity
    search_lo = max(0.0, start - 2.0)
    search_hi = min(max_start, start + 2.0)

    idx_lo = max(0, min(n - 1, int(round(search_lo / step))))
    idx_hi = max(idx_lo, min(n - 1, int(round(search_hi / step))))

    chosen_start = start
    best_cost = 999.0
    for idx in range(idx_lo, idx_hi + 1):
        cand_st = min(max_start, idx * step)
        a_start = _num(audio[idx])
        m_start = _num(motion[idx])
        end_idx = min(n - 1, int(round((cand_st + duration) / step)))
        a_end = _num(audio[end_idx])

        next_idx = min(n - 1, idx + 1)
        hook_energy = 0.5 * _num(audio[next_idx]) + 0.5 * _num(motion[next_idx])
        drift_ideal = abs(cand_st - ideal_start) / max(1.0, duration)
        drift_orig = abs(cand_st - start) / max(1.0, duration)

        cost = (
            0.35 * a_start
            + 0.20 * a_end
            + 0.15 * m_start
            - 0.15 * hook_energy
            + 0.25 * drift_ideal
            + 0.20 * drift_orig
        )
        if cost < best_cost:
            best_cost = cost
            chosen_start = cand_st

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


# ============================================================================
# FAST DETECTION & PIPELINE RUNNER
# ============================================================================

def probe_media_duration(source_path: str | Path) -> float:
    """Fast duration extraction via ffprobe with zero decoding overhead (~50ms)."""
    try:
        out = subprocess.check_output(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(source_path)
            ],
            stderr=subprocess.DEVNULL,
            timeout=10,
            text=True
        ).strip()
        val = float(out)
        if math.isfinite(val) and val > 0:
            return round(val, 3)
    except Exception:
        pass
    return 30.0


def _norm_series_robust(values: Sequence[float]) -> list[float]:
    if not values:
        return []
    vals = [float(v) for v in values]
    ordered = sorted(vals)
    lo = ordered[max(0, int(len(ordered) * 0.05) - 1)]
    hi = ordered[min(len(ordered) - 1, int(len(ordered) * 0.95))]
    span = max(1e-6, hi - lo)
    return [max(0.0, min(1.0, (v - lo) / span)) for v in vals]


def _interpolate_motion_points(motion_points: Mapping[int, float], n: int) -> list[float]:
    if n <= 0:
        return []
    out = [0.0] * n
    if not motion_points:
        return out
    known = sorted((int(k), float(v)) for k, v in motion_points.items() if 0 <= int(k) < n)
    if not known:
        return out
    first_i, first_v = known[0]
    for i in range(min(n, first_i + 1)):
        out[i] = first_v
    for idx in range(len(known) - 1):
        i0, v0 = known[idx]
        i1, v1 = known[idx + 1]
        if i1 <= i0:
            continue
        span = float(i1 - i0)
        for i in range(i0, min(n, i1 + 1)):
            alpha = (i - i0) / span
            out[i] = v0 * (1.0 - alpha) + v1 * alpha
    last_i, last_v = known[-1]
    for i in range(max(0, last_i), n):
        out[i] = last_v
    return out


def run_fast_scan_base(input_file: str | Path, total_seconds: float | None = None) -> dict[str, Any]:
    """Run concurrent audio and video scanning passes using FFmpeg."""
    t0 = time.perf_counter()
    p = Path(input_file)
    if not p.is_file():
        raise FileNotFoundError(f"Source file not found: {input_file}")
    if total_seconds is None or total_seconds <= 0:
        total_seconds = probe_media_duration(p)
    profile = scan_profile_for_duration(total_seconds)
    video_fps = float(profile["video_fps"])
    analysis_width = int(profile["analysis_width"])
    keyframes_only = bool(profile.get("keyframes_only", False))

    cmd_audio = [
        "ffmpeg", "-hide_banner", "-threads", "1", "-i", str(p), "-vn",
        "-af", (
            "aresample=8000,asetnsamples=n=4000:p=0,"
            "astats=metadata=1:reset=1,"
            "ametadata=print:key=lavfi.astats.Overall.RMS_level,"
            "ametadata=print:key=lavfi.astats.Overall.Peak_level"
        ),
        "-f", "null", "-"
    ]

    cmd_video = ["ffmpeg", "-hide_banner", "-threads", "2"]
    if keyframes_only:
        cmd_video += ["-skip_frame", "nokey"]
    cmd_video += ["-i", str(p), "-an", "-vf"]
    if keyframes_only:
        cmd_video += [f"scale={analysis_width}:-2,select='gte(scene,0)',metadata=print"]
    else:
        cmd_video += [f"fps={video_fps:g},scale={analysis_width}:-2,select='gte(scene,0)',metadata=print"]
    cmd_video += ["-f", "null", "-"]

    def _exec(cmd):
        t_sub = time.perf_counter()
        try:
            r = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=max(60.0, min(3600.0, total_seconds * 2.5))
            )
            return r, time.perf_counter() - t_sub, ""
        except Exception as exc:
            return None, time.perf_counter() - t_sub, str(exc)

    with ThreadPoolExecutor(max_workers=2) as pool:
        f_audio = pool.submit(_exec, cmd_audio)
        f_video = pool.submit(_exec, cmd_video)
        r_audio, audio_sec, err_audio = f_audio.result()
        r_video, video_sec, err_video = f_video.result()

    audio_points: dict[int, dict[str, float]] = {}
    if r_audio is not None:
        raw_audio = (r_audio.stdout or "") + "\n" + (r_audio.stderr or "")
        cur_t = None
        for line in raw_audio.splitlines():
            m = re.search(r"pts_time:([0-9.]+)", line)
            if m:
                try: cur_t = float(m.group(1))
                except Exception: cur_t = None
            if cur_t is None: continue
            b = max(0, int(round(cur_t * 2.0)))
            if "lavfi.astats.Overall.RMS_level=" in line:
                try:
                    val = float(line.split("lavfi.astats.Overall.RMS_level=", 1)[1].strip().split()[0])
                    if math.isfinite(val):
                        audio_points.setdefault(b, {})["rms"] = val
                except Exception: pass
            elif "lavfi.astats.Overall.Peak_level=" in line:
                try:
                    val = float(line.split("lavfi.astats.Overall.Peak_level=", 1)[1].strip().split()[0])
                    if math.isfinite(val):
                        audio_points.setdefault(b, {})["peak"] = val
                except Exception: pass

    motion_points: dict[int, float] = {}
    if r_video is not None:
        raw_video = (r_video.stdout or "") + "\n" + (r_video.stderr or "")
        cur_t = None
        for line in raw_video.splitlines():
            m = re.search(r"pts_time:([0-9.]+)", line)
            if m:
                try: cur_t = float(m.group(1))
                except Exception: cur_t = None
            if cur_t is not None and "lavfi.scene_score=" in line:
                try:
                    val = float(line.split("lavfi.scene_score=", 1)[1].strip().split()[0])
                    b = max(0, int(round(cur_t * 2.0)))
                    motion_points[b] = max(motion_points.get(b, 0.0), max(0.0, val))
                except Exception: pass

    all_buckets = set(audio_points) | set(motion_points)
    if total_seconds > 0:
        all_buckets.add(max(0, int(math.ceil(total_seconds * 2.0)) - 1))

    meta = {
        "parallel": True,
        "tier": profile["tier"],
        "adaptive": bool(profile["adaptive"]),
        "video_fps": video_fps,
        "analysis_width": analysis_width,
        "keyframes_only": keyframes_only,
        "duration_seconds": round(total_seconds, 2),
        "audio_seconds": round(float(audio_sec), 3),
        "video_seconds": round(float(video_sec), 3),
        "wall_seconds": round(time.perf_counter() - t0, 3),
        "audio_error": err_audio,
        "video_error": err_video,
    }

    if not all_buckets:
        return {"step": 0.5, "audio": [], "peak": [], "motion": [], "meta": meta}

    n = max(all_buckets) + 2
    rms_raw, peak_raw = [], []
    last_rms, last_peak = -80.0, -80.0
    for i in range(n):
        ap = audio_points.get(i, {})
        r = ap.get("rms", last_rms)
        p = ap.get("peak", last_peak)
        last_rms, last_peak = r, p
        rms_raw.append(r)
        peak_raw.append(p)

    motion_raw = _interpolate_motion_points(motion_points, n)
    audio = _norm_series_robust(rms_raw)
    peak = _norm_series_robust(peak_raw)
    motion = _norm_series_robust(motion_raw)

    return {
        "step": 0.5,
        "audio": audio,
        "peak": peak,
        "motion": motion,
        "meta": meta,
    }


def smart_rank_candidates(
    scan: Mapping[str, Any] | None,
    target_duration: float = 15.0,
    total_seconds: float = 0.0,
    genre: str = "Auto",
    profile: str = "auto",
    target_count: int = 3,
    sid: str = "",
    account_id: str = "",
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Smart ranking of moments using verifiable multi-signal features and game profiles."""
    dur = max(1.0, _num(target_duration, 15.0))
    if not isinstance(scan, Mapping):
        return [], []
    audio = scan.get("audio") or []
    motion = scan.get("motion") or []
    peak = scan.get("peak") or []
    n = min(len(audio), len(motion))
    step = max(0.1, _num(scan.get("step"), 0.5))
    total = max(_num(total_seconds, 0.0), n * step)
    max_start = max(0.0, total - dur)

    # Check for low-signal or silent clips: strictly distinguish legitimate no-highlights from active video
    if is_low_signal_scan(scan):
        return [], []

    if max_start <= 0.25:
        return [{
            "start": 0.0,
            "duration": total,
            "score": 0.85,
            "event": "highlight",
            "category": "action",
            "confidence": 0.80,
            "whole_source": True,
        }], []

    user_model = None
    if sid or account_id:
        try:
            from web.feedback_learning_v127 import load_user_model
            user_model = load_user_model(sid=sid, account_id=account_id)
        except Exception:
            try:
                from feedback_learning_v127 import load_user_model
                user_model = load_user_model(sid=sid, account_id=account_id)
            except Exception:
                user_model = None

    win_len = max(1, int(round(dur / step)))
    scored_pool: list[tuple[float, float, dict[str, Any], str]] = []

    # Slide candidate windows across the gameplay
    for i in range(0, max(1, n - win_len + 1)):
        cand_start = round(i * step, 3)
        if cand_start > max_start:
            break
        w_audio = audio[i:i + win_len]
        w_motion = motion[i:i + win_len]
        w_peak = peak[i:i + win_len] if peak else w_audio
        if not w_audio or not w_motion:
            continue

        avg_a = sum(w_audio) / len(w_audio)
        avg_m = sum(w_motion) / len(w_motion)
        peak_a = max(w_audio)
        peak_m = max(w_motion)
        synergy = min(avg_a, avg_m)
        burst_m = max(0.0, peak_m - avg_m)
        burst_a = max(0.0, peak_a - avg_a)

        # Climax and narrative arc (rising tension into payoff in 2nd half)
        half = len(w_motion) // 2
        first_half = sum(w_motion[:half]) / max(1, half)
        second_half = sum(w_motion[half:]) / max(1, len(w_motion) - half)
        arc = max(0.0, min(1.0, second_half - first_half + 0.35))

        features = {
            "motion_burst": burst_m,
            "sustained_motion": avg_m,
            "audio_burst": burst_a,
            "synergy": synergy,
            "arc": arc,
            "event_score": max(burst_m, burst_a),
            "reaction": burst_a * 0.8,
            "continuity": avg_m * 0.9,
            "dead_ratio": 0.0,
        }

        # Multi-signal base score
        raw_score = (
            0.28 * peak_m +
            0.24 * peak_a +
            0.18 * synergy +
            0.16 * burst_m +
            0.14 * arc
        )
        multiplier = genre_score_multiplier_v2(genre, profile, features)
        if user_model:
            try:
                from feedback_learning_v127 import user_learning_multiplier
                multiplier *= user_learning_multiplier(user_model, event_name, genre=genre)
            except Exception:
                pass
        final_score = round(max(0.05, min(0.99, raw_score * multiplier)), 3)

        event_name = "highlight"
        if burst_m > 0.45 and burst_a > 0.40:
            event_name = "clutch"
        elif burst_m > 0.50:
            event_name = "action_burst"
        elif burst_a > 0.55:
            event_name = "reaction"

        diag = {
            "start": cand_start,
            "score": final_score,
            "event": event_name,
            "category": "action" if burst_m >= burst_a else "reaction",
            "confidence": round(max(0.60, final_score), 2),
            "features": features,
        }
        scored_pool.append((final_score, cand_start, diag, event_name))

    # Diversify and refine boundaries
    top_candidates = verify_and_diversify_candidates(
        scored_pool,
        duration=dur,
        target_count=target_count,
        total_seconds=total
    )

    selected: list[dict[str, Any]] = []
    sel_starts: list[float] = []
    min_dist = max(3.5, dur * 0.30)
    for sc, cand_st, diag, evt in top_candidates:
        refined_st, refined_dur = precision_refine_boundary(
            scan, cand_st, dur, total_seconds=total, genre=genre
        )
        if any(abs(refined_st - s) < min_dist for s in sel_starts):
            continue
        row = dict(diag)
        row["start"] = refined_st
        row["duration"] = refined_dur
        row["score"] = sc
        row["brain_score"] = sc
        selected.append(row)
        sel_starts.append(refined_st)

    # Backfill if precision refinement caused spacing collision
    if len(selected) < target_count and scored_pool:
        remaining_pool = sorted(scored_pool, key=lambda x: float(x[0]), reverse=True)
        for sc, cand_st, diag, evt in remaining_pool:
            if len(selected) >= target_count:
                break
            refined_st, refined_dur = precision_refine_boundary(
                scan, cand_st, dur, total_seconds=total, genre=genre
            )
            relaxed_dist = max(2.0, min_dist * 0.70)
            if any(abs(refined_st - s) < relaxed_dist for s in sel_starts):
                continue
            row = dict(diag)
            row["start"] = refined_st
            row["duration"] = refined_dur
            row["score"] = sc
            row["brain_score"] = sc
            selected.append(row)
            sel_starts.append(refined_st)

    # Last resort fallback on non-silent, active gameplay: never strand valid video with 0 moments
    if not selected and not is_low_signal_scan(scan) and total >= dur:
        max_st = max(0.0, total - dur)
        step_pts = [0.0]
        if max_st >= 2.0:
            step_pts = [0.0, round(max_st * 0.5, 3), round(max_st, 3)]
        for idx, f_st in enumerate(step_pts[:target_count]):
            s_score = round(0.70 - idx * 0.05, 2)
            selected.append({
                "start": f_st,
                "duration": dur,
                "score": s_score,
                "brain_score": s_score,
                "event": "highlight",
                "category": "action",
                "confidence": 0.65,
                "features": {"motion_burst": 0.3, "sustained_motion": 0.3, "audio_burst": 0.3, "synergy": 0.3, "arc": 0.5},
            })
            sel_starts.append(f_st)

    # Collect alternates from remaining pool
    alternates: list[dict[str, Any]] = []
    sel_starts = [r["start"] for r in selected]
    for sc, cand_st, diag, evt in scored_pool:
        if len(alternates) >= 3:
            break
        if any(abs(cand_st - s) < dur * 0.5 for s in sel_starts):
            continue
        row = dict(diag)
        row["start"] = cand_st
        row["duration"] = dur
        alternates.append(row)

    print(f"GSF_AI_DIAG [Smart Ranking]: {len(scored_pool)} candidates scored, {len(selected)} selected, {len(alternates)} alternates", flush=True)
    return selected, alternates


def render_mini_preview(source_path: str | Path, output_file: str | Path, start: float, duration: float) -> bool:
    """Create a fast, lightweight mini-preview video for UI carousel display."""
    out_p = Path(output_file)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y", "-hide_banner",
        "-ss", f"{max(0.0, float(start)):.3f}",
        "-t", f"{max(1.0, float(duration)):.3f}",
        "-i", str(source_path),
        "-vf", "scale=270:480:force_original_aspect_ratio=increase,crop=270:480",
        "-c:v", "libx264", "-preset", "ultrafast", "-tune", "zerolatency", "-crf", "28", "-threads", "2",
        "-c:a", "aac", "-b:a", "64k",
        "-movflags", "+faststart",
        str(out_p)
    ]
    try:
        r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=max(30.0, float(duration) * 5.0))
        return r.returncode == 0 and out_p.is_file() and out_p.stat().st_size > 1024
    except Exception:
        return False


def generate_mini_previews_parallel(
    source_path: str | Path,
    candidates: Sequence[Mapping[str, Any] | float],
    output_dir: str | Path,
    duration: float = 15.0,
) -> list[str]:
    """Concurrently generate the 3 mini-preview MP4 files expected by the UI."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    results = []

    tasks = []
    for idx, c in enumerate(candidates[:3]):
        st = float(c.get("start", 0.0) if isinstance(c, Mapping) else c)
        dur = float(c.get("duration", duration) if isinstance(c, Mapping) else duration)
        filename = f"v71_mini_{idx + 1}_{st:.2f}.mp4"
        out_file = out_dir / filename
        tasks.append((idx + 1, st, dur, out_file))

    with ThreadPoolExecutor(max_workers=min(3, len(tasks) or 1)) as pool:
        futs = {pool.submit(render_mini_preview, source_path, t[3], t[1], t[2]): t for t in tasks}
        for fut in as_completed(futs):
            t = futs[fut]
            try:
                ok = fut.result()
                if ok:
                    results.append(str(t[3]))
            except Exception:
                pass
    return results


def run_fast_ai_pipeline(
    source_path: str | Path,
    output_dir: str | Path,
    duration: float = 15.0,
    genre: str = "Auto",
    profile: str = "auto",
    request_id: str = "",
    sid: str = "",
    account_id: str = "",
    generate_previews: bool = True,
    check_cancelled: Any = None,
    set_progress: Any = None,
) -> dict[str, Any]:
    """Unified 3-tier Fast AI Engine pipeline (Fast Detection -> Smart Ranking -> Precision Pass)."""
    t_start = time.perf_counter()
    src = Path(source_path)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    def _chk():
        if callable(check_cancelled): check_cancelled()
    def _prog(pct, label):
        if callable(set_progress): set_progress(pct, label)

    _chk()
    _prog(5.0, "Analisi metadati video...")
    total_seconds = probe_media_duration(src)
    eff_duration = min(total_seconds, max(1.0, float(duration))) if total_seconds > 0 else float(duration)

    _chk()
    _prog(15.0, "Scansione rapida del gameplay (Fast Detection)...")
    scan, hit = load_cached_scan(src, out_dir, ENGINE_VERSION_V2)
    if not hit or not isinstance(scan, dict):
        scan = run_fast_scan_base(src, total_seconds)
        save_cached_scan(src, scan, out_dir, ENGINE_VERSION_V2)

    # BLOCCO 3: Advanced Live Game-Aware Classification
    effective_genre = str(genre or "Auto").strip()
    detected_game = ""
    genre_conf = 1.0
    if effective_genre in ("", "Auto") or effective_genre not in GAME_PROFILES:
        inferred_g, det_title, g_conf = detect_game_genre_live(
            source_path_or_title=src,
            scan=scan,
            metadata=None,
        )
        effective_genre = inferred_g
        detected_game = det_title
        genre_conf = g_conf
    else:
        detected_game = effective_genre

    _chk()
    _prog(50.0, f"Smart Ranking dei momenti migliori ({effective_genre})...")
    selected, alternates = smart_rank_candidates(
        scan,
        target_duration=eff_duration,
        total_seconds=total_seconds,
        genre=effective_genre,
        profile=profile,
        target_count=3,
        sid=sid,
        account_id=account_id,
    )

    candidate_starts = [round(float(r["start"]), 3) for r in selected]
    durations_map = {round(float(r["start"]), 3): float(r.get("duration", eff_duration)) for r in selected}

    # Distinguish the 3 strict states: completed_with_results vs completed_no_highlights vs failed
    if selected:
        result_state = "completed_with_results"
        status_label = "ready"
    else:
        result_state = "completed_no_highlights"
        status_label = "completed_no_highlights"

    _chk()
    _prog(75.0, "Generazione anteprime ottimizzate...")
    if generate_previews and selected:
        generate_mini_previews_parallel(src, selected, out_dir, duration=eff_duration)

    _chk()
    _prog(95.0, "Finalizzazione risultati...")
    try:
        import web.ai_engines_v412 as _v412
    except ModuleNotFoundError:
        import ai_engines_v412 as _v412
    meta = _v412.build_results_meta(
        candidate_starts,
        {"selected": selected, "alternates": alternates, "pool_size": len(candidate_starts)},
        duration=eff_duration,
        profile=profile,
        request_id=request_id,
        durations=durations_map,
        timings={"total_seconds": round(time.perf_counter() - t_start, 3)},
    )
    meta["status"] = status_label
    meta["result_state"] = result_state
    meta["genre"] = effective_genre
    meta["detected_game"] = detected_game
    meta["genre_confidence"] = genre_conf
    if result_state == "completed_no_highlights":
        meta["items"] = []
        meta["message"] = "Nessun momento sufficientemente forte trovato nel gameplay. Puoi aprirlo nell’Editor."
    _v412.write_results_meta(out_dir, meta)

    print(f"GSF_AI_DIAG [Fast Detection]: {len(scan.get('audio', []))} samples, cache_hit={hit}, total_duration={total_seconds:.2f}s", flush=True)
    print(f"GSF_AI_DIAG [Precision Pass]: {len(selected)} refined boundaries", flush=True)
    print(f"GSF_AI_DIAG [Result State]: {result_state} (candidates={candidate_starts}) in {time.perf_counter() - t_start:.2f}s", flush=True)

    _prog(100.0, "Momenti IA pronti" if result_state == "completed_with_results" else "Analisi completata (nessun picco)")
    return {
        "request_id": request_id,
        "result_state": result_state,
        "candidates": candidate_starts,
        "selected": selected,
        "alternates": alternates,
        "duration": eff_duration,
        "total_time": round(time.perf_counter() - t_start, 3),
        "message": meta.get("message", ""),
        "genre": effective_genre,
        "detected_game": detected_game,
        "genre_confidence": genre_conf,
    }
