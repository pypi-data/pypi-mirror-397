from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec
import yaml
import inspect

from .progress import load_state, save_state, record_completion
from .submit import record_pending_sync, submit_pending
from .challenge_resolver import find_challenge_by_id


def normalize_result(result):
    if isinstance(result, dict):
        return {
            "success": bool(result.get("success")),
            "message": result.get("message", "Validation failed"),
            "missing": result.get("missing", []),
        }

    if isinstance(result, tuple):
        success = bool(result[0])
        second = result[1] if len(result) > 1 else None

        if isinstance(second, list):
            return {
                "success": success,
                "message": "Validation failed" if not success else "Validation passed",
                "missing": second,
            }

        if isinstance(second, str):
            return {
                "success": success,
                "message": second,
                "missing": [],
            }

    if isinstance(result, bool):
        return {
            "success": result,
            "message": "Validation passed" if result else "Validation failed",
            "missing": [],
        }

    return {
        "success": False,
        "message": "Invalid validator return type",
        "missing": [],
    }


def call_validator(func, workspace_path: Path):
    sig = inspect.signature(func)
    if len(sig.parameters) == 0:
        return func()
    return func(workspace_path)


def validate_only(challenge_id: str, workspace_path: Path):
    # ─────────────────────────────────────────────
    # Resolve challenge source
    # ─────────────────────────────────────────────

    source = find_challenge_by_id(challenge_id)
    if not source:
        return "❌ Challenge source not found."

    meta_path = source / "challenge.yaml"
    if not meta_path.exists():
        return "❌ challenge.yaml missing in challenge source."

    meta = yaml.safe_load(meta_path.read_text()) or {}

    skills = meta.get("skills", [])
    hint = meta.get("hint")
    validator_file = meta.get("validator", "validator.py")

    # 🔥 GENERIC XP METADATA
    xp = int(meta.get("xp", 100))
    stack = meta.get("stack")
    difficulty = meta.get("difficulty")

    validator_path = source / validator_file
    if not validator_path.exists():
        return f"❌ {validator_file} missing in challenge source."

    # ─────────────────────────────────────────────
    # Load validator
    # ─────────────────────────────────────────────

    spec = spec_from_file_location("challenge_validator", validator_path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    if not hasattr(module, "validate"):
        return f"❌ {validator_file} must define validate()"

    # ─────────────────────────────────────────────
    # Track badges BEFORE validation
    # ─────────────────────────────────────────────

    state_before = load_state()
    badges_before = set(
        state_before.get("achievements_unlocked", [])
        + state_before.get("profile", {}).get("achievements", [])
    )

    try:
        raw = call_validator(module.validate, workspace_path)
    except Exception as e:
        return f"❌ Validator crashed: {e}"

    result = normalize_result(raw)

    success = result["success"]
    message = result["message"]
    missing = result["missing"]

    # ─────────────────────────────────────────────
    # FAILURE
    # ─────────────────────────────────────────────

    if not success:
        state = load_state()
        failures = state.setdefault("validation_failures", {})
        failures[challenge_id] = failures.get(challenge_id, 0) + 1
        save_state(state)

        lines = [f"❌ {message}"]

        if missing:
            lines.append("\n❗ Missing / Incorrect:")
            for m in missing:
                lines.append(f"  • {m}")

        if failures[challenge_id] >= 3 and hint:
            lines.append(f"\n💡 Hint:\n{hint}")

        return "\n".join(lines)

    # ─────────────────────────────────────────────
    # SUCCESS (GLOBAL FIX)
    # ─────────────────────────────────────────────

    record_completion(
        challenge_id=challenge_id,
        xp=xp,
        stack=stack,
        difficulty=difficulty,
    )

    state = load_state()
    failures = state.get("validation_failures", {})
    failures.pop(challenge_id, None)
    state["validation_failures"] = failures
    save_state(state)

    lines = [f"✅ {message}"]

    if skills:
        lines.append("\n🧠 Skills reinforced:")
        for s in skills:
            lines.append(f"  • {s}")

    state_after = load_state()
    badges_after = set(
        state_after.get("achievements_unlocked", [])
        + state_after.get("profile", {}).get("achievements", [])
    )

    new_badges = badges_after - badges_before
    if new_badges:
        lines.append("\n🏅 Badges unlocked:")
        for b in new_badges:
            lines.append(f"  • {b}")

    # 🔄 SYNC (ALWAYS)
    record_pending_sync()
    sync_status = submit_pending()
    lines.append(f"\n🔄 Sync status:\n{sync_status}")

    return "\n".join(lines)
