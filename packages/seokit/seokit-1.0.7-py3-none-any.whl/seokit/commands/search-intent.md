Analyze search intent for keyword: $ARGUMENTS

## Instructions

Run the search intent analysis using Perplexity API:

```bash
# Validate arguments
if [ -z "$ARGUMENTS" ]; then
    echo "Error: No keyword provided. Usage: /search-intent <keyword>"
    exit 1
fi

KEYWORD_SLUG=$(echo "$ARGUMENTS" | iconv -f UTF-8 -t ASCII//TRANSLIT 2>/dev/null || echo "$ARGUMENTS" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd '[:alnum:]-')
if [ -z "$KEYWORD_SLUG" ]; then
    KEYWORD_SLUG=$(echo "$ARGUMENTS" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd '[:alnum:]-')
fi

export SEOKIT_HOME="$HOME/.claude/seokit"
export SEOKIT_KEYWORD="$KEYWORD_SLUG"

# Check if venv exists
if [ ! -d "$SEOKIT_HOME/venv" ]; then
    echo "Error: SEOKit not properly installed. Run 'seokit setup' first."
    exit 1
fi

source "$SEOKIT_HOME/venv/bin/activate"
python "$SEOKIT_HOME/scripts/search-intent-analyzer.py" "$ARGUMENTS"
```

## Expected Output

The script will provide:
1. **Primary Search Intent** - Type (informational/navigational/transactional/commercial)
2. **User Profile & Pain Points** - Who searches this and why
3. **Top Questions** - Common questions users ask
4. **Related Keywords** - Semantically related terms
5. **Content Recommendations** - Best format and approach
6. **SERP Features** - Opportunities for featured snippets, etc.

Results are saved to: `./{keyword-slug}/search-intent.md`

## Next Steps
After analyzing search intent, run `/top-article $ARGUMENTS` to find competitor articles.
