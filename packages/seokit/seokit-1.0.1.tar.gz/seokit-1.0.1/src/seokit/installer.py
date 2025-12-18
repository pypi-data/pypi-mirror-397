"""SEOKit installer utilities - handles first-run detection and command installation."""
import shutil
from pathlib import Path

from seokit.config import get_commands_dir, get_package_commands_dir


def get_marker_file() -> Path:
    """Get the installation marker file path."""
    return get_commands_dir() / '.seokit-installed'


def is_installed() -> bool:
    """Check if commands are already installed."""
    return get_marker_file().exists()


def ensure_commands_installed(quiet: bool = False) -> bool:
    """
    Ensure commands are installed (first-run detection).

    Returns True if commands were installed, False if already installed.
    """
    if is_installed():
        return False

    install_commands(quiet=quiet)
    get_marker_file().touch()
    return True


def install_commands(force: bool = False, quiet: bool = False) -> list[str]:
    """
    Copy slash commands to ~/.claude/commands/.

    Args:
        force: If True, reinstall even if already installed
        quiet: If True, don't print output

    Returns:
        List of installed command filenames
    """
    marker = get_marker_file()

    if not force and marker.exists():
        if not quiet:
            print("Commands already installed. Use --force to reinstall.")
        return []

    src = get_package_commands_dir()
    dst = get_commands_dir()
    dst.mkdir(parents=True, exist_ok=True)

    installed = []
    for cmd_file in src.glob('*.md'):
        shutil.copy(cmd_file, dst / cmd_file.name)
        installed.append(cmd_file.name)

    # Create/update marker
    marker.touch()

    return installed


def uninstall_commands() -> list[str]:
    """
    Remove slash commands from ~/.claude/commands/.

    Returns:
        List of removed command filenames
    """
    src = get_package_commands_dir()
    dst = get_commands_dir()

    removed = []
    for cmd_file in src.glob('*.md'):
        target = dst / cmd_file.name
        if target.exists():
            target.unlink()
            removed.append(cmd_file.name)

    # Remove marker
    marker = get_marker_file()
    if marker.exists():
        marker.unlink()

    return removed
