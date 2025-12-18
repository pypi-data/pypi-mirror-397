## Prerequisites

Before generating the outline, ensure you have completed:
1.  **Search Intent Analysis**: Run `seokit search-intent <keyword>` and review `~/.claude/seokit/<keyword-slug>/01-search-intent.md`.
2.  **Competitor Analysis**: Run `seokit top-articles <keyword>` and review `~/.claude/seokit/<keyword-slug>/02-top-articles.md`.

## Instructions

To create the outline, gather insights from the `01-search-intent.md` and `02-top-articles.md` files for your keyword.

### 1. Mode Selection

Choose between **Auto** or **Manual** competitor selection:

-   **Auto Mode**: Automatically select top 5 articles from `02-top-articles.md` results, analyze and synthesize into an optimal outline.
-   **Manual Mode**: Present a numbered list of competitors found in `02-top-articles.md`. You will then select which articles to analyze (e.g., "1, 3, 5, 7, 9"). A minimum of 3 articles is recommended.

### 2. Language Settings

Specify the language for outline generation:

-   **Detected keyword language**: [Auto-detected or specify]
-   **Output language**: (default: same as keyword). If the keyword is English but you want Vietnamese output, specify here.

### 3. Read Reference Materials

Apply these key principles from Google's Search Quality Evaluator Guidelines:

**E-E-A-T Framework:**
-   **Experience**: Include sections demonstrating first-hand experience
-   **Expertise**: Structure shows deep knowledge of subject
-   **Authoritativeness**: Reference authoritative sources
-   **Trustworthiness**: Clear, accurate, verifiable information

**Helpful Content Principles:**
-   Created for humans first, not search engines
-   Provides substantial value beyond what competitors offer
-   Demonstrates original insights or unique perspective
-   Satisfies user need completely

### 4. Competitor Analysis

For selected articles, analyze and extract:

1.  **Common Topics** (must include):
    -   H2 headings that appear in 3+ articles
    -   Core subtopics users expect
2.  **Unique Topics** (differentiation):
    -   Valuable content only 1-2 articles have
    -   Your opportunity to stand out
3.  **Content Gaps** (opportunities):
    -   Questions not fully answered
    -   Missing perspectives or data
    -   Outdated information to refresh
4.  **Structural Patterns**:
    -   Average word count per section
    -   FAQ patterns and questions
    -   Media usage (images, tables, videos)

### 5. Generate Outline

Create outline following this structure:

```markdown
# H1: [Main Title - Matches Primary Search Intent]

> Target word count: [based on competitor average + 20%]
> Primary keyword: [keyword]
> Secondary keywords: [from research]

## Introduction
- Hook addressing user pain point
- What reader will learn
- Why this content is authoritative
[~150-200 words]

---
## MAIN CONTENT (80% of article)
---

## H2: [Core Topic 1 - Most Important]
### H3: [Subtopic if needed]
### H3: [Subtopic if needed]
[Estimated words: XXX]

## H2: [Core Topic 2]
### H3: [Subtopic]
[Estimated words: XXX]

## H2: [Core Topic 3]
...

## H2: [Core Topic N]

---
## SUPPLEMENTAL CONTENT (20% of article)
---

## H2: Frequently Asked Questions
### Q1: [Boolean question]?
### Q2: [Definitional question]?
### Q3: [Grouping question]?
### Q4: [Comparative question]?

## H2: [Related Topic / Additional Context]
- Expand on related information
- Provide additional perspectives

---

## H2: Conclusion
- Summary of key points
- Actionable next steps
- Call to action
[~150-200 words]
```

### 6. Apply Outline Rules

Verify outline follows these rules:
- [ ] Single H1 only
- [ ] H2s are sub-headings of H1
- [ ] H3s are sub-headings of H2s
- [ ] Logical contextual flow throughout
- [ ] Main content (80%) fully addresses primary topic
- [ ] Supplemental content (20%) enhances without diluting
- [ ] First 10 headings are highest quality
- [ ] Related headings grouped together
- [ ] First and last headings connect/mirror each other
- [ ] FAQ uses 4 question types if possible
- [ ] Incremental lists where appropriate

### 7. Output

Save outline to: `~/.claude/seokit/<keyword-slug>/03-outline.md`

Present outline to user for review before proceeding to `seokit outline --file <path-to-03-outline.md>`.

## Next Steps

After user reviews outline:
1.  Run `seokit outline --file <path-to-03-outline.md>` to refine and finalize.
2.  Export to DOCX for external review if needed.
