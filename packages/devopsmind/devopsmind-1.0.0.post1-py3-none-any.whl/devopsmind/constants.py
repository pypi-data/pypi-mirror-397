from pathlib import Path
import os

VERSION = "1.0.0"

# -------------------------------------------------
# XP → Rank Mapping (Player Progression)
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

# -------------------------------------------------
# Difficulty System (Challenge-Level)
# -------------------------------------------------

# Canonical difficulty order (semantic, NOT alphabetical)
DIFFICULTY_ORDER = {
    "Easy": 1,
    "Medium": 2,
    "Hard": 3,
    "Expert": 4,
    "Master": 5,
    "Architect": 6,
    "Principal": 7,
    "Staff": 8,
    "Distinguished": 9,
    "Fellow": 10,
}

# Canonical XP per difficulty (authoritative reference)
DIFFICULTY_XP = {
    "Easy": 50,
    "Medium": 100,
    "Hard": 150,
    "Master": 300,
    "Expert": 500,
    "Architect": 750,
    "Principal": 1000,
    "Staff": 1300,
    "Distinguished": 1600,
    "Fellow": 2000,
}

# -------------------------------------------------
# Paths & Storage
# -------------------------------------------------

XDG = os.environ.get("XDG_DATA_HOME")
DATA_DIR = Path(XDG) / "devopsmind" if XDG else Path.home() / ".devopsmind"

PROFILE_DIR = DATA_DIR / "profiles"
LEADERBOARD_FILE = DATA_DIR / "leaderboard.json"
PENDING_SYNC_DIR = DATA_DIR / "pending_sync"

BUNDLED_CHALLENGES = Path(__file__).resolve().parent / "challenges"

DATA_DIR.mkdir(parents=True, exist_ok=True)
PROFILE_DIR.mkdir(parents=True, exist_ok=True)
PENDING_SYNC_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------
# User Workspace (Visible)
# -------------------------------------------------

WORKSPACE_ROOT = Path.home() / "workspace"
WORKSPACE_ROOT.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------
# UI Colors
# -------------------------------------------------

PRIMARY_COLOR = "cyan"
SUCCESS_COLOR = "green"
ERROR_COLOR = "red"
