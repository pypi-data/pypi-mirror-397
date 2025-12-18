"""
Tests for Phase 01: Project Restructure
Verifies package structure, imports, and module accessibility.
"""
import pytest
import sys
from pathlib import Path

# Add src to path for testing
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


class TestPackageStructure:
    """Test that package structure is correct."""

    def test_src_seokit_exists(self):
        """Verify src/seokit directory exists."""
        seokit_dir = src_path / "seokit"
        assert seokit_dir.exists(), "src/seokit/ directory not found"
        assert seokit_dir.is_dir(), "src/seokit/ is not a directory"

    def test_core_directory_exists(self):
        """Verify src/seokit/core directory exists."""
        core_dir = src_path / "seokit" / "core"
        assert core_dir.exists(), "src/seokit/core/ directory not found"
        assert core_dir.is_dir(), "src/seokit/core/ is not a directory"

    def test_commands_directory_exists(self):
        """Verify src/seokit/commands directory exists."""
        commands_dir = src_path / "seokit" / "commands"
        assert commands_dir.exists(), "src/seokit/commands/ directory not found"
        assert commands_dir.is_dir(), "src/seokit/commands/ is not a directory"

    def test_init_files_exist(self):
        """Verify all __init__.py files exist."""
        expected_inits = [
            src_path / "seokit" / "__init__.py",
            src_path / "seokit" / "core" / "__init__.py",
            src_path / "seokit" / "commands" / "__init__.py",
        ]
        for init_file in expected_inits:
            assert init_file.exists(), f"{init_file} not found"

    def test_main_entry_point_exists(self):
        """Verify __main__.py exists for python -m seokit."""
        main_file = src_path / "seokit" / "__main__.py"
        assert main_file.exists(), "__main__.py not found"


class TestCoreModules:
    """Test core module files exist and are importable."""

    def test_config_module(self):
        """Test config module exists and is importable."""
        config_file = src_path / "seokit" / "config.py"
        assert config_file.exists(), "config.py not found"

        from seokit.config import PERPLEXITY_API_URL, validate_config
        assert PERPLEXITY_API_URL == "https://api.perplexity.ai/chat/completions"

    def test_perplexity_client_module(self):
        """Test perplexity_client module is importable."""
        from seokit.core.perplexity_client import query_perplexity, format_output_with_citations
        assert callable(query_perplexity)
        assert callable(format_output_with_citations)

    def test_search_intent_module(self):
        """Test search_intent module is importable."""
        from seokit.core.search_intent import analyze_search_intent
        assert callable(analyze_search_intent)

    def test_top_articles_module(self):
        """Test top_articles module is importable."""
        from seokit.core.top_articles import find_top_articles
        assert callable(find_top_articles)

    def test_outline_module(self):
        """Test outline module is importable."""
        from seokit.core.outline import analyze_outline, generate_report, calculate_score
        assert callable(analyze_outline)
        assert callable(generate_report)
        assert callable(calculate_score)

    def test_docx_generator_module(self):
        """Test docx_generator module is importable."""
        from seokit.core.docx_generator import md_to_docx
        assert callable(md_to_docx)

    def test_language_utils_module(self):
        """Test language_utils module is importable."""
        from seokit.core.language_utils import detect_language, get_language_instruction
        assert callable(detect_language)
        assert callable(get_language_instruction)

    def test_word_utils_module(self):
        """Test word_utils module is importable."""
        from seokit.core.word_utils import count_words, calculate_keyword_density, get_content_stats
        assert callable(count_words)
        assert callable(calculate_keyword_density)
        assert callable(get_content_stats)


class TestCoreExports:
    """Test that core __init__.py exports work correctly."""

    def test_core_exports(self):
        """Test all expected exports from core package."""
        from seokit.core import (
            analyze_search_intent,
            find_top_articles,
            analyze_outline,
            generate_report,
            md_to_docx,
        )
        assert callable(analyze_search_intent)
        assert callable(find_top_articles)
        assert callable(analyze_outline)
        assert callable(generate_report)
        assert callable(md_to_docx)


class TestSlashCommands:
    """Test slash command files are bundled correctly."""

    def test_command_files_exist(self):
        """Verify all 5 command files exist in package."""
        commands_dir = src_path / "seokit" / "commands"
        expected_commands = [
            "01-search-intent.md",
            "02-top-articles.md",
            "03-create-outline.md",
            "04-optimize-outline.md",
            "05-write-seo.md",
        ]
        for cmd in expected_commands:
            cmd_file = commands_dir / cmd
            assert cmd_file.exists(), f"Command file {cmd} not found"

    def test_commands_helper_functions(self):
        """Test commands package helper functions."""
        from seokit.commands import get_command_files, get_command

        files = get_command_files()
        assert len(files) == 5, f"Expected 5 command files, got {len(files)}"

        search_cmd = get_command("01-search-intent")
        assert search_cmd is not None, "01-search-intent.md not found via get_command"
        assert search_cmd.exists()


class TestPackageVersion:
    """Test package versioning."""

    def test_version_exists(self):
        """Test that package version is accessible."""
        import seokit
        assert hasattr(seokit, "__version__")
        assert seokit.__version__ == "1.0.0"


class TestFunctionality:
    """Test actual functionality of modules."""

    def test_outline_analyzer(self):
        """Test outline analyzer with sample content."""
        from seokit.core.outline import analyze_outline, calculate_score

        sample_outline = """# Best Running Shoes Guide

## Introduction
This is an intro.

## Top Brands
Content about brands.

## How to Choose
Selection guide.

## FAQ
Questions and answers.

## Conclusion
Final thoughts.
"""
        analysis = analyze_outline(sample_outline)
        assert analysis["h1_count"] == 1
        assert analysis["h2_count"] == 5
        assert len(analysis["main_h2s"]) == 3
        assert len(analysis["supplemental_h2s"]) == 2

        score = calculate_score(analysis)
        assert 0 <= score <= 100

    def test_word_utils(self):
        """Test word counting utilities."""
        from seokit.core.word_utils import count_words, calculate_keyword_density

        text = "# Title\n\nThis is a test article about running shoes. Running shoes are great."
        word_count = count_words(text)
        assert word_count > 0

        density = calculate_keyword_density(text, "running shoes")
        assert density > 0

    def test_language_detection(self):
        """Test language detection."""
        from seokit.core.language_utils import detect_language

        assert detect_language("Hello world") == "English"
        assert detect_language("Xin chào thế giới") == "Vietnamese"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
