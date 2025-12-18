"""
Search Intent Analyzer
Analyzes user search intent for a given keyword using Perplexity API.
"""
import sys

from seokit.core.perplexity_client import query_perplexity, format_output_with_citations
from seokit.config import OUTPUTS_DIR


def analyze_search_intent(keyword: str) -> str:
    """
    Analyze search intent for a keyword.

    Args:
        keyword: The main keyword to analyze

    Returns:
        Formatted analysis string with citations
    """
    system = """You are an expert SEO analyst specializing in search intent analysis.
Provide actionable, data-driven insights based on current search trends and SERP analysis."""

    prompt = f"""Analyze the search intent for the keyword: "{keyword}"

Provide a comprehensive analysis including:

## 1. Primary Search Intent
- Type: (informational / navigational / transactional / commercial investigation)
- Confidence level and reasoning

## 2. Secondary Intents
- Any related or secondary intents users might have

## 3. User Profile & Pain Points
- Who is searching for this?
- What problems are they trying to solve?
- What stage of the buyer journey are they in?

## 4. Top Questions Users Ask
List the top 5-7 questions users commonly ask about this topic

## 5. Related Keywords & Topics
- Semantically related keywords
- Topics that should be covered for comprehensive content

## 6. Content Format Recommendations
- Best content format (guide, listicle, comparison, tutorial, etc.)
- Recommended word count range
- Key elements to include

## 7. SERP Features to Target
- Featured snippets opportunity
- People Also Ask boxes
- Other SERP features

Be specific, actionable, and base your analysis on current search trends."""

    result = query_perplexity(prompt, system)
    output = format_output_with_citations(result)

    # Save to outputs directory (folder-based, no keyword suffix needed)
    output_file = OUTPUTS_DIR / "search-intent.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# Search Intent Analysis: {keyword}\n\n")
        f.write(output)

    return output


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m seokit.core.search_intent <keyword>")
        print("Example: python -m seokit.core.search_intent 'best running shoes'")
        sys.exit(1)

    keyword = " ".join(sys.argv[1:])
    print(f"Analyzing search intent for: {keyword}\n")
    print("=" * 50)
    print(analyze_search_intent(keyword))
