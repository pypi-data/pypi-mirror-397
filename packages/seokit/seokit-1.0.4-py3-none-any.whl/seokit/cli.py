"""SEOKit CLI - Claude Code toolkit for SEO articles."""
import re
import shutil
from pathlib import Path
import click

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


@click.group()
@click.version_option()
def main():
    """SEOKit - Claude Code toolkit for creating high-quality SEO articles."""
    pass


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
    click.echo("")
    click.echo("To also remove the pip package, run:")
    click.echo("  pip uninstall seokit")


if __name__ == "__main__":
    main()
