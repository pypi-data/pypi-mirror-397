"""SEOKit CLI - Claude Code toolkit for creating high-quality SEO articles."""
import re
import click
from pathlib import Path

from seokit.config import (
    get_commands_dir,
    get_claude_dir,
    PERPLEXITY_API_KEY,
    validate_config,
)


@click.group()
@click.version_option()
@click.pass_context
def main(ctx):
    """SEOKit - Claude Code toolkit for creating high-quality SEO articles."""
    # First-run detection: auto-install commands
    from seokit.installer import ensure_commands_installed
    if ensure_commands_installed(quiet=True):
        click.echo("First run detected - installed slash commands to ~/.claude/commands/")
    ctx.ensure_object(dict)


@main.command()
@click.option('--force', '-f', is_flag=True, help='Force reinstall even if already installed')
def install(force: bool):
    """Install SEOKit slash commands to ~/.claude/commands/."""
    from seokit.installer import install_commands
    installed = install_commands(force=force)

    if installed:
        dst = get_commands_dir()
        click.echo(f"Installed {len(installed)} commands to {dst}")
        for name in installed:
            click.echo(f"  - {name}")
    else:
        click.echo("Commands already installed. Use --force to reinstall.")


@main.command()
def uninstall():
    """Remove SEOKit slash commands from ~/.claude/commands/."""
    from seokit.installer import uninstall_commands
    removed = uninstall_commands()

    click.echo(f"Removed {len(removed)} commands")
    for name in removed:
        click.echo(f"  - {name}")


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


@main.command('search-intent')
@click.argument('keyword')
def search_intent(keyword: str):
    """Analyze search intent for KEYWORD."""
    if not validate_config():
        raise click.Abort()

    click.echo(f"Analyzing search intent for: {keyword}")
    click.echo("=" * 50)

    from seokit.core.search_intent import analyze_search_intent
    result = analyze_search_intent(keyword)
    click.echo(result)


@main.command('top-articles')
@click.argument('keyword')
def top_articles(keyword: str):
    """Collect top 10 articles for KEYWORD."""
    if not validate_config():
        raise click.Abort()

    click.echo(f"Finding top articles for: {keyword}")
    click.echo("=" * 50)

    from seokit.core.top_articles import find_top_articles
    result = find_top_articles(keyword)
    click.echo(result)


@main.command()
@click.option('--file', '-f', type=click.Path(exists=True), help='Outline file path')
def outline(file: str):
    """Analyze and optimize article outline."""
    if not file:
        click.echo("Error: Please specify an outline file with --file or -f")
        raise click.Abort()

    click.echo(f"Analyzing outline: {file}")
    click.echo("=" * 50)

    from seokit.core.outline import generate_report
    content = Path(file).read_text(encoding='utf-8')
    result = generate_report(content)
    click.echo(result)


@main.command()
@click.option('--outline', '-o', type=click.Path(exists=True), help='Markdown file to convert')
@click.option('--output', type=click.Path(), help='Output DOCX file path')
def write(outline: str, output: str):
    """Generate DOCX article from markdown outline."""
    if not outline:
        click.echo("Error: Please specify a markdown file with --outline or -o")
        raise click.Abort()

    click.echo(f"Converting to DOCX: {outline}")

    from seokit.core.docx_generator import md_to_docx, count_words_in_docx
    try:
        result_path = md_to_docx(outline, output)
        word_count = count_words_in_docx(result_path)
        click.echo(f"DOCX generated: {result_path}")
        click.echo(f"Word count: {word_count}")
    except ImportError as e:
        click.echo(f"Error: {e}")
        click.echo("Install with: pip install python-docx")
        raise click.Abort()
    except FileNotFoundError as e:
        click.echo(f"Error: {e}")
        raise click.Abort()


if __name__ == "__main__":
    main()
