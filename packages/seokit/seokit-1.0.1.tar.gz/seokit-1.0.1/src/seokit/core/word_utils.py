"""
Word Utilities
Text analysis utilities for SEO content.
"""
import re


def count_words(text: str) -> int:
    """
    Count words in text, excluding markdown syntax.

    Args:
        text: Text content to analyze

    Returns:
        Word count
    """
    # Remove markdown headers
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    # Remove bold/italic markers
    text = re.sub(r'\*+', '', text)
    # Remove links but keep text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    # Remove code blocks
    text = re.sub(r'```[\s\S]*?```', '', text)
    # Remove inline code
    text = re.sub(r'`[^`]+`', '', text)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove horizontal rules
    text = re.sub(r'^---+$', '', text, flags=re.MULTILINE)
    # Remove metadata blocks
    text = re.sub(r'^>.*$', '', text, flags=re.MULTILINE)

    # Split and count non-empty words
    words = [w for w in text.split() if w.strip()]
    return len(words)


def calculate_keyword_density(text: str, keyword: str) -> float:
    """
    Calculate keyword density as percentage.

    Args:
        text: Full text content
        keyword: Keyword to check

    Returns:
        Density percentage (e.g., 1.5 for 1.5%)
    """
    total_words = count_words(text)
    if total_words == 0:
        return 0.0

    # Clean text for counting
    clean_text = text.lower()

    # Count keyword occurrences (case-insensitive)
    keyword_lower = keyword.lower()
    # Use word boundary matching for accurate count
    pattern = r'\b' + re.escape(keyword_lower) + r'\b'
    keyword_count = len(re.findall(pattern, clean_text))

    return (keyword_count / total_words) * 100


def analyze_readability(text: str) -> dict:
    """
    Basic readability analysis.

    Args:
        text: Text to analyze

    Returns:
        dict with readability metrics
    """
    # Clean markdown
    clean = re.sub(r'[#*_`\[\]()]', '', text)

    sentences = re.split(r'[.!?]+', clean)
    sentences = [s.strip() for s in sentences if s.strip()]

    words = clean.split()
    words = [w for w in words if w.strip()]

    avg_words_per_sentence = len(words) / len(sentences) if sentences else 0

    # Count syllables (rough estimate)
    def count_syllables(word):
        word = word.lower()
        vowels = 'aeiouàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵ'
        count = sum(1 for char in word if char in vowels)
        return max(1, count)

    total_syllables = sum(count_syllables(w) for w in words)
    avg_syllables_per_word = total_syllables / len(words) if words else 0

    # Flesch Reading Ease (approximate)
    # 206.835 - 1.015 * (words/sentences) - 84.6 * (syllables/words)
    if sentences and words:
        flesch = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * avg_syllables_per_word)
        flesch = max(0, min(100, flesch))
    else:
        flesch = 0

    return {
        "word_count": len(words),
        "sentence_count": len(sentences),
        "avg_words_per_sentence": round(avg_words_per_sentence, 1),
        "avg_syllables_per_word": round(avg_syllables_per_word, 2),
        "flesch_reading_ease": round(flesch, 1),
        "reading_level": get_reading_level(flesch)
    }


def get_reading_level(flesch_score: float) -> str:
    """Convert Flesch score to reading level description."""
    if flesch_score >= 90:
        return "Very Easy (5th grade)"
    elif flesch_score >= 80:
        return "Easy (6th grade)"
    elif flesch_score >= 70:
        return "Fairly Easy (7th grade)"
    elif flesch_score >= 60:
        return "Standard (8th-9th grade)"
    elif flesch_score >= 50:
        return "Fairly Difficult (10th-12th grade)"
    elif flesch_score >= 30:
        return "Difficult (College)"
    else:
        return "Very Difficult (Professional)"


def get_content_stats(content: str, keyword: str = None) -> dict:
    """
    Get comprehensive content statistics.

    Args:
        content: Markdown content
        keyword: Optional primary keyword

    Returns:
        dict with all statistics
    """
    # Count headings
    h1_count = len(re.findall(r'^# [^#]', content, re.MULTILINE))
    h2_count = len(re.findall(r'^## [^#]', content, re.MULTILINE))
    h3_count = len(re.findall(r'^### [^#]', content, re.MULTILINE))

    # Word count
    word_count = count_words(content)

    # Readability
    readability = analyze_readability(content)

    stats = {
        "word_count": word_count,
        "h1_count": h1_count,
        "h2_count": h2_count,
        "h3_count": h3_count,
        "readability": readability
    }

    if keyword:
        stats["keyword_density"] = round(calculate_keyword_density(content, keyword), 2)

    return stats
