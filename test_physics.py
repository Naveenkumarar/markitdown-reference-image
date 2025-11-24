#!/usr/bin/env python3
"""Test script for physics document multiline text."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from markitdown_reference_image import MarkitdownImageExtractor

markdown_file = "/Users/naveen/Downloads/development/sketch/sketch-backend/data/68a6415116eeed84df698d2e/physics99/output/iesc109.md"

# Your original text with line breaks
text = """water  is  1  g  cm–3,  will  the  substance  float  or  sink?  \n22. The  volume  of  a  500  g  sealed  packet  is  350  cm3.  Will  the\npacket  float  or  sink  in  water  if  the  density  of  water  is  1  g\ncm–3?  What  will  be  the  mass  of  the  water  displaced  by  this\npacket?  \n112  \nSCIENCE  \nReprint 2025-26"""

print("Testing physics document with multiline text...")
print(f"Text length: {len(text)} chars, {text.count(chr(10))} newlines")

try:
    extractor = MarkitdownImageExtractor()
    result = extractor.extract_with_highlight(
        markdown_file=markdown_file,
        chunk_text=text,
        output_path="physics_output.png",
        score=0.90
    )
    print(f"✅ SUCCESS! Image saved to: {result}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

