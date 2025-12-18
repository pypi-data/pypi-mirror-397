"""
Top Articles Finder
Finds and analyzes top 10 ranking articles for a keyword using Perplexity API.
"""
import sys

from seokit.core.perplexity_client import query_perplexity, format_output_with_citations
from seokit.config import OUTPUTS_DIR


def find_top_articles(keyword: str) -> str:
    """
    Find top 10 ranking articles for a keyword.

    Args:
        keyword: The main keyword to search

    Returns:
        Formatted article analysis with citations
    """
    system = """You are an expert SEO researcher and content analyst.
Your task is to find and analyze the top-ranking content for specific keywords,
providing detailed insights about what makes them successful."""

    prompt = f"""Find the 10 best online articles that answer the query: "{keyword}"

For each article, provide:

## Article [Number]: [Title]
- **URL**: [full URL]
- **Estimated Word Count**: [approximate word count]
- **Content Type**: (guide, listicle, comparison, tutorial, etc.)
- **Main Topics/H2 Headings**:
  - List the main sections covered
- **Unique Value**: What makes this article stand out?
- **E-E-A-T Signals**: How does it demonstrate expertise and authority?
- **Content Gaps**: What could be improved or is missing?

Focus on:
1. Authoritative sources (industry leaders, well-known publications)
2. Recent content (preferably last 2 years)
3. Content that ranks well for this keyword
4. Variety of content formats and approaches

After listing all articles, provide:

## Summary Analysis
- Common topics covered across top articles
- Content gaps in the market (opportunities)
- Average word count of top performers
- Recommended approach to outperform these articles"""

    result = query_perplexity(prompt, system)
    output = format_output_with_citations(result)

    # Save to outputs directory (folder-based, no keyword suffix needed)
    output_file = OUTPUTS_DIR / "top-articles.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# Top 10 Articles for: {keyword}\n\n")
        f.write(output)

    return output


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m seokit.core.top_articles <keyword>")
        print("Example: python -m seokit.core.top_articles 'best running shoes'")
        sys.exit(1)

    keyword = " ".join(sys.argv[1:])
    print(f"Finding top articles for: {keyword}\n")
    print("=" * 50)
    print(find_top_articles(keyword))
