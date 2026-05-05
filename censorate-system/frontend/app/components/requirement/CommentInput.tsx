'use client';

import { useState } from 'react';
import RichTextEditor from '../common/RichTextEditor';

interface CommentInputProps {
  onSubmit: (content: string, attachments?: any[]) => void;
  placeholder?: string;
  isLoading?: boolean;
  requirementId?: string;
}

export default function CommentInput({ onSubmit, placeholder, isLoading = false, requirementId }: CommentInputProps) {
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
      <div className="border border-[#d0d7de] rounded-md overflow-hidden bg-white">
        <RichTextEditor
          value={content}
          onChange={setContent}
          placeholder={placeholder || 'Add a comment...'}
          minHeight="100px"
          requirementId={requirementId}
        />
      </div>
      <div className="flex items-center justify-end">
        <button
          onClick={handleSubmit}
          disabled={!content.trim() || isSubmitting || isLoading}
          className="inline-flex items-center px-4 py-1.5 text-sm font-medium text-white bg-[#1a7f37] border border-[#1a7f37]/90 rounded-md hover:bg-[#1f883d] hover:border-[#1f883d]/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <span>{isSubmitting ? 'Sending...' : 'Comment'}</span>
        </button>
      </div>
    </div>
  );
}
