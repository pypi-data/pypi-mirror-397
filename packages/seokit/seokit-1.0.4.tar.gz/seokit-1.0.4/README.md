# SEOKit

[![PyPI version](https://badge.fury.io/py/seokit.svg)](https://pypi.org/project/seokit/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)

Claude Code toolkit for creating high-quality SEO articles.

## Installation

### PyPI (Recommended)

```bash
pip install seokit
```

## Features

- Search Intent Analysis - Understand user needs via Perplexity API
- Competitor Research - Analyze top 10 ranking articles
- Outline Creation - Structure content following Google E-E-A-T guidelines
- Outline Optimization - Apply 80/20 content distribution rules
- Article Writing - Generate full articles with DOCX export

## Usage

After installation, SEOKit slash commands are available in Claude Code. Refer to the `.claude/commands/` directory for detailed usage of each command.

### Workflow

1. `/search-intent "keyword"` - Analyze search intent
2. `/top-article "keyword"` - Find top 10 competitor articles
3. `/create-outline` - Create structured outline
4. `/optimize-outline` - Optimize with 80/20 rule
5. `/write-seo` - Generate full article + DOCX

### Output Structure

```
your-project/
└── keyword-slug/           # Auto-created per keyword
    ├── search-intent.md
    ├── top-articles.md
    ├── outline.md
    ├── outline-optimized.md
    ├── article.md
    └── article.docx
```

## Commands

| Command | Description |
|---------|-------------|
| `/search-intent [keyword]` | Analyze search intent |
| `/top-article [keyword]` | Find top competitor articles |
| `/create-outline` | Create article outline |
| `/optimize-outline` | Optimize outline structure |
| `/write-seo` | Write full article |

## CLI Commands

```bash
seokit --help                   # Show help
seokit config                   # Configure API key
seokit uninstall                # Remove SEOKit data and slash commands
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SEOKIT_HOME` | `~/.claude/seokit` | Global installation path |
| `SEOKIT_KEYWORD` | (empty) | Output folder name |
| `PERPLEXITY_API_KEY` | - | API key (required) |

## Requirements

- Python 3.10+
- Claude Code CLI
- Perplexity API key ([get one here](https://www.perplexity.ai/settings/api))

## Troubleshooting

### "PERPLEXITY_API_KEY not configured"

```bash
seokit config
# Or manually:
echo "PERPLEXITY_API_KEY=pplx-your-key" >> ~/.claude/seokit/.env
```

### Commands not found

Ensure you have run `pip install seokit`. The slash commands will be made available when you run any Claude command after installation.

## Update

```bash
pip install -U seokit
```

## Uninstall

```bash
seokit uninstall  # Remove SEOKit data and slash commands
pip uninstall seokit # Remove the pip package
```

## Documentation

See `docs/` folder for detailed documentation:
- [Codebase Summary](docs/codebase-summary.md) - Architecture overview
- [Project Overview](docs/project-overview-pdr.md) - Product requirements
- [Code Standards](docs/code-standards.md) - Development guidelines

## License

Proprietary - see [LICENSE](LICENSE) for details.
