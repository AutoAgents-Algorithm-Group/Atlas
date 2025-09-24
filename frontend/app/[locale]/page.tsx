'use client';

import React, { useState, useEffect, useCallback } from 'react';
import toast from 'react-hot-toast';
import { useTranslations } from 'next-intl';
import ChatHeader from '@/components/ChatHeader';
import ChatArea from '@/components/ChatArea';
import ChatInput from '@/components/ChatInput';
import Artifacts from '@/components/Artifacts';

// 数据类型定义
interface SessionStatus {
  success: boolean;
  active: boolean;
  initialized: boolean;
  stream_url?: string;
  message: string;
}

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

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8100';

export default function ChatPage() {
  const t = useTranslations();
  
  // 会话状态
  const [isCreatingSession, setIsCreatingSession] = useState(false);
  // const [isClosingSession, setIsClosingSession] = useState(false); // Removed as no longer needed
  const [streamUrl, setStreamUrl] = useState<string>('');
  const [isActive, setIsActive] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);
  // const [statusMessage, setStatusMessage] = useState(''); // Removed as no longer needed
  
  // 聊天状态
  const [currentMessage, setCurrentMessage] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  
  // 文件状态
  const [sandboxFiles, setSandboxFiles] = useState<SandboxFile[]>([]);
  const [isLoadingFiles, setIsLoadingFiles] = useState(false);
  const [isFilesDialogOpen, setIsFilesDialogOpen] = useState(false);
  
  // 步骤/进度状态
  const [currentStep, setCurrentStep] = useState(1);
  const [totalSteps, setTotalSteps] = useState(1);
  const [currentCommand, setCurrentCommand] = useState('');
  const [currentFilePath, setCurrentFilePath] = useState('');
  const [currentBrowserUrl, setCurrentBrowserUrl] = useState('');
  

  // 检查会话状态
  const checkSessionStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/session/status`);
      const data: SessionStatus = await response.json();
      
      if (data.success) {
        setIsActive(data.active);
        setIsInitialized(data.initialized);
        if (data.stream_url) {
          setStreamUrl(data.stream_url);
        }
      }
    } catch (error) {
      console.error('Failed to check session status:', error);
      toast.error(t('messages.backendConnectFailed'));
    }
  };

  // 创建会话
  const createSession = async () => {
    setIsCreatingSession(true);
    
    try {
      const response = await fetch(`${API_BASE}/api/session/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      const data = await response.json();
      
      if (data.success) {
        setStreamUrl(data.stream_url);
        setIsActive(true);
        setIsInitialized(true);
        toast.success(t('messages.sessionCreatedSuccess'));
      } else {
        toast.error(data.error || t('messages.backendConnectFailed'));
      }
    } catch (error) {
      console.error('Error creating session:', error);
      toast.error(t('messages.backendConnectFailed'));
    } finally {
      setIsCreatingSession(false);
    }
  };

  // pauseSession function removed as no longer needed

  // 恢复会话
  const resumeSession = async () => {
    setIsCreatingSession(true);
    
    try {
      const response = await fetch(`${API_BASE}/api/session/resume`, {
        method: 'POST',
      });
      
      const data = await response.json();
      
      if (data.success) {
        setStreamUrl(data.stream_url);
        setIsActive(true);
        toast.success(t('messages.sessionResumedSuccess'));
        await checkSessionStatus(); // 重新检查状态
      } else {
        toast.error(data.error || t('messages.backendConnectFailed'));
      }
    } catch (error) {
      console.error('Error resuming session:', error);
      toast.error(t('messages.backendConnectFailed'));
    } finally {
      setIsCreatingSession(false);
    }
  };

  // 终止会话
  const terminateSession = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/session/terminate`, {
        method: 'DELETE',
      });
      
      const data = await response.json();
      
      if (data.success) {
        setStreamUrl('');
        setIsActive(false);
        setIsInitialized(false);
        setChatHistory([]);
        setSandboxFiles([]);
        toast.success(t('messages.sessionTerminatedSuccess'));
      } else {
        toast.error(data.error || t('messages.backendConnectFailed'));
      }
    } catch (error) {
      console.error('Error terminating session:', error);
      toast.error(t('messages.backendConnectFailed'));
    }
  };

  // 发送消息
  const sendMessage = async () => {
    if (!currentMessage.trim()) {
      toast.error(t('messages.enterMessage'));
      return;
    }

    if (!isActive || !isInitialized) {
      toast.error(t('messages.createSessionFirst'));
      return;
    }

    const messageId = Date.now().toString();
    const message = currentMessage.trim();
    
    // 添加用户消息到历史记录
    const newMessage: ChatMessage = {
      id: messageId,
      message: message,
      response: '',
      success: false,
      timestamp: new Date()
    };
    
    setChatHistory(prev => [...prev, newMessage]);
    setCurrentMessage('');
    setIsSending(true);
    
    try {
      const response = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          context: {}
        }),
      });
      
      const data = await response.json();
      
      // 更新消息状态
      setChatHistory(prev => 
        prev.map(msg => 
          msg.id === messageId 
            ? { ...msg, response: data.result || data.message, success: data.success }
            : msg
        )
      );
      
      if (data.success) {
        toast.success(t('messages.taskCompletedSuccess'));
        // Update step tracking
        setCurrentCommand(message);
        setTotalSteps(chatHistory.length + 1);
        setCurrentStep(chatHistory.length + 1);
      } else {
        toast.error(data.error || t('messages.taskExecutionFailed'));
      }
      
    } catch (error) {
      console.error('Error sending message:', error);
      setChatHistory(prev => 
        prev.map(msg => 
          msg.id === messageId 
            ? { ...msg, response: t('messages.backendConnectFailed'), success: false }
            : msg
        )
      );
      toast.error(t('messages.backendConnectFailed'));
    } finally {
      setIsSending(false);
    }
  };


  // 步骤导航
  const handlePreviousStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleNextStep = () => {
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
    }
  };

  // 从聊天历史中提取URL
  const extractUrlFromChatHistory = () => {
    if (chatHistory.length === 0) return;
    
    // 查看最近的几条成功消息，寻找URL
    const recentMessages = chatHistory.slice(-3).reverse();
    
    for (const message of recentMessages) {
      if (message.success && (message.message || message.response)) {
        const text = `${message.message} ${message.response}`.toLowerCase();
        
        // 查找常见的URL模式
        const urlPatterns = [
          /https?:\/\/[^\s]+/gi,
          /www\.[^\s]+/gi,
          /(访问|打开|浏览|visit|open|browse)\s+([^\s]+\.[^\s]+)/gi,
          /(搜索|search)\s+([^\s]+)/gi
        ];
        
        for (const pattern of urlPatterns) {
          const matches = text.match(pattern);
          if (matches && matches[0]) {
            let url = matches[0];
            
            // 如果是搜索指令，构造搜索URL
            if (text.includes('搜索') || text.includes('search')) {
              const searchTerm = url.replace(/(搜索|search)\s+/, '');
              url = `https://www.google.com/search?q=${encodeURIComponent(searchTerm)}`;
            }
            // 如果没有协议，添加https
            else if (!url.startsWith('http') && url.includes('.')) {
              url = `https://${url}`;
            }
            
            if (url && url !== currentBrowserUrl) {
              setCurrentBrowserUrl(url);
              return;
            }
          }
        }
      }
    }
  };

  // 获取沙盒文件列表
  const fetchSandboxFiles = useCallback(async () => {
    if (!isActive) return;
    
    setIsLoadingFiles(true);
    try {
      const response = await fetch(`${API_BASE}/api/files`);
      const data = await response.json();
      
      if (data.success) {
        setSandboxFiles(data.files || []);
      } else {
        console.error('Failed to fetch files:', data.error);
      }
    } catch (error) {
      console.error('Error fetching files:', error);
    } finally {
      setIsLoadingFiles(false);
    }
  }, [isActive]);

  // 下载文件
  const downloadFile = async (file: SandboxFile) => {
    try {
      const response = await fetch(`${API_BASE}/api/files/download?file_path=${encodeURIComponent(file.path)}`);
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = file.name;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        toast.success(t('messages.downloadSuccess', { filename: file.name }));
      } else {
        toast.error(t('messages.downloadFailed'));
      }
    } catch (error) {
      console.error('Error downloading file:', error);
      toast.error(t('messages.downloadFailed'));
    }
  };

  // 预设消息
  const quickMessages = t.raw('quickMessages') as string[];

  // 页面加载时检查状态并暂停会话
  useEffect(() => {
    const initializePage = async () => {
      await checkSessionStatus();
    };
    initializePage();
  }, []);

  // 监听会话状态变化，自动获取文件列表
  useEffect(() => {
    if (isActive && isInitialized) {
      fetchSandboxFiles();
    }
  }, [isActive, isInitialized, fetchSandboxFiles]);

  // 监听聊天历史变化，提取URL信息
  useEffect(() => {
    if (isActive) {
      extractUrlFromChatHistory();
    } else {
      setCurrentBrowserUrl('');
    }
  }, [chatHistory, isActive]);

  // 监听聊天历史，检测文件创建
  useEffect(() => {
    if (chatHistory.length > 0) {
      const lastMessage = chatHistory[chatHistory.length - 1];
      if (lastMessage.success && lastMessage.response.includes('file')) {
        // 延迟一秒后刷新文件列表，确保文件已创建
        setTimeout(() => {
          fetchSandboxFiles();
        }, 1000);
        
        // Try to extract file path from response
        const pathMatch = lastMessage.response.match(/\/[^\s]+\.[a-z]+/i);
        if (pathMatch) {
          setCurrentFilePath(pathMatch[0]);
        }
      }
    }
  }, [chatHistory, fetchSandboxFiles]);

  return (
    <div className="h-screen bg-[#faf9f6] flex">
      {/* 左侧区域 */}
      <div className="flex-1 flex flex-col">
        <ChatHeader
          isActive={isActive}
          sandboxFiles={sandboxFiles}
          isFilesDialogOpen={isFilesDialogOpen}
          setIsFilesDialogOpen={setIsFilesDialogOpen}
          isLoadingFiles={isLoadingFiles}
          fetchSandboxFiles={fetchSandboxFiles}
          downloadFile={downloadFile}
        />
        
        <ChatArea
          chatHistory={chatHistory}
          isSending={isSending}
        />
        
        <ChatInput
          currentMessage={currentMessage}
          setCurrentMessage={setCurrentMessage}
          sendMessage={sendMessage}
          isSending={isSending}
          isActive={isActive}
          isInitialized={isInitialized}
          quickMessages={quickMessages}
        />
      </div>
      
      {/* 右侧预览面板容器 */}
      <div className="w-[48rem] py-4 pr-4">
        <Artifacts
          streamUrl={streamUrl}
          isActive={isActive}
          isInitialized={isInitialized}
          isCreatingSession={isCreatingSession}
          currentStep={currentStep}
          totalSteps={totalSteps}
          currentCommand={currentCommand}
          currentFilePath={currentFilePath}
          currentBrowserUrl={currentBrowserUrl}
          createSession={createSession}
          resumeSession={resumeSession}
          terminateSession={terminateSession}
          handlePreviousStep={handlePreviousStep}
          handleNextStep={handleNextStep}
        />
      </div>
    </div>
  );
}