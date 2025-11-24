// Function to normalize text (remove extra whitespace, lowercase)
function normalizeText(text) {
    return text.replace(/\s+/g, ' ').trim().toLowerCase();
}

// Function to strip markdown formatting characters
function stripMarkdown(text) {
    return text
        .replace(/\*\*(.+?)\*\*/g, '$1')  // Bold
        .replace(/\*(.+?)\*/g, '$1')       // Italic
        .replace(/__(.+?)__/g, '$1')         // Bold alt
        .replace(/_(.+?)_/g, '$1')           // Italic alt
        .replace(/`(.+?)`/g, '$1')           // Code
        .replace(/~~(.+?)~~/g, '$1')         // Strikethrough
        .replace(/^#+\s+/gm, '')            // Headers
        .replace(/^[0-9]+\.\s+/gm, '')     // Numbered lists
        .replace(/^[-*+]\s+/gm, '')         // Bullet lists
        .replace(/\[(.+?)\]\(.+?\)/g, '$1') // Links
        .trim();
}

// Function to generate all possible search variants
function generateSearchVariants(text) {
    const variants = [];
    
    // Strip markdown first
    const stripped = stripMarkdown(text);
    
    // Fully normalized (collapse all whitespace)
    const fullyNormalized = stripped.replace(/\s+/g, ' ').trim();
    
    // For very long text, also create a unique signature (first + middle + last parts)
    if (fullyNormalized.length > 100) {
        const words = fullyNormalized.split(' ');
        // Create a signature from start, middle, and end
        const signatureWords = [
            ...words.slice(0, 5),  // First 5 words
            ...words.slice(Math.floor(words.length / 2) - 2, Math.floor(words.length / 2) + 3),  // Middle 5 words
            ...words.slice(-5)  // Last 5 words
        ];
        const signature = signatureWords.join(' ');
        variants.push(signature);
        console.log('Added signature variant:', signature.substring(0, 80));
    }
    
    // Add full normalized
    variants.push(fullyNormalized);
    
    // Replace newlines with spaces
    variants.push(text.replace(/[\n\r\t]+/g, ' ').trim());
    variants.push(stripped.replace(/[\n\r\t]+/g, ' ').trim());
    
    // Original fully normalized
    variants.push(text.replace(/\s+/g, ' ').trim());
    
    // Original text
    variants.push(text);
    variants.push(stripped);
    
    // Remove duplicate variants and empty strings
    const unique = [...new Set(variants)].filter(v => v && v.trim().length > 0);
    
    // Sort by length (try longer matches first)
    unique.sort((a, b) => b.length - a.length);
    
    console.log('Generated ' + unique.length + ' variants, lengths:', unique.map(v => v.length));
    
    return unique;
}

// Function to find text using multiple strategies
function findTextInDocument(searchText) {
    const bodyElement = document.body;
    const fullText = bodyElement.innerText || bodyElement.textContent;
    const normalizedFull = normalizeText(fullText);
    
    // Generate search variants
    const variants = generateSearchVariants(searchText);
    
    // Filter out variants that are too short (likely to match wrong text)
    const MIN_LENGTH = 20;  // Require at least 20 chars
    const longVariants = variants.filter(v => v.trim().length >= MIN_LENGTH);
    
    if (longVariants.length === 0) {
        console.warn('All variants too short, using original variants');
        // Fall back to original variants if all are too short
        longVariants.push(...variants);
    }
    
    // First check if any variant exists in the document (for debugging)
    let bestVariant = null;
    for (const variant of longVariants) {
        const normalized = normalizeText(variant);
        if (normalized.length >= MIN_LENGTH && normalizedFull.indexOf(normalized) !== -1) {
            bestVariant = variant;
            console.log('Found matching variant (length: ' + variant.length + '):', variant.substring(0, 100));
            break;
        }
    }
    
    if (!bestVariant) {
        console.warn('No variant found in document');
        console.warn('Tried variants:', longVariants.map(v => v.substring(0, 50)));
        console.warn('Document text (first 500 chars):', normalizedFull.substring(0, 500));
        return null;
    }
    
    // Try to find using window.find() with each variant
    // Start with longer variants first (more specific)
    if (window.find) {
        for (const variant of longVariants) {
            if (!variant || !variant.trim() || variant.trim().length < 10) continue;
            
            // Clear previous selection
            if (window.getSelection) {
                window.getSelection().removeAllRanges();
            }
            
            const trimmed = variant.trim();
            console.log('Trying to find (length: ' + trimmed.length + '):', trimmed.substring(0, 80));
            
            // Try to find this variant
            const found = window.find(trimmed, false, false, false, false, false, false);
            
            if (found) {
                const selection = window.getSelection();
                const selectedText = selection.toString();
                console.log('Found match (length: ' + selectedText.length + '):', selectedText.substring(0, 80));
                
                // Verify it's a substantial match (at least 10 chars)
                if (selectedText.length >= 10) {
                    console.log('✓ Successfully found using window.find');
                    return selection;
                } else {
                    console.warn('Match too short, continuing search...');
                    window.getSelection().removeAllRanges();
                }
            }
        }
    }
    
    console.warn('window.find() failed for all variants');
    return null;
}

// Function to find elements containing parts of the search text
function findAllElementsWithText(searchText) {
    const normalizedSearch = searchText.replace(/\s+/g, ' ').trim().toLowerCase();
    const searchWords = normalizedSearch.split(' ').filter(w => w.length > 3);
    
    console.log('Searching for', searchWords.length, 'words across document');
    
    // Get all text-containing elements
    const allElements = document.querySelectorAll('p, li, div, h1, h2, h3, h4, h5, h6, span, blockquote');
    const matchingElements = [];
    
    for (let elem of allElements) {
        const elemText = (elem.innerText || elem.textContent || '').replace(/\s+/g, ' ').trim().toLowerCase();
        
        // Count how many search words this element contains
        const matches = searchWords.filter(word => elemText.includes(word)).length;
        
        if (matches > 0) {
            const rect = elem.getBoundingClientRect();
            matchingElements.push({
                element: elem,
                matches: matches,
                y: rect.top + window.scrollY,
                text: elemText.substring(0, 100)
            });
        }
    }
    
    // Sort by Y position (top to bottom)
    matchingElements.sort((a, b) => a.y - b.y);
    
    console.log('Found', matchingElements.length, 'elements with matching text');
    
    return matchingElements;
}

// Function to expand selection to include more text
function expandSelectionToIncludeMore(range, searchText) {
    try {
        const selectedText = range.toString();
        console.log('Initial selection length:', selectedText.length);
        console.log('Target search text length:', searchText.length);
        
        // If selection is already substantial (>50% of search text), just return it
        if (selectedText.length >= searchText.length * 0.5) {
            console.log('Selection already captures 50%+ of target, keeping as is');
            return range;
        }
        
        // Try to find a parent element that contains more of the text
        let container = range.commonAncestorContainer;
        if (container.nodeType === 3) { // Text node
            container = container.parentElement;
        }
        
        console.log('Starting from container:', container.tagName);
        
        // Count matching words in search text
        const searchWords = searchText.replace(/\s+/g, ' ').trim().toLowerCase().split(' ').filter(w => w.length > 3);
        const searchTextNormalized = searchText.replace(/\s+/g, ' ').trim().toLowerCase();
        console.log('Search has', searchWords.length, 'significant words');
        
        // Walk up the DOM tree to find best container
        let bestContainer = container;
        let bestScore = 0;
        let bestLength = selectedText.length;
        
        for (let i = 0; i < 5 && container; i++) {  // Only check 5 levels max
            const containerText = (container.innerText || container.textContent || '').replace(/\s+/g, ' ').trim().toLowerCase();
            const containerLen = containerText.length;
            
            // Don't consider containers that are way too large (more than 2x our search text)
            if (containerLen > searchText.length * 2) {
                console.log('Level', i, ':', container.tagName, '- too large (', containerLen, 'vs', searchText.length, '), skipping');
                container = container.parentElement;
                continue;
            }
            
            // Count how many search words are in this container
            const matches = searchWords.filter(w => containerText.includes(w)).length;
            const score = matches / searchWords.length;
            
            console.log('Level', i, ':', container.tagName, 'matches', matches, '/', searchWords.length, '=', (score*100).toFixed(0) + '%', 'length:', containerLen);
            
            // Only consider containers that:
            // 1. Have at least 70% of our words
            // 2. Are not too much longer than our search text
            // 3. Have a better score than current best
            if (score >= 0.7 && score > bestScore && containerLen <= searchText.length * 1.5) {
                bestScore = score;
                bestContainer = container;
                bestLength = containerLen;
                console.log('  → New best container!');
            }
            
            // If we found 90%+ matches with reasonable length, stop here
            if (score >= 0.9 && containerLen <= searchText.length * 1.3) {
                console.log('  → Excellent match with good length, stopping search');
                break;
            }
            
            container = container.parentElement;
        }
        
        // If we found a better container, use it
        if (bestContainer !== range.commonAncestorContainer && bestScore >= 0.7) {
            console.log('Expanding to', bestContainer.tagName, 'with', (bestScore*100).toFixed(0) + '% match, length:', bestLength);
            const newRange = document.createRange();
            newRange.selectNodeContents(bestContainer);
            
            const newText = newRange.toString();
            console.log('Expanded selection length:', newText.length);
            return newRange;
        }
        
        console.log('No better container found, keeping original range');
        return range;
        
    } catch (e) {
        console.log('Error expanding selection:', e.message);
        return range;
    }
}

// Function to wrap selection in a highlight span
function wrapSelection(selection, searchText) {
    if (!selection || selection.rangeCount === 0) {
        console.error('No selection to wrap');
        return false;
    }
    
    let range = selection.getRangeAt(0);
    
    // Check if range is valid
    if (!range.startContainer || !range.endContainer) {
        console.error('Invalid range');
        return false;
    }
    
    console.log('Wrapping selection, collapsed:', range.collapsed);
    console.log('Start:', range.startContainer.nodeName, 'Offset:', range.startOffset);
    console.log('End:', range.endContainer.nodeName, 'Offset:', range.endOffset);
    console.log('Selection length:', range.toString().length);
    
    // Try to expand the selection to include more of the search text
    if (searchText) {
        range = expandSelectionToIncludeMore(range, searchText);
        console.log('After expansion, selection length:', range.toString().length);
    }
    
    const span = document.createElement('span');
    span.id = 'highlight-target';
    span.style.position = 'relative';
    span.style.display = 'inline';
    
    try {
        // Try the simple approach first (works if selection is within a single element)
        range.surroundContents(span);
        console.log('✓ Successfully wrapped text (simple method)');
        console.log('Span innerHTML length:', span.innerHTML.length);
        console.log('Span text content:', span.textContent.substring(0, 100));
        return true;
    } catch (e) {
        console.log('Simple wrap failed:', e.message);
        
        try {
            // Extract contents and insert in wrapper
            const contents = range.extractContents();
            span.appendChild(contents);
            range.insertNode(span);
            console.log('✓ Successfully wrapped text (extract method)');
            console.log('Span innerHTML length:', span.innerHTML.length);
            console.log('Span text content:', span.textContent.substring(0, 100));
            return true;
        } catch (e2) {
            console.log('Extract method failed:', e2.message);
            
            try {
                // Last resort: Create wrapper at start position
                const startNode = range.startContainer;
                const startParent = startNode.nodeType === 3 ? startNode.parentNode : startNode;
                
                // Insert span at the start of selection
                range.insertNode(span);
                
                // Move range contents into span
                try {
                    span.appendChild(range.extractContents());
                    console.log('✓ Successfully wrapped text (fallback method A)');
                } catch (e3) {
                    // If that fails, just wrap the parent element
                    const wrapper = document.createElement('span');
                    wrapper.id = 'highlight-target';
                    wrapper.style.position = 'relative';
                    startParent.parentNode.insertBefore(wrapper, startParent);
                    wrapper.appendChild(startParent);
                    console.log('✓ Successfully wrapped text (fallback method B - wrapped parent)');
                }
                
                console.log('Span innerHTML length:', span.innerHTML.length);
                console.log('Span text content:', span.textContent ? span.textContent.substring(0, 100) : 'empty');
                return true;
            } catch (e3) {
                console.error('All wrapping methods failed:', e3.message);
                return false;
            }
        }
    }
}

// Fallback: Manual DOM search and wrap
function manualTextSearch(searchText) {
    console.log('Trying manual DOM search...');
    
    const normalized = searchText.replace(/\s+/g, ' ').trim();
    const bodyText = document.body.innerText || document.body.textContent;
    const bodyNormalized = bodyText.replace(/\s+/g, ' ').trim().toLowerCase();
    const searchNormalized = normalized.toLowerCase();
    
    // Find position in normalized text
    const pos = bodyNormalized.indexOf(searchNormalized);
    if (pos === -1) {
        console.error('Text not found even in normalized body text');
        console.log('Searching for:', searchNormalized.substring(0, 100));
        console.log('In text:', bodyNormalized.substring(0, 500));
        return false;
    }
    
    console.log('Found text at position', pos, 'in normalized body');
    
    // Find the FIRST element that contains the START of the text
    // Use first 20-30 words to identify the starting element
    const searchWords = searchNormalized.split(' ').slice(0, 15).join(' ');
    const allElements = document.body.querySelectorAll('p, li, div, h1, h2, h3, h4, h5, h6, blockquote');
    
    let foundElement = null;
    let minPosition = Infinity;
    
    for (let elem of allElements) {
        const elemText = (elem.innerText || elem.textContent || '').replace(/\s+/g, ' ').trim().toLowerCase();
        const elemPos = elemText.indexOf(searchWords.split(' ').slice(0, 5).join(' '));
        
        if (elemPos !== -1) {
            // Check the actual position in the document
            const rect = elem.getBoundingClientRect();
            const docPosition = rect.top + window.scrollY;
            
            if (docPosition < minPosition) {
                minPosition = docPosition;
                foundElement = elem;
                console.log('Found candidate element at position', docPosition, ':', elem.tagName);
            }
        }
    }
    
    if (foundElement) {
        console.log('Selected first element containing text start:', foundElement.tagName);
        
        // Wrap this element only (not the whole text if it spans multiple elements)
        const wrapper = document.createElement('span');
        wrapper.id = 'highlight-target';
        wrapper.style.position = 'relative';
        wrapper.style.display = 'inline-block';
        
        // Insert wrapper around element
        foundElement.parentNode.insertBefore(wrapper, foundElement);
        wrapper.appendChild(foundElement);
        
        console.log('✓ Wrapped first element with highlight-target');
        return true;
    }
    
    console.error('Could not find containing element');
    return false;
}

// Main function to find and wrap text across nodes
function highlightText(searchText) {
    console.log('=== HIGHLIGHT TEXT START ===');
    console.log('Attempting to highlight text (length: ' + searchText.length + ')');
    console.log('First 100 chars:', searchText.substring(0, 100));
    console.log('Last 100 chars:', searchText.substring(Math.max(0, searchText.length - 100)));
    
    // Strategy 1: Use window.find()
    console.log('Strategy 1: window.find()');
    const selection = findTextInDocument(searchText);
    
    if (selection) {
        const wrapped = wrapSelection(selection, searchText);
        if (wrapped) {
            console.log('✓ Successfully highlighted using window.find()');
            console.log('=== HIGHLIGHT TEXT END (SUCCESS) ===');
            return true;
        }
    }
    
    // Strategy 2: Manual DOM search
    console.log('Strategy 2: Manual DOM search');
    if (manualTextSearch(searchText)) {
        console.log('✓ Successfully highlighted using manual search');
        console.log('=== HIGHLIGHT TEXT END (SUCCESS) ===');
        return true;
    }
    
    // Strategy 3: Try with a unique portion from the MIDDLE of the text
    console.log('Strategy 3: Middle portion search (most unique)');
    const normalized = searchText.replace(/\s+/g, ' ').trim();
    const words = normalized.split(' ');
    
    // Take a chunk from the middle (usually more unique than start/end)
    if (words.length > 15) {
        const midStart = Math.floor(words.length / 3);
        const midEnd = Math.min(midStart + 15, words.length);
        const chunk = words.slice(midStart, midEnd).join(' ');
        
        console.log('Trying with middle chunk (words', midStart, '-', midEnd, '):', chunk.substring(0, 80));
        
        if (window.find) {
            window.getSelection().removeAllRanges();
            
            if (window.find(chunk, false, false, false, false, false, false)) {
                const sel = window.getSelection();
                console.log('Found middle chunk! Now expanding to full text...');
                
                if (wrapSelection(sel, searchText)) {
                    console.log('✓ Successfully highlighted using middle chunk + expansion');
                    console.log('=== HIGHLIGHT TEXT END (SUCCESS) ===');
                    return true;
                }
            } else {
                console.log('Middle chunk not found, trying with meaningful start...');
                
                // Fallback: Find first meaningful sequence (skip 1, 6, etc.)
                let meaningfulIdx = 0;
                for (let i = 0; i < words.length; i++) {
                    if (words[i].length > 4) {
                        meaningfulIdx = i;
                        break;
                    }
                }
                
                if (meaningfulIdx < words.length - 5) {
                    const startChunk = words.slice(meaningfulIdx, Math.min(meaningfulIdx + 15, words.length)).join(' ');
                    console.log('Trying meaningful start chunk:', startChunk.substring(0, 80));
                    
                    window.getSelection().removeAllRanges();
                    if (window.find(startChunk, false, false, false, false, false, false)) {
                        const sel = window.getSelection();
                        if (wrapSelection(sel, searchText)) {
                            console.log('✓ Successfully highlighted using start chunk');
                            console.log('=== HIGHLIGHT TEXT END (SUCCESS) ===');
                            return true;
                        }
                    }
                }
            }
        }
    }
    
    console.error('❌ All strategies failed');
    console.log('=== HIGHLIGHT TEXT END (FAILURE) ===');
    return false;
}

// Wait for page to load, then highlight
window.addEventListener('load', function() {
    setTimeout(function() {
        const found = highlightText(TARGET_TEXT);
        if (!found) {
            console.warn('Could not find text to highlight:', TARGET_TEXT);
        }
    }, 100);
});

