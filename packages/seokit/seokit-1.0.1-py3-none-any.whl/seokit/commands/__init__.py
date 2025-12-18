"""SEOKit bundled slash commands for Claude Code."""
import os
from pathlib import Path

COMMANDS_DIR = Path(__file__).parent


def get_command_files() -> list[Path]:
    """Return list of all command markdown files."""
    return list(COMMANDS_DIR.glob("*.md"))


def get_command(name: str) -> Path | None:
    """Get path to a specific command file.

    Supports both exact match (01-search-intent.md) and
    partial match (search-intent -> 01-search-intent.md).
    """
    # Try exact match first
    cmd_file = COMMANDS_DIR / f"{name}.md"
    if cmd_file.exists():
        return cmd_file

    # Try pattern match with numbered prefix
    for f in COMMANDS_DIR.glob("*.md"):
        if name in f.stem:
            return f

    return None
