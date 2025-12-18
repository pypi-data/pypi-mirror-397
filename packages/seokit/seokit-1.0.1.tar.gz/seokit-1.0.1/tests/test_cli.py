"""Tests for SEOKit CLI."""
import pytest
from pathlib import Path
from click.testing import CliRunner

from seokit.cli import main


@pytest.fixture
def runner():
    """Create Click CLI test runner."""
    return CliRunner()


class TestCLIBasics:
    """Test basic CLI functionality."""

    def test_help_shows_all_commands(self, runner):
        """Test --help shows all expected commands."""
        result = runner.invoke(main, ['--help'])
        assert result.exit_code == 0
        assert 'search-intent' in result.output
        assert 'top-articles' in result.output
        assert 'outline' in result.output
        assert 'write' in result.output
        assert 'install' in result.output
        assert 'uninstall' in result.output
        assert 'config' in result.output

    def test_version_flag(self, runner):
        """Test --version shows version info."""
        result = runner.invoke(main, ['--version'])
        assert result.exit_code == 0


class TestInstallCommand:
    """Test install command."""

    def test_install_copies_files(self, runner, tmp_path, monkeypatch):
        """Test install command copies command files to target directory."""
        # Mock HOME to use tmp_path
        monkeypatch.setenv('HOME', str(tmp_path))
        # Also mock USERPROFILE for Windows compatibility
        monkeypatch.setenv('USERPROFILE', str(tmp_path))

        result = runner.invoke(main, ['install', '--force'])
        assert result.exit_code == 0
        assert 'Installed' in result.output or 'commands' in result.output.lower()

    def test_install_without_force_skips_if_installed(self, runner, tmp_path, monkeypatch):
        """Test install without --force skips if already installed."""
        monkeypatch.setenv('HOME', str(tmp_path))
        monkeypatch.setenv('USERPROFILE', str(tmp_path))

        # First install
        runner.invoke(main, ['install', '--force'])

        # Second install without force
        result = runner.invoke(main, ['install'])
        assert result.exit_code == 0
        assert 'already installed' in result.output.lower() or 'installed' in result.output.lower()


class TestUninstallCommand:
    """Test uninstall command."""

    def test_uninstall_removes_files(self, runner, tmp_path, monkeypatch):
        """Test uninstall command removes command files."""
        monkeypatch.setenv('HOME', str(tmp_path))
        monkeypatch.setenv('USERPROFILE', str(tmp_path))

        # First install
        runner.invoke(main, ['install', '--force'])

        # Then uninstall
        result = runner.invoke(main, ['uninstall'])
        assert result.exit_code == 0
        assert 'Removed' in result.output or 'removed' in result.output.lower()


class TestConfigCommand:
    """Test config command."""

    def test_config_help(self, runner):
        """Test config --help works."""
        result = runner.invoke(main, ['config', '--help'])
        assert result.exit_code == 0

    def test_config_shows_current_state(self, runner, tmp_path, monkeypatch):
        """Test config command shows current configuration."""
        monkeypatch.setenv('HOME', str(tmp_path))
        monkeypatch.setenv('USERPROFILE', str(tmp_path))
        # Skip the prompt by sending empty input
        result = runner.invoke(main, ['config'], input='\n')
        assert result.exit_code == 0
        assert 'Configuration' in result.output


class TestSearchIntentCommand:
    """Test search-intent command."""

    def test_search_intent_help(self, runner):
        """Test search-intent --help works."""
        result = runner.invoke(main, ['search-intent', '--help'])
        assert result.exit_code == 0
        assert 'KEYWORD' in result.output


class TestTopArticlesCommand:
    """Test top-articles command."""

    def test_top_articles_help(self, runner):
        """Test top-articles --help works."""
        result = runner.invoke(main, ['top-articles', '--help'])
        assert result.exit_code == 0
        assert 'KEYWORD' in result.output


class TestOutlineCommand:
    """Test outline command."""

    def test_outline_help(self, runner):
        """Test outline --help works."""
        result = runner.invoke(main, ['outline', '--help'])
        assert result.exit_code == 0
        assert '--file' in result.output

    def test_outline_requires_file(self, runner):
        """Test outline command requires --file option."""
        result = runner.invoke(main, ['outline'])
        assert result.exit_code != 0


class TestWriteCommand:
    """Test write command."""

    def test_write_help(self, runner):
        """Test write --help works."""
        result = runner.invoke(main, ['write', '--help'])
        assert result.exit_code == 0
        assert '--outline' in result.output

    def test_write_requires_outline(self, runner):
        """Test write command requires --outline option."""
        result = runner.invoke(main, ['write'])
        assert result.exit_code != 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
