# RichTextEditor Bug Fix Design

**Date**: 2026-04-24  
**Author**: Claude Code  
**Status**: Approved

## Context

The RichTextEditor component has two critical bugs:
1. **Editing and saving fails** - The editor doesn't properly synchronize with external value changes
2. **Cursor always appears at the beginning** - When focusing or updating, the cursor jumps to the start of the editor

These issues are caused by:
- The `useEffect` only running once on mount with empty dependencies
- Using `dangerouslySetInnerHTML` on a `contentEditable` element, which causes React to re-render content and lose cursor position

## Design Approach

### Core Principles
1. **Avoid `dangerouslySetInnerHTML` on `contentEditable`** - Use direct DOM manipulation via refs instead
2. **Smart synchronization** - Only update from external values when necessary
3. **Cursor preservation** - Save and restore selection when external updates happen

### Architecture

#### Component Structure
```
RichTextEditor
├── Toolbar (unchanged)
├── Editor div (contentEditable, no dangerouslySetInnerHTML)
└── State management
    ├── editorRef (for direct DOM access)
    ├── showColorPicker, showHighlightPicker (unchanged)
    └── isBold, isItalic, isUnderline (unchanged)
```

### Key Changes

#### 1. Remove `dangerouslySetInnerHTML`
- Replace with direct `innerHTML` assignment via ref
- Only set innerHTML on initial mount and when external `value` changes

#### 2. Fix `useEffect`
```typescript
useEffect(() => {
  if (editorRef.current) {
    const currentContent = editorRef.current.innerHTML;
    if (value !== currentContent) {
      // Save selection before update
      const selection = saveSelection();
      // Update content
      editorRef.current.innerHTML = value;
      // Restore selection
      restoreSelection(selection);
    }
  }
}, [value]);  // Only run when value changes
```

#### 3. Add Selection Utilities
```typescript
const saveSelection = () => {
  const selection = window.getSelection();
  if (selection && selection.rangeCount > 0) {
    return selection.getRangeAt(0).cloneRange();
  }
  return null;
};

const restoreSelection = (savedRange: Range | null) => {
  if (!savedRange || !editorRef.current) return;
  
  try {
    const selection = window.getSelection();
    if (selection) {
      selection.removeAllRanges();
      // Check if the range is still valid in the new content
      // For simplicity, we'll just restore if possible or place at end
      if (savedRange.startContainer.parentNode === editorRef.current || 
          editorRef.current.contains(savedRange.startContainer)) {
        selection.addRange(savedRange);
      } else {
        // Place cursor at end if saved position is invalid
        const range = document.createRange();
        range.selectNodeContents(editorRef.current);
        range.collapse(false);
        selection.addRange(range);
      }
    }
  } catch (e) {
    // Fallback: don't restore selection if there's an error
    console.warn('Could not restore selection:', e);
  }
};
```

#### 4. Update Editor Div
```typescript
<div
  ref={editorRef}
  contentEditable
  onInput={handleInput}
  onKeyDown={handleKeyDown}
  onMouseUp={updateState}
  onKeyUp={updateState}
  placeholder={placeholder}
  style={{ minHeight: minHeight || '200px' }}
  className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-gray-300 focus:border-gray-400 outline-none transition-all prose prose-sm max-w-none"
  // No dangerouslySetInnerHTML!
/>
```

### Data Flow

1. **Initial mount**:
   - useEffect sets initial content from `value` prop
   - No cursor to preserve yet

2. **User editing**:
   - `onInput` fires → `handleInput` reads `innerHTML` → calls `onChange`
   - Parent component updates its state → passes new `value` back
   - useEffect sees `value` is same as current content → no update → no cursor jump!

3. **External update** (e.g., reset, load saved content):
   - `value` prop changes to something different
   - useEffect saves current selection
   - Updates content
   - Restores selection (or puts cursor at end if invalid)

### Error Handling

- **Selection restore fails**: Catch errors and fall back gracefully (don't restore selection)
- **Invalid saved range**: Check if range is still valid in new DOM, if not put cursor at end
- **Toolbar state**: Continue using `updateState` on mouse/key events to keep buttons in sync

## Files to Modify

1. **`frontend/app/components/common/RichTextEditor.tsx`** - Main fix
2. No other files should need modification - the API remains the same

## Verification Steps

1. Test typing in the editor - cursor should stay in place
2. Test bold/italic/underline - should work without cursor jumping
3. Test saving and reloading - content should persist correctly
4. Test external updates (e.g., clicking "Edit" then "Save") - cursor should behave properly
5. Test all toolbar functions still work

## Success Criteria

- [ ] Editor saves content correctly without failure
- [ ] Cursor stays in position while typing
- [ ] Cursor doesn't jump to beginning on focus or updates
- [ ] All existing toolbar features still work
- [ ] No performance regressions
