'use client';

import { useEffect, useRef, forwardRef, useImperativeHandle, useState } from 'react';
import dynamic from 'next/dynamic';

// Create a simple fallback editor
const SimpleEditor = forwardRef<{ getValue: () => string; setValue: (val: string) => void }, {
  value?: string;
  onChange?: (value: string) => void;
  placeholder?: string;
  minHeight?: string;
}>(({ value, onChange, placeholder, minHeight }, ref) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useImperativeHandle(ref, () => ({
    getValue: () => textareaRef.current?.value || '',
    setValue: (val: string) => {
      if (textareaRef.current) {
        textareaRef.current.value = val;
      }
    },
  }));

  return (
    <textarea
      ref={textareaRef}
      defaultValue={value}
      onChange={(e) => onChange?.(e.target.value)}
      placeholder={placeholder}
      className="w-full border border-gray-200 rounded-xl p-4 resize-none focus:outline-none focus:ring-2 focus:ring-gray-300"
      style={{ minHeight: minHeight }}
    />
  );
});

SimpleEditor.displayName = 'SimpleEditor';

interface CherryMarkdownEditorProps {
  value?: string;
  onChange?: (value: string) => void;
  placeholder?: string;
  minHeight?: string;
  requirementId?: string;
  onImageUpload?: (file: File) => Promise<string>;
}

export interface CherryMarkdownEditorRef {
  getValue: () => string;
  setValue: (value: string) => void;
}

// CherryMarkdownEditor component that uses simple editor by default
const CherryMarkdownEditor = forwardRef<CherryMarkdownEditorRef, CherryMarkdownEditorProps>(({
  value,
  onChange,
  placeholder,
  minHeight = '200px',
  requirementId,
  onImageUpload,
}, ref) => {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  // Just use SimpleEditor for now - it's stable
  return (
    <div className="w-full">
      <SimpleEditor
        ref={ref}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        minHeight={minHeight}
      />
    </div>
  );
});

CherryMarkdownEditor.displayName = 'CherryMarkdownEditor';

export default CherryMarkdownEditor;
