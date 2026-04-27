'use client';

import { useState } from 'react';
import { Send } from 'lucide-react';
import RichTextEditor from '../common/RichTextEditor';

interface CommentInputProps {
  onSubmit: (content: string, attachments?: any[]) => void;
  placeholder?: string;
  isLoading?: boolean;
}

export default function CommentInput({ onSubmit, placeholder, isLoading = false }: CommentInputProps) {
  const [content, setContent] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (!content.trim() || isSubmitting || isLoading) return;

    setIsSubmitting(true);
    try {
      await onSubmit(content);
      setContent('');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-3">
      <RichTextEditor
        value={content}
        onChange={setContent}
        placeholder={placeholder || 'Add a comment...'}
        minHeight="120px"
      />
      <div className="flex items-center justify-end">
        <button
          onClick={handleSubmit}
          disabled={!content.trim() || isSubmitting || isLoading}
          className="flex items-center gap-2 px-4 py-2 bg-gray-800 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <Send size={16} />
          <span>{isSubmitting ? 'Sending...' : 'Comment'}</span>
        </button>
      </div>
    </div>
  );
}
