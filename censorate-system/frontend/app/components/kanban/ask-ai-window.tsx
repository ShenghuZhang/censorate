"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import {
  Minus,
  Plus,
  Check,
  ChevronDown,
  Bot,
  Send,
  Loader2,
  FileText,
} from "lucide-react";
import { useChatStore, type ChatMessage } from "@/app/stores/chat-store";
import { remoteAgentsAPI, type RemoteAgent } from "@/lib/api/remoteAgents";
import { useProjectStore } from "@/app/stores/projectStore";
import { useRequirementStore, type Requirement } from "@/app/stores/requirementStore";
import { useAuth } from "@/app/hooks/useAuth";

const STARTER_PROMPTS = [
  { icon: "📋", text: "What requirements aren't started yet?" },
  { icon: "📝", text: "Summarize this project's status" },
  { icon: "💡", text: "What should I work on next?" },
];

export function AskAIWindow() {
  const isOpen = useChatStore((s) => s.isOpen);
  const messages = useChatStore((s) => s.messages);
  const selectedAgentId = useChatStore((s) => s.selectedAgentId);
  const isSending = useChatStore((s) => s.isSending);
  const setIsOpen = useChatStore((s) => s.setIsOpen);
  const setSelectedAgentId = useChatStore((s) => s.setSelectedAgentId);
  const setIsSending = useChatStore((s) => s.setIsSending);
  const addMessage = useChatStore((s) => s.addMessage);
  const clearMessages = useChatStore((s) => s.clearMessages);

  const [registeredAgents, setRegisteredAgents] = useState<RemoteAgent[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoadingAgents, setIsLoadingAgents] = useState(true);
  const [showRequirementDropdown, setShowRequirementDropdown] = useState(false);
  const [requirementDropdownPosition, setRequirementDropdownPosition] = useState({ start: 0, end: 0 });
  const [selectedRequirementIndex, setSelectedRequirementIndex] = useState(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const { currentProject } = useProjectStore();
  const { requirements } = useRequirementStore();
  const { user } = useAuth();

  // Filter requirements for the current project
  const projectRequirements = currentProject
    ? requirements.filter((req) => req.projectId === currentProject.id)
    : [];

  // Load registered agents
  useEffect(() => {
    const loadAgents = async () => {
      try {
        const agents = await remoteAgentsAPI.listAgents();
        setRegisteredAgents(agents);
        // Auto-select first available agent
        if (agents.length > 0 && !selectedAgentId) {
          setSelectedAgentId(agents[0].id);
        }
      } catch (error) {
        console.error("Failed to load agents:", error);
      } finally {
        setIsLoadingAgents(false);
      }
    };

    if (isOpen) {
      loadAgents();
    }
  }, [isOpen, selectedAgentId, setSelectedAgentId]);

  // Auto-scroll to bottom of messages
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node) &&
          inputRef.current && !inputRef.current.contains(event.target as Node)) {
        setShowRequirementDropdown(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const activeAgent = registeredAgents.find((a) => a.id === selectedAgentId) ?? null;

  // Extract mentioned requirements from user input
  const extractMentionedRequirements = useCallback((text: string): Requirement[] => {
    const reqPattern = /REQ-(\d+)/g;
    const matches = [...text.matchAll(reqPattern)];
    const reqNumbers = matches.map(match => parseInt(match[1]));

    return requirements.filter(req => reqNumbers.includes(req.reqNumber));
  }, [requirements]);

  // Build detailed context for mentioned requirements
  const buildRequirementDetails = useCallback((req: Requirement): string => {
    let details = `\n--- REQ-${req.reqNumber} DETAILS ---\n`;
    details += `Title: ${req.title}\n`;
    details += `Status: ${req.status || 'backlog'}\n`;
    details += `Priority: ${req.priority || 'medium'}\n`;

    if (req.description) {
      details += `Description: ${req.description}\n`;
    }

    if (req.assigned_to_name) {
      details += `Assigned to: ${req.assigned_to_name}\n`;
    }

    if (req.expectedCompletionAt) {
      details += `Due date: ${new Date(req.expectedCompletionAt).toLocaleDateString()}\n`;
    }

    if (req.completedAt) {
      details += `Completed at: ${new Date(req.completedAt).toLocaleDateString()}\n`;
    }

    details += `Created: ${new Date(req.createdAt).toLocaleDateString()}\n`;

    if (req.ai_suggestions) {
      details += `AI Suggestions: ${JSON.stringify(req.ai_suggestions)}\n`;
    }

    return details;
  }, []);

  // Build project context with detailed requirement information for mentioned requirements
  const buildProjectContext = useCallback((userMessage: string = "") => {
    if (!currentProject) return "";

    let context = `Project: ${currentProject.name}\n`;
    if (currentProject.description) {
      context += `Description: ${currentProject.description}\n`;
    }
    context += "\n";

    if (requirements.length > 0) {
      const projectRequirements = requirements.filter(req => req.projectId === currentProject.id);
      context += `Requirements Summary (${projectRequirements.length} total):\n`;

      // First add a summary of all requirements
      projectRequirements.forEach((req) => {
        const status = req.status || "backlog";
        const title = req.title || "Untitled requirement";
        context += `- [${status}] REQ-${req.reqNumber}: ${title}\n`;
      });

      // Then add detailed information for mentioned requirements
      const mentionedRequirements = extractMentionedRequirements(userMessage);
      if (mentionedRequirements.length > 0) {
        context += "\n==============================\n";
        context += "DETAILED INFORMATION FOR MENTIONED REQUIREMENTS:\n";
        context += "==============================\n";

        mentionedRequirements.forEach(req => {
          context += buildRequirementDetails(req);
        });
        context += "\n==============================\n";
      }
    }

    return context;
  }, [currentProject, requirements, extractMentionedRequirements, buildRequirementDetails]);

  // Check if we should show the requirement dropdown
  const checkForMentionTrigger = useCallback((value: string, cursorPosition: number) => {
    const textBeforeCursor = value.substring(0, cursorPosition);
    const lastAtIndex = textBeforeCursor.lastIndexOf('@');

    if (lastAtIndex !== -1) {
      const textAfterAt = textBeforeCursor.substring(lastAtIndex + 1);
      const hasSpaceAfterAt = textAfterAt.includes(' ');

      if (!hasSpaceAfterAt) {
        setShowRequirementDropdown(true);
        setRequirementDropdownPosition({ start: lastAtIndex, end: cursorPosition });
        setSelectedRequirementIndex(0);
        return true;
      }
    }

    setShowRequirementDropdown(false);
    return false;
  }, []);

  // Handle input change
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    const cursorPosition = e.target.selectionStart || newValue.length;
    setInputValue(newValue);
    checkForMentionTrigger(newValue, cursorPosition);
  };

  // Handle inserting a requirement
  const handleInsertRequirement = (requirement: Requirement) => {
    const requirementText = `REQ-${requirement.reqNumber}:${requirement.title.substring(0, 20)}...`;
    const newInputValue =
      inputValue.substring(0, requirementDropdownPosition.start) +
      requirementText + " " +
      inputValue.substring(requirementDropdownPosition.end);

    setInputValue(newInputValue);
    setShowRequirementDropdown(false);

    // Focus back on input
    setTimeout(() => {
      inputRef.current?.focus();
    }, 10);
  };

  // Handle keyboard navigation in dropdown
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (showRequirementDropdown) {
      switch (e.key) {
        case "ArrowDown":
          e.preventDefault();
          setSelectedRequirementIndex((prev) =>
            Math.min(prev + 1, projectRequirements.length - 1)
          );
          break;
        case "ArrowUp":
          e.preventDefault();
          setSelectedRequirementIndex((prev) => Math.max(prev - 1, 0));
          break;
        case "Enter":
          e.preventDefault();
          if (projectRequirements[selectedRequirementIndex]) {
            handleInsertRequirement(projectRequirements[selectedRequirementIndex]);
          }
          break;
        case "Escape":
          e.preventDefault();
          setShowRequirementDropdown(false);
          break;
      }
    } else if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend(inputValue);
    }
  };

  // Handle click on input to check for mention trigger
  const handleInputClick = () => {
    if (inputRef.current) {(checkForMentionTrigger)(inputValue, inputRef.current.selectionStart || inputValue.length);
    }
  };

  const handleSend = useCallback(
    async (content: string) => {
      if (!activeAgent || !content.trim() || isSending) return;

      const trimmedContent = content.trim();
      setInputValue("");
      setIsSending(true);

      // Add user message immediately (optimistic)
      const userMessage: ChatMessage = {
        id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        role: "user",
        content: trimmedContent,
        timestamp: new Date().toISOString(),
      };
      addMessage(userMessage);

      try {
        const context = buildProjectContext(trimmedContent);
        const fullMessage = context
          ? `${context}\n\nUser question: ${trimmedContent}`
          : trimmedContent;

        const response = await remoteAgentsAPI.sendMessage(activeAgent.id, {
          message: fullMessage,
          projectId: currentProject?.id,
        });

        // Add agent response
        const agentMessage: ChatMessage = {
          id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          role: "agent",
          content: response.response,
          timestamp: response.timestamp || new Date().toISOString(),
        };
        addMessage(agentMessage);
      } catch (error) {
        console.error("Failed to send message:", error);
        // Add error message
        const errorMessage: ChatMessage = {
          id: `msg-${Date.now()}-error`,
          role: "agent",
          content: "Sorry, I encountered an error. Please try again.",
          timestamp: new Date().toISOString(),
        };
        addMessage(errorMessage);
      } finally {
        setIsSending(false);
      }
    },
    [activeAgent, isSending, addMessage, buildProjectContext, currentProject]
  );

  const handlePickPrompt = (text: string) => {
    handleSend(text);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col w-96 h-[500px] rounded-xl bg-white shadow-2xl border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-100 px-4 py-2.5 bg-gradient-to-r from-blue-50 to-purple-50">
        <div className="flex items-center gap-2 min-w-0">
          <button
            onClick={() => {
              clearMessages();
            }}
            aria-label="Start new chat"
            className="p-1.5 hover:bg-gray-200 rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2"
            title="New chat"
          >
            <Plus className="size-4 text-gray-600" />
          </button>
          <AgentSelector
            agents={registeredAgents}
            activeAgent={activeAgent}
            onSelect={(agent) => {
              setSelectedAgentId(agent.id);
              clearMessages();
            }}
          />
        </div>
        <button
          onClick={() => setIsOpen(false)}
          aria-label="Minimize chat window"
          className="p-1.5 hover:bg-gray-200 rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2"
        >
          <Minus className="size-4 text-gray-600" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4">
        {isLoadingAgents ? (
          <div className="flex items-center justify-center h-full">
            <Loader2 className="size-5 animate-spin text-gray-400" />
          </div>
        ) : messages.length === 0 ? (
          <EmptyState
            agentName={activeAgent?.name}
            onPickPrompt={handlePickPrompt}
          />
        ) : (
          <div className="space-y-4">
            {messages.map((message) => (
              <ChatBubble key={message.id} message={message} />
            ))}
            {isSending && (
              <div className="flex items-start gap-2">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center flex-shrink-0">
                  <Bot className="size-4 text-white" />
                </div>
                <div className="flex gap-1 p-3 bg-gray-100 rounded-2xl rounded-tl-sm">
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                  <span
                    className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                    style={{ animationDelay: "0.1s" }}
                  />
                  <span
                    className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                    style={{ animationDelay: "0.2s" }}
                  />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input */}
      <div className="border-t border-gray-100 p-4 bg-gray-50 relative">
        <div className="flex gap-2">
          <div className="flex-1 relative">
            <input
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              onClick={handleInputClick}
              placeholder={activeAgent ? `Ask ${activeAgent.name}... Type @ to mention requirements` : "No agent available"}
              disabled={!activeAgent || isSending}
              className="flex-1 w-full px-4 py-2.5 bg-white border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50"
            />

            {/* Requirement dropdown */}
            {showRequirementDropdown && projectRequirements.length > 0 && (
              <div
                ref={dropdownRef}
                className="absolute bottom-full left-0 mb-2 w-80 max-h-60 overflow-y-auto bg-white rounded-lg shadow-xl border border-gray-200 z-20"
              >
                <div className="p-2 text-xs font-semibold text-gray-500 border-b border-gray-100">
                  Select a requirement to mention
                </div>
                {projectRequirements.map((req, index) => (
                  <button
                    key={req.id}
                    onClick={() => handleInsertRequirement(req)}
                    onMouseEnter={() => setSelectedRequirementIndex(index)}
                    className={`w-full flex items-center gap-2 px-3 py-2 text-left transition-colors ${
                      index === selectedRequirementIndex
                        ? "bg-blue-50 text-blue-900"
                        : "hover:bg-gray-50 text-gray-700"
                    }`}
                  >
                    <FileText className="size-4 text-gray-400 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-semibold">REQ-{req.reqNumber}</span>
                        <span className="text-xs px-1.5 py-0.5 rounded bg-gray-100 text-gray-600">
                          {req.status}
                        </span>
                      </div>
                      <p className="text-xs text-gray-500 truncate">
                        {req.title}
                      </p>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>

          <button
            onClick={() => handleSend(inputValue)}
            disabled={!activeAgent || !inputValue.trim() || isSending}
            aria-label="Send message"
            className="px-4 py-2.5 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2"
          >
            {isSending ? (
              <Loader2 className="size-4 animate-spin" />
            ) : (
              <Send className="size-4" />
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

function AgentSelector({
  agents,
  activeAgent,
  onSelect,
}: {
  agents: RemoteAgent[];
  activeAgent: RemoteAgent | null;
  onSelect: (agent: RemoteAgent) => void;
}) {
  const [isOpen, setIsOpen] = useState(false);

  if (!activeAgent) {
    return <span className="text-xs text-gray-500">No agents</span>;
  }

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Select AI agent"
        className="flex items-center gap-1.5 rounded-md px-1.5 py-1 cursor-pointer hover:bg-gray-200 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2"
      >
        <div className="w-6 h-6 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
          <Bot className="size-3.5 text-white" />
        </div>
        <span className="text-sm font-medium truncate max-w-32">
          {activeAgent.name}
        </span>
        <ChevronDown className="size-3 text-gray-50 shrink-0" />
      </button>

      {isOpen && (
        <div className="absolute bottom-full left-0 mb-1 w-56 bg-white rounded-lg shadow-xl border border-gray-200 py-1 z-10">
          {agents.map((agent) => (
            <button
              key={agent.id}
              onClick={() => {
                onSelect(agent);
                setIsOpen(false);
              }}
              className={`w-full flex items-center gap-2 px-3 py-2 hover:bg-gray-100 text-left transition-colors ${
                agent.id === activeAgent.id ? "bg-blue-50" : ""
              }`}
            >
              <div className="w-6 h-6 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center flex-shrink-0">
                <Bot className="size-3.5 text-white" />
              </div>
              <span className="flex-1 text-sm truncate">{agent.name}</span>
              {agent.id === activeAgent.id && (
                <Check className="size-3.5 text-blue-600" />
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

function ChatBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[85%] p-3 rounded-2xl ${
          isUser
            ? "bg-gradient-to-br from-blue-600 to-purple-600 text-white rounded-tr-sm"
            : "bg-gray-100 text-gray-900 rounded-tl-sm"
        }`}
      >
        <p className="text-sm whitespace-pre-wrap">{message.content}</p>
        <p
          className={`text-xs mt-1 opacity-70 ${
            isUser ? "text-right" : "text-left"
          }`}
        >
          {new Date(message.timestamp).toLocaleTimeString()}
        </p>
      </div>
    </div>
  );
}

function EmptyState({
  agentName,
  onPickPrompt,
}: {
  agentName?: string;
  onPickPrompt: (text: string) => void;
}) {
  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-5 px-6 py-8">
      <div className="text-center space-y-1">
        <h3 className="text-base font-semibold text-gray-900">
          {agentName ? `Hi, I'm ${agentName}` : "Ask AI"}
        </h3>
        <p className="text-sm text-gray-500">Try asking about this project. Type @ to mention requirements.</p>
      </div>
      <div className="w-full max-w-xs space-y-2">
        {STARTER_PROMPTS.map((prompt) => (
          <button
            key={prompt.text}
            type="button"
            onClick={() => onPickPrompt(prompt.text)}
            className="w-full rounded-lg border border-gray-200 bg-white px-3 py-2 text-left text-sm text-gray-700 transition-colors hover:bg-blue-50 hover:border-blue-200"
          >
            <span className="mr-2">{prompt.icon}</span>
            {prompt.text}
          </button>
        ))}
      </div>
    </div>
  );
}
