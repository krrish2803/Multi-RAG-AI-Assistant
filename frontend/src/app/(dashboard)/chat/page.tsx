"use client";

import { useState, useEffect, useRef, FormEvent, KeyboardEvent } from "react";
import { useSearchParams } from "next/navigation";
import api from "@/lib/api";
import { useChatStore } from "@/stores/chatStore";
import { useAuthStore } from "@/stores/authStore";
import type { ChatResponse, Conversation, Message, SourceCitation } from "@/types";
import { Send, Plus, MessageSquare, FileText, Clock, AlertTriangle, X } from "lucide-react";
import ReactMarkdown from "react-markdown";

export default function ChatPage() {
  const { user } = useAuthStore();
  const searchParams = useSearchParams();
  const initialDocId = searchParams.get("document_id");
  const {
    conversations,
    currentConversationId,
    messages,
    isStreaming,
    setConversations,
    setCurrentConversation,
    addMessage,
    setMessages,
    setIsStreaming,
  } = useChatStore();

  const [input, setInput] = useState("");
  const [selectedSources, setSelectedSources] = useState<SourceCitation[] | null>(null);
  const [documentIds, setDocumentIds] = useState<string[]>(() => initialDocId ? [initialDocId] : []);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadConversations();
  }, []);

  useEffect(() => {
    if (currentConversationId) {
      loadMessages(currentConversationId);
    }
  }, [currentConversationId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const loadConversations = async () => {
    try {
      const res = await api.get<Conversation[]>("/chat/conversations");
      setConversations(res.data);
    } catch {}
  };

  const loadMessages = async (conversationId: string) => {
    try {
      const res = await api.get<Message[]>(`/chat/conversations/${conversationId}`);
      setMessages(res.data);
    } catch {}
  };

  const handleNewChat = () => {
    setCurrentConversation(null);
    setMessages([]);
    setDocumentIds([]);
    // Remove document_id from URL
    const url = new URL(window.location.href);
    url.searchParams.delete("document_id");
    window.history.replaceState({}, "", url.toString());
  };

  const handleSend = async (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;

    const userMessage: Message = {
      id: `temp-${Date.now()}`,
      role: "user",
      content: input,
      created_at: new Date().toISOString(),
    };
    addMessage(userMessage);
    setInput("");
    setIsStreaming(true);

    try {
      const payload: Record<string, any> = {
        message: input,
        conversation_id: currentConversationId,
      };
      if (documentIds.length > 0) {
        payload.document_ids = documentIds;
      }
      const res = await api.post<ChatResponse>("/chat/send", payload);

      const assistantMessage: Message = {
        id: `resp-${Date.now()}`,
        role: "assistant",
        content: res.data.response,
        sources: res.data.sources,
        created_at: new Date().toISOString(),
      };
      addMessage(assistantMessage);

      if (res.data.conversation_id !== currentConversationId) {
        setCurrentConversation(res.data.conversation_id);
      }

      loadConversations();
    } catch (err: any) {
      addMessage({
        id: `err-${Date.now()}`,
        role: "assistant",
        content: `Error: ${err.response?.data?.detail || "Failed to get response"}`,
        created_at: new Date().toISOString(),
      });
    } finally {
      setIsStreaming(false);
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend(e);
    }
  };

  return (
    <div className="flex h-full">
      {/* Conversations sidebar */}
      <div className="w-72 border-r border-border flex flex-col bg-sidebar-bg">
        <div className="p-3">
          <button
            onClick={handleNewChat}
            className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:opacity-90 transition-opacity"
          >
            <Plus className="w-4 h-4" />
            New Chat
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {conversations.map((conv) => (
            <button
              key={conv.id}
              onClick={() => setCurrentConversation(conv.id)}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
                currentConversationId === conv.id
                  ? "bg-accent text-accent-foreground"
                  : "text-muted-foreground hover:bg-accent/50"
              }`}
            >
              <div className="flex items-center gap-2">
                <MessageSquare className="w-3 h-3 flex-shrink-0" />
                <span className="truncate">{conv.title}</span>
              </div>
              <div className="flex items-center gap-1 mt-1 text-xs text-muted-foreground">
                <Clock className="w-3 h-3" />
                {new Date(conv.updated_at).toLocaleDateString()}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Chat area */}
      <div className="flex-1 flex flex-col">
        {/* Document filter banner */}
        {documentIds.length > 0 && (
          <div className="px-4 py-2 bg-primary/10 border-b border-primary/20 flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm text-primary">
              <FileText className="w-4 h-4" />
              <span>Querying a specific document</span>
            </div>
            <button
              onClick={() => { setDocumentIds([]); const url = new URL(window.location.href); url.searchParams.delete("document_id"); window.history.replaceState({}, "", url.toString()); }}
              className="flex items-center gap-1 text-xs text-primary hover:underline"
            >
              <X className="w-3 h-3" />
              Clear filter
            </button>
          </div>
        )}

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="w-16 h-16 bg-primary/10 rounded-2xl flex items-center justify-center mb-4">
                <MessageSquare className="w-8 h-8 text-primary" />
              </div>
              <h2 className="text-xl font-semibold text-foreground mb-2">
                Enterprise Knowledge Assistant
              </h2>
              <p className="text-muted-foreground max-w-md">
                Ask questions about company documents, policies, and procedures.
                Your access is restricted based on your role ({user?.role}).
              </p>
            </div>
          )}

          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-2xl rounded-2xl px-4 py-3 ${
                  msg.role === "user"
                    ? "bg-primary text-primary-foreground"
                    : "bg-card border border-border"
                }`}
              >
                {msg.role === "assistant" ? (
                  <div className="markdown-content text-sm text-card-foreground">
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  </div>
                ) : (
                  <p className="text-sm">{msg.content}</p>
                )}

                {msg.sources && msg.sources.length > 0 && (
                  <button
                    onClick={() => setSelectedSources(msg.sources!)}
                    className="mt-2 flex items-center gap-1 text-xs text-primary hover:underline"
                  >
                    <FileText className="w-3 h-3" />
                    {msg.sources.length} source(s)
                  </button>
                )}
              </div>
            </div>
          ))}

          {isStreaming && (
            <div className="flex justify-start">
              <div className="bg-card border border-border rounded-2xl px-4 py-3">
                <div className="flex items-center gap-1">
                  <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                  <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                  <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-4 border-t border-border">
          <form onSubmit={handleSend} className="flex gap-3">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask a question about company documents..."
              rows={1}
              className="flex-1 px-4 py-2.5 bg-background border border-input rounded-xl focus:outline-none focus:ring-2 focus:ring-ring resize-none text-foreground text-sm"
            />
            <button
              type="submit"
              disabled={!input.trim() || isStreaming}
              className="px-4 py-2.5 bg-primary text-primary-foreground rounded-xl hover:opacity-90 transition-opacity disabled:opacity-50"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>

      {/* Sources panel */}
      {selectedSources && (
        <div className="w-80 border-l border-border bg-card p-4 overflow-y-auto">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-foreground">Sources</h3>
            <button
              onClick={() => setSelectedSources(null)}
              className="text-muted-foreground hover:text-foreground text-sm"
            >
              Close
            </button>
          </div>
          <div className="space-y-3">
            {selectedSources.map((source, idx) => (
              <div key={idx} className="p-3 bg-background border border-border rounded-lg">
                <div className="flex items-center gap-2 mb-1">
                  <FileText className="w-3 h-3 text-primary" />
                  <span className="text-sm font-medium text-foreground truncate">
                    {source.filename}
                  </span>
                </div>
                <div className="flex items-center gap-2 text-xs text-muted-foreground mb-2">
                  <span className="px-1.5 py-0.5 bg-muted rounded">{source.department}</span>
                  <span>Score: {(source.score * 100).toFixed(0)}%</span>
                </div>
                <p className="text-xs text-muted-foreground line-clamp-3">
                  {source.content_snippet}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
