'use client';

import { useRef, useEffect } from 'react';
import { Bot, Loader2 } from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';

interface ChatMessage {
  id: string;
  message: string;
  response: string;
  success: boolean;
  timestamp: Date;
  files?: SandboxFile[];
}

interface SandboxFile {
  name: string;
  path: string;
  size: number;
  type: string;
}

interface ChatAreaProps {
  chatHistory: ChatMessage[];
  isSending: boolean;
}

export default function ChatArea({ chatHistory, isSending }: ChatAreaProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatHistory]);

  return (
    <div className="flex-1 flex flex-col">
      <ScrollArea className="flex-1 px-6">
        {chatHistory.length === 0 ? (
          <div className="text-center text-gray-500 mt-70">
            <div className="max-w-md mx-auto">
              <h3 className="text-lg font-medium mb-2">Welcome to Atlas</h3>
            </div>
          </div>
        ) : (
          <div className="space-y-6 py-6">
            {chatHistory.map((chat) => (
              <div key={chat.id} className="space-y-3">
                {/* 用户消息 */}
                <div className="flex justify-end">
                  <div className="bg-white border border-gray-200 text-gray-900 rounded-lg p-3 max-w-[80%] shadow-sm">
                    <p className="text-sm">{chat.message}</p>
                  </div>
                </div>
                
                {/* AI响应 */}
                {chat.response && (
                  <div className="flex justify-start">
                    <div className={`rounded-lg p-3 max-w-[80%] ${
                      chat.success 
                        ? 'bg-green-50 border border-green-200' 
                        : 'bg-red-50 border border-red-200'
                    }`}>
                      <div className="flex items-start gap-2">
                        <Bot className={`h-4 w-4 mt-0.5 ${
                          chat.success ? 'text-green-600' : 'text-red-600'
                        }`} />
                        <div>
                          <p className={`text-sm ${
                            chat.success ? 'text-green-800' : 'text-red-800'
                          }`}>
                            {chat.response}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
            
            {/* 加载指示器 */}
            {isSending && (
              <div className="flex justify-start">
                <div className="bg-gray-100 rounded-lg p-3">
                  <div className="flex items-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin text-gray-600" />
                    <p className="text-sm text-gray-600">AI is working...</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
        <div ref={messagesEndRef} />
      </ScrollArea>
    </div>
  );
}
