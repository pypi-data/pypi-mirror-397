Optimize an existing article outline.

## Input

Specify the outline file to optimize:
- Default: Look in `./{keyword-slug}/` for most recent outline
- Or specify path: `./{keyword-slug}/outline.md`

---

## Step 1: Load and Analyze Outline

Run the outline analyzer:
```bash
export SEOKIT_HOME="$HOME/.claude/seokit"
source "$SEOKIT_HOME/venv/bin/activate"
python "$SEOKIT_HOME/scripts/outline-analyzer.py" "{outline_path}"
```

This will generate a report showing:
- **Score**: 0-100 optimization score
- **Structure Analysis**: H1, H2, H3 counts and validation
- **Content Distribution**: Main vs Supplemental ratio (target 80/20)
- **Issues**: Problems that need fixing
- **Recommendations**: Actionable improvement steps

---

## Step 2: Apply Optimization Rules

Based on the search intent analysis from Step 1, optimize the outline following these rules:

### Structural Rules
1. **Single H1** - Contains primary keyword, matches search intent
2. **H2 Hierarchy** - 5-10 main sections, logically ordered
3. **H3 Depth** - Subdivide complex H2s with 2+ H3s each
4. **No Level Skipping** - H1 → H2 → H3 → H4 (never skip)

### Content Distribution (80/20 Rule)
- **80% Main Content**: Core topics directly answering search intent
- **20% Supplemental**: FAQ, conclusion, related topics, resources

### Flow & Coherence Rules
1. **Logical Flow** - General → Specific → Application → Summary
2. **First 10 Headings** - Must be highest quality, answer key questions
3. **Group Related** - Similar topics clustered together
4. **Bridge Sections** - Smooth transition between main and supplemental
5. **First-Last Connection** - Opening and closing themes mirror each other

### List & Structure Rules
- Use **incremental lists** for benefits, steps, or features
- Each H2 should have roughly equal weight (10-15% of content)
- Introduction and conclusion: 5-8% each

### FAQ Section Rules
Use 4 types of questions:
1. **Boolean**: "Is X better than Y?"
2. **Definitional**: "What is X?"
3. **Grouping**: "What are the types of X?"
4. **Comparative**: "How does X compare to Y?"

---

## Step 3: Generate Optimized Outline

Re-structure the outline following this format:

```markdown
# H1: [Primary Keyword + Compelling Hook]

> **Target Word Count**: [competitor avg + 20%]
> **Primary Keyword**: [main keyword]
> **Search Intent**: [informational/transactional/etc.]

---

## Introduction
- Hook addressing user pain point
- Promise of value (what reader will learn)
- Credibility signal
[Target: 150-200 words, 5-8% of total]

---
## === MAIN CONTENT (80%) ===
---

## H2: [Most Important Topic - Directly Answers Query]
### H3: [Subtopic 1]
### H3: [Subtopic 2]
[Target: 300-500 words per H2]

## H2: [Second Key Topic]
### H3: [Detail 1]
### H3: [Detail 2]

## H2: [Third Key Topic]
...

[Continue with 5-8 main H2 sections]

---
## === SUPPLEMENTAL CONTENT (20%) ===
---

## H2: Frequently Asked Questions
### Q1: [Boolean question]?
### Q2: [Definitional question]?
### Q3: [Grouping question]?
### Q4: [Comparative question]?

## H2: [Related Topic / Additional Context]
- Bridge content connecting to broader context
- Additional perspectives

---

## H2: Conclusion
- Summary of key takeaways (3-5 points)
- Actionable next steps
- Call to action
[Target: 150-200 words, 5-8% of total]
```

---

## Step 4: Validation Checklist

Before finalizing, verify:
- [ ] Single H1 with primary keyword
- [ ] 5-10 H2 sections with logical flow
- [ ] 80% main content / 20% supplemental ratio
- [ ] First 10 headings are highest quality
- [ ] Related headings grouped together
- [ ] First heading and last heading connect thematically
- [ ] FAQ uses multiple question types
- [ ] Incremental lists where appropriate
- [ ] All competitor topics covered + unique angles added
- [ ] Satisfies primary search intent

---

## Step 5: Output

Save optimized outline to: `./{keyword-slug}/outline-optimized.md`

Display optimization summary showing:
- Before/After score comparison
- Key changes made
- Ready for `/write-seo` command

---

## Step 6: Export to DOCX (Optional)

If user requests DOCX export:
```bash
export SEOKIT_HOME="$HOME/.claude/seokit"
source "$SEOKIT_HOME/venv/bin/activate"
python "$SEOKIT_HOME/scripts/docx-generator.py" "./{keyword-slug}/outline-optimized.md"
```

---

## Next Steps

After optimization is approved:
1. Run `/write-seo` to generate the full article
2. Follow the Article Checklist during writing
