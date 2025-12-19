import json
import requests
from pathlib import Path
from datetime import datetime

from rich.text import Text
from rich.table import Table
from rich.console import Group

from devopsmind.cli import frame
from devopsmind.constants import DATA_DIR, VERSION
from devopsmind.progress import load_state, save_state
from devopsmind.update_check import check_for_update


# -------------------------------------------------
# Optional YAML support (NO hard dependency)
# -------------------------------------------------

try:
    import yaml
except Exception:
    yaml = None


# -------------------------------------------------
# Sources
# -------------------------------------------------

GITHUB_LEADERBOARD_URL = (
    "https://raw.githubusercontent.com/"
    "InfraForgeLabs/DevOpsMind/leaderboard/leaderboard/leaderboard.json"
)

CACHE_PATH = DATA_DIR / "leaderboard.json"
LOCAL_LEADERBOARD = Path.cwd() / "leaderboard" / "leaderboard.json"

SNAPSHOT_PATH = Path.home() / ".devopsmind" / "snapshot.json"

# 🔥 ADDITIVE: Cloudflare Worker snapshot relay
SNAPSHOT_RELAY_URL = "https://devopsmind-relay.gauravchile05.workers.dev/snapshot"


# -------------------------------------------------
# Helpers
# -------------------------------------------------

def _now():
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _load_json(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def _save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def _fetch_github():
    r = requests.get(GITHUB_LEADERBOARD_URL, timeout=10)
    r.raise_for_status()
    return r.json()


# -------------------------------------------------
# 🔥 ADDITIVE: fetch snapshot from Worker
# -------------------------------------------------

def _fetch_snapshot_from_worker(user_id: str):
    try:
        r = requests.get(f"{SNAPSHOT_RELAY_URL}/{user_id}", timeout=10)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None


# -------------------------------------------------
# 🔥 ADDITIVE: snapshot restore (SAFE)
# -------------------------------------------------

def _restore_from_snapshot(state):
    if not SNAPSHOT_PATH.exists():
        return state

    try:
        raw = SNAPSHOT_PATH.read_text()
        snapshot = yaml.safe_load(raw) if yaml else json.loads(raw)
    except Exception:
        return state

    if snapshot.get("user_id") != state.get("identity"):
        return state

    snapshot_xp = int(snapshot.get("xp", 0))
    local_xp = int(state.get("xp", 0))

    if snapshot_xp <= local_xp:
        return state

    state["xp"] = snapshot_xp
    state.setdefault("progress", {})
    state["progress"]["completed"] = snapshot.get(
        "completed_challenges", []
    )

    state.setdefault("profile", {})
    state["profile"]["rank"] = snapshot.get("rank", "Beginner")
    state["last_synced"] = snapshot.get("updated_at")

    save_state(state)
    return state


# -------------------------------------------------
# Deterministic merge helper
# -------------------------------------------------

def _is_remote_authoritative(local_xp, local_ts, remote_xp, remote_ts):
    if remote_xp > local_xp:
        return True
    if remote_xp == local_xp and remote_ts and local_ts:
        return remote_ts > local_ts
    return False


# -------------------------------------------------
# Public API (MUST always return renderable)
# -------------------------------------------------

def sync_default(local: bool = False):
    """
    devopsmind sync
    devopsmind sync --local
    """

    # ------------------------------
    # Load state
    # ------------------------------
    state = load_state()

    # ------------------------------
    # 🔥 ADDITIVE: fetch snapshot from Worker (cross-machine)
    # ------------------------------
    user_id = state.get("identity")
    if user_id:
        remote_snapshot = _fetch_snapshot_from_worker(user_id)
        if remote_snapshot:
            SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
            SNAPSHOT_PATH.write_text(
                json.dumps(remote_snapshot, indent=2)
            )

    # ------------------------------
    # Restore from snapshot (local or fetched)
    # ------------------------------
    state = _restore_from_snapshot(state)

    state.setdefault("progress", {})
    state["progress"].setdefault("completed", [])
    state.setdefault("last_synced", None)

    profile = state.get("profile", {})
    local_xp = int(state.get("xp", 0))
    local_rank = profile.get("rank", "Beginner")
    local_ts = state.get("last_synced")

    leaderboard = None
    source = None

    # ------------------------------
    # Leaderboard source selection
    # ------------------------------
    if local:
        leaderboard = _load_json(LOCAL_LEADERBOARD)
        if leaderboard:
            source = "local"

    if leaderboard is None:
        try:
            leaderboard = _fetch_github()
            _save_json(CACHE_PATH, leaderboard)
            source = "github"
        except Exception:
            leaderboard = None

    if leaderboard is None:
        leaderboard = _load_json(CACHE_PATH)
        source = "cache"

    if not leaderboard:
        return frame(
            "🔄 Sync",
            Text(
                "❌ Unable to reach GitHub and no cached data available.",
                style="red",
            ),
        )

    # ------------------------------
    # Remote player match
    # ------------------------------
    email_hash = profile.get("email_hash")
    remote = None

    for p in leaderboard.get("players", []):
        if p.get("email_hash") == email_hash:
            remote = p
            break

    # ------------------------------
    # Merge if remote authoritative
    # ------------------------------
    if remote:
        remote_xp = int(remote.get("xp", 0))
        remote_rank = remote.get("rank", local_rank)
        remote_ts = remote.get("timestamp")

        if _is_remote_authoritative(
            local_xp, local_ts, remote_xp, remote_ts
        ):
            state["xp"] = remote_xp
            state.setdefault("profile", {})
            state["profile"]["rank"] = remote_rank
            state["last_synced"] = remote_ts
            save_state(state)

            local_xp = remote_xp
            local_rank = remote_rank

    # ------------------------------
    # Render
    # ------------------------------
    table = Table(show_header=True, header_style="bold")
    table.add_column("Source")
    table.add_column("XP", justify="right")
    table.add_column("Rank")

    table.add_row("Local", str(local_xp), local_rank)

    if remote:
        table.add_row(
            source.capitalize(),
            str(remote.get("xp", "—")),
            remote.get("rank", "—"),
        )
    else:
        table.add_row(source.capitalize(), "—", "—")

    notes = []

    if source == "local":
        notes.append(
            Text("🧪 Using local leaderboard (developer mode).", style="cyan")
        )
    elif source == "github":
        notes.append(Text("✔ Synced from GitHub.", style="green"))
    else:
        notes.append(Text("⚠ Offline mode. Using cached data.", style="yellow"))

    # ------------------------------
    # Update check
    # ------------------------------
    update_available, latest, release_notes = check_for_update()

    if update_available:
        notes.append(
            Text(
                f"⬆ New version available: {latest}\n"
                f"Run `pipx upgrade devopsmind` to get new challenges.",
                style="cyan",
            )
        )
        if release_notes:
            notes.append(Text(f"📝 {release_notes}", style="dim"))

    # ------------------------------
    # Always return renderable
    # ------------------------------
    return frame("🔄 Sync", Group(table, *notes))
