from typing import Optional
from pathlib import Path

from .play import play as _play
from .validator import validate_only as _validate_only
from .stats import stats as _stats

WORKSPACE_DIR = Path.home() / "workspace"


def play(challenge_id: Optional[str] = None):
    return _play(challenge_id)


def validate_only(challenge_id: Optional[str] = None):
    if not challenge_id:
        return "❌ Please provide a challenge id."

    workspace = WORKSPACE_DIR / challenge_id
    if not workspace.exists():
        return "❌ Workspace not found. Run `devopsmind play <challenge>` first."

    return _validate_only(challenge_id, workspace)


def stats():
    data = _stats()
    return (
        f"👤 {data.get('username')} ({data.get('gamer')})\n"
        f"🧠 XP: {data.get('xp')}\n"
        f"🏅 Rank: {data.get('profile', {}).get('rank')}\n"
        f"✅ Completed: {len(data.get('progress', {}).get('completed', []))}"
    )


__all__ = ["play", "validate_only", "stats"]
