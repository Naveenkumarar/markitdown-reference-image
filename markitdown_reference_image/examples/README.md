# Examples for markitdown-reference-image

This directory contains example code demonstrating how to use the markitdown-reference-image package.

## 📚 Available Examples

### Basic Usage Examples

#### 1. `basic_extraction.py` - Basic Image Extraction
Shows the most basic usage pattern:

**Run it:**
```bash
python -m markitdown_reference_image.examples.basic_extraction
```

#### 2. `with_score.py` - Adding Scores to Bounding Boxes
Shows how to add scores to bounding boxes:

**Run it:**
```bash
python -m markitdown_reference_image.examples.with_score
```

#### 3. `custom_styling.py` - Custom Styling Options
Shows how to customize the appearance:

**Run it:**
```bash
python -m markitdown_reference_image.examples.custom_styling
```

### Advanced Usage Examples

#### 4. `batch_processing.py` - Batch Processing Multiple Files
Shows how to process multiple markdown files:

**Run it:**
```bash
python -m markitdown_reference_image.examples.batch_processing
```

#### 5. `component_usage.py` - Using Individual Components
Shows how to use TextFinder and ImageProcessor separately:

**Run it:**
```bash
python -m markitdown_reference_image.examples.component_usage
```

#### 6. `error_handling.py` - Proper Error Handling
Shows proper error handling patterns:

**Run it:**
```bash
python -m markitdown_reference_image.examples.error_handling
```

### Command Line Examples

#### 7. `cli_basic.py` - Basic Command Line Usage
Shows basic CLI usage:

**Run it:**
```bash
python -m markitdown_reference_image.examples.cli_basic
```

#### 8. `cli_with_score.py` - CLI with Score Display
Shows CLI usage with scores:

**Run it:**
```bash
python -m markitdown_reference_image.examples.cli_with_score
```

#### 9. `cli_custom_styling.py` - CLI with Custom Styling
Shows CLI usage with custom styling:

**Run it:**
```bash
python -m markitdown_reference_image.examples.cli_custom_styling
```

### Advanced Features Examples

#### 10. `improved_positioning.py` - Enhanced Bounding Box Positioning
Shows the improved positioning algorithm with custom font metrics:

**Run it:**
```bash
python -m markitdown_reference_image.examples.improved_positioning
```

#### 11. `multiline_text_example.py` - Multi-Line Text Highlighting
Demonstrates accurate highlighting of text that spans multiple lines or crosses element boundaries:

**Run it:**
```bash
python -m markitdown_reference_image.examples.multiline_text_example
```

## 🚀 Quick Start

### Basic Python Usage
```python
from markitdown_reference_image import MarkitdownImageExtractor

extractor = MarkitdownImageExtractor()
image_path = extractor.extract_with_highlight(
    markdown_file="document.md",
    chunk_text="text to find",
    output_path="output.png",
    score=0.85
)
```

### Command Line Usage
```bash
markitdown-extract document.md "text to find" -o output.png -s 0.85
```

## 📋 Prerequisites

Before running the examples:

1. **Install the package:**
   ```bash
   pip install -e .
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Have Chrome browser installed** (required for image extraction)

## 🎯 Example Outputs

The examples will create various output images:

- `highlighted_output.png` - Basic extraction
- `highlighted_with_score.png` - With score display
- `custom_styled_output.png` - Custom styling
- `batch_output/` - Batch processing results
- Various CLI output files

## 💡 Tips for Users

### For Python Users:
- Use the `MarkitdownImageExtractor` class for most use cases
- Access individual components (`TextFinder`, `ImageProcessor`) for custom workflows
- Implement proper error handling for production use
- Use `Path` objects for better file handling

### For Command Line Users:
- Use quotes around text with spaces
- RGB values for colors are space-separated
- Use `--help` to see all available options
- Combine with shell scripts for batch processing

### For Both:
- Make sure your markdown files exist before processing
- Check that the text you're looking for actually exists in the file
- Experiment with different styling options
- Use temporary files when you don't need to keep the output

## 🔧 Customization

### Custom Styling Options:
```python
extractor.extract_with_highlight(
    markdown_file="doc.md",
    chunk_text="text",
    output_path="output.png",
    score=0.9,
    box_color=(255, 0, 0),      # Red box
    box_width=5,                # Thick border
    score_color=(255, 255, 0),  # Yellow text
    score_bg_color=(0, 0, 0)    # Black background
)
```

### Batch Processing:
```python
files = ["doc1.md", "doc2.md", "doc3.md"]
texts = ["text1", "text2", "text3"]

for file, text in zip(files, texts):
    extractor.extract_with_highlight(
        markdown_file=file,
        chunk_text=text,
        output_path=f"output_{file}.png"
    )
```

## 🐛 Troubleshooting

### Common Issues:

1. **"Chunk text not found"**
   - Check that the text exists in your markdown file
   - Try using a shorter, more specific text chunk
   - Check for extra spaces or formatting

2. **"File not found"**
   - Verify the markdown file path is correct
   - Use absolute paths if needed

3. **Chrome/Selenium errors**
   - Make sure Chrome browser is installed
   - The package will automatically download ChromeDriver

4. **Import errors**
   - Make sure the package is installed: `pip install -e .`
   - Check that all dependencies are installed

## 📖 More Information

- See the main package documentation in the root README.md
- Check the API documentation in the docs/ directory
- Look at the source code for more advanced usage patterns

## 🤝 Contributing

If you create useful examples, consider contributing them to the package by:

1. Adding your example to this directory
2. Updating this README.md
3. Following the existing code style and documentation patterns
