import hashlib
import json
from datetime import datetime

from .progress import load_state

SNAPSHOT_SCHEMA = "v3.0"

# -------------------------------------------------
# 🏆 AUTHORITATIVE XP → RANK LADDER (ADDITIVE)
# -------------------------------------------------
XP_LEVELS = [
    (0, "Beginner"),
    (1000, "Apprentice"),
    (5000, "Operator"),
    (10000, "Engineer"),
    (20000, "Specialist"),
    (35000, "Advanced"),
    (55000, "Expert"),
    (80000, "Master"),
    (120000, "Architect"),
    (180000, "Grandmaster"),
    (260000, "Legend"),
    (370000, "Mythic"),
    (520000, "Eternal"),
    (750000, "Ascendant"),
    (1_000_000, "Vanguard"),
    (1_500_000, "Paragon"),
    (2_000_000, "Virtuoso"),
    (3_000_000, "Transcendent"),
    (5_000_000, "Celestial"),
    (10_000_000, "Infinite"),
]


def rank_from_xp(xp: int) -> str:
    """
    Derive rank from XP (authoritative).

    XP is the single source of truth.
    """
    current = "Beginner"
    for threshold, name in XP_LEVELS:
        if xp >= threshold:
            current = name
        else:
            break
    return current


def sign_snapshot(snapshot: dict, email_hash: str) -> dict:
    """
    Sign snapshot using email hash for integrity.

    This function MUST exist because submit.py imports it.
    """

    payload = json.dumps(snapshot, sort_keys=True).encode()
    signature = hashlib.sha256(payload + email_hash.encode()).hexdigest()

    signed = dict(snapshot)
    signed["signature"] = signature
    return signed


def build_snapshot():
    """
    Build canonical snapshot of user state.

    ADDITIVE:
    - Include badges / achievements
    """

    state = load_state() or {}
    profile = state.get("profile", {}) or {}

    progress = state.get("progress", {}) or {}
    completed = progress.get("completed", []) or []

    # -------------------------------------------------
    # 🔥 ADDITIVE: collect badges
    # -------------------------------------------------
    global_badges = state.get("achievements_unlocked", []) or []
    profile_badges = profile.get("achievements", []) or []

    badges = sorted(set(global_badges) | set(profile_badges))

    xp = int(state.get("xp", 0) or 0)

    snapshot = {
        "schema": SNAPSHOT_SCHEMA,
        "user_id": state.get("identity"),
        "username": state.get("username"),
        "handle": state.get("gamer"),
        "xp": xp,
        # -------------------------------------------------
        # 🔒 DERIVED: rank always computed from XP
        # -------------------------------------------------
        "rank": rank_from_xp(xp),
        "completed_challenges": list(completed),
        "badges": badges,
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "device_id": state.get("device_id"),
    }

    return snapshot
