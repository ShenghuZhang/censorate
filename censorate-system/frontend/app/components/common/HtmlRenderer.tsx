'use client';

interface HtmlRendererProps {
  content: string;
  className?: string;
}

export default function HtmlRenderer({ content, className = '' }: HtmlRendererProps) {
  if (!content) {
    return null;
  }

  return (
    <div
      className={`prose prose-sm max-w-none ${className}`}
      dangerouslySetInnerHTML={{ __html: content }}
    />
  );
}
