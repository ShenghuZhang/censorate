'use client';

import { useState, useRef } from 'react';
import { Upload, X, Image as ImageIcon } from 'lucide-react';
import { clsx } from 'clsx';

interface LogoUploadProps {
  currentLogo?: string;
  onLogoChange: (logoUrl: string) => void;
}

export default function LogoUpload({ currentLogo, onLogoChange }: LogoUploadProps) {
  const [preview, setPreview] = useState<string | null>(currentLogo || null);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = (file: File) => {
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onloadend = () => {
        const result = reader.result as string;
        setPreview(result);
        onLogoChange(result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file) handleFile(file);
  };

  const handleRemove = () => {
    setPreview(null);
    onLogoChange('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="flex items-start gap-6">
      <div className="relative">
        {preview ? (
          <div className="relative group">
            <div className="w-24 h-24 rounded-2xl overflow-hidden bg-surface-soft border border-border shadow-soft">
              <img
                src={preview}
                alt="Project logo"
                className="w-full h-full object-cover"
              />
            </div>
            <button
              onClick={handleRemove}
              className="absolute -top-3 -right-3 w-7 h-7 bg-text-primary text-white rounded-full flex items-center justify-center hover:bg-text-secondary transition-all shadow-md hover:scale-110"
            >
              <X size={14} strokeWidth={2.5} />
            </button>
          </div>
        ) : (
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={clsx(
              'w-24 h-24 rounded-2xl flex flex-col items-center justify-center cursor-pointer transition-all border-2 border-dashed',
              isDragOver
                ? 'border-primary bg-primary-soft'
                : 'border-border bg-surface-soft hover:border-text-tertiary hover:bg-surface-softer'
            )}
          >
            <ImageIcon size={28} className={clsx('mb-1', isDragOver ? 'text-primary' : 'text-text-muted')} />
            <span className="text-xs font-medium text-text-muted">Upload</span>
          </div>
        )}
      </div>

      <div className="pt-1">
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className="hidden"
        />
        {!preview && (
          <button
            onClick={() => fileInputRef.current?.click()}
            className="inline-flex items-center gap-2 px-5 py-3 bg-slate-600 text-white rounded-xl hover:bg-slate-700 transition-all duration-200 text-sm font-medium shadow-md hover:shadow-lg"
          >
            <Upload size={16} strokeWidth={2} />
            Upload Logo
          </button>
        )}
      </div>
    </div>
  );
}
