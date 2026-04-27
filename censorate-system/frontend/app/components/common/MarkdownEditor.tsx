'use client';

import { useRef } from 'react';
import {
  Bold,
  Italic,
  Code,
  List,
  ListOrdered,
  Heading1,
  Heading2,
  Quote,
  Link,
  Image
} from 'lucide-react';

interface MarkdownEditorProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  minHeight?: string;
}

export default function MarkdownEditor({ value, onChange, placeholder, minHeight }: MarkdownEditorProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const insertText = (before: string, after: string = '') => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = value.substring(start, end);
    const newText = value.substring(0, start) + before + selectedText + after + value.substring(end);

    onChange(newText);

    // Set cursor position
    setTimeout(() => {
      textarea.focus();
      if (selectedText) {
        textarea.setSelectionRange(start + before.length, start + before.length + selectedText.length);
      } else {
        textarea.setSelectionRange(start + before.length, start + before.length);
      }
    }, 0);
  };

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // TODO: Upload image to server and get URL
    // For now, we'll just insert a placeholder
    const imageUrl = URL.createObjectURL(file);
    insertText(`![Image](${imageUrl})`);
  };

  const toolbarButtons = [
    { icon: Heading1, label: 'H1', onClick: () => insertText('# ') },
    { icon: Heading2, label: 'H2', onClick: () => insertText('## ') },
    { icon: Bold, label: 'Bold', onClick: () => insertText('**', '**') },
    { icon: Italic, label: 'Italic', onClick: () => insertText('*', '*') },
    { icon: Code, label: 'Code', onClick: () => insertText('`', '`') },
    { icon: List, label: 'List', onClick: () => insertText('- ') },
    { icon: ListOrdered, label: 'Ordered List', onClick: () => insertText('1. ') },
    { icon: Quote, label: 'Quote', onClick: () => insertText('> ') },
    { icon: Link, label: 'Link', onClick: () => insertText('[', '](url)') },
  ];

  return (
    <div className="w-full">
      {/* Toolbar */}
      <div className="flex flex-wrap gap-1 mb-2 p-2 bg-gray-50 rounded-lg border border-gray-200">
        {toolbarButtons.map((btn, idx) => (
          <button
            key={idx}
            onClick={btn.onClick}
            className="p-2 hover:bg-gray-200 rounded-lg transition-colors text-gray-600 hover:text-gray-900"
            title={btn.label}
          >
            <btn.icon size={16} />
          </button>
        ))}
        <div className="w-px bg-gray-300 mx-1" />
        <label className="p-2 hover:bg-gray-200 rounded-lg transition-colors text-gray-600 hover:text-gray-900 cursor-pointer">
          <Image size={16} />
          <input
            type="file"
            accept="image/*"
            onChange={handleImageUpload}
            className="hidden"
          />
        </label>
      </div>

      {/* Editor */}
      <textarea
        ref={textareaRef}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        style={{ minHeight: minHeight || '200px' }}
        className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-gray-300 focus:border-gray-400 resize-none transition-all font-mono text-sm"
      />
    </div>
  );
}
