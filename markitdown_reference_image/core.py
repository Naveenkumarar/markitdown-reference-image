"""
Core module for markitdown image extraction functionality.
"""

import os
import tempfile
from pathlib import Path
from typing import Optional, Tuple, Union

from .text_finder import TextFinder
from .image_processor import ImageProcessor


class MarkitdownImageExtractor:
    """
    Main class for extracting images from markdown files and highlighting text chunks.
    
    This class coordinates the process of:
    1. Finding text chunks in markdown content
    2. Rendering markdown to HTML and capturing as image
    3. Drawing bounding boxes around found text
    4. Saving the result
    """
    
    def __init__(self, font_size: int = 16, line_height: int = 24, char_width: int = 9):
        """
        Initialize the extractor with required components.
        
        Args:
            font_size: Base font size in pixels for positioning calculations
            line_height: Line height including spacing in pixels
            char_width: Approximate character width in pixels
        """
        self.text_finder = TextFinder()
        self.image_processor = ImageProcessor(font_size, line_height, char_width)
    
    def _normalize_for_search(self, text: str) -> str:
        """
        Normalize text for searching by collapsing whitespace.
        
        This handles text that may have been copied from PDFs or markdown files
        with excessive line breaks and spacing.
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text with collapsed whitespace
        """
        import re
        # Collapse all whitespace (spaces, tabs, newlines) into single spaces
        normalized = re.sub(r'\s+', ' ', text)
        # Strip leading/trailing whitespace
        normalized = normalized.strip()
        # Lowercase for case-insensitive comparison
        normalized = normalized.lower()
        return normalized
    
    def _map_normalized_to_actual_positions(self, markdown_content: str, norm_start: int, norm_end: int) -> tuple:
        """
        Map positions from normalized content back to actual markdown content.
        
        Args:
            markdown_content: Original markdown
            norm_start: Start position in normalized content
            norm_end: End position in normalized content
            
        Returns:
            Tuple of (actual_start, actual_end)
        """
        # Build mapping from normalized to actual positions
        normalized = self._normalize_for_search(markdown_content)
        
        actual_pos = 0
        norm_pos = 0
        actual_start = None
        actual_end = None
        
        # Walk through original content character by character
        for actual_pos in range(len(markdown_content)):
            char = markdown_content[actual_pos]
            
            # Check if we've reached the start position
            if norm_pos == norm_start and actual_start is None:
                actual_start = actual_pos
            
            # Check if we've reached the end position
            if norm_pos == norm_end and actual_end is None:
                actual_end = actual_pos
                break
            
            # Advance normalized position based on the character
            if char.isspace():
                # Only count if previous wasn't also space (collapses whitespace)
                if norm_pos == 0 or normalized[norm_pos-1:norm_pos] != ' ':
                    if norm_pos < len(normalized):
                        norm_pos += 1
            else:
                if norm_pos < len(normalized) and normalized[norm_pos] == char.lower():
                    norm_pos += 1
        
        # Handle edge cases
        if actual_start is None:
            actual_start = 0
        if actual_end is None:
            actual_end = len(markdown_content)
        
        return (actual_start, actual_end)
    
    def _extract_chunk_by_first_last_words(self, markdown_content: str, chunk_text: str) -> tuple:
        """
        Extract chunk using first 10 and last 10 words approach.
        
        Args:
            markdown_content: Full markdown content
            chunk_text: Text chunk to find
            
        Returns:
            Tuple of (page_content, chunk_start_in_page, chunk_end_in_page)
        """
        # Get first 10 words
        chunk_words = chunk_text.split()
        first_10_words = ' '.join(chunk_words[:10])
        last_10_words = ' '.join(chunk_words[-10:])
        
        # Normalize both content and search phrases (collapse whitespace)
        normalized_content = self._normalize_for_search(markdown_content)
        normalized_first = self._normalize_for_search(first_10_words)
        normalized_last = self._normalize_for_search(last_10_words)
        
        # Find in normalized content
        start_pos = normalized_content.find(normalized_first)
        
        if start_pos == -1:
            # Try with fewer words
            for i in range(9, 3, -1):
                test_phrase = self._normalize_for_search(' '.join(chunk_words[:i]))
                start_pos = normalized_content.find(test_phrase)
                if start_pos != -1:
                    break
        
        if start_pos == -1:
            raise ValueError("Could not find start of chunk in markdown")
        
        # Find last 10 words in markdown (search from start_pos onwards)
        end_search_start = start_pos + len(normalized_first)
        end_pos = normalized_content.find(normalized_last, end_search_start)
        
        if end_pos == -1:
            # Try with fewer words
            for i in range(9, 3, -1):
                test_phrase = self._normalize_for_search(' '.join(chunk_words[-i:]))
                end_pos = normalized_content.find(test_phrase, end_search_start)
                if end_pos != -1:
                    end_pos += len(test_phrase)
                    break
        else:
            end_pos += len(normalized_last)
        
        if end_pos == -1:
            raise ValueError("Could not find end of chunk in markdown")
        
        # Now map normalized positions back to actual markdown positions
        actual_start, actual_end = self._map_normalized_to_actual_positions(
            markdown_content, 
            start_pos, 
            end_pos
        )
        
        # Extract the chunk from actual markdown
        chunk_in_md = markdown_content[actual_start:actual_end]
        
        # Add context before and after to center it on the page
        # Add ~300 chars before and after
        context_before_start = max(0, actual_start - 300)
        context_after_end = min(len(markdown_content), actual_end + 300)
        
        page_content = markdown_content[context_before_start:context_after_end]
        
        # Calculate where the chunk is within this page content
        chunk_start_in_page = actual_start - context_before_start
        chunk_end_in_page = actual_end - context_before_start
        
        return (page_content, chunk_start_in_page, chunk_end_in_page)
    
    def _extract_context_around_chunk_with_markers(self, markdown_content: str, chunk_text: str, context_lines: int = 5) -> tuple:
        """
        Extract markdown content with context and return chunk position markers.
        
        Returns:
            Tuple of (context_markdown, chunk_start_pos, chunk_end_pos)
        """
        context = self._extract_context_around_chunk(markdown_content, chunk_text, context_lines)
        
        # Now find where the chunk is within this context
        # Normalize both to find position
        normalized_context = self._normalize_for_search(context)
        normalized_chunk = self._normalize_for_search(chunk_text)
        
        chunk_pos = normalized_context.find(normalized_chunk)
        
        if chunk_pos == -1:
            
            # Try to find start and end separately
            chunk_words = normalized_chunk.split()
            
            # Find first few words
            start_phrase = ' '.join(chunk_words[:5])
            start_pos = normalized_context.find(start_phrase)
            
            # Find last few words  
            end_phrase = ' '.join(chunk_words[-5:])
            end_pos = normalized_context.find(end_phrase)
            
            if start_pos != -1 and end_pos != -1:
                chunk_pos = start_pos
                chunk_len = end_pos - start_pos + len(end_phrase)
            else:
                return (context, 0, len(context))
        else:
            chunk_len = len(normalized_chunk)
        
        # Map normalized positions back to actual positions in context
        # Build a mapping by processing character by character
        norm_to_actual = []
        actual_pos = 0
        
        for char in context:
            if not char.isspace() or (norm_to_actual and norm_to_actual[-1] != actual_pos):
                norm_to_actual.append(actual_pos)
            actual_pos += 1
        
        # Ensure we have enough mappings
        while len(norm_to_actual) < len(normalized_context):
            norm_to_actual.append(len(context))
        
        # Get actual start and end positions
        actual_start = norm_to_actual[min(chunk_pos, len(norm_to_actual)-1)]
        actual_end = norm_to_actual[min(chunk_pos + chunk_len - 1, len(norm_to_actual)-1)] + 1
        
        return (context, actual_start, actual_end)
    
    def _extract_context_around_chunk(self, markdown_content: str, chunk_text: str, context_lines: int = 5) -> str:
        """
        Extract markdown content with context around the chunk.
        Find the exact text in markdown and extract surrounding lines.
        
        Args:
            markdown_content: Full markdown content
            chunk_text: Text chunk to find (exact or normalized)
            context_lines: Number of lines before/after to include
            
        Returns:
            Markdown content with context around chunk
        """
        lines = markdown_content.split('\n')
        
        # Try to find the chunk text in the content
        # First normalize both for searching
        normalized_content = self._normalize_for_search(markdown_content)
        normalized_chunk = self._normalize_for_search(chunk_text)
        
        # Find position in normalized content
        pos = normalized_content.find(normalized_chunk)
        
        if pos == -1:
            # Try finding start and end by matching words
            chunk_words = chunk_text.split()
            
            # Find start: look for first 5 words
            start_words = [w.lower() for w in chunk_words[:5] if len(w) > 2]
            start_line = None
            
            for i, line in enumerate(lines):
                line_lower = line.lower()
                matches = sum(1 for w in start_words if w in line_lower)
                if matches >= min(3, len(start_words)):
                    start_line = i
                    break
            
            # Find end: look for last 5 words
            end_words = [w.lower() for w in chunk_words[-5:] if len(w) > 2]
            end_line = None
            
            if start_line is not None:
                # Search from start_line onwards
                for i in range(start_line, len(lines)):
                    line_lower = lines[i].lower()
                    matches = sum(1 for w in end_words if w in line_lower)
                    if matches >= min(3, len(end_words)):
                        end_line = i
                        break
            
            if start_line is not None:
                if end_line is None:
                    end_line = start_line + len(chunk_words) // 5  # Estimate
                
                context_start = max(0, start_line - context_lines)
                context_end = min(len(lines), end_line + context_lines + 1)
                return '\n'.join(lines[context_start:context_end])
            
            return markdown_content
        
        # Map position back to original lines by building normalized content line by line
        current_pos = 0
        start_line = None
        end_line = None
        
        for i, line in enumerate(lines):
            line_normalized = self._normalize_for_search(line)
            line_len = len(line_normalized)
            
            # Check if chunk starts in or before this line
            if start_line is None and current_pos <= pos < current_pos + line_len + 1:
                start_line = i
            
            # Check if chunk ends in or after this line
            if start_line is not None and current_pos + line_len >= pos + len(normalized_chunk):
                end_line = i
                break
            
            current_pos += line_len + 1  # +1 for space between lines
        
        if start_line is None:
            start_line = 0
        if end_line is None:
            end_line = len(lines) - 1
        
        # Extract with context
        # Make sure we include enough lines to cover the entire chunk
        lines_in_chunk = end_line - start_line + 1
        context_start = max(0, start_line - context_lines)
        context_end = min(len(lines), end_line + context_lines + 1)
        
        # Return the EXACT lines from markdown (no normalization)
        extracted = '\n'.join(lines[context_start:context_end])
        
        return extracted
    
    def find_text_in_markdown(
        self,
        markdown_file: Union[str, Path],
        search_query: str,
        context_lines: int = 5
    ) -> Optional[str]:
        """
        Find text in markdown file and return it with context.
        
        Args:
            markdown_file: Path to the markdown file
            search_query: Short text to search for
            context_lines: Number of lines before/after to include
            
        Returns:
            Found text with context, or None if not found
        """
        markdown_path = Path(markdown_file)
        if not markdown_path.exists():
            return None
            
        with open(markdown_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Normalize for searching
        normalized_content = self._normalize_for_search(content)
        normalized_query = self._normalize_for_search(search_query)
        
        # Find position
        pos = normalized_content.find(normalized_query)
        if pos == -1:
            return None
        
        # Map the position back to the original content
        # Count characters while preserving line structure
        lines = content.split('\n')
        current_pos = 0
        start_line = 0
        
        for i, line in enumerate(lines):
            line_normalized = self._normalize_for_search(line)
            line_len = len(line_normalized)
            
            if current_pos <= pos < current_pos + line_len + 1:
                start_line = i
                break
            
            current_pos += line_len + 1  # +1 for space/newline
        
        # Get context lines
        start = max(0, start_line - context_lines)
        end = min(len(lines), start_line + context_lines + 1)
        
        return '\n'.join(lines[start:end])
    
    def search_and_highlight(
        self,
        markdown_file: Union[str, Path],
        search_query: str,
        output_path: Optional[Union[str, Path]] = None,
        score: Optional[float] = None,
        context_lines: int = 10,
        **kwargs
    ) -> str:
        """
        Search for text in markdown and highlight it (convenience method).
        
        Args:
            markdown_file: Path to the markdown file
            search_query: Short text query to search for
            output_path: Path to save the output image
            score: Optional score to display
            context_lines: Lines of context to include around match
            **kwargs: Additional arguments
            
        Returns:
            str: Path to the saved image file
        """
        # Find the text with context
        found_text = self.find_text_in_markdown(
            markdown_file=markdown_file,
            search_query=search_query,
            context_lines=context_lines
        )
        
        if not found_text:
            # If not found with context, try just the search query
            found_text = search_query
        
        # Highlight it
        return self.extract_with_highlight(
            markdown_file=markdown_file,
            chunk_text=found_text,
            output_path=output_path,
            score=score,
            **kwargs
        )
    
    def extract_with_highlight(
        self,
        markdown_file: Union[str, Path],
        chunk_text: str,
        output_path: Optional[Union[str, Path]] = None,
        score: Optional[float] = None,
        **kwargs
    ) -> str:
        """
        Extract image from markdown file and highlight the specified chunk.
        
        Args:
            markdown_file: Path to the markdown file
            chunk_text: The text chunk to find and highlight
            output_path: Path to save the output image. If None, uses temp file
            score: Optional score to display in the bounding box
            **kwargs: Additional arguments for image processing
            
        Returns:
            str: Path to the saved image file
            
        Raises:
            ValueError: If chunk_text is not found in markdown file
            FileNotFoundError: If markdown file or output directory doesn't exist
        """
        # Read the markdown file
        markdown_path = Path(markdown_file)
        if not markdown_path.exists():
            raise FileNotFoundError(f"Markdown file '{markdown_file}' not found")
        
        with open(markdown_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # Basic validation - check if some key words exist
        chunk_words = [w for w in chunk_text.split() if len(w) > 3]
        if len(chunk_words) >= 3:
            normalized_content = self._normalize_for_search(markdown_content)
            found_words = sum(1 for word in chunk_words[:10] if word.lower() in normalized_content)
            if found_words < 3:
                raise ValueError(f"Text doesn't appear to exist in document. Found only {found_words} matching words.")
        
        # Extract context using first/last words method
        try:
            context_markdown, chunk_start, chunk_end = self._extract_chunk_by_first_last_words(
                markdown_content, 
                chunk_text
            )
            
            # Convert markdown to HTML with text highlighting
            # Now we know exactly where the chunk is in the context
            html_content = self._markdown_to_html_with_marked_chunk(context_markdown, chunk_start, chunk_end)
            
            # Capture image and get bounding box coordinates from the rendered page
            image_path, bbox_coords = self._html_to_image_with_bbox(html_content)
        except RuntimeError as e:
            raise RuntimeError(f"Image extraction failed: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error during image extraction: {e}")
        
        # Draw bounding box using actual coordinates
        result_path = self.image_processor.draw_bounding_box_from_coords(
            image_path=image_path,
            bbox_coords=bbox_coords,
            output_path=output_path,
            score=score,
            **kwargs
        )
        
        # Clean up temporary files if we created them
        if output_path is None and image_path != result_path:
            try:
                os.unlink(image_path)
            except OSError:
                pass  # Ignore cleanup errors
        
        return result_path
    
    def _markdown_to_html_with_marked_chunk(self, markdown_content: str, chunk_start: int, chunk_end: int) -> str:
        """
        Convert markdown to HTML and mark the chunk position.
        
        Args:
            markdown_content: Markdown content
            chunk_start: Start position of chunk in markdown
            chunk_end: End position of chunk in markdown
            
        Returns:
            HTML with marked chunk
        """
        import markdown
        
        # Insert markers around the chunk in markdown
        before = markdown_content[:chunk_start]
        chunk = markdown_content[chunk_start:chunk_end]
        after = markdown_content[chunk_end:]
        
        # Insert marker spans at start and end
        # Keep them simple so they survive markdown conversion
        start_marker = '<span id="chunk-start"></span>'
        end_marker = '<span id="chunk-end"></span>'
        
        marked_markdown = before + start_marker + chunk + end_marker + after
        
        # Convert to HTML
        html = markdown.markdown(marked_markdown, extensions=['extra'])
        
        # Wrap in HTML structure
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                @page {{
                    size: A4;
                    margin: 0;
                }}
                
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    width: 794px;
                    min-height: 1123px;
                    margin: 0;
                    padding: 40px;
                    box-sizing: border-box;
                    background: white;
                }}
                
                h1, h2, h3, h4, h5, h6 {{
                    color: #333;
                }}
                
                code {{
                    background-color: #f4f4f4;
                    padding: 2px 4px;
                    border-radius: 3px;
                }}
                
                pre {{
                    background-color: #f4f4f4;
                    padding: 10px;
                    border-radius: 5px;
                    overflow-x: auto;
                }}
                
                #highlight-target {{
                    position: relative !important;
                    display: inline !important;
                }}
            </style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """
        
        return full_html
    
    def _markdown_to_html(self, markdown_content: str, target_text: str = None, highlight_full_chunk: bool = False) -> str:
        """
        Convert markdown content to HTML with optional text marking.
        Uses JavaScript to find and wrap text after page load for better multi-line support.
        
        Args:
            markdown_content: Raw markdown content
            target_text: Optional text to mark for positioning
            
        Returns:
            str: HTML content with JavaScript to mark target text
        """
        import markdown
        import json
        
        # Convert markdown to HTML
        html = markdown.markdown(markdown_content)
        
        # Prepare JavaScript to mark text (if provided)
        mark_script = ""
        if target_text:
            # Escape the target text for JavaScript
            escaped_target = json.dumps(target_text)
            
            # Read the JavaScript from external file
            script_path = Path(__file__).parent / 'utils' / 'script.js'
            with open(script_path, 'r', encoding='utf-8') as f:
                js_content = f.read()
            
            # Replace TARGET_TEXT placeholder with actual value
            js_with_target = js_content.replace('TARGET_TEXT', escaped_target)
            
            mark_script = f"""
            <script>
                {js_with_target}
            </script>
            """
        
        # Wrap in basic HTML structure for better rendering
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                @page {{
                    size: A4;
                    margin: 0;
                }}
                
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    width: 794px;
                    min-height: 1123px;
                    margin: 0;
                    padding: 40px;
                    box-sizing: border-box;
                    background: white;
                }}
                
                h1, h2, h3, h4, h5, h6 {{
                    color: #333;
                }}
                
                code {{
                    background-color: #f4f4f4;
                    padding: 2px 4px;
                    border-radius: 3px;
                }}
                
                pre {{
                    background-color: #f4f4f4;
                    padding: 10px;
                    border-radius: 5px;
                    overflow-x: auto;
                }}
                
                #highlight-target {{
                    position: relative;
                    display: inline;
                }}
            </style>
            {mark_script}
        </head>
        <body>
            {html}
        </body>
        </html>
        """
        
        return full_html
    
    def _html_to_image_with_bbox(self, html_content: str) -> Tuple[str, Tuple[int, int, int, int]]:
        """
        Convert HTML to image and get bounding box coordinates of marked element.
        
        Args:
            html_content: HTML content with marked target element
            
        Returns:
            Tuple of (image_path, (left, top, right, bottom))
        """
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.common.by import By
            from webdriver_manager.chrome import ChromeDriverManager
        except ImportError as e:
            raise RuntimeError(f"Selenium not available: {e}")
        
        html_file_path = None
        driver = None
        
        try:
            # Create temporary HTML file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                html_file_path = f.name
            
            if not html_file_path or not os.path.exists(html_file_path):
                raise RuntimeError("Failed to create temporary HTML file")
            
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            # A4 size at 96 DPI: 794x1123 pixels
            chrome_options.add_argument('--window-size=794,1123')
            
            # Setup Chrome driver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Load the HTML file
            file_url = f"file://{os.path.abspath(html_file_path)}"
            driver.get(file_url)
            
            # Wait for JavaScript to execute and mark the text
            # Give more time for the window.find() and DOM manipulation
            import time
            time.sleep(2)  # Wait for page load and JavaScript execution
            
            # Get bounding box coordinates of the marked element
            bbox_coords = None
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    # Use JavaScript to find markers, create wrapper, and get bounding rect
                    bbox_rect = driver.execute_script("""
                        const startMarker = document.getElementById('chunk-start');
                        const endMarker = document.getElementById('chunk-end');
                        
                        if (!startMarker || !endMarker) {
                            console.error('❌ Markers not found!', 'start:', !!startMarker, 'end:', !!endMarker);
                            return null;
                        }
                        
                        console.log('✓ Found both markers');
                        console.log('  Start marker:', startMarker.outerHTML.substring(0, 100));
                        console.log('  End marker:', endMarker.outerHTML.substring(0, 100));
                        
                        // Create a range from start to end marker
                        const range = document.createRange();
                        range.setStartAfter(startMarker);
                        range.setEndBefore(endMarker);
                        
                        const rangeText = range.toString();
                        console.log('Range text length:', rangeText.length);
                        console.log('Range text (first 50):', rangeText.substring(0, 50));
                        console.log('Range text (last 50):', rangeText.substring(rangeText.length - 50));
                        
                        const rect = range.getBoundingClientRect();
                        console.log('Range rect:', JSON.stringify({
                            x: rect.x, y: rect.y, w: rect.width, h: rect.height
                        }));
                        
                        // Try to create a visual wrapper for the bounding box drawing
                        // This is just for visualization, the rect is already captured
                        const wrapper = document.createElement('span');
                        wrapper.id = 'highlight-target';
                        wrapper.style.cssText = 'position: relative; display: inline;';
                        
                        try {
                            // Clone the range to avoid modifying the original
                            const cloneRange = range.cloneRange();
                            cloneRange.surroundContents(wrapper);
                            console.log('✓ Created highlight-target wrapper');
                        } catch (e) {
                            console.log('⚠ Could not wrap (multi-element span):', e.message);
                            // Fallback: manually insert wrapper
                            try {
                                const fallbackRange = range.cloneRange();
                                const fragment = fallbackRange.extractContents();
                                wrapper.appendChild(fragment);
                                fallbackRange.insertNode(wrapper);
                                console.log('✓ Created highlight-target using manual insertion');
                            } catch (e2) {
                                console.log('⚠ Manual insertion also failed:', e2.message);
                                // Give up on wrapper, just ensure the element exists for the draw_box code
                                document.body.appendChild(wrapper);
                                console.log('✓ Added dummy highlight-target to body');
                            }
                        }
                        
                        return {
                            x: rect.x,
                            y: rect.y,
                            width: rect.width,
                            height: rect.height,
                            top: rect.top,
                            left: rect.left
                        };
                    """)
                    
                    if bbox_rect and bbox_rect['width'] > 0 and bbox_rect['height'] > 0:
                        left = int(bbox_rect['left'])
                        top = int(bbox_rect['top'])
                        right = int(bbox_rect['left'] + bbox_rect['width'])
                        bottom = int(bbox_rect['top'] + bbox_rect['height'])
                    
                    bbox_coords = (left, top, right, bottom)
                    break
                except Exception as e:
                    if attempt < max_attempts - 1:
                        time.sleep(0.5)  # Wait a bit more
                    else:
                        raise RuntimeError(f"Failed to get bounding box after {max_attempts} attempts")
            
            # Take screenshot
            screenshot = driver.get_screenshot_as_png()
            
            if not screenshot:
                raise RuntimeError("Failed to capture screenshot")
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                f.write(screenshot)
                image_path = f.name
            
            if not image_path or not os.path.exists(image_path):
                raise RuntimeError("Failed to save screenshot")
            
            return image_path, bbox_coords
                
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass
            
            if html_file_path and os.path.exists(html_file_path):
                try:
                    os.unlink(html_file_path)
                except OSError:
                    pass
    
    def _html_to_image(self, html_content: str) -> str:
        """
        Convert HTML content to image using Selenium.
        
        Args:
            html_content: HTML content to render
            
        Returns:
            str: Path to the generated image file
            
        Raises:
            RuntimeError: If Chrome/Selenium setup fails
        """
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
        except ImportError as e:
            raise RuntimeError(f"Selenium not available: {e}. Please install with: pip install selenium webdriver-manager")
        
        # Create temporary HTML file
        html_file_path = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                html_file_path = f.name
            
            if not html_file_path or not os.path.exists(html_file_path):
                raise RuntimeError("Failed to create temporary HTML file")
            
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1200,800')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-plugins')
            
            driver = None
            try:
                # Setup Chrome driver
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
                
                # Load the HTML file
                file_url = f"file://{os.path.abspath(html_file_path)}"
                driver.get(file_url)
                
                # Wait for page to load
                driver.implicitly_wait(3)
                
                # Take screenshot
                screenshot = driver.get_screenshot_as_png()
                
                if not screenshot:
                    raise RuntimeError("Failed to capture screenshot")
                
                # Save to temporary file
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                    f.write(screenshot)
                    image_path = f.name
                
                if not image_path or not os.path.exists(image_path):
                    raise RuntimeError("Failed to save screenshot")
                
                return image_path
                    
            finally:
                if driver:
                    try:
                        driver.quit()
                    except Exception:
                        pass
                
        except Exception as e:
            raise RuntimeError(f"Failed to convert HTML to image: {e}")
            
        finally:
            # Clean up HTML file
            if html_file_path and os.path.exists(html_file_path):
                try:
                    os.unlink(html_file_path)
                except OSError:
                    pass
