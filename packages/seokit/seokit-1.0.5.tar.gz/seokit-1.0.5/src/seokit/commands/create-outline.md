Create SEO article outline based on research.

## Prerequisites

Before running this command, ensure you have completed:
1. `/search-intent [keyword]` - Understanding user intent
2. `/top-article [keyword]` - Competitor analysis

Check `./{keyword-slug}/` folder for: `search-intent.md` and `top-articles.md`

---

## Step 1: Mode Selection

Ask user: **Auto or Manual competitor selection?**

### Auto Mode
- Automatically select top 5 articles from `/top-article` results
- Analyze and synthesize into optimal outline

### Manual Mode
- Present numbered list of competitors found
- User selects which articles to analyze (e.g., "1, 3, 5, 7, 9")
- Minimum 3 articles recommended

---

## Step 2: Language Settings

Detect keyword language and ask user:

1. **Detected keyword language**: [Auto-detected or specify]
2. **Output language**: (default: same as keyword)
   - If keyword is English but user wants Vietnamese output, specify here

---

## Step 3: Read Reference Materials

### Google Guidelines Integration
Apply these key principles from Google's Search Quality Evaluator Guidelines:

**E-E-A-T Framework:**
- **Experience**: Include sections demonstrating first-hand experience
- **Expertise**: Structure shows deep knowledge of subject
- **Authoritativeness**: Reference authoritative sources
- **Trustworthiness**: Clear, accurate, verifiable information

**Helpful Content Principles:**
- Created for humans first, not search engines
- Provides substantial value beyond what competitors offer
- Demonstrates original insights or unique perspective
- Satisfies user need completely

### Read Outline Checklist
```bash
export SEOKIT_HOME="$HOME/.claude/seokit"
cat "$SEOKIT_HOME/checklists/outline-checklist-example.md"
```
Or use business-specific checklist if available: `$SEOKIT_HOME/checklists/outline-checklist-{business}.md`

---

## Step 4: Competitor Analysis

For selected articles, analyze and extract:

1. **Common Topics** (must include):
   - H2 headings that appear in 3+ articles
   - Core subtopics users expect

2. **Unique Topics** (differentiation):
   - Valuable content only 1-2 articles have
   - Your opportunity to stand out

3. **Content Gaps** (opportunities):
   - Questions not fully answered
   - Missing perspectives or data
   - Outdated information to refresh

4. **Structural Patterns**:
   - Average word count per section
   - FAQ patterns and questions
   - Media usage (images, tables, videos)

---

## Step 5: Generate Outline

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

---

## Step 6: Apply Outline Rules

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

---

## Step 7: Output

Save outline to: `./{keyword-slug}/outline.md`

Present outline to user for review before proceeding to `/optimize-outline`.

---

## Next Steps

After user reviews outline:
1. Run `/optimize-outline` to refine and finalize
2. Export to DOCX for external review if needed
