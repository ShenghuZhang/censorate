'use client';

import { useState } from 'react';
import { Smile } from 'lucide-react';

const COMMON_EMOJIS = [
  '📋', '📁', '📂', '🚀', '💡', '⚡', '🎯', '✨',
  '🔥', '💎', '🌟', '💫', '🎨', '🎭', '🎪', '🎬',
  '📚', '📖', '📝', '✏️', '🖊️', '🔍', '🔎', '💼',
  '🏢', '🏗️', '🔧', '🔨', '⚙️', '🛠️', '💻', '🖥️',
  '📱', '📲', '🔌', '🔋', '💾', '📀', '🌐', '🛜',
  '☁️', '🌈', '☀️', '🌤️', '🌥️', '🌦️', '🌧️', '⛈️',
  '🌩️', '🌪️', '🌫️', '🌬️', '🌀', '🌈', '🌂', '☂️',
  '🍀', '🍁', '🍂', '🍃', '🌿', '🌱', '🌲', '🌳'
];

interface EmojiPickerProps {
  value?: string;
  onChange: (emoji: string) => void;
}

export default function EmojiPicker({ value, onChange }: EmojiPickerProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-12 h-12 rounded-xl bg-slate-100 hover:bg-slate-200 transition-colors flex items-center justify-center text-2xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-slate-300"
      >
        {value || <Smile size={24} className="text-slate-400" />}
      </button>

      {isOpen && (
        <>
          <div className="fixed inset-0 z-[80]" onClick={() => setIsOpen(false)} />
          <div className="absolute top-full left-0 mt-2 w-72 bg-white rounded-2xl shadow-xl border border-slate-200 z-[85] p-3">
            <div className="grid grid-cols-8 gap-1">
              {COMMON_EMOJIS.map((emoji) => (
                <button
                  key={emoji}
                  type="button"
                  onClick={() => {
                    onChange(emoji);
                    setIsOpen(false);
                  }}
                  className={`w-8 h-8 flex items-center justify-center rounded-lg hover:bg-slate-100 transition-colors text-xl ${
                    value === emoji ? 'bg-slate-200 ring-2 ring-slate-400' : ''
                  }`}
                >
                  {emoji}
                </button>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
