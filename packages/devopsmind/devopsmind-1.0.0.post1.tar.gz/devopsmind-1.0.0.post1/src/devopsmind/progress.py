import json
from pathlib import Path

from .constants import DATA_DIR

STATE_FILE = DATA_DIR / "state.json"


def load_state():
    if not STATE_FILE.exists():
        return {
            "username": None,
            "gamer": None,
            "identity": None,
            "xp": 0,
            "badges": [],
            "achievements_unlocked": [],
            "progress": {
                "completed": [],
                "by_stack": {},
                "by_difficulty": {},
            },
            "attempts": {},
        }

    state = json.loads(STATE_FILE.read_text())

    # ---- Backward compatibility ----
    state.setdefault("badges", [])
    state.setdefault("achievements_unlocked", [])

    progress = state.setdefault("progress", {})
    progress.setdefault("completed", [])
    progress.setdefault("by_stack", {})
    progress.setdefault("by_difficulty", {})

    return state


def save_state(state):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def record_completion(challenge_id, xp, stack=None, difficulty=None):
    state = load_state()

    progress = state["progress"]

    if challenge_id in progress["completed"]:
        return state

    progress["completed"].append(challenge_id)
    state["xp"] += xp

    if stack:
        progress["by_stack"][stack] = progress["by_stack"].get(stack, 0) + 1

    if difficulty:
        progress["by_difficulty"][difficulty] = (
            progress["by_difficulty"].get(difficulty, 0) + 1
        )

    save_state(state)
    return state
