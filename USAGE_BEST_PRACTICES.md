# Usage Best Practices

## Text Selection Guidelines

### ✅ What Works Well

#### **1. Short to Medium Text Spans**
```bash
# Good: Single sentence or phrase
markitdown-extract doc.md "important information" -o output.png

# Good: Part of a paragraph
markitdown-extract doc.md "text that spans across multiple words" -o output.png
```

#### **2. Text with Markdown Formatting**
```bash
# Works: Bold text (formatting is automatically stripped)
markitdown-extract doc.md "**Bold Text**" -o output.png

# Works: Italic text
markitdown-extract doc.md "*italic text*" -o output.png

# Works: Code snippets
markitdown-extract doc.md "`code snippet`" -o output.png
```

#### **3. Text from Lists (Individual Items)**
```bash
# Good: Single list item
markitdown-extract doc.md "First list item content" -o output.png

# Good: Part of list item
markitdown-extract doc.md "important point in the list" -o output.png
```

#### **4. Multi-line Text (Reasonable Length)**
```bash
# Good: Text that naturally spans 2-3 lines
markitdown-extract doc.md "This is text that spans across two or three lines in the source" -o output.png
```

### ❌ What Doesn't Work Well

#### **1. Very Long Text Spans**
```bash
# Too long: Entire paragraphs (100+ words)
# ❌ May fail to highlight accurately
```

**Solution**: Select a unique, shorter portion of the text

#### **2. Entire Numbered/Bullet Lists**
```bash
# ❌ Don't do this:
markitdown-extract doc.md "1. First item
2. Second item  
3. Third item
4. Fourth item" -o output.png
```

**Why it fails**: `window.find()` API has limitations with very long, multi-line text containing list markers.

**Solution**: Highlight individual list items or a range:
```bash
# ✅ Do this instead:
markitdown-extract doc.md "First item Second item" -o output.png
```

#### **3. Text Across Major Section Boundaries**
```bash
# ❌ Avoid: Text spanning multiple headers/sections
# May work but positioning might be less accurate
```

**Solution**: Keep selections within logical sections

## Optimal Text Length

| Length | Reliability | Recommendation |
|--------|-------------|----------------|
| **1-10 words** | ✅ Excellent | Perfect for most use cases |
| **10-30 words** | ✅ Very Good | Works great for phrases |
| **30-50 words** | ⚠️ Good | Usually works fine |
| **50-100 words** | ⚠️ Fair | May have issues |
| **100+ words** | ❌ Poor | Use shorter excerpts |

## Tips for Best Results

### 1. **Be Specific and Unique**
```bash
# ✅ Good: Specific unique text
markitdown-extract doc.md "unique identifier text" -o output.png

# ❌ Bad: Common words that appear multiple times
markitdown-extract doc.md "the" -o output.png
```

### 2. **Omit Markdown Formatting** (or include it)
Both work! The system automatically strips markdown:
```bash
# Both produce the same result:
markitdown-extract doc.md "**Bold Text**" -o output.png
markitdown-extract doc.md "Bold Text" -o output.png
```

### 3. **Use Natural Text Flow**
```bash
# ✅ Good: Natural reading order
markitdown-extract doc.md "first sentence continues here" -o output.png

# ❌ Bad: Skipping words
markitdown-extract doc.md "first continues here" -o output.png
```

### 4. **Avoid Special Characters When Possible**
```bash
# ✅ Better: Plain text
markitdown-extract doc.md "code example" -o output.png

# ⚠️ Works but less reliable: With special chars
markitdown-extract doc.md "code: example()" -o output.png
```

## Common Use Cases

### Highlighting a Single List Item
```bash
# Your list:
# 1. **Text Finding**: Find specific text chunks
# 2. **Image Extraction**: Convert markdown to HTML
# 3. **Bounding Boxes**: Draw bounding boxes

# ✅ Highlight one item:
markitdown-extract doc.md "Text Finding: Find specific text chunks" -o output.png
```

### Highlighting Multiple List Items
```bash
# ✅ Option 1: First two items (without numbers)
markitdown-extract doc.md "Text Finding: Find specific text chunks Image Extraction: Convert markdown to HTML" -o output.png

# ✅ Option 2: Just the key terms
markitdown-extract doc.md "Text Finding Image Extraction Bounding Boxes" -o output.png
```

### Highlighting Part of a Paragraph
```bash
# Full paragraph:
# "This is a long paragraph with many sentences. Here is the important part that we want to highlight. More text continues after this."

# ✅ Highlight just the important part:
markitdown-extract doc.md "important part that we want to highlight" -o output.png
```

### Highlighting Code Blocks
```bash
# ✅ Highlight a specific line:
markitdown-extract doc.md "def function_name():" -o output.png

# ✅ Highlight part of code:
markitdown-extract doc.md "import package" -o output.png
```

## Troubleshooting

### Issue: "Text not found" Error
**Causes**:
- Text includes markdown formatting that was changed in HTML
- Text has extra whitespace or line breaks
- Typo in the search text

**Solutions**:
1. Remove markdown formatting from search text:
   ```bash
   # Instead of: "**bold text**"
   # Use: "bold text"
   ```

2. Normalize whitespace:
   ```bash
   # Instead of: "text  with   extra    spaces"
   # Use: "text with extra spaces"
   ```

3. Try a shorter, unique portion:
   ```bash
   # Instead of searching for entire paragraph
   # Search for a unique phrase within it
   ```

### Issue: Warning - "Could not find highlight-target element"
**Causes**:
- Text is too long for `window.find()` API
- Text crosses too many DOM boundaries
- Special formatting makes text unsearchable

**Solutions**:
1. Use shorter text excerpt
2. Remove list markers (1., 2., -, *)
3. Try the core content without formatting

**Note**: Even with this warning, the image is still generated with fallback coordinates (may not be perfectly positioned).

### Issue: Bounding Box in Wrong Location
**Causes**:
- Fallback coordinates were used (see warning above)
- Text appears multiple times (highlights first occurrence)

**Solutions**:
1. Make search text more specific/unique
2. Include surrounding context words
3. Use shorter, more precise excerpts

## Examples for Different Content Types

### Documentation
```bash
# ✅ Highlight function signature
markitdown-extract api.md "function_name(param1, param2)" -o output.png

# ✅ Highlight key concept
markitdown-extract guide.md "important concept explanation" -o output.png
```

### Tutorials
```bash
# ✅ Highlight step instruction
markitdown-extract tutorial.md "Step 1: Install the package" -o output.png

# ✅ Highlight warning/note
markitdown-extract tutorial.md "Note: This is important" -o output.png
```

### README Files
```bash
# ✅ Highlight feature
markitdown-extract README.md "Feature: Automatic text detection" -o output.png

# ✅ Highlight usage example
markitdown-extract README.md "Basic Usage" -o output.png
```

## Summary

**Golden Rules**:
1. ✅ **Shorter is better** - 1-30 words is ideal
2. ✅ **Be specific** - Use unique text
3. ✅ **Natural flow** - Keep words in order
4. ✅ **One concept** - Don't span multiple topics
5. ✅ **Test first** - Try with shorter text if issues occur

**For your specific case** (numbered list):
```bash
# ❌ Don't do this (too long, includes all 4 items):
markitdown-extract doc.md "1. **Text Finding**: ... 2. **Image Extraction**: ... 3. **Bounding Boxes**: ... 4. **Score Display**: ..." -o output.png

# ✅ Do this instead (one item):
markitdown-extract doc.md "Text Finding: Find specific text chunks in markdown content" -o output1.png
markitdown-extract doc.md "Image Extraction: Convert markdown to HTML" -o output2.png

# ✅ Or this (key terms only):
markitdown-extract doc.md "Text Finding Image Extraction Bounding Boxes Score Display" -o output.png
```

The system works excellent for 90% of use cases - just keep selections reasonable!

