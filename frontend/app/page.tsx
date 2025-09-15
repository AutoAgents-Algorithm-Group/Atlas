'use client';

import { useState, useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { AlertCircle, Monitor, Play, Pause, Square, Loader2, Bot, Send, MessageSquare, Globe, ExternalLink, Download, FileText, Computer, Shield, ShieldCheck } from 'lucide-react';
import { Textarea } from '@/components/ui/textarea';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  ResizablePanelGroup,
  ResizablePanel,
  ResizableHandle,
} from '@/components/ui/resizable';
import toast from 'react-hot-toast';

// 数据类型定义
interface SessionStatus {
  success: boolean;
  active: boolean;
  initialized: boolean;
  taken_over: boolean;
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

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function ChatPage() {
  // 会话状态
  const [isCreatingSession, setIsCreatingSession] = useState(false);
  const [isClosingSession, setIsClosingSession] = useState(false);
  const [streamUrl, setStreamUrl] = useState<string>('');
  const [isActive, setIsActive] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);
  const [isTakenOver, setIsTakenOver] = useState(false);
  const [isTakingOver, setIsTakingOver] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');
  
  // 聊天状态
  const [currentMessage, setCurrentMessage] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  
  // 文件状态
  const [sandboxFiles, setSandboxFiles] = useState<SandboxFile[]>([]);
  const [isLoadingFiles, setIsLoadingFiles] = useState(false);
  
  // 引用
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatHistory]);

  // 检查会话状态
  const checkSessionStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/session/status`);
      const data: SessionStatus = await response.json();
      
      if (data.success) {
        setIsActive(data.active);
        setIsInitialized(data.initialized);
        setIsTakenOver(data.taken_over || false);
        if (data.stream_url) {
          setStreamUrl(data.stream_url);
        }
        setStatusMessage(data.message);
      }
    } catch (error) {
      console.error('Failed to check session status:', error);
      setStatusMessage('Failed to connect to backend');
      toast.error('Failed to connect to backend');
    }
  };

  // 创建会话
  const createSession = async () => {
    setIsCreatingSession(true);
    setStatusMessage('Creating browser session...');
    
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
        setStatusMessage(data.message);
        toast.success('Browser session created successfully!');
      } else {
        setStatusMessage(data.error || 'Failed to create session');
        toast.error(data.error || 'Failed to create session');
      }
    } catch (error) {
      console.error('Error creating session:', error);
      setStatusMessage('Failed to connect to backend');
      toast.error('Failed to connect to backend');
    } finally {
      setIsCreatingSession(false);
    }
  };

  // 暂停会话
  const pauseSession = async () => {
    setIsClosingSession(true);
    setStatusMessage('Pausing browser session...');
    
    try {
      const response = await fetch(`${API_BASE}/api/session/close`, {
        method: 'DELETE',
      });
      
      const data = await response.json();
      
      if (data.success) {
        setStreamUrl('');
        setIsActive(false);
        setIsInitialized(false);
        setIsTakenOver(false);
        setStatusMessage(data.message);
        toast.success('Session paused successfully (sandbox preserved)');
      } else {
        setStatusMessage(data.error || 'Failed to pause session');
        toast.error(data.error || 'Failed to pause session');
      }
    } catch (error) {
      console.error('Error pausing session:', error);
      setStatusMessage('Failed to connect to backend');
      toast.error('Failed to connect to backend');
    } finally {
      setIsClosingSession(false);
    }
  };

  // 恢复会话
  const resumeSession = async () => {
    setIsCreatingSession(true);
    setStatusMessage('Resuming browser session...');
    
    try {
      const response = await fetch(`${API_BASE}/api/session/resume`, {
        method: 'POST',
      });
      
      const data = await response.json();
      
      if (data.success) {
        setStreamUrl(data.stream_url);
        setIsActive(true);
        setStatusMessage(data.message);
        toast.success('Session resumed successfully');
        await checkSessionStatus(); // 重新检查状态
      } else {
        setStatusMessage(data.error || 'Failed to resume session');
        toast.error(data.error || 'Failed to resume session');
      }
    } catch (error) {
      console.error('Error resuming session:', error);
      setStatusMessage('Failed to connect to backend');
      toast.error('Failed to connect to backend');
    } finally {
      setIsCreatingSession(false);
    }
  };

  // 销毁会话
  const destroySession = async () => {
    if (!window.confirm('Are you sure you want to destroy the session? This will permanently delete the sandbox.')) {
      return;
    }
    
    setIsClosingSession(true);
    setStatusMessage('Destroying browser session...');
    
    try {
      const response = await fetch(`${API_BASE}/api/session/destroy`, {
        method: 'DELETE',
      });
      
      const data = await response.json();
      
      if (data.success) {
        setStreamUrl('');
        setIsActive(false);
        setIsInitialized(false);
        setIsTakenOver(false);
        setStatusMessage(data.message);
        setChatHistory([]); // 清空聊天记录
        setSandboxFiles([]); // 清空文件列表
        toast.success('Session destroyed successfully');
      } else {
        setStatusMessage(data.error || 'Failed to destroy session');
        toast.error(data.error || 'Failed to destroy session');
      }
    } catch (error) {
      console.error('Error destroying session:', error);
      setStatusMessage('Failed to connect to backend');
      toast.error('Failed to connect to backend');
    } finally {
      setIsClosingSession(false);
    }
  };

  // 接管桌面
  const takeOverDesktop = async () => {
    setIsTakingOver(true);
    
    try {
      const response = await fetch(`${API_BASE}/api/desktop/takeover`, {
        method: 'POST',
      });
      
      const data = await response.json();
      
      if (data.success) {
        setIsTakenOver(true);
        toast.success('Desktop control taken over successfully!');
      } else {
        toast.error(data.message || 'Failed to take over desktop');
      }
    } catch (error) {
      console.error('Error taking over desktop:', error);
      toast.error('Failed to connect to backend');
    } finally {
      setIsTakingOver(false);
    }
  };

  // 释放桌面
  const releaseDesktop = async () => {
    setIsTakingOver(true);
    
    try {
      const response = await fetch(`${API_BASE}/api/desktop/release`, {
        method: 'POST',
      });
      
      const data = await response.json();
      
      if (data.success) {
        setIsTakenOver(false);
        toast.success('Desktop control released successfully!');
      } else {
        toast.error(data.message || 'Failed to release desktop');
      }
    } catch (error) {
      console.error('Error releasing desktop:', error);
      toast.error('Failed to connect to backend');
    } finally {
      setIsTakingOver(false);
    }
  };

  // 发送消息
  const sendMessage = async () => {
    if (!currentMessage.trim()) {
      toast.error('Please enter a message');
      return;
    }

    if (!isActive || !isInitialized) {
      toast.error('Please create a session first');
      return;
    }

    if (!isTakenOver) {
      toast.error('Please take over desktop control first');
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
        toast.success('Task completed successfully');
      } else {
        toast.error(data.error || 'Task execution failed');
      }
      
    } catch (error) {
      console.error('Error sending message:', error);
      setChatHistory(prev => 
        prev.map(msg => 
          msg.id === messageId 
            ? { ...msg, response: 'Failed to connect to backend', success: false }
            : msg
        )
      );
      toast.error('Failed to connect to backend');
    } finally {
      setIsSending(false);
    }
  };

  // 处理键盘事件
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // 获取沙盒文件列表
  const fetchSandboxFiles = async () => {
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
  };

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
        toast.success(`Downloaded ${file.name}`);
      } else {
        toast.error('Failed to download file');
      }
    } catch (error) {
      console.error('Error downloading file:', error);
      toast.error('Failed to download file');
    }
  };

  // 预设消息
  const quickMessages = [
    "打开 Google 并搜索人工智能",
    "访问 GitHub 并浏览热门项目",
    "打开淘宝搜索手机",
    "访问百度并搜索今天的新闻",
    "打开 YouTube 并搜索编程教程"
  ];

  // 页面加载时检查状态
  useEffect(() => {
    checkSessionStatus();
  }, []);

  // 监听会话状态变化，自动获取文件列表
  useEffect(() => {
    if (isActive && isInitialized) {
      fetchSandboxFiles();
    }
  }, [isActive, isInitialized]);

  // 监听聊天历史，检测文件创建
  useEffect(() => {
    if (chatHistory.length > 0) {
      const lastMessage = chatHistory[chatHistory.length - 1];
      if (lastMessage.success && lastMessage.response.includes('file')) {
        // 延迟一秒后刷新文件列表，确保文件已创建
        setTimeout(() => {
          fetchSandboxFiles();
        }, 1000);
      }
    }
  }, [chatHistory]);

  return (
    <div className="h-screen bg-[#faf9f6]">
      {/* 可调整大小的面板组 */}
      <ResizablePanelGroup direction="horizontal" className="h-screen p-4 gap-4">
        {/* 左侧聊天面板 */}
        <ResizablePanel defaultSize={50} minSize={35}>
          <Card className="h-full flex flex-col">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <Bot className="h-5 w-5 text-blue-600" />
                    Browser Use Chat
                  </CardTitle>
                  <CardDescription>
                    Control your browser with natural language
                  </CardDescription>
                </div>
                
                <div className="flex items-center gap-3">
                  {/* 状态指示 */}
                  <div className="flex items-center gap-2">
                    <Badge variant={isActive && isInitialized ? 'default' : 'secondary'}>
                      {isActive && isInitialized ? 'Ready' : 'Inactive'}
                    </Badge>
                    {isActive && isInitialized && (
                      <Badge variant={isTakenOver ? 'destructive' : 'outline'}>
                        {isTakenOver ? 'Controlled' : 'View Only'}
                      </Badge>
                    )}
                    {streamUrl && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => window.open(streamUrl, '_blank')}
                      >
                        <ExternalLink className="h-4 w-4 mr-1" />
                        View Desktop
                      </Button>
                    )}
                  </div>
                  
                  {/* 会话控制按钮 */}
                  <div className="flex gap-2">
                    <Button
                      onClick={createSession}
                      disabled={isCreatingSession || isActive}
                      size="sm"
                    >
                      {isCreatingSession ? (
                        <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                      ) : (
                        <Play className="h-4 w-4 mr-1" />
                      )}
                      Start Session
                    </Button>
                    
                    {isActive && isInitialized && (
                      <Button
                        onClick={isTakenOver ? releaseDesktop : takeOverDesktop}
                        disabled={isTakingOver}
                        variant={isTakenOver ? "outline" : "default"}
                        size="sm"
                      >
                        {isTakingOver ? (
                          <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                        ) : isTakenOver ? (
                          <Shield className="h-4 w-4 mr-1" />
                        ) : (
                          <ShieldCheck className="h-4 w-4 mr-1" />
                        )}
                        {isTakenOver ? 'Release' : 'Take Over'}
                      </Button>
                    )}
                    
                    <Button
                      onClick={pauseSession}
                      disabled={isClosingSession || !isActive}
                      variant="outline"
                      size="sm"
                    >
                      {isClosingSession ? (
                        <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                      ) : (
                        <Pause className="h-4 w-4 mr-1" />
                      )}
                      Pause
                    </Button>
                    
                    <Button
                      onClick={resumeSession}
                      disabled={isCreatingSession || isActive}
                      variant="default"
                      size="sm"
                    >
                      {isCreatingSession ? (
                        <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                      ) : (
                        <Play className="h-4 w-4 mr-1" />
                      )}
                      Resume
                    </Button>
                    
                    <Button
                      onClick={destroySession}
                      disabled={isClosingSession}
                      variant="destructive"
                      size="sm"
                    >
                      {isClosingSession ? (
                        <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                      ) : (
                        <Square className="h-4 w-4 mr-1" />
                      )}
                      Destroy
                    </Button>
                  </div>
                </div>
              </div>
              
              {/* 状态消息 */}
              {statusMessage && (
                <div className="mt-3 flex items-start gap-2 p-3 bg-blue-50 rounded-lg">
                  <AlertCircle className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                  <p className="text-sm text-blue-800">{statusMessage}</p>
                </div>
              )}
            </CardHeader>
            
            <CardContent className="flex-1 flex flex-col p-0">
              {/* 聊天消息区域 */}
              <ScrollArea className="flex-1 px-6">
                {chatHistory.length === 0 ? (
                  <div className="text-center text-gray-500 mt-20">
                    <MessageSquare className="h-16 w-16 mx-auto mb-4 text-gray-300" />
                    <h3 className="text-lg font-medium mb-2">Welcome to Browser Use Chat</h3>
                    <p className="text-sm">
                      Start a session and send a message to control your browser with AI
                    </p>
                    
                    {/* 快捷消息 */}
                    {!isActive && (
                      <div className="mt-6">
                        <p className="text-sm font-medium mb-3">Quick start examples:</p>
                        <div className="grid grid-cols-1 gap-2 max-w-md mx-auto">
                          {quickMessages.slice(0, 3).map((msg, index) => (
                            <div key={index} className="text-xs bg-gray-100 rounded-lg p-2 text-gray-600">
                              "{msg}"
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="space-y-6 py-6">
                    {chatHistory.map((chat) => (
                      <div key={chat.id} className="space-y-3">
                        {/* 用户消息 */}
                        <div className="flex justify-end">
                          <div className="bg-blue-600 text-white rounded-lg p-3 max-w-[80%]">
                            <p className="text-sm">{chat.message}</p>
                            <p className="text-xs text-blue-100 mt-1">
                              {chat.timestamp.toLocaleTimeString()}
                            </p>
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

              {/* 输入区域 */}
              <div className="border-t p-4">
                {/* 快捷消息按钮 */}
                {isActive && isInitialized && isTakenOver && (
                  <div className="mb-3">
                    <p className="text-xs text-gray-500 mb-2">Quick actions:</p>
                    <div className="flex flex-wrap gap-2">
                      {quickMessages.map((msg, index) => (
                        <Button
                          key={index}
                          variant="outline"
                          size="sm"
                          className="text-xs h-8"
                          onClick={() => setCurrentMessage(msg)}
                          disabled={isSending}
                        >
                          {msg.length > 30 ? msg.substring(0, 30) + '...' : msg}
                        </Button>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* 消息输入框 */}
                <div className="flex gap-3">
                  <Textarea
                    placeholder={
                      !isActive || !isInitialized 
                        ? "Start a session first to begin chatting"
                        : !isTakenOver
                        ? "Take over desktop control to send commands"
                        : "Type your message here... (e.g., 'Open Google and search for AI')"
                    }
                    value={currentMessage}
                    onChange={(e) => setCurrentMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    className="flex-1 min-h-[60px] resize-none"
                    disabled={isSending || !isActive || !isInitialized || !isTakenOver}
                  />
                  <Button
                    onClick={sendMessage}
                    disabled={isSending || !isActive || !isInitialized || !isTakenOver || !currentMessage.trim()}
                    size="lg"
                    className="px-6"
                  >
                    {isSending ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Send className="h-4 w-4" />
                    )}
                  </Button>
                </div>
                
                <p className="text-xs text-gray-500 mt-2">
                  Press Enter to send, Shift+Enter for new line
                </p>
              </div>
            </CardContent>
          </Card>
        </ResizablePanel>

        <ResizableHandle withHandle />

        {/* 右侧信息面板 */}
        <ResizablePanel defaultSize={50} minSize={35}>
          <Tabs defaultValue="computer" className="h-full">
            <Card className="h-full flex flex-col">
              <CardHeader className="">
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>E2B Sandbox</CardTitle>
                    <CardDescription>
                      Real-time browser control and file management
                    </CardDescription>
                  </div>
                  
                  {/* Tab样式模仿图片中的设计 */}
                  <TabsList className="bg-gray-100 p-1 rounded-lg h-auto">
                    <TabsTrigger 
                      value="computer" 
                      className="flex items-center gap-2 px-3 py-1.5 rounded-md text-sm font-medium transition-all data-[state=active]:bg-gray-900 data-[state=active]:text-white data-[state=inactive]:text-gray-600 data-[state=inactive]:hover:text-gray-900 data-[state=inactive]:bg-transparent"
                    >
                      <Computer className="h-4 w-4" />
                      Computer
                    </TabsTrigger>
                    <TabsTrigger 
                      value="files" 
                      className="flex items-center gap-2 px-3 py-1.5 rounded-md text-sm font-medium transition-all data-[state=active]:bg-gray-900 data-[state=active]:text-white data-[state=inactive]:text-gray-600 data-[state=inactive]:hover:text-gray-900 data-[state=inactive]:bg-transparent"
                    >
                      <FileText className="h-4 w-4" />
                      Files
                    </TabsTrigger>
                  </TabsList>
                </div>
              </CardHeader>
              
              <CardContent className="flex-1 p-0">
                <TabsContent value="computer" className="h-full m-0 p-6">
                  <div className="h-full flex flex-col">
                    <div className="mb-4">
                      <p className="text-sm text-gray-600">
                        {isActive ? 'Watch AI control your browser in real-time' : 'Start a session to see desktop'}
                      </p>
                      {isActive && isInitialized && (
                        <div className={`mt-2 text-xs p-2 rounded-lg ${
                          isTakenOver 
                            ? 'bg-red-50 text-red-700 border border-red-200' 
                            : 'bg-blue-50 text-blue-700 border border-blue-200'
                        }`}>
                          {isTakenOver 
                            ? '🔴 Desktop Control Active - AI can interact with the browser'
                            : '👁️ View Only Mode - Click "Take Over" to enable AI control'
                          }
                        </div>
                      )}
                    </div>
                    
                    <div className="flex-1 rounded-lg border overflow-hidden">
                      {streamUrl ? (
                        <iframe
                          src={streamUrl}
                          className="w-full h-full border-0"
                          allow="camera; microphone; clipboard-read; clipboard-write"
                          title="E2B Desktop VNC"
                        />
                      ) : (
                        <div className="h-full flex items-center justify-center bg-gray-50">
                          <div className="text-center">
                            <Computer className="h-20 w-20 text-gray-300 mx-auto mb-4" />
                            <h3 className="text-lg font-medium text-gray-900 mb-2">
                              No Active Session
                            </h3>
                            <p className="text-gray-600 mb-4">
                              Start a browser session to see the desktop here
                            </p>
                            <Button
                              onClick={createSession}
                              disabled={isCreatingSession || isActive}
                              variant="outline"
                            >
                              {isCreatingSession ? (
                                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                              ) : (
                                <Play className="h-4 w-4 mr-2" />
                              )}
                              Start Session
                            </Button>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </TabsContent>

                <TabsContent value="files" className="h-full m-0 p-6">
                  <div className="h-full flex flex-col">
                    <div className="flex items-center justify-between mb-4">
                      <p className="text-sm text-gray-600">
                        Files created by AI in the sandbox
                      </p>
                      <Button
                        onClick={fetchSandboxFiles}
                        disabled={isLoadingFiles || !isActive}
                        variant="outline"
                        size="sm"
                      >
                        {isLoadingFiles ? (
                          <Loader2 className="h-3 w-3 animate-spin" />
                        ) : (
                          'Refresh'
                        )}
                      </Button>
                    </div>
                    
                    <ScrollArea className="flex-1">
                      {!isActive ? (
                        <div className="text-center text-gray-500 mt-20">
                          <FileText className="h-16 w-16 mx-auto mb-4 text-gray-300" />
                          <h3 className="text-lg font-medium mb-2">Start a session</h3>
                          <p className="text-sm">
                            Files generated by AI will appear here
                          </p>
                        </div>
                      ) : sandboxFiles.length === 0 ? (
                        <div className="text-center text-gray-500 mt-20">
                          <FileText className="h-16 w-16 mx-auto mb-4 text-gray-300" />
                          <h3 className="text-lg font-medium mb-2">No files generated yet</h3>
                          <p className="text-sm">
                            Ask AI to create files and they'll appear here
                          </p>
                        </div>
                      ) : (
                        <div className="space-y-3">
                          {sandboxFiles.map((file, index) => (
                            <Card key={index} className="p-4">
                              <div className="flex items-center justify-between">
                                <div className="flex-1 min-w-0">
                                  <h4 className="text-sm font-medium text-gray-900 truncate">
                                    {file.name}
                                  </h4>
                                  <p className="text-xs text-gray-500">
                                    {file.size > 0 ? `${Math.round(file.size / 1024)}KB` : 'Unknown size'}
                                  </p>
                                </div>
                                <Button
                                  onClick={() => downloadFile(file)}
                                  variant="outline"
                                  size="sm"
                                  className="ml-3"
                                >
                                  <Download className="h-4 w-4" />
                                </Button>
                              </div>
                            </Card>
                          ))}
                        </div>
                      )}
                    </ScrollArea>
                  </div>
                </TabsContent>
              </CardContent>
            </Card>
          </Tabs>
        </ResizablePanel>
      </ResizablePanelGroup>
    </div>
  );
}