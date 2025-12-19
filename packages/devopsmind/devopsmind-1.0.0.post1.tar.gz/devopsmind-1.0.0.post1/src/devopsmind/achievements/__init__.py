from pathlib import Path
import yaml

from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from rich.console import Group

from devopsmind.progress import load_state, save_state

ACHIEVEMENTS_DIR = Path(__file__).resolve().parent


def _bell():
    print("\a", end="", flush=True)


def _load_achievements():
    achievements = []
    for file in sorted(ACHIEVEMENTS_DIR.glob("*.yaml")):
        data = yaml.safe_load(file.read_text()) or []
        if isinstance(data, list):
            achievements.extend(data)
    return achievements


def _rarity(ach):
    cond = ach.get("condition", {})
    if "special" in cond:
        return "Legendary"
    if "difficulty_completed_gte" in cond:
        diff = next(iter(cond["difficulty_completed_gte"].keys()))
        if diff in {
            "expert", "architect", "principal", "staff", "distinguished", "fellow"
        }:
            return "Legendary"
        return "Rare"
    if "stack_completed_gte" in cond:
        return "Rare"
    if "xp_gte" in cond and cond["xp_gte"] >= 5000:
        return "Rare"
    return "Common"


def _evaluate(condition, state):
    progress = state.get("progress", {})
    special = state.get("special", {})

    if "completed_gte" in condition:
        return len(progress.get("completed", [])) >= condition["completed_gte"]
    if "xp_gte" in condition:
        return state.get("xp", 0) >= condition["xp_gte"]
    if "difficulty_completed_gte" in condition:
        k, v = next(iter(condition["difficulty_completed_gte"].items()))
        return progress.get("by_difficulty", {}).get(k, 0) >= v
    if "stack_completed_gte" in condition:
        k, v = next(iter(condition["stack_completed_gte"].items()))
        return progress.get("by_stack", {}).get(k, 0) >= v
    if "special" in condition:
        return special.get(condition["special"], False)
    return False


def _progress(condition, state):
    progress = state.get("progress", {})
    if "completed_gte" in condition:
        return len(progress.get("completed", [])), condition["completed_gte"]
    if "xp_gte" in condition:
        return state.get("xp", 0), condition["xp_gte"]
    if "difficulty_completed_gte" in condition:
        k, v = next(iter(condition["difficulty_completed_gte"].items()))
        return progress.get("by_difficulty", {}).get(k, 0), v
    if "stack_completed_gte" in condition:
        k, v = next(iter(condition["stack_completed_gte"].items()))
        return progress.get("by_stack", {}).get(k, 0), v
    return 0, 0


def show_badges():
    state = load_state()
    achievements = _load_achievements()

    unlocked_before = set(state.get("achievements_unlocked", []))
    unlocked_now = set(unlocked_before)
    newly_unlocked = []

    table = Table(title="🏅 Achievements", show_header=True)
    table.add_column("Icon")
    table.add_column("Name")
    table.add_column("Rarity")
    table.add_column("Progress")
    table.add_column("Status")

    for ach in achievements:
        ach_id = ach["id"]
        hidden = ach.get("hidden", False)
        earned = _evaluate(ach["condition"], state)

        if hidden and not earned:
            continue

        if earned and ach_id not in unlocked_before:
            newly_unlocked.append(ach)
            unlocked_now.add(ach_id)

        cur, tgt = _progress(ach["condition"], state)

        rarity = _rarity(ach)
        rarity_style = {
            "Common": "dim",
            "Rare": "cyan",
            "Legendary": "bold yellow",
        }[rarity]

        # Only the table rows (optional)
        table.add_row(
            ach.get("icon", "🏅"),
            Text(ach["name"], style="bold" if earned else ""),
            Text(rarity, style=rarity_style),
            f"{cur}/{tgt}" if tgt else "",
            "✅" if earned else "❌",
        )

    # Persist updated unlocked achievements
    state["achievements_unlocked"] = sorted(unlocked_now)
    save_state(state)

    # Only show the banner for newly unlocked achievements
    if newly_unlocked:
        _bell()
        banner = Panel.fit(
            "\n".join(f"{a['icon']} {a['name']}" for a in newly_unlocked),
            title="🎉 Achievement Unlocked!",
            border_style="yellow",
        )
        return banner  # ✅ Only newly earned

    return None  # No banner if nothing new
