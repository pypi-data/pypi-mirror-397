import hashlib
import requests

from rich.panel import Panel
from rich.text import Text

from .progress import load_state, save_state


IDENTITY_ENDPOINT = "https://devopsmind-relay.gauravchile05.workers.dev/identity/resolve"


# -------------------------------------------------
# Helpers
# -------------------------------------------------

def _hash_email(email: str) -> str:
    return hashlib.sha256(email.encode()).hexdigest()


def _resolve_user_id(email_hash: str) -> str:
    """
    Resolve global user_id via worker.
    Falls back to local_* if offline.
    """
    try:
        r = requests.post(
            IDENTITY_ENDPOINT,
            json={"email_hash": email_hash},
            timeout=5,
        )
        r.raise_for_status()
        return r.json()["user_id"]
    except Exception:
        return f"local_{email_hash[:12]}"


# -------------------------------------------------
# PUBLIC API
# -------------------------------------------------

def create_profile(username: str, gamer: str, email: str):
    state = load_state()

    email_hash = _hash_email(email)
    user_id = _resolve_user_id(email_hash)

    profile = {
        "username": username,
        "gamer": gamer,
        "email_hash": email_hash,
        "user_id": user_id,
        "rank": "Beginner",
    }

    state.setdefault("profiles", {})
    state["profiles"][username] = profile
    state["profile"] = profile

    # ✅ Update top-level fields for submit_pending()
    state["username"] = username
    state["gamer"] = gamer
    state["identity"] = user_id

    save_state(state)

    return Panel(
        Text("✅ Profile created successfully.", style="green"),
        border_style="green",
    )


def show_profile():
    state = load_state()
    profile = state.get("profile")

    if not profile:
        return Panel(
            Text("⚠️ No active profile.", style="yellow"),
            border_style="yellow",
        )

    body = (
        f"Username: {profile['username']}\n"
        f"Gamer: {profile['gamer']}\n"
        f"Rank: {profile.get('rank', 'Beginner')}\n"
        f"User ID: {profile['user_id']}"
    )

    return Panel(
        Text(body),
        title="👤 Profile",
        border_style="blue",
    )


def list_profiles():
    state = load_state()
    profiles = state.get("profiles", {})

    if not profiles:
        return Panel(
            Text("⚠️ No profiles found.", style="yellow"),
            border_style="yellow",
        )

    body = "\n".join(
        f"- {p['username']} ({p['gamer']})"
        for p in profiles.values()
    )

    return Panel(
        Text(body),
        title="📂 Profiles",
        border_style="blue",
    )


def login_profile(username: str):
    state = load_state()
    profiles = state.get("profiles", {})

    if username not in profiles:
        return Panel(
            Text(f"❌ Profile '{username}' not found.", style="red"),
            border_style="red",
        )

    profile = profiles[username]
    state["profile"] = profile

    # ✅ Update top-level fields for submit_pending()
    state["username"] = profile["username"]
    state["gamer"] = profile["gamer"]
    state["identity"] = profile["user_id"]

    save_state(state)

    return Panel(
        Text(f"🔐 Logged in as {username}.", style="green"),
        border_style="green",
    )


def get_active_username():
    """
    REQUIRED by __main__.py
    Returns the currently active username or None.
    """
    state = load_state()
    profile = state.get("profile")
    if not profile:
        return None
    return profile.get("username")
