"""SEOKit CLI - Claude Code toolkit for SEO articles."""
import re
import shutil
import subprocess
import sys
from pathlib import Path
import click

from seokit import (
    __version__,
    _install_commands,
    _install_scripts,
    _create_venv,
    _is_setup_complete,
    _print_update_banner,
    _update_checklists,
    _cleanup_obsolete_commands,
)
from seokit.config import (
    get_commands_dir,
    get_claude_dir,
    get_seokit_data_dir,
    PERPLEXITY_API_KEY,
)

# Slash command files to remove
SLASH_COMMANDS = [
    'search-intent.md',
    'top-article.md',
    'create-outline.md',
    'optimize-outline.md',
    'write-seo.md',
]


@click.group(invoke_without_command=True)
@click.version_option()
@click.pass_context
def main(ctx):
    """SEOKit - Claude Code toolkit for creating high-quality SEO articles."""
    # If no subcommand provided, show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        return

    # Skip validation for setup command
    if ctx.invoked_subcommand == 'setup':
        return

    # Warn if setup not complete
    if not _is_setup_complete():
        click.echo("SEOKit not configured. Run: seokit setup")
        ctx.exit(1)


@main.command()
def config():
    """Configure SEOKit (API keys, settings)."""
    env_file = get_claude_dir() / '.env'

    click.echo("SEOKit Configuration")
    click.echo("-" * 40)

    # Check current API key
    if PERPLEXITY_API_KEY:
        if len(PERPLEXITY_API_KEY) > 12:
            masked = PERPLEXITY_API_KEY[:8] + "..." + PERPLEXITY_API_KEY[-4:]
        else:
            masked = "***"
        click.echo(f"Current Perplexity API Key: {masked}")
    else:
        click.echo("Perplexity API Key: Not set")

    # Prompt for new key
    new_key = click.prompt(
        "Enter new Perplexity API Key (or press Enter to skip)",
        default="",
        show_default=False
    )

    if new_key:
        env_file.parent.mkdir(parents=True, exist_ok=True)

        if env_file.exists():
            content = env_file.read_text()
            if 'PERPLEXITY_API_KEY' in content:
                content = re.sub(
                    r'PERPLEXITY_API_KEY=.*',
                    f'PERPLEXITY_API_KEY={new_key}',
                    content
                )
            else:
                content = content.rstrip() + f'\nPERPLEXITY_API_KEY={new_key}\n'
        else:
            content = f'PERPLEXITY_API_KEY={new_key}\n'

        env_file.write_text(content)
        click.echo("API Key updated!")
    else:
        click.echo("Skipped - no changes made")


@main.command()
def setup():
    """Install SEOKit runtime files (commands, scripts, venv)."""
    click.echo("Setting up SEOKit...")

    # Install slash commands
    _install_commands()

    # Install scripts
    _install_scripts()

    # Create venv
    try:
        _create_venv()
    except Exception as e:
        click.echo(f"Setup failed: {e}")
        return

    # Install checklists
    _update_checklists()

    click.echo("SEOKit setup complete!")
    click.echo("")
    click.echo("Run 'seokit config' to set your Perplexity API key.")


@main.command()
@click.option('--force', '-f', is_flag=True, help='Overwrite all files including user customizations')
def update(force: bool):
    """Update SEOKit files (preserves user customizations)."""
    _print_update_banner()

    # Self-update from PyPI using pipx
    click.echo("Checking for updates...")
    result = subprocess.run(
        ['pipx', 'upgrade', 'seokit'],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        # Fallback to pip if pipx not available
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '--upgrade', 'seokit'],
            capture_output=True,
            text=True
        )

    # Reload version after upgrade
    from importlib.metadata import version as get_version
    try:
        new_version = get_version("seokit")
    except Exception:
        new_version = __version__

    # Slash commands: overwrite + cleanup obsolete
    _install_commands()
    _cleanup_obsolete_commands()

    # Update scripts
    _install_scripts()
    click.echo("  + Scripts updated")

    # Checklists: merge or force overwrite
    _update_checklists(overwrite=force)

    # Output success message
    if force:
        click.echo(f"SEOKit v{new_version} - Reset to defaults!")
    else:
        click.echo(f"SEOKit v{new_version} - Updated successfully!")


@main.command()
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation prompt')
def uninstall(yes: bool):
    """Completely remove SEOKit from the system."""
    seokit_dir = get_seokit_data_dir()
    commands_dir = get_commands_dir()

    click.echo("SEOKit Uninstaller")
    click.echo("=" * 40)
    click.echo("")
    click.echo("This will remove:")
    click.echo(f"  - {seokit_dir}/ (scripts, venv, config)")

    # Check which commands exist
    existing_commands = []
    for cmd in SLASH_COMMANDS:
        cmd_path = commands_dir / cmd
        if cmd_path.exists():
            existing_commands.append(cmd)

    if existing_commands:
        click.echo(f"  - Slash commands from {commands_dir}/:")
        for cmd in existing_commands:
            click.echo(f"      {cmd}")

    click.echo("")

    if not yes:
        if not click.confirm("Continue?", default=False):
            click.echo("Cancelled.")
            return

    click.echo("")

    # Remove seokit data directory
    if seokit_dir.exists():
        shutil.rmtree(seokit_dir)
        click.echo(f"Removed: {seokit_dir}/")

    # Remove slash commands
    for cmd in SLASH_COMMANDS:
        cmd_path = commands_dir / cmd
        if cmd_path.exists():
            cmd_path.unlink()
            click.echo(f"Removed: {cmd_path}")

    click.echo("")
    click.echo("=" * 40)
    click.echo("SEOKit uninstalled successfully!")

    # Uninstall pip package
    click.echo("")
    click.echo("Uninstalling pip package...")
    result = subprocess.run(
        [sys.executable, '-m', 'pip', 'uninstall', '-y', 'seokit'],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        click.echo("Removed: seokit pip package")
    elif "not installed" in result.stderr.lower():
        click.echo("Note: pip package already removed")
    else:
        click.echo("")
        click.echo("Could not auto-remove pip package.")
        click.echo("Please run manually:")
        click.echo(f"  {sys.executable} -m pip uninstall seokit")


if __name__ == "__main__":
    main()
