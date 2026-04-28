"use client";

import { MessageCircle } from "lucide-react";
import { useChatStore } from "@/app/stores/chat-store";

export function AskAIFab() {
  const isOpen = useChatStore((s) => s.isOpen);
  const toggleOpen = useChatStore((s) => s.toggleOpen);

  // Don't show FAB when chat is already open
  if (isOpen) return null;

  return (
    <button
      onClick={toggleOpen}
      aria-label="Open AI chat assistant"
      className="fixed bottom-6 right-6 z-50 flex size-14 cursor-pointer items-center justify-center rounded-full bg-gradient-to-br from-blue-600 to-purple-600 text-white shadow-lg ring-1 ring-white/20 transition-transform hover:scale-110 hover:from-blue-700 hover:to-purple-700 active:scale-95 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2"
    >
      <MessageCircle className="size-6" />
    </button>
  );
}
