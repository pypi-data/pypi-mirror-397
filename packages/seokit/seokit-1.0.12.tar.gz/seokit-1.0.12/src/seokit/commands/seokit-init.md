Initialize SEOKit workspace context for your project.

Collects business context via interactive questionnaire and saves to `.seokit-context.md`. This context is automatically used by `/create-outline`, `/optimize-outline`, and `/write-seo` commands.

---

## Step 1: Detect Existing Context

Check if `.seokit-context.md` exists in current working directory:

```bash
[ -f ".seokit-context.md" ] && echo "EXISTS" || echo "NOT_FOUND"
```

### If EXISTS:
Ask user: **"Đã tìm thấy file `.seokit-context.md`. Bạn muốn cập nhật nó? [Y/n]"**

- **Y (default)**: Continue to questionnaire, pre-fill answers from existing file
- **n**: Exit with message "Đã giữ nguyên context hiện tại."

### If NOT_FOUND:
Continue to Step 2 (Questionnaire).

---

## Step 2: Interactive Questionnaire

Ask user the following 8 questions in Vietnamese. Collect answers one by one.

### Q1: Loại website
**Question**: "Loại website của bạn?"
**Options**:
- `personal_blog` - Blog cá nhân
- `business_website` - Website doanh nghiệp (default)
- `e_commerce` - Thương mại điện tử
- `news` - Tin tức
- `other` - Khác

### Q2: URL website
**Question**: "URL website của bạn? (VD: https://example.com)"
**Type**: Text input
**Validation**: None (accept any input)

### Q3: Xưng hô tác giả
**Question**: "Bạn xưng gì khi viết bài?"
**Options**:
- `mình` - Mình (thân mật)
- `tôi` - Tôi (trang trọng cá nhân)
- `chúng tôi` - Chúng tôi (đại diện công ty) (default)
- `[custom]` - Khác (cho phép nhập tùy chọn)

### Q4: Gọi độc giả
**Question**: "Gọi độc giả là gì?"
**Options**:
- `bạn` - Bạn (thân thiện) (default)
- `anh/chị` - Anh/chị (lịch sự)
- `quý khách` - Quý khách (trang trọng)
- `[custom]` - Khác (cho phép nhập tùy chọn)

### Q5: Lĩnh vực
**Question**: "Website thuộc lĩnh vực nào?"
**Options**:
- `tech` - Công nghệ
- `health` - Sức khỏe
- `finance` - Tài chính
- `education` - Giáo dục
- `lifestyle` - Phong cách sống
- `food` - Ẩm thực
- `travel` - Du lịch
- `fashion` - Thời trang
- `real_estate` - Bất động sản
- `other` - Khác

### Q6: Sản phẩm/Dịch vụ
**Question**: "Liệt kê các sản phẩm/dịch vụ muốn nhắc đến trong bài viết (mỗi dòng một sản phẩm):"
**Type**: Multi-line text input
**Format**: Accept multiple lines, each line is one product/service

### Q7: Thông tin bổ sung (Optional)
**Question**: "Thông tin bổ sung về doanh nghiệp? (VD: thành lập năm nào, USP...)"
**Type**: Text input
**Default**: Empty (skip if user presses Enter)

### Q8: Lưu ý viết bài (Optional)
**Question**: "Lưu ý khi viết bài? (VD: tránh từ ngữ nào, phong cách...)"
**Type**: Text input
**Default**: Empty (skip if user presses Enter)

---

## Step 3: Generate Context File

Create `.seokit-context.md` in current working directory with collected data:

```markdown
# SEOKit Workspace Context

## Website Info
- **Type**: [Q1 answer]
- **URL**: [Q2 answer]
- **Industry**: [Q5 answer]

## Voice & Tone
- **Author pronoun**: [Q3 answer]
- **Reader address**: [Q4 answer]

## Products/Services
[Q6 answers - each on new line with bullet point]
- Product 1
- Product 2
- ...

## Writing Notes
[Q8 answer or "Không có" if empty]

## Additional Info
[Q7 answer or "Không có" if empty]
```

---

## Step 4: Confirmation

After generating file:

1. Display the generated content to user
2. Show message: **"Đã tạo file `.seokit-context.md` thành công!"**
3. Explain: "Context này sẽ được sử dụng tự động bởi các lệnh `/create-outline`, `/optimize-outline`, và `/write-seo`."

---

## Usage Notes

- Run this command once per project/workspace
- Context file can be edited manually if needed
- Re-run `/seokit-init` anytime to update context
- Other SEO commands will auto-detect and load this context

---

## Next Steps

After initialization:
1. Run `/search-intent [keyword]` to start SEO research
2. Or run existing SEO workflow if research already done
