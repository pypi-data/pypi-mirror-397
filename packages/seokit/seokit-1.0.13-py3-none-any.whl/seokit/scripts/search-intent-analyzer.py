"""
Search Intent Analyzer
Analyzes user search intent for a given keyword using Perplexity API.

Exit codes:
    0: Success
    1: Usage error (no keyword provided)
    2: API key missing/invalid (can fallback to Claude Code)
    3: API request error (network, timeout, auth, rate limit)
    4: File write error (permissions, disk space)
    5: Unexpected error (bug or unhandled case)

Error code prefixes in output:
    [CONFIG_*]: Configuration errors (API key, env file)
    [API_*]: API-related errors (network, auth, rate limit)
    [FILE_*]: File system errors (write, permissions)
    [UNEXPECTED_*]: Unexpected errors requiring investigation
"""
import sys
import json
import traceback
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from perplexity_client import (
    query_perplexity,
    format_output_with_citations,
    APIKeyMissingError,
    APITimeoutError,
    APIRequestError,
    APIConnectionError,
    APIResponseParseError,
    PerplexityError
)
from config import OUTPUTS_DIR, get_env_status, get_output_dir_status


def analyze_search_intent(keyword: str) -> str:
    """
    Analyze search intent for a keyword.

    Args:
        keyword: The main keyword to analyze

    Returns:
        Formatted analysis string with citations

    Raises:
        APIKeyMissingError: When API key is not configured
        APIConnectionError: When network connection fails
        APITimeoutError: When request times out
        APIRequestError: When API returns an error
        APIResponseParseError: When response is malformed
        OSError: When file write fails
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

    # Save to outputs directory
    output_file = OUTPUTS_DIR / "search-intent.md"
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"# Search Intent Analysis: {keyword}\n\n")
            f.write(output)
    except PermissionError as e:
        raise OSError(
            f"[FILE_PERMISSION_ERROR] Cannot write to '{output_file}'.\n"
            f"Permission denied. Check directory write permissions.\n"
            f"Directory: {OUTPUTS_DIR}\n"
            f"Original error: {e}"
        ) from e
    except OSError as e:
        # More specific error messages based on error type
        if e.errno == 28:  # ENOSPC - No space left on device
            raise OSError(
                f"[FILE_DISK_FULL] Cannot write to '{output_file}'.\n"
                f"No disk space left. Free up space and try again.\n"
                f"Original error: {e}"
            ) from e
        elif e.errno == 30:  # EROFS - Read-only file system
            raise OSError(
                f"[FILE_READONLY_FS] Cannot write to '{output_file}'.\n"
                f"File system is read-only.\n"
                f"Original error: {e}"
            ) from e
        else:
            raise OSError(
                f"[FILE_WRITE_ERROR] Failed to write output file '{output_file}'.\n"
                f"Error type: {type(e).__name__} (errno={e.errno})\n"
                f"Check directory permissions and disk space.\n"
                f"Original error: {e}"
            ) from e

    print(f"\n✓ Analysis saved to: {output_file}")
    return output


def print_error(error_code: str, message: str, details: dict = None):
    """Print formatted error to stderr."""
    print(f"\n[{error_code}]", file=sys.stderr)
    print(f"Error: {message}", file=sys.stderr)
    if details:
        for key, value in details.items():
            if value is not None:
                print(f"  {key}: {value}", file=sys.stderr)


def _get_suggestion_for_status_code(status_code: int) -> str:
    """Return a suggestion based on HTTP status code."""
    suggestions = {
        400: "Check if the keyword contains invalid characters",
        401: "Verify your API key is correct in the .env file",
        403: "Your API key may be revoked. Generate a new one at https://perplexity.ai/settings/api",
        429: "Wait 1-2 minutes before retrying. Consider upgrading your API plan for higher limits.",
        500: "Perplexity is having issues. Try again in a few minutes.",
        502: "Perplexity gateway error. Usually resolves within minutes.",
        503: "Perplexity is under maintenance. Check https://status.perplexity.ai",
        504: "Request took too long. Try a shorter keyword or try again later."
    }
    return suggestions.get(status_code, "Check the error details above and try again")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_error(
            "USAGE_NO_KEYWORD",
            "No keyword provided",
            {
                "usage": "python search-intent-analyzer.py <keyword>",
                "example": "python search-intent-analyzer.py 'best running shoes'"
            }
        )
        sys.exit(1)

    keyword = " ".join(sys.argv[1:])
    print(f"Analyzing search intent for: {keyword}\n")
    print("=" * 50)

    # Print diagnostic info for debugging
    env_status = get_env_status()
    output_status = get_output_dir_status()

    try:
        print(analyze_search_intent(keyword))

    except APIKeyMissingError as e:
        # Exit code 2: Signal to Claude Code that it can offer to run analysis directly
        print_error(
            e.error_code,
            str(e),
            {
                "env_path": e.env_path,
                "suggestion": e.suggestion,
                "env_status": json.dumps(env_status) if env_status.get("error") else None
            }
        )
        sys.exit(2)

    except APITimeoutError as e:
        print_error(
            e.error_code,
            str(e),
            {
                "timeout_seconds": e.context.get("timeout_seconds"),
                "url": e.context.get("url"),
                "suggestion": "Try again later or check if Perplexity API is experiencing issues"
            }
        )
        sys.exit(3)

    except APIConnectionError as e:
        print_error(
            e.error_code,
            str(e),
            {
                "url": e.context.get("url"),
                "original_error": e.context.get("original_error"),
                "suggestion": "Check your internet connection and firewall settings"
            }
        )
        sys.exit(3)

    except APIRequestError as e:
        print_error(
            e.error_code,
            str(e),
            {
                "status_code": e.status_code,
                "url": e.request_url,
                "response_preview": e.response_body[:200] if e.response_body else None,
                "suggestion": _get_suggestion_for_status_code(e.status_code)
            }
        )
        sys.exit(3)

    except APIResponseParseError as e:
        print_error(
            e.error_code,
            str(e),
            {
                "parse_error": e.context.get("parse_error"),
                "response_preview": e.raw_response[:200] if e.raw_response else None,
                "suggestion": "This may be a temporary API issue. Try again in a few minutes."
            }
        )
        sys.exit(3)

    except OSError as e:
        print_error(
            "FILE_ERROR",
            str(e),
            {
                "output_dir": str(OUTPUTS_DIR),
                "output_status": json.dumps(output_status) if output_status.get("error") else None
            }
        )
        sys.exit(4)

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(130)

    except Exception as e:
        # Unexpected error - provide full traceback for debugging
        print_error(
            f"UNEXPECTED_{type(e).__name__.upper()}",
            str(e),
            {
                "error_type": type(e).__name__,
                "module": type(e).__module__,
                "traceback": traceback.format_exc()
            }
        )
        print("\nThis is an unexpected error. Please report this issue.", file=sys.stderr)
        sys.exit(5)
