from pathlib import Path
import json
from rich.table import Table
from rich.text import Text

CACHE_PATH = Path.home() / ".devopsmind" / "leaderboard.json"


def show_leaderboards():
    if not CACHE_PATH.exists():
        return Text(
            "Leaderboard not synced yet.\nRun devopsmind sync first.",
            style="yellow"
        )

    with open(CACHE_PATH, "r") as f:
        data = json.load(f)

    players = data.get("players", [])

    table = Table(title="Global Leaderboard")
    table.add_column("#", justify="right")
    table.add_column("Gamer")
    table.add_column("Username", style="dim")
    table.add_column("XP", justify="right")
    table.add_column("Rank")

    players = sorted(players, key=lambda p: p.get("xp", 0), reverse=True)

    for idx, player in enumerate(players, start=1):
        table.add_row(
            str(idx),
            player.get("handle", "-"),
            player.get("username", "-"),
            str(player.get("xp", 0)),
            player.get("rank", "-"),
        )

    return table
