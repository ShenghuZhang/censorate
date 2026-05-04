'use client';

import { useRef, useState, useEffect } from 'react';
import {
  Bold,
  Italic,
  Underline,
  Strikethrough,
  Code,
  List,
  ListOrdered,
  Heading1,
  Heading2,
  Heading3,
  Quote,
  Link as LinkIcon,
  Image as ImageIcon,
  Undo,
  Redo,
  AlignLeft,
  AlignCenter,
  AlignRight,
  AlignJustify,
  Highlighter,
  Type,
  Table,
  Loader2
} from 'lucide-react';

interface RichTextEditorProps {
  value?: string;
  onChange?: (value: string) => void;
  placeholder?: string;
  minHeight?: string;
  requirementId?: string;
  onImageUpload?: (file: File) => Promise<string>;
}

export default function RichTextEditor({
  value,
  onChange,
  placeholder,
  minHeight = '200px',
  requirementId,
  onImageUpload
}: RichTextEditorProps) {
  const editorRef = useRef<HTMLDivElement>(null);
  const [showToolbar, setShowToolbar] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const initializedRef = useRef(false);

  // Only initialize content once on mount
  useEffect(() => {
    if (editorRef.current && !initializedRef.current) {
      editorRef.current.innerHTML = value || '';
      initializedRef.current = true;
    }
  }, []);

  // Update content only when value changes from outside
  useEffect(() => {
    if (editorRef.current && initializedRef.current) {
      const currentContent = editorRef.current.innerHTML;
      if (value !== undefined && value !== currentContent) {
        editorRef.current.innerHTML = value || '';
      }
    }
  }, [value]);

  const handleInput = () => {
    if (editorRef.current && onChange) {
      onChange(editorRef.current.innerHTML);
    }
  };

  const execCommand = (command: string, value: string | null = null) => {
    document.execCommand(command, false, value);
    editorRef.current?.focus();
  };

  const formatBlock = (tag: string) => {
    // First try with angle brackets
    try {
      document.execCommand('formatBlock', false, `<${tag}>`);
    } catch (e) {
      // If that fails, try without
      try {
        document.execCommand('formatBlock', false, tag);
      } catch (e2) {
        // If all else fails, manually wrap selection
        wrapSelection(tag);
      }
    }
    editorRef.current?.focus();
  };

  const wrapSelection = (tag: string) => {
    const selection = window.getSelection();
    if (!selection || selection.rangeCount === 0) return;

    const range = selection.getRangeAt(0);
    const selectedText = range.toString();

    if (!selectedText) {
      // If no text selected, insert an empty element
      const element = document.createElement(tag);
      element.innerHTML = '<br>';
      range.deleteContents();
      range.insertNode(element);
      // Move cursor inside
      range.setStart(element, 0);
      range.setEnd(element, 0);
    } else {
      // Create the element and wrap the content
      const element = document.createElement(tag);
      const content = range.extractContents();
      element.appendChild(content);
      range.insertNode(element);
      // Select the content
      range.selectNodeContents(element);
    }
    selection.removeAllRanges();
    selection.addRange(range);
  };

  const insertLink = () => {
    const url = prompt('Enter URL:');
    if (url) {
      execCommand('createLink', url);
    }
  };

  const insertImage = async () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.onchange = async (e: any) => {
      const file = e.target.files[0];
      if (file) {
        if (onImageUpload || requirementId) {
          setIsUploading(true);
          try {
            let imageUrl: string;
            if (onImageUpload) {
              imageUrl = await onImageUpload(file);
            } else {
              const { attachmentsApi } = await import('@/lib/api/attachments');
              const attachment = await attachmentsApi.uploadAttachment(requirementId!, file);
              imageUrl = attachment.url!;
            }
            execCommand('insertImage', imageUrl);
          } catch (error) {
            console.error('Failed to upload image:', error);
            alert('Failed to upload image. Please try again.');
          } finally {
            setIsUploading(false);
          }
        } else {
          // Fallback to temporary URL
          const url = URL.createObjectURL(file);
          execCommand('insertImage', url);
        }
      }
    };
    input.click();
  };

  const insertTable = () => {
    const tableHtml = `
      <table style="border-collapse: collapse; width: 100%; margin: 10px 0;">
        <tr>
          <td style="border: 1px solid #ccc; padding: 8px;">Cell 1</td>
          <td style="border: 1px solid #ccc; padding: 8px;">Cell 2</td>
          <td style="border: 1px solid #ccc; padding: 8px;">Cell 3</td>
        </tr>
        <tr>
          <td style="border: 1px solid #ccc; padding: 8px;">Cell 4</td>
          <td style="border: 1px solid #ccc; padding: 8px;">Cell 5</td>
          <td style="border: 1px solid #ccc; padding: 8px;">Cell 6</td>
        </tr>
      </table>
    `;
    document.execCommand('insertHTML', false, tableHtml);
    editorRef.current?.focus();
  };

  const toolbarButtons = [
    { icon: Undo, label: 'Undo', onClick: () => execCommand('undo') },
    { icon: Redo, label: 'Redo', onClick: () => execCommand('redo') },
    { divider: true },
    { icon: Bold, label: 'Bold', onClick: () => execCommand('bold') },
    { icon: Italic, label: 'Italic', onClick: () => execCommand('italic') },
    { icon: Underline, label: 'Underline', onClick: () => execCommand('underline') },
    { icon: Strikethrough, label: 'Strikethrough', onClick: () => execCommand('strikeThrough') },
    { divider: true },
    { icon: Heading1, label: 'H1', onClick: () => formatBlock('h1') },
    { icon: Heading2, label: 'H2', onClick: () => formatBlock('h2') },
    { icon: Heading3, label: 'H3', onClick: () => formatBlock('h3') },
    { divider: true },
    { icon: List, label: 'Bullet List', onClick: () => execCommand('insertUnorderedList') },
    { icon: ListOrdered, label: 'Numbered List', onClick: () => execCommand('insertOrderedList') },
    { divider: true },
    { icon: Quote, label: 'Quote', onClick: () => formatBlock('blockquote') },
    { icon: Code, label: 'Code', onClick: () => formatBlock('pre') },
    { divider: true },
    { icon: LinkIcon, label: 'Link', onClick: insertLink },
    { icon: isUploading ? Loader2 : ImageIcon, label: 'Image', onClick: insertImage, disabled: isUploading },
    { icon: Table, label: 'Table', onClick: insertTable },
  ];

  return (
    <div
      className="w-full"
      onMouseEnter={() => setShowToolbar(true)}
      onMouseLeave={() => setShowToolbar(false)}
    >
      {/* Toolbar */}
      <div className={`flex flex-wrap gap-1 mb-2 p-2 bg-gray-50 rounded-lg border border-gray-200 sticky top-0 z-10 transition-all duration-200 ${
        showToolbar ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-2 pointer-events-none'
      }`}>
        {toolbarButtons.map((btn, idx) => {
          if (btn.divider) {
            return <div key={idx} className="w-px bg-gray-300 mx-1" />;
          }
          return (
            <button
              key={idx}
              onClick={btn.onClick}
              disabled={btn.disabled}
              className={`p-2 rounded-lg transition-colors ${
                btn.disabled
                  ? 'text-gray-300 cursor-not-allowed'
                  : 'text-gray-600 hover:bg-gray-200 hover:text-gray-900'
              }`}
              title={btn.label}
            >
              <btn.icon size={16} className={btn.disabled ? 'animate-spin' : ''} />
            </button>
          );
        })}
      </div>

      {/* Editor */}
      <div
        ref={editorRef}
        contentEditable
        onInput={handleInput}
        placeholder={placeholder}
        style={{ minHeight }}
        className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-gray-300 focus:border-gray-400 outline-none transition-all prose prose-sm max-w-none"
      />
    </div>
  );
}
