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
  MoreHorizontal
} from 'lucide-react';

interface RichTextEditorProps {
  value?: string;
  onChange?: (value: string) => void;
  placeholder?: string;
  minHeight?: string;
}

const COLORS = [
  { name: 'Black', value: '#000000' },
  { name: 'Dark Gray', value: '#374151' },
  { name: 'Red', value: '#EF4444' },
  { name: 'Orange', value: '#F97316' },
  { name: 'Yellow', value: '#EAB308' },
  { name: 'Green', value: '#22C55E' },
  { name: 'Blue', value: '#3B82F6' },
  { name: 'Purple', value: '#A855F7' },
];

const HIGHLIGHTS = [
  { name: 'Yellow', value: '#FEF08A' },
  { name: 'Green', value: '#BBF7D0' },
  { name: 'Blue', value: '#BFDBFE' },
  { name: 'Purple', value: '#E9D5FF' },
  { name: 'Pink', value: '#FBCFE8' },
];

export default function RichTextEditor({ value, onChange, placeholder, minHeight }: RichTextEditorProps) {
  const editorRef = useRef<HTMLDivElement>(null);
  const [showColorPicker, setShowColorPicker] = useState(false);
  const [showHighlightPicker, setShowHighlightPicker] = useState(false);
  const [isBold, setIsBold] = useState(false);
  const [isItalic, setIsItalic] = useState(false);
  const [isUnderline, setIsUnderline] = useState(false);
  const [showToolbar, setShowToolbar] = useState(false);
  const initializedRef = useRef(false);

  // Only initialize content once on mount
  useEffect(() => {
    if (editorRef.current && !initializedRef.current) {
      editorRef.current.innerHTML = value || '';
      initializedRef.current = true;
    }
  }, []);

  // Update content only when value changes from outside (e.g. reset, save complete)
  useEffect(() => {
    if (editorRef.current && initializedRef.current) {
      const currentContent = editorRef.current.innerHTML;
      if (value !== undefined && value !== currentContent) {
        editorRef.current.innerHTML = value || '';
      }
    }
  }, [value]);

  const execCommand = (command: string, commandValue: string | null = null) => {
    document.execCommand(command, false, commandValue);
    editorRef.current?.focus();
    updateState();
  };

  const updateState = () => {
    setIsBold(document.queryCommandState('bold'));
    setIsItalic(document.queryCommandState('italic'));
    setIsUnderline(document.queryCommandState('underline'));
  };

  const handleInput = () => {
    if (editorRef.current && onChange) {
      onChange(editorRef.current.innerHTML);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
      e.preventDefault();
      execCommand('bold');
    } else if ((e.ctrlKey || e.metaKey) && e.key === 'i') {
      e.preventDefault();
      execCommand('italic');
    } else if ((e.ctrlKey || e.metaKey) && e.key === 'u') {
      e.preventDefault();
      execCommand('underline');
    }
  };

  const insertLink = () => {
    const url = prompt('Enter URL:');
    if (url) {
      execCommand('createLink', url);
    }
  };

  const insertImage = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.onchange = (e: any) => {
      const file = e.target.files[0];
      if (file) {
        const url = URL.createObjectURL(file);
        execCommand('insertImage', url);
      }
    };
    input.click();
  };

  const insertTable = () => {
    const tableHtml = `
      <table style="border-collapse: collapse; width: 100%; margin: 10px 0;">
        <tr>
          <td style="border: 1px solid #ddd; padding: 8px;">Cell 1</td>
          <td style="border: 1px solid #ddd; padding: 8px;">Cell 2</td>
          <td style="border: 1px solid #ddd; padding: 8px;">Cell 3</td>
        </tr>
        <tr>
          <td style="border: 1px solid #ddd; padding: 8px;">Cell 4</td>
          <td style="border: 1px solid #ddd; padding: 8px;">Cell 5</td>
          <td style="border: 1px solid #ddd; padding: 8px;">Cell 6</td>
        </tr>
      </table>
    `;
    execCommand('insertHTML', tableHtml);
  };

  const toolbarButtons = [
    { icon: Undo, label: 'Undo', onClick: () => execCommand('undo') },
    { icon: Redo, label: 'Redo', onClick: () => execCommand('redo') },
    { divider: true },
    { icon: Bold, label: 'Bold', onClick: () => execCommand('bold'), isActive: isBold },
    { icon: Italic, label: 'Italic', onClick: () => execCommand('italic'), isActive: isItalic },
    { icon: Underline, label: 'Underline', onClick: () => execCommand('underline'), isActive: isUnderline },
    { icon: Strikethrough, label: 'Strikethrough', onClick: () => execCommand('strikeThrough') },
    { divider: true },
    { icon: Highlighter, label: 'Text Color', onClick: () => setShowColorPicker(!showColorPicker), hasDropdown: true },
    { icon: Type, label: 'Highlight', onClick: () => setShowHighlightPicker(!showHighlightPicker), hasDropdown: true },
    { divider: true },
    { icon: Heading1, label: 'H1', onClick: () => execCommand('formatBlock', 'h1') },
    { icon: Heading2, label: 'H2', onClick: () => execCommand('formatBlock', 'h2') },
    { icon: Heading3, label: 'H3', onClick: () => execCommand('formatBlock', 'h3') },
    { divider: true },
    { icon: List, label: 'Bullet List', onClick: () => execCommand('insertUnorderedList') },
    { icon: ListOrdered, label: 'Numbered List', onClick: () => execCommand('insertOrderedList') },
    { divider: true },
    { icon: Quote, label: 'Quote', onClick: () => execCommand('formatBlock', 'blockquote') },
    { icon: Code, label: 'Code', onClick: () => execCommand('formatBlock', 'pre') },
    { divider: true },
    { icon: AlignLeft, label: 'Align Left', onClick: () => execCommand('justifyLeft') },
    { icon: AlignCenter, label: 'Align Center', onClick: () => execCommand('justifyCenter') },
    { icon: AlignRight, label: 'Align Right', onClick: () => execCommand('justifyRight') },
    { icon: AlignJustify, label: 'Justify', onClick: () => execCommand('justifyFull') },
    { divider: true },
    { icon: LinkIcon, label: 'Link', onClick: insertLink },
    { icon: ImageIcon, label: 'Image', onClick: insertImage },
    { icon: Table, label: 'Table', onClick: insertTable },
  ];

  // Public method to get content - can be called via ref if needed
  const getContent = () => editorRef.current?.innerHTML || '';

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
            <div key={idx} className="relative">
              <button
                onClick={btn.onClick}
                className={`p-2 rounded-lg transition-colors ${
                  btn.isActive
                    ? 'bg-gray-800 text-white'
                    : 'text-gray-600 hover:bg-gray-200 hover:text-gray-900'
                }`}
                title={btn.label}
              >
                <btn.icon size={16} />
              </button>
              {btn.hasDropdown && showColorPicker && (
                <div className="absolute top-full left-0 mt-2 p-3 bg-white rounded-lg shadow-xl border border-gray-200 z-20">
                  <div className="grid grid-cols-4 gap-2">
                    {COLORS.map((color, cIdx) => (
                      <button
                        key={cIdx}
                        onClick={() => {
                          execCommand('foreColor', color.value);
                          setShowColorPicker(false);
                        }}
                        className="w-8 h-8 rounded-full border border-gray-200 hover:scale-110 transition-transform"
                        style={{ backgroundColor: color.value }}
                        title={color.name}
                      />
                    ))}
                  </div>
                </div>
              )}
              {btn.hasDropdown && showHighlightPicker && (
                <div className="absolute top-full left-0 mt-2 p-3 bg-white rounded-lg shadow-xl border border-gray-200 z-20">
                  <div className="grid grid-cols-4 gap-2">
                    {HIGHLIGHTS.map((color, cIdx) => (
                      <button
                        key={cIdx}
                        onClick={() => {
                          execCommand('hiliteColor', color.value);
                          setShowHighlightPicker(false);
                        }}
                        className="w-8 h-8 rounded-full border border-gray-200 hover:scale-110 transition-transform"
                        style={{ backgroundColor: color.value }}
                        title={color.name}
                      />
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Editor - uncontrolled, manages its own state */}
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
      />
    </div>
  );
}
