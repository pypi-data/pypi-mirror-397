
## Instructions

Run the top articles finder:

```bash
seokit top-articles "$ARGUMENTS"
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

Results are saved to: ~/.claude/seokit/<keyword-slug>/02-top-articles.md

## Next Steps

After finding top articles, use `seokit outline --file <path-to-search-intent-output>` to create an optimized content outline.
