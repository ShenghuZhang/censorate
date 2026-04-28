"use client";

import { useState, useEffect } from "react";
import KanbanBoard from "./KanbanBoard";
import { AskAIFab } from "./ask-ai-fab";
import { AskAIWindow } from "./ask-ai-window";

// This wrapper ensures we only render the drag-and-drop board on the client
export default function KanbanBoardClient() {
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  if (!isClient) {
    // Render a simple placeholder on the server
    return (
      <div className="flex flex-col h-[calc(100vh-12rem)]">
        <div className="flex items-center justify-between mb-6">
          <div className="px-4 py-1.5 rounded-xl bg-gray-100 text-gray-900 border border-gray-300 text-sm font-medium">
            All
          </div>
        </div>
        <div className="flex gap-4 overflow-x-auto flex-1 pb-4">
          {/* Placeholder swimlanes */}
          {["Backlog", "Todo", "In Review", "Done"].map((title) => (
            <div
              key={title}
              className="min-w-[300px] max-w-[300px] rounded-2xl bg-gray-50/50"
            >
              <div className="px-4 py-4">
                <div className="flex items-center gap-2">
                  <span className="px-3 py-1 rounded-lg text-sm font-semibold bg-gray-100 text-gray-700">
                    {title}
                  </span>
                </div>
              </div>
              <div className="px-3 pb-3 min-h-[400px]" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <>
      <KanbanBoard />
      <AskAIFab />
      <AskAIWindow />
    </>
  );
}
