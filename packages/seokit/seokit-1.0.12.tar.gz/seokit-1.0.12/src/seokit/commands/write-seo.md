Write SEO article from optimized outline.

## Prerequisites

Ensure you have:
1. Optimized outline at: `./{keyword-slug}/outline-optimized.md`
2. Article checklist at: `$SEOKIT_HOME/checklists/article-checklist-example.md` (or custom business checklist)

---

## Step 0: Load Workspace Context

Check for workspace context file:

```bash
cat .seokit-context.md 2>/dev/null
```

**If file exists**:
- Load context for use throughout article writing
- **Author pronoun**: Use consistently (e.g., "Chúng tôi..." vs "Mình...")
- **Reader address**: Use consistently (e.g., "Bạn có thể..." vs "Anh/chị...")
- **Products**: Note for natural mention in relevant sections (1-2 mentions max)
- **Writing notes**: Apply as style constraints throughout

**If file not found**:
- Continue with standard writing (no context applied)

---

## Step 1: Pre-Writing Setup

### 1.1 Load Outline
Read the optimized outline file and extract:
- Target word count
- Primary keyword
- Section structure (H2s, H3s)
- Content notes per section

### 1.2 Load Checklist
```bash
export SEOKIT_HOME="$HOME/.claude/seokit"
cat "$SEOKIT_HOME/checklists/article-checklist-example.md"
```
Or use business-specific checklist if available.

### 1.3 Confirm Settings
Ask user (pre-fill from context if available):
1. **Output language**: [From context or auto-detect from outline]
2. **Target word count**: [Use outline suggestion or specify]
3. **Tone**: [Suggest based on website type from context]
4. **Author pronoun**: [From context: {author_pronoun} or ask]
5. **Reader address**: [From context: {reader_address} or ask]
6. **Brand voice notes**: [From context: writing_notes or ask]

---

## Step 2: Section-by-Section Writing

Write each section following outline structure:

**Context Application (if loaded from Step 0):**
- Use **author pronoun** consistently throughout (e.g., "Chúng tôi giới thiệu..." not mixing with "Mình...")
- Use **reader address** consistently (e.g., "Bạn có thể..." not mixing with "Anh/chị...")
- Apply **writing notes** as style constraints
- Look for 1-2 natural opportunities to mention **products** (don't force)

### Introduction (5-8% of total)
- **Hook**: Open with compelling statement, question, or statistic
- **Context**: Briefly introduce the topic and why it matters
- **Promise**: What reader will learn/gain from this article
- **Keyword**: Include primary keyword naturally in first 100 words
- **Voice**: Use author pronoun in self-reference (if context loaded)

**Target**: 150-200 words

### Main Content Sections (H2s)

For each H2 section in outline:

1. **Topic Sentence**: Clear statement of what this section covers
2. **Body Content**:
   - Provide depth based on outline notes
   - Include specific examples and data
   - Use bullet points for lists (3+ items)
   - Add tables for comparisons
   - Reference sources where applicable
   - **Product mention** (if context loaded): Find natural opportunity in 1-2 relevant sections
3. **Subsections (H3s)**: Write as marked in outline
4. **Transition**: Smooth connection to next section

**Target per H2**: 300-500 words (adjust based on total target)

### FAQ Section

For each question:
- **Direct answer** in first sentence
- **Supporting detail** (1-2 sentences)
- **Actionable takeaway** if applicable

**Target per Q&A**: 50-100 words

Format for schema markup:
```markdown
### Q: [Question text]?

[Direct answer followed by supporting details.]
```

### Conclusion (5-8% of total)

1. **Summary**: Recap 3-5 key takeaways
2. **Reinforcement**: Restate primary keyword and main value
3. **Call to Action**: Clear next step for reader (use reader address if context loaded)
4. **Closing hook**: Connect back to opening theme

**Target**: 150-200 words

---

## Step 3: Quality Checklist Verification

After writing, verify:

### Content Quality
- [ ] Original, non-plagiarized content
- [ ] Accurate, fact-checked information
- [ ] Clear, concise writing style
- [ ] Active voice preferred
- [ ] Short paragraphs (3-4 sentences max)

### SEO Elements
- [ ] Primary keyword in first 100 words
- [ ] Primary keyword in at least one H2
- [ ] Natural keyword distribution (1-2% density)
- [ ] LSI keywords included naturally

### E-E-A-T Signals
- [ ] First-hand experience mentioned where relevant
- [ ] Expert perspective demonstrated
- [ ] Data and statistics cited
- [ ] Sources referenced

### Structure
- [ ] Hook in first paragraph
- [ ] Smooth transitions between sections
- [ ] Bullet points for lists
- [ ] Strong conclusion with CTA

### Context Compliance (if .seokit-context.md loaded)
- [ ] Author pronoun used consistently throughout
- [ ] Reader address used consistently throughout
- [ ] Products mentioned naturally (1-2 times, not forced)
- [ ] Writing notes applied as constraints

---

## Step 4: Generate Outputs

### 4.1 Save Markdown
Save article to: `./{keyword-slug}/article.md`

### 4.2 Generate DOCX
```bash
export SEOKIT_HOME="$HOME/.claude/seokit"
source "$SEOKIT_HOME/venv/bin/activate"
python "$SEOKIT_HOME/scripts/docx-generator.py" "./{keyword-slug}/article.md"
```

### 4.3 Generate Statistics
Analyze the article:
- Word count
- Keyword density
- Readability score
- Section breakdown

---

## Step 5: Final Report

Present completion summary:

```markdown
## Article Generation Complete

### Article Details
- **Title**: [H1 Title]
- **Primary Keyword**: [keyword]
- **Word Count**: X words
- **Target**: Y words
- **Sections**: X H2s, Y H3s

### SEO Metrics
- **Keyword Density**: X.X%
- **Primary Keyword in First 100 Words**: ✓/✗
- **Readability Score**: X/100 (Grade Level)

### Output Files
- **Markdown**: `./{keyword-slug}/article.md`
- **DOCX**: `./{keyword-slug}/article.docx`

### Checklist Compliance
- Content Quality: X/Y items ✓
- SEO Elements: X/Y items ✓
- E-E-A-T Signals: X/Y items ✓
- Structure: X/Y items ✓
- Context Compliance: X/Y items ✓ (if context loaded)

### Suggested Next Steps
1. Add featured image (suggested: [topic-related image])
2. Insert in-content images at: [specific locations]
3. Review and personalize examples for your audience
4. Add internal links to related pages
5. Create meta description (150-160 characters)
6. Prepare alt text for images
```

---

## Meta Description Generator

Generate a compelling meta description:
- Include primary keyword
- 150-160 characters
- Include value proposition
- End with subtle CTA or hook

Example format:
```
[Primary benefit] + [Secondary value] + [Keyword] + [CTA/hook]. [150-160 chars]
```

---

## Optional: Export for Review

If user needs to share for review:
1. DOCX file is ready for Google Docs / Word review
2. Consider adding comments in document for reviewer notes
3. Highlight areas needing SME (Subject Matter Expert) input
