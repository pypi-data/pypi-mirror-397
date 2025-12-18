"""SEOKit - Claude Code toolkit for SEO articles."""
import shutil
from pathlib import Path

from seokit.config import get_commands_dir, get_seokit_data_dir

__version__ = "1.0.6"

# SEOKit command prefixes for cleanup detection
SEOKIT_COMMAND_PREFIXES = (
    'search-intent', 'top-article', 'create-outline',
    'optimize-outline', 'write-seo'
)


def _print_update_banner():
    """Print update banner."""
    import click
    click.echo()
    click.echo("  ╭───────────────────────────────╮")
    click.echo("  │      SEOKit Updating...       │")
    click.echo("  ╰───────────────────────────────╯")
    click.echo()


def _install_commands():
    """Copy slash commands to ~/.claude/commands/ on package load."""
    commands_src = Path(__file__).parent / 'commands'
    commands_dest = get_commands_dir()

    if not commands_src.exists():
        return

    commands_dest.mkdir(parents=True, exist_ok=True)

    for cmd_file in commands_src.glob('*.md'):
        shutil.copy2(cmd_file, commands_dest / cmd_file.name)


def _update_checklists(overwrite=False):
    """Copy checklists. Skip existing unless overwrite=True."""
    src = Path(__file__).parent / 'checklists'
    dest = get_seokit_data_dir() / 'checklists'

    if not src.exists():
        return

    dest.mkdir(parents=True, exist_ok=True)

    for file in src.glob('*.md'):
        dest_file = dest / file.name
        if not overwrite and dest_file.exists():
            continue
        shutil.copy2(file, dest_file)


def _cleanup_obsolete_commands():
    """Remove SEOKit slash commands no longer in package."""
    src = Path(__file__).parent / 'commands'
    dest = get_commands_dir()

    if not src.exists() or not dest.exists():
        return

    package_commands = {f.name for f in src.glob('*.md')}

    for installed in dest.glob('*.md'):
        if installed.name.startswith(SEOKIT_COMMAND_PREFIXES):
            if installed.name not in package_commands:
                installed.unlink()


_install_commands()
