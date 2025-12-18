Analyze search intent for keyword: $ARGUMENTS

## Instructions

Run the search intent analysis using Perplexity API:

```bash
KEYWORD_SLUG=$(echo "$ARGUMENTS" | iconv -f UTF-8 -t ASCII//TRANSLIT 2>/dev/null | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd '[:alnum:]-')
export SEOKIT_HOME="$HOME/.claude/seokit"
export SEOKIT_KEYWORD="$KEYWORD_SLUG"
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
