"""
Perplexity API Client
Provides web-search enabled queries via Perplexity's sonar models.
"""
import requests

from seokit.config import (
    PERPLEXITY_API_KEY,
    PERPLEXITY_API_URL,
    PERPLEXITY_MODEL,
    validate_config,
)


def query_perplexity(prompt: str, system_prompt: str = "", max_tokens: int = 4096) -> dict:
    """
    Query Perplexity API with web search capability.

    Args:
        prompt: User query/prompt
        system_prompt: Optional system instructions
        max_tokens: Maximum response tokens (default 4096)

    Returns:
        dict with 'content' and 'citations' keys
    """
    if not validate_config():
        return {"content": "ERROR: API key not configured", "citations": []}

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": PERPLEXITY_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.3
    }

    try:
        response = requests.post(PERPLEXITY_API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()

        return {
            "content": data["choices"][0]["message"]["content"],
            "citations": data.get("citations", [])
        }
    except requests.exceptions.Timeout:
        return {"content": "ERROR: Request timed out. Please try again.", "citations": []}
    except requests.exceptions.HTTPError as e:
        return {"content": f"ERROR: API request failed - {e}", "citations": []}
    except Exception as e:
        return {"content": f"ERROR: Unexpected error - {e}", "citations": []}


def format_output_with_citations(result: dict) -> str:
    """Format result with citations appended."""
    output = result["content"]
    if result["citations"]:
        output += "\n\n## Sources\n"
        for url in result["citations"]:
            output += f"- {url}\n"
    return output
