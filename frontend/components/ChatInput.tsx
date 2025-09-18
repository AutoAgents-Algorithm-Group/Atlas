'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import Image from 'next/image';
import { useTranslations } from 'next-intl';

interface ChatInputProps {
  currentMessage: string;
  setCurrentMessage: (message: string) => void;
  sendMessage: () => void;
  isSending: boolean;
  isActive: boolean;
  isInitialized: boolean;
  quickMessages: string[];
}

export default function ChatInput({
  currentMessage,
  setCurrentMessage,
  sendMessage,
  isSending,
  isActive,
  isInitialized,
  quickMessages
}: ChatInputProps) {
  const t = useTranslations();
  const [isHovering, setIsHovering] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // 自动调整 textarea 高度
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      const scrollHeight = textareaRef.current.scrollHeight;
      const maxHeight = 150;
      textareaRef.current.style.height = Math.min(scrollHeight, maxHeight) + 'px';
    }
  }, [currentMessage]);

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setCurrentMessage(e.target.value);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (currentMessage.trim() && !isSending && isActive && isInitialized) {
      sendMessage();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const isDisabled = isSending || !isActive || !isInitialized;
  const canSend = currentMessage.trim() && !isDisabled;

  return (
    <div className="p-4 bg-[#faf9f6]">
      {/* 快捷消息按钮 */}
      {isActive && isInitialized && !isSending && (
        <div className="mb-3">
          <p className="text-xs text-gray-500 mb-2">{t('chat.quickActions')}</p>
          <div className="flex flex-wrap gap-2">
            {quickMessages.map((msg, index) => (
              <Button
                key={index}
                variant="outline"
                size="sm"
                className="text-xs h-8 hover:bg-gray-100 cursor-pointer"
                onClick={() => setCurrentMessage(msg)}
              >
                {msg.length > 30 ? msg.substring(0, 30) + '...' : msg}
              </Button>
            ))}
          </div>
        </div>
      )}
      
      {/* 输入表单 */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm">
        <form onSubmit={handleSubmit} className="p-4">
          <div className="flex gap-3 items-end">
            <div className="flex-1">
              <textarea
                ref={textareaRef}
                value={currentMessage}
                onChange={handleInputChange}
                onKeyDown={handleKeyDown}
                placeholder={
                  !isActive || !isInitialized 
                    ? t('chat.startSessionFirst')
                    : t('chat.planAndExecute')
                }
                className="w-full bg-transparent border-none focus:outline-none text-gray-700 text-sm placeholder-gray-400 resize-none overflow-y-auto"
                disabled={isDisabled}
                rows={1}
                style={{ 
                  minHeight: '20px',
                  maxHeight: '150px'
                }}
              />
            </div>
            
            {/* 发送按钮 */}
            <button 
              type="submit" 
              onMouseEnter={() => setIsHovering(true)}
              onMouseLeave={() => setIsHovering(false)}
              className="p-2 rounded-full text-white transition-all duration-200 min-h-[36px] min-w-[36px] flex items-center justify-center cursor-pointer"
              style={{
                backgroundColor: canSend || isSending
                  ? (isHovering ? '#4d4d4d' : '#000000') 
                  : '#d7d7d7',
                transform: isHovering && (canSend || isSending) ? 'scale(1.05)' : 'scale(1)'
              }}
              disabled={!canSend && !isSending}
            >
              {isSending ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Image 
                  src="/send.svg" 
                  alt="Send" 
                  width={20} 
                  height={20} 
                  className="w-5 h-5 filter brightness-0 invert"
                />
              )}
            </button>
          </div>
        </form>
      </div>

      {/* 提示文本 */}
      <p className="text-xs text-gray-500 mt-2 text-center">
        {t('chat.agentPatience')}
      </p>
    </div>
  );
}
