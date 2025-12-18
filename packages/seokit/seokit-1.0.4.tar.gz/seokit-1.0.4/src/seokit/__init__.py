"""SEOKit - Claude Code toolkit for SEO articles."""
import shutil
from pathlib import Path

__version__ = "1.0.4"

# Auto-install slash commands on import
def _install_commands():
    """Copy slash commands to ~/.claude/commands/ on package load."""
    commands_src = Path(__file__).parent / 'commands'
    commands_dest = Path.home() / '.claude' / 'commands'

    if not commands_src.exists():
        return

    commands_dest.mkdir(parents=True, exist_ok=True)

    for cmd_file in commands_src.glob('*.md'):
        shutil.copy2(cmd_file, commands_dest / cmd_file.name)

_install_commands()
