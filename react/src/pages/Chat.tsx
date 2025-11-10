import { useState, useRef, useEffect } from 'react';
import { gsap } from 'gsap';
import { useGSAP } from '@gsap/react';
import { queryRAG } from '../utils/api';
import { Button, Card } from '../components/ui';
import type { RAGQueryResponse } from '../types/api';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  context?: RAGQueryResponse['context_used'];
  timestamp: Date;
}

export function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useGSAP(() => {
    if (!messagesContainerRef.current) return;

    const lastMessage = messagesContainerRef.current.lastElementChild;
    if (lastMessage) {
      gsap.from(lastMessage, {
        opacity: 0,
        y: 20,
        duration: 0.5,
        ease: 'power2.out',
      });
    }
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await queryRAG({ query: input });

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: response.answer,
        context: response.context_used,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: `Error: ${error instanceof Error ? error.message : 'Failed to get response'}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const exampleQuestions = [
    'What are the best weapons for a stealth build?',
    'Compare the Fixer vs Handmade rifle',
    'What perks work well with heavy weapons?',
    'Tell me about bloodied builds',
    'What mutations should I use for melee?',
  ];

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="text-center space-y-2">
        <h1 className="text-4xl font-bold text-pink-400">AI Chat Assistant</h1>
        <p className="text-gray-400">Ask questions about builds, items, and strategies</p>
      </div>

      {/* Chat Container */}
      <Card className="bg-base-200 h-[600px] flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4" ref={messagesContainerRef}>
          {messages.length === 0 && (
            <div className="text-center space-y-6 py-12">
              <div className="text-gray-400">
                <svg
                  className="w-16 h-16 mx-auto mb-4 text-pink-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                  />
                </svg>
                <p className="text-lg mb-4">Start a conversation with the AI</p>
                <p className="text-sm">Powered by RAG & Claude AI</p>
              </div>

              <div className="space-y-2">
                <p className="text-sm text-gray-500">Try asking:</p>
                <div className="flex flex-wrap gap-2 justify-center">
                  {exampleQuestions.map((question, index) => (
                    <button
                      key={index}
                      className="btn btn-sm btn-outline"
                      onClick={() => setInput(question)}
                    >
                      {question}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {messages.map((message) => (
            <div
              key={message.id}
              className={`chat ${message.type === 'user' ? 'chat-end' : 'chat-start'}`}
            >
              <div className="chat-image avatar">
                <div className="w-10 rounded-full bg-base-300 flex items-center justify-center">
                  {message.type === 'user' ? (
                    <svg
                      className="w-6 h-6"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                      />
                    </svg>
                  ) : (
                    <svg
                      className="w-6 h-6 text-pink-400"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                      />
                    </svg>
                  )}
                </div>
              </div>
              <div className="chat-header">
                {message.type === 'user' ? 'You' : 'AI Assistant'}
                <time className="text-xs opacity-50 ml-2">
                  {message.timestamp.toLocaleTimeString()}
                </time>
              </div>
              <div
                className={`chat-bubble ${
                  message.type === 'user' ? 'chat-bubble-primary' : 'chat-bubble-secondary'
                }`}
              >
                {message.content}
              </div>

              {/* Context Sources */}
              {message.context && message.context.length > 0 && (
                <div className="chat-footer mt-2">
                  <details className="collapse collapse-arrow bg-base-300 rounded-box">
                    <summary className="collapse-title text-xs">
                      Sources ({message.context.length} items)
                    </summary>
                    <div className="collapse-content">
                      <div className="space-y-2">
                        {message.context.slice(0, 5).map((item, idx) => (
                          <div key={idx} className="text-xs bg-base-100 p-2 rounded">
                            <div className="font-semibold text-blue-400">{item.item_name}</div>
                            <div className="text-gray-500">
                              {item.item_type} - Similarity: {(item.similarity * 100).toFixed(1)}%
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </details>
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="chat chat-start">
              <div className="chat-image avatar">
                <div className="w-10 rounded-full bg-base-300 flex items-center justify-center">
                  <span className="loading loading-spinner loading-sm text-pink-400"></span>
                </div>
              </div>
              <div className="chat-bubble chat-bubble-secondary">Thinking...</div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <form onSubmit={handleSubmit} className="border-t border-base-300 p-4">
          <div className="flex gap-2">
            <input
              type="text"
              className="input input-bordered flex-1"
              placeholder="Ask about builds, weapons, armor, perks..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={loading}
            />
            <Button type="submit" variant="primary" disabled={loading || !input.trim()}>
              {loading ? <span className="loading loading-spinner"></span> : 'Send'}
            </Button>
          </div>
        </form>
      </Card>

      {/* Info */}
      <div className="alert alert-info">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          className="stroke-current shrink-0 w-6 h-6"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <div>
          <h3 className="font-bold">How it works</h3>
          <div className="text-sm">
            This chat uses Retrieval-Augmented Generation (RAG) combining semantic search with
            Claude AI for accurate, context-aware responses about Fallout 76 builds
          </div>
        </div>
      </div>
    </div>
  );
}
