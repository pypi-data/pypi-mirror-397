import argparse
import sys
import json
from rich.console import Console, Group
from rich.text import Text
from rich.columns import Columns
from rich.panel import Panel
from . import __version__

from .cli import frame, prompt_new_profile
from .engine import play, validate_only, stats
from .list import list_challenges, search_challenges
from .profiles import (
    show_profile,
    create_profile,
    login_profile,
    get_active_username,
    list_profiles,          # ➕ ADDED
)
from .hint import show_hint
from .describe import describe_challenge
from .doctor import run_doctor
from .badges import show_badges
from .leaderboard import show_leaderboards
from .sync import sync_default
from .submit import submit_pending
from .progress import load_state
from .constants import XP_LEVELS, DATA_DIR

console = Console()

UPDATE_STATUS_FILE = DATA_DIR / "update_status.json"


# -------------------------------------------------
# Helpers
# -------------------------------------------------

def compute_rank(xp: int) -> str:
    rank = XP_LEVELS[0][1]
    for threshold, name in XP_LEVELS:
        if xp >= threshold:
            rank = name
    return rank


def profile_bar():
    state = load_state()
    profile = state.get("profile", {})
    xp = state.get("xp", 0)

    return Columns(
        [
            Text(f"🎮 {profile.get('gamer', '—')}", style="bold"),
            Text(f"👤 {profile.get('username', '—')}", style="dim"),
            Text(f"🏅 {compute_rank(xp)}", style="yellow"),
            Text(f"🧠 XP {xp}", style="green"),
        ],
        expand=True,
    )


def update_banner():
    if not UPDATE_STATUS_FILE.exists():
        return None

    try:
        data = json.loads(UPDATE_STATUS_FILE.read_text())
    except Exception:
        return None

    lines = []

    if data.get("new_version"):
        lines.append(f"⬆️ New DevOpsMind version available: {data['new_version']}")

    if data.get("new_challenges"):
        lines.append("🧩 New challenges available")

    if not lines:
        return None

    lines.append("\nRun:\n  pipx upgrade devopsmind")

    return Panel(
        "\n".join(lines),
        title="🆕 Updates Available",
        border_style="yellow",
    )


def render(title, body):
    items = [profile_bar(), Text("")]

    banner = update_banner()
    if banner:
        items.extend([banner, Text("")])

    items.append(body)
    return frame(title, Group(*items))


def cancelled():
    console.print(
        Panel(Text("❌ Command cancelled.", style="red"), border_style="red")
    )
    sys.exit(0)


# -------------------------------------------------
# Main
# -------------------------------------------------

def main():
    try:
        if not get_active_username():
            console.print(
                frame(
                    "🧠 Welcome to DevOpsMind!",
                    "Let's create your player profile (one-time setup).",
                )
            )

            username, gamer, email = prompt_new_profile()

            console.print(
                frame(
                    f"➕ Profile · Create · {username}",
                    create_profile(username, gamer, email),
                )
            )

            # -------------------------------------------------
            # 🔥 ADDITIVE FIX: Snapshot auto-restore hook
            # -------------------------------------------------
            try:
                sync_default()
            except Exception:
                pass

            console.print(render("🔄 Initial Sync", sync_default()))

        parser = argparse.ArgumentParser(prog="devopsmind")
        parser.add_argument("--stack", help="Filter challenges by stack")

        # -----------------------------
        # --version flag (ADDED)
        # -----------------------------
        parser.add_argument(
            "--version",
            action="store_true",
            help="Show DevOpsMind version",
        )

        sub = parser.add_subparsers(dest="cmd")

        # -----------------------------
        # version command (ADDED)
        # -----------------------------
        sub.add_parser("version")

        for c in [
            "list", "stats", "leaderboard", "doctor",
            "badges", "submit"
        ]:
            sub.add_parser(c)

        # -----------------------------
        # sync (WITH --local)
        # -----------------------------
        p_sync = sub.add_parser("sync")
        p_sync.add_argument(
            "--local",
            action="store_true",
            help="Use local leaderboard (developer mode)",
        )

        p_play = sub.add_parser("play")
        p_play.add_argument("id")

        p_val = sub.add_parser("validate")
        p_val.add_argument("id")

        p_desc = sub.add_parser("describe")
        p_desc.add_argument("id")

        p_hint = sub.add_parser("hint")
        p_hint.add_argument("id")

        p_search = sub.add_parser("search")
        p_search.add_argument("term")

        # -----------------------------
        # profile (UPDATED)
        # -----------------------------
        p_profile = sub.add_parser("profile")
        profile_sub = p_profile.add_subparsers(dest="action", required=True)
        profile_sub.add_parser("show")
        profile_sub.add_parser("create")
        profile_sub.add_parser("login")
        profile_sub.add_parser("list")   # ➕ ADDED

        args = parser.parse_args()

        # -----------------------------
        # version handling (FIRST)
        # -----------------------------
        if args.version or args.cmd == "version":
            console.print(f"DevOpsMind v{__version__}")
            return

        if args.cmd == "play":
            console.print(render(f"🎮 Play · {args.id}", play(args.id)))
            return

        if args.cmd == "validate":
            console.print(render(f"🧪 Validate · {args.id}", validate_only(args.id)))
            return

        if args.cmd == "describe":
            console.print(render(f"📖 Describe · {args.id}", describe_challenge(args.id)))
            return

        if args.cmd == "hint":
            console.print(render(f"💡 Hint · {args.id}", show_hint(args.id)))
            return

        if args.cmd == "search":
            console.print(render("🔍 Search", search_challenges(args.term)))
            return

        if args.cmd == "stats":
            console.print(render("📊 Stats", stats()))
            return

        if args.cmd == "leaderboard":
            console.print(render("🏆 Leaderboard", show_leaderboards()))
            return

        if args.cmd == "doctor":
            console.print(render("🩺 Doctor", run_doctor()))
            return

        if args.cmd == "badges":
            console.print(render("🏅 Badges", show_badges()))
            return

        if args.cmd == "sync":
            console.print(render("🔄 Sync", sync_default(local=args.local)))
            return

        if args.cmd == "submit":
            console.print(render("📤 Submit", submit_pending()))
            return

        if args.cmd == "profile":
            if args.action == "show":
                console.print(render("👤 Profile", show_profile()))
            elif args.action == "create":
                username, gamer, email = prompt_new_profile()
                console.print(
                    render(
                        f"➕ Profile · Create · {username}",
                        create_profile(username, gamer, email),
                    )
                )
            elif args.action == "login":
                username = console.input("Username to login: ")
                console.print(
                    render(
                        f"🔐 Profile · Login · {username}",
                        login_profile(username),
                    )
                )
            elif args.action == "list":
                console.print(render("👤 Profiles", list_profiles()))
            return

        console.print(
            render(
                "📋 Available Stacks",
                list_challenges(stack=args.stack),
            )
        )

    except KeyboardInterrupt:
        cancelled()


if __name__ == "__main__":
    main()
