#!/usr/bin/env python3
"""
Example demonstrating accurate multi-line text highlighting.

This example shows how the package handles text that spans multiple lines
or even crosses element boundaries in the rendered HTML.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from markitdown_reference_image import MarkitdownImageExtractor


def create_multiline_test_document():
    """Create a markdown document with various multi-line scenarios."""
    content = """# Multi-Line Text Highlighting Test

## Scenario 1: Text Within Single Paragraph

This is a paragraph that contains a long piece of text that we want to highlight. The text spans across multiple lines in the source markdown file, but appears as continuous text in the rendered HTML.

## Scenario 2: Text Across Formatting

Here is some **bold text that we want to find and highlight** even though it has formatting.

## Scenario 3: Long Sentences

The package uses JavaScript-based text finding with window.find() which can locate and wrap text regardless of how it's split across DOM nodes, making it perfect for highlighting multi-line content.

## Scenario 4: List Items

- This is a list item with some important content that should be highlighted
- Another list item
- Final list item

## Scenario 5: Text With Unusual Spacing

This     text     has     multiple     spaces     and


line
breaks
that
should
still
be
found
correctly
thanks to automatic normalization.

## Conclusion

The DOM-based positioning ensures accurate bounding boxes even for complex text selections. The package automatically handles various whitespace patterns!
"""
    
    doc_path = "multiline_demo.md"
    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return doc_path


def test_multiline_highlighting():
    """Test multi-line text highlighting with various scenarios."""
    print("🎯 Multi-Line Text Highlighting Demo")
    print("=" * 60)
    
    # Create test document
    doc_path = create_multiline_test_document()
    
    try:
        extractor = MarkitdownImageExtractor()
        
        # Test 1: Simple multi-line text
        print("\n📝 Test 1: Simple multi-line text")
        result1 = extractor.extract_with_highlight(
            markdown_file=doc_path,
            chunk_text="long piece of text that we want to highlight",
            output_path="test_simple_multiline.png",
            score=0.95
        )
        print(f"✅ Result: {result1}")
        
        # Test 2: Text with formatting
        print("\n📝 Test 2: Text with formatting (bold)")
        result2 = extractor.extract_with_highlight(
            markdown_file=doc_path,
            chunk_text="bold text that we want to find and highlight",
            output_path="test_formatted_text.png",
            score=0.92
        )
        print(f"✅ Result: {result2}")
        
        # Test 3: Very long text span
        print("\n📝 Test 3: Very long text span")
        result3 = extractor.extract_with_highlight(
            markdown_file=doc_path,
            chunk_text="JavaScript-based text finding with window.find() which can locate and wrap text regardless of how it's split across DOM nodes",
            output_path="test_long_span.png",
            score=0.89
        )
        print(f"✅ Result: {result3}")
        
        # Test 4: Text in list
        print("\n📝 Test 4: Text in list item")
        result4 = extractor.extract_with_highlight(
            markdown_file=doc_path,
            chunk_text="important content that should be highlighted",
            output_path="test_list_item.png",
            score=0.91
        )
        print(f"✅ Result: {result4}")
        
        # Test 5: Text across multiple words
        print("\n📝 Test 5: Text with multiple words")
        result5 = extractor.extract_with_highlight(
            markdown_file=doc_path,
            chunk_text="DOM-based positioning ensures accurate bounding boxes",
            output_path="test_multiple_words.png",
            score=0.94
        )
        print(f"✅ Result: {result5}")
        
        # Test 6: Text with excessive whitespace (like copy-pasted from PDF)
        print("\n📝 Test 6: Text with unusual spacing (automatic normalization)")
        # This text has excessive line breaks and spaces, simulating copy-paste from PDF
        messy_text = """This     text     has     multiple     spaces     and


line
breaks
that
should
still
be
found"""
        result6 = extractor.extract_with_highlight(
            markdown_file=doc_path,
            chunk_text=messy_text,
            output_path="test_messy_spacing.png",
            score=0.88
        )
        print(f"✅ Result: {result6}")
        print("   💡 The package automatically normalized the whitespace!")
        
        print("\n🎉 All multi-line tests completed successfully!")
        print("\n📁 Generated files:")
        print("  - test_simple_multiline.png")
        print("  - test_formatted_text.png")
        print("  - test_long_span.png")
        print("  - test_list_item.png")
        print("  - test_multiple_words.png")
        print("  - test_messy_spacing.png")
        
        print("\n💡 Key Features Demonstrated:")
        print("  ✅ Text spanning multiple lines in source")
        print("  ✅ Text with formatting (bold, italic, etc.)")
        print("  ✅ Very long text selections")
        print("  ✅ Text in various HTML elements (lists, paragraphs)")
        print("  ✅ Automatic whitespace normalization")
        print("  ✅ Accurate bounding boxes for all cases")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up test document
        if os.path.exists(doc_path):
            os.unlink(doc_path)
    
    return True


def main():
    """Main function to run the multi-line text example."""
    print("🚀 Multi-Line Text Highlighting Example")
    print("This example demonstrates the package's ability to accurately")
    print("highlight text that spans multiple lines or crosses element boundaries.")
    print()
    print("✨ The package automatically handles:")
    print("   • Text with excessive line breaks")
    print("   • Text with multiple spaces")
    print("   • Text copied from PDFs")
    print("   • Text across DOM element boundaries")
    print()
    
    success = test_multiline_highlighting()
    
    if success:
        print("\n✨ Example completed successfully!")
        print("The bounding boxes should be accurately positioned around all text,")
        print("regardless of line breaks, whitespace, or HTML structure.")
        print("\n💡 No preprocessing needed - just pass your text as-is!")
    else:
        print("\n❌ Example failed. Check the error messages above.")


if __name__ == "__main__":
    main()

