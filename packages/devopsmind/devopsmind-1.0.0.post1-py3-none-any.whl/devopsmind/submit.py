import yaml
import requests
from pathlib import Path
from datetime import datetime

from .progress import load_state, save_state
from .snapshot import build_snapshot, sign_snapshot

SYNC_DIR = Path.home() / ".devopsmind" / "pending_sync"
SNAPSHOT_PATH = Path.home() / ".devopsmind" / "snapshot.json"

RELAY_URL = "https://devopsmind-relay.gauravchile05.workers.dev"
SNAPSHOT_ENDPOINT = f"{RELAY_URL}/snapshot"
TIMEOUT = 10


# -------------------------------------------------
# 🔥 ADDITIVE: auto snapshot push
# -------------------------------------------------
def _push_snapshot_to_worker(snapshot: dict):
    try:
        requests.post(
            SNAPSHOT_ENDPOINT,
            data=yaml.safe_dump(snapshot, sort_keys=False),
            headers={"Content-Type": "text/yaml"},
            timeout=TIMEOUT,
        )
    except Exception:
        # Snapshot sync must never block validation
        pass


def record_pending_sync():
    """
    Create pending YAML if there is UNSYNCED progress.
    This MUST be called during VALIDATE.

    ADDITIVE:
    - Snapshot generation
    - Signed canonical state
    - 🔥 Automatic snapshot upload
    """

    state = load_state() or {}

    synced_completed = set(state.get("synced_completed", []) or [])
    synced_achievements = set(state.get("synced_achievements", []) or [])

    progress = state.get("progress", {}) or {}
    completed = set(progress.get("completed", []) or [])

    challenge_achievements = set(state.get("achievements_unlocked", []) or [])

    profile = state.get("profile", {}) or {}
    profile_achievements = set(profile.get("achievements", []) or [])

    achievements = challenge_achievements | profile_achievements

    new_completed = sorted(completed - synced_completed)
    new_achievements = sorted(achievements - synced_achievements)

    # -------------------------------------------------
    # 🔥 ALWAYS build & push snapshot
    # -------------------------------------------------
    snapshot = build_snapshot()
    email_hash = profile.get("email_hash")

    if email_hash:
        signed = sign_snapshot(snapshot, email_hash)
        SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
        SNAPSHOT_PATH.write_text(
            yaml.safe_dump(signed, sort_keys=False)
        )

        # 🔥 AUTO PUSH SNAPSHOT TO WORKER
        _push_snapshot_to_worker(signed)

    # -------------------------------------------------
    # No delta → snapshot already synced, exit
    # -------------------------------------------------
    if not new_completed and not new_achievements:
        return False

    payload = {
        "user_id": state.get("identity"),
        "username": state.get("username"),
        "gamer": state.get("gamer"),
        "xp": int(state.get("xp", 0) or 0),
        "rank": profile.get("rank", "Beginner"),
        "completed": list(new_completed),
        "badges": list(new_achievements),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "status": "pending",
        "schema": "v1",
    }

    ts = datetime.utcnow().strftime("%Y-%m-%dT%H%M%S")
    fname = f"{payload['username']}_{payload['user_id']}_{ts}.yaml"
    payload["filename"] = fname

    SYNC_DIR.mkdir(parents=True, exist_ok=True)
    (SYNC_DIR / fname).write_text(yaml.safe_dump(payload, sort_keys=False))

    pending_completed = set(state.get("pending_completed", []) or [])
    pending_achievements = set(state.get("pending_achievements", []) or [])

    pending_completed.update(new_completed)
    pending_achievements.update(new_achievements)

    state["pending_completed"] = sorted(pending_completed)
    state["pending_achievements"] = sorted(pending_achievements)

    save_state(state)

    return True


def submit_pending():
    """
    Reliable queue-based YAML sync.
    """

    pending_files = sorted(SYNC_DIR.glob("*.yaml"))

    if not pending_files:
        return "📦 No pending sync files."

    path = pending_files[0]
    payload_text = path.read_text()

    try:
        response = requests.post(
            RELAY_URL,
            data=payload_text,
            headers={"Content-Type": "text/yaml"},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
    except Exception as e:
        return f"❌ Sync failed for {path.name}: {e}"

    try:
        data = yaml.safe_load(payload_text) or {}
    except Exception:
        return f"❌ Failed to parse local YAML: {path.name}"

    state = load_state() or {}

    synced_completed = set(state.get("synced_completed", []) or [])
    synced_achievements = set(state.get("synced_achievements", []) or [])

    pending_completed = set(state.get("pending_completed", []) or [])
    pending_achievements = set(state.get("pending_achievements", []) or [])

    completed_now = set(data.get("completed", []) or [])
    achievements_now = set(data.get("badges", []) or [])

    synced_completed.update(completed_now)
    synced_achievements.update(achievements_now)

    pending_completed.difference_update(completed_now)
    pending_achievements.difference_update(achievements_now)

    state["synced_completed"] = sorted(synced_completed)
    state["synced_achievements"] = sorted(synced_achievements)
    state["pending_completed"] = sorted(pending_completed)
    state["pending_achievements"] = sorted(pending_achievements)

    save_state(state)
    path.unlink()

    return f"✅ Synced: {path.name}"
