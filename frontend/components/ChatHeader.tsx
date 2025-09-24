'use client';

import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { Computer, Share, Download, FileText, Loader2, User, Settings, LogOut, Sparkles, ChevronRight, RefreshCw, Brain, Home, HelpCircle, ExternalLink, Hand, UserCheck, AlertCircle } from 'lucide-react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useTranslations, useLocale } from 'next-intl';
import { useRouter, usePathname } from 'next/navigation';
import { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import ProfileDialog from './ProfileDialog';

interface SandboxFile {
  name: string;
  path: string;
  size: number;
  type: string;
}

interface ChatHeaderProps {
  isActive: boolean;
  sandboxFiles: SandboxFile[];
  isFilesDialogOpen: boolean;
  setIsFilesDialogOpen: (open: boolean) => void;
  isLoadingFiles: boolean;
  fetchSandboxFiles: () => void;
  downloadFile: (file: SandboxFile) => void;
}

export default function ChatHeader({
  isActive,
  sandboxFiles,
  isFilesDialogOpen,
  setIsFilesDialogOpen,
  isLoadingFiles,
  fetchSandboxFiles,
  downloadFile
}: ChatHeaderProps) {
  const t = useTranslations();
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();
  
  // Dialog状态管理
  const [isProfileDialogOpen, setIsProfileDialogOpen] = useState(false);
  
  // Takeover状态管理
  const [takeoverState, setTakeoverState] = useState({
    isActive: false,
    isLoading: false
  });

  const handleLanguageChange = (newLocale: string) => {
    try {
      // 调试信息
      console.log('Current locale:', locale);
      console.log('Target locale:', newLocale);
      console.log('Pathname:', pathname);
      console.log('Window path:', window.location.pathname);
      
      // 方法1: 使用 Next.js router (推荐)
      const currentPath = pathname || window.location.pathname;
      const pathWithoutLocale = currentPath.replace(/^\/[a-z]{2}/, '');
      const newPath = `/${newLocale}${pathWithoutLocale || ''}`;
      
      console.log('Attempting router.push to:', newPath);
      router.push(newPath);
      
      // 方法2: 备用方案 - 直接刷新
      setTimeout(() => {
        if (window.location.pathname === currentPath) {
          console.log('Router push failed, using window.location');
          window.location.href = newPath;
        }
      }, 100);
      
    } catch (error) {
      console.error('Language change error:', error);
      // 最后的备用方案
      const fallbackPath = `/${newLocale}`;
      window.location.href = fallbackPath;
    }
  };

  // API基础URL配置
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8100';

  // Takeover相关功能
  const checkTakeoverStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/takeover/status`);
      const data = await response.json();
      if (data.success) {
        setTakeoverState(prev => ({
          ...prev,
          isActive: data.data.takeover_active || false
        }));
      }
    } catch (error) {
      console.error('检查takeover状态失败:', error);
    }
  };

  const toggleTakeover = async () => {
    if (!isActive) {
      toast.error(t('messages.createSessionFirst'));
      return;
    }

    setTakeoverState(prev => ({ ...prev, isLoading: true }));

    try {
      const endpoint = takeoverState.isActive ? `${API_BASE}/api/takeover/disable` : `${API_BASE}/api/takeover/enable`;
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();

      if (data.success) {
        setTakeoverState(prev => ({
          ...prev,
          isActive: !prev.isActive,
          isLoading: false
        }));
        
        // 显示成功消息
        const message = takeoverState.isActive 
          ? t('takeover.messages.disableSuccess')
          : t('takeover.messages.enableSuccess');
        
        toast.success(message);
      } else {
        throw new Error(data.message || data.error);
      }
    } catch (error) {
      console.error('Takeover操作失败:', error);
      const errorMessage = takeoverState.isActive 
        ? t('takeover.messages.disableError')
        : t('takeover.messages.enableError');
      toast.error(`${errorMessage}: ${error.message}`);
      
      setTakeoverState(prev => ({ ...prev, isLoading: false }));
    }
  };

  // 定期检查takeover状态
  useEffect(() => {
    if (isActive) {
      checkTakeoverStatus();
      const interval = setInterval(checkTakeoverStatus, 5000); // 每5秒检查一次
      return () => clearInterval(interval);
    }
  }, [isActive]);

  return (
    <div className="h-16 px-6 flex items-center justify-between bg-[#faf9f6]">
      {/* 左侧用户头像 */}
      <div className="flex items-center gap-3">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <div className="relative group cursor-pointer">
              <Avatar className="h-10 w-10 ring-2 ring-transparent hover:ring-gray-300 transition-all duration-300 relative overflow-hidden">
                <AvatarImage src="/default-avatar.png" alt="User" />
                <AvatarFallback className="bg-gradient-to-br from-gray-100 to-gray-200 text-gray-700 font-semibold text-sm">
                  U
                </AvatarFallback>
                {/* 擦亮效果 */}
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700 ease-in-out" />
              </Avatar>
            </div>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start" className="w-80 p-0 overflow-hidden">
            {/* 用户信息头部 */}
            <div className="p-4">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <Avatar className="h-12 w-12">
                    <AvatarImage src="/default-avatar.png" alt="Frank" />
                      <AvatarFallback className="bg-orange-100 text-orange-600 text-sm font-semibold">
                        F
                      </AvatarFallback>
                  </Avatar>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-gray-900 text-sm">Frank</h3>
                    <p className="text-xs text-gray-600 truncate">frank@autoagent.ai</p>
                  </div>
                </div>
                <Button variant="ghost" size="sm" className="p-1 h-6 w-6">
                  <RefreshCw className="h-3 w-3" />
                </Button>
              </div>

              {/* Free 计划卡片 */}
              <div className="bg-gray-50 rounded-lg p-3 mb-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-semibold text-gray-900 text-sm">Free</span>
                  <Button size="sm" className="bg-black text-white hover:bg-gray-800 text-xs h-6 px-2">
                    Upgrade
                  </Button>
                </div>
                
                {/* Credits */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Sparkles className="h-3 w-3 text-gray-600" />
                    <span className="text-xs text-gray-600">Credits</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <span className="font-semibold text-sm">1,300</span>
                    <ChevronRight className="h-3 w-3 text-gray-400" />
                  </div>
                </div>
              </div>
            </div>

            <DropdownMenuSeparator />

            {/* Knowledge 部分 */}
            <DropdownMenuItem className="flex items-center gap-3 px-4 py-2">
              <Brain className="h-4 w-4 text-gray-600" />
              <span className="text-sm">Knowledge</span>
            </DropdownMenuItem>

            <DropdownMenuSeparator />

            {/* 菜单项 */}
            <DropdownMenuItem 
              className="flex items-center gap-3 px-4 py-2 cursor-pointer"
              onSelect={() => setIsProfileDialogOpen(true)}
            >
              <User className="h-4 w-4 text-gray-600" />
              <span className="text-sm">Account</span>
            </DropdownMenuItem>
            
            <DropdownMenuItem className="flex items-center gap-3 px-4 py-2">
              <Settings className="h-4 w-4 text-gray-600" />
              <span className="text-sm">Settings</span>
            </DropdownMenuItem>

            <DropdownMenuSeparator />

            {/* 外部链接 */}
            <DropdownMenuItem className="flex items-center justify-between px-4 py-2">
              <div className="flex items-center gap-3">
                <Home className="h-4 w-4 text-gray-600" />
                <span className="text-sm">Homepage</span>
              </div>
              <ExternalLink className="h-3 w-3 text-gray-400" />
            </DropdownMenuItem>
            
            <DropdownMenuItem className="flex items-center justify-between px-4 py-2">
              <div className="flex items-center gap-3">
                <HelpCircle className="h-4 w-4 text-gray-600" />
                <span className="text-sm">Get help</span>
              </div>
              <ExternalLink className="h-3 w-3 text-gray-400" />
            </DropdownMenuItem>

            <DropdownMenuSeparator />

            {/* 退出登录 */}
            <DropdownMenuItem className="flex items-center gap-3 px-4 py-2 text-red-600 hover:bg-red-50 focus:bg-red-50">
              <LogOut className="h-4 w-4" />
              <span className="text-sm">Sign out</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
      
      {/* 中部 Session Title */}
      <div className="flex-1 text-center">
        <h2 className="text-sm font-medium text-gray-700">
          {isActive ? t('header.activeSession') : t('header.noActiveSession')}
        </h2>
      </div>
      
      {/* 右侧按钮 */}
      <div className="flex items-center gap-2">
        {/* Files Dialog */}
        <Dialog open={isFilesDialogOpen} onOpenChange={setIsFilesDialogOpen}>
          <DialogTrigger asChild>
            <Button variant="outline" size="sm" className="cursor-pointer">
              <svg 
                xmlns="http://www.w3.org/2000/svg" 
                width="16" 
                height="16" 
                viewBox="0 0 24 24" 
                fill="none" 
                stroke="currentColor" 
                strokeWidth="2" 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                className="lucide lucide-file-search"
              >
                <path d="M14 2v4a2 2 0 0 0 2 2h4"></path>
                <path d="M4.268 21a2 2 0 0 0 1.727 1H18a2 2 0 0 0 2-2V7l-5-5H6a2 2 0 0 0-2 2v3"></path>
                <path d="m9 18-1.5-1.5"></path>
                <circle cx="5" cy="14" r="3"></circle>
              </svg>
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[80vh]">
            <DialogHeader>
              <DialogTitle>{t('header.sandboxFiles')}</DialogTitle>
              <DialogDescription>
                {t('header.filesDescription')}
              </DialogDescription>
            </DialogHeader>
            
            <div className="flex items-center justify-between mb-4">
              <p className="text-sm text-gray-600">
                {sandboxFiles.length} {t('common.files')} {t('common.found')}
              </p>
              <Button
                onClick={fetchSandboxFiles}
                disabled={isLoadingFiles || !isActive}
                variant="outline"
                size="sm"
                className="cursor-pointer"
              >
                {isLoadingFiles ? (
                  <Loader2 className="h-3 w-3 animate-spin" />
                ) : (
                  t('common.refresh')
                )}
              </Button>
            </div>
            
            <ScrollArea className="max-h-96">
              {!isActive ? (
                <div className="text-center text-gray-500 py-8">
                  <FileText className="h-16 w-16 mx-auto mb-4 text-gray-300" />
                  <h3 className="text-lg font-medium mb-2">{t('header.startSession')}</h3>
                  <p className="text-sm">
                    {t('header.filesGeneratedHere')}
                  </p>
                </div>
              ) : sandboxFiles.length === 0 ? (
                <div className="text-center text-gray-500 py-8">
                  <FileText className="h-16 w-16 mx-auto mb-4 text-gray-300" />
                  <h3 className="text-lg font-medium mb-2">{t('header.noFilesGenerated')}</h3>
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
                          className="ml-3 cursor-pointer"
                        >
                          <Download className="h-4 w-4" />
                        </Button>
                      </div>
                    </Card>
                  ))}
                </div>
              )}
            </ScrollArea>
          </DialogContent>
        </Dialog>
        
        {/* Takeover Button */}
        <Button
          onClick={toggleTakeover}
          disabled={!isActive || takeoverState.isLoading}
          variant={takeoverState.isActive ? "default" : "outline"}
          className={`cursor-pointer ${
            takeoverState.isActive 
              ? 'bg-orange-500 hover:bg-orange-600 text-white' 
              : ''
          }`}
          size="sm"
          title={
            takeoverState.isActive 
              ? t('takeover.tooltip.enabled')
              : t('takeover.tooltip.disabled')
          }
        >
          {takeoverState.isLoading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : takeoverState.isActive ? (
            <UserCheck className="h-4 w-4" />
          ) : (
            <Hand className="h-4 w-4" />
          )}
          <span className="ml-1 text-xs">
            {takeoverState.isLoading ? (
              takeoverState.isActive ? t('takeover.disabling') : t('takeover.enabling')
            ) : (
              takeoverState.isActive ? t('takeover.disable') : t('takeover.enable')
            )}
          </span>
        </Button>

        {/* Share Button */}
        <Button variant="outline" className='cursor-pointer' size="sm">
          <Share className="h-4 w-4" />
        </Button>
        
      </div>

      {/* Profile Dialog */}
      <ProfileDialog 
        isOpen={isProfileDialogOpen} 
        onClose={() => setIsProfileDialogOpen(false)} 
      />
    </div>
  );
}
