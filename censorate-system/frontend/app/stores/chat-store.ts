"use client";

import { create } from "zustand";
import { devtools } from "zustand/middleware";

export interface ChatMessage {
  id: string;
  role: "user" | "agent";
  content: string;
  timestamp: string;
}

interface ChatState {
  isOpen: boolean;
  messages: ChatMessage[];
  selectedAgentId: string | null;
  isSending: boolean;

  // Actions
  setIsOpen: (open: boolean) => void;
  toggleOpen: () => void;
  setSelectedAgentId: (agentId: string | null) => void;
  setIsSending: (sending: boolean) => void;
  addMessage: (message: ChatMessage) => void;
  clearMessages: () => void;
}

export const useChatStore = create<ChatState>()(
  devtools(
    (set, get) => ({
      isOpen: false,
      messages: [],
      selectedAgentId: null,
      isSending: false,

      setIsOpen: (open: boolean) => set({ isOpen: open }),
      toggleOpen: () => set((state) => ({ isOpen: !state.isOpen })),
      setSelectedAgentId: (agentId: string | null) => set({ selectedAgentId: agentId }),
      setIsSending: (sending: boolean) => set({ isSending: sending }),
      addMessage: (message: ChatMessage) =>
        set((state) => ({ messages: [...state.messages, message] })),
      clearMessages: () => set({ messages: [] }),
    }),
    { name: "ChatStore" }
  )
);
