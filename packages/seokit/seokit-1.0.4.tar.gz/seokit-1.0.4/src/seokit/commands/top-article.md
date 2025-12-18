Find top 10 articles for keyword: $ARGUMENTS

## Instructions

Run the top articles finder using Perplexity API:

```bash
KEYWORD_SLUG=$(echo "$ARGUMENTS" | iconv -f UTF-8 -t ASCII//TRANSLIT 2>/dev/null | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd '[:alnum:]-')
export SEOKIT_HOME="$HOME/.claude/seokit"
export SEOKIT_KEYWORD="$KEYWORD_SLUG"
source "$SEOKIT_HOME/venv/bin/activate"
python "$SEOKIT_HOME/scripts/top-articles-finder.py" "$ARGUMENTS"
```

## Expected Output

For each of the top 10 articles:
- **Title and URL**
- **Estimated Word Count**
- **Content Type** (guide, listicle, comparison, etc.)
- **Main Topics/H2 Headings**
- **Unique Value** - What makes it rank well
- **E-E-A-T Signals** - Expertise and authority indicators
- **Content Gaps** - Areas for improvement

Plus a **Summary Analysis** with:
- Common topics across top articles
- Content gaps (opportunities)
- Average word count
- Recommended approach to outperform

Results are saved to: `./{keyword-slug}/top-articles.md`

## Next Steps
After finding top articles, run `/create-outline` to create an optimized content outline.
