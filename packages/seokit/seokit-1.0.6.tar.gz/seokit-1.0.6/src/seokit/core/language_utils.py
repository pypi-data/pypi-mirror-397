"""
Language Detection Utilities
Simple language detection and localization helpers for SEOKit.
"""


def detect_language(text: str) -> str:
    """
    Detect language based on character patterns.

    Args:
        text: Text to analyze

    Returns:
        Language name (Vietnamese, English, etc.)
    """
    # Vietnamese-specific characters
    vietnamese_chars = set('àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđÀÁẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÈÉẺẼẸÊẾỀỂỄỆÌÍỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴĐ')
    if any(c in vietnamese_chars for c in text):
        return "Vietnamese"

    # Japanese detection (hiragana, katakana, kanji ranges)
    for char in text:
        code = ord(char)
        if (0x3040 <= code <= 0x309F) or (0x30A0 <= code <= 0x30FF) or (0x4E00 <= code <= 0x9FFF):
            return "Japanese"

    # Korean detection (Hangul range)
    for char in text:
        code = ord(char)
        if 0xAC00 <= code <= 0xD7AF:
            return "Korean"

    # Chinese detection (simplified/traditional)
    for char in text:
        code = ord(char)
        if 0x4E00 <= code <= 0x9FFF:
            return "Chinese"

    # Default to English
    return "English"


def get_language_instruction(keyword_lang: str, output_lang: str) -> str:
    """
    Generate language instruction for prompts.

    Args:
        keyword_lang: Language of the keyword/research
        output_lang: Desired output language

    Returns:
        Instruction string for prompts
    """
    if keyword_lang.lower() == output_lang.lower():
        return f"Write all content in {output_lang}."
    return f"The keyword is in {keyword_lang}. Write the final content in {output_lang}."


def format_language_options() -> str:
    """Return formatted language options for user selection."""
    return """
**Language Options:**
1. English
2. Vietnamese
3. Japanese
4. Korean
5. Chinese
6. Other (specify)
"""
