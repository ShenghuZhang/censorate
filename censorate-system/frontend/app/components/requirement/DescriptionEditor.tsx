'use client';

import { useRef, forwardRef, useImperativeHandle } from 'react';
import CherryMarkdownEditor, { CherryMarkdownEditorRef } from '../common/CherryMarkdownEditor';

interface DescriptionEditorProps {
  initialValue: string;
  requirementId: string;
  onSave: (content: string) => Promise<void>;
  onCancel: () => void;
}

export interface DescriptionEditorRef {
  getValue: () => string;
}

const DescriptionEditor = forwardRef<DescriptionEditorRef, DescriptionEditorProps>(({
  initialValue,
  requirementId,
  onSave,
  onCancel,
}, ref) => {
  const editorRef = useRef<CherryMarkdownEditorRef>(null);

  useImperativeHandle(ref, () => ({
    getValue: () => {
      return editorRef.current?.getValue() || '';
    },
  }));

  return (
    <div className="space-y-4">
      <CherryMarkdownEditor
        ref={editorRef}
        value={initialValue}
        placeholder="Add a description..."
        minHeight="200px"
        requirementId={requirementId}
      />
      <div className="flex justify-end gap-2">
        <button
          onClick={onCancel}
          className="px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-xl transition-colors"
        >
          Cancel
        </button>
        <button
          onClick={async () => {
            const content = editorRef.current?.getValue() || initialValue;
            await onSave(content);
          }}
          className="px-4 py-2 text-sm bg-gray-900 text-white rounded-xl hover:bg-gray-800 transition-colors"
        >
          Save
        </button>
      </div>
    </div>
  );
});

DescriptionEditor.displayName = 'DescriptionEditor';

export default DescriptionEditor;
