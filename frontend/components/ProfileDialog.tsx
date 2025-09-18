'use client';

import React, { useState, useTransition } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useTranslations, useLocale } from 'next-intl';
import { useRouter, usePathname } from 'next/navigation';
import { 
  User, 
  Settings, 
  CreditCard, 
  Calendar, 
  Mail, 
  Database,
  Globe,
  Plug,
  HelpCircle,
  X
} from 'lucide-react';

interface ProfileDialogProps {
  isOpen: boolean;
  onClose: () => void;
}

const menuItems = [
  { id: 'account', label: 'Account', icon: User },
  { id: 'settings', label: 'Settings', icon: Settings },
  { id: 'usage', label: 'Usage', icon: CreditCard },
  { id: 'scheduled', label: 'Scheduled tasks', icon: Calendar },
  { id: 'mail', label: 'Mail Manus', icon: Mail },
  { id: 'data', label: 'Data controls', icon: Database },
  { id: 'browser', label: 'Cloud browser', icon: Globe },
  { id: 'connectors', label: 'Connectors', icon: Plug },
  { id: 'integrations', label: 'Integrations', icon: Settings },
];

export default function ProfileDialog({ isOpen, onClose }: ProfileDialogProps) {
  const [activeSection, setActiveSection] = useState('account');
  const [isPending, startTransition] = useTransition();
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();

  // 从路径中提取实际语言，作为 fallback（参考 LanguageSwitcher 的实现）
  const pathLocale = pathname.split('/')[1];
  const actualLocale = ['en', 'zh'].includes(pathLocale) ? pathLocale : locale;

  const handleLanguageChange = (newLocale: string) => {
    if (newLocale === actualLocale) return; // 相同语言，不处理
    
    startTransition(() => {
      // 使用正则表达式移除当前语言前缀（参考 LanguageSwitcher 的实现）
      const pathWithoutLocale = pathname.replace(/^\/[a-z]{2}/, '') || '/';
      // 添加新语言前缀
      const newPath = `/${newLocale}${pathWithoutLocale}`;
      console.log('Language change:', { from: actualLocale, to: newLocale, pathname, newPath });
      router.push(newPath);
    });
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="!h-[85vh] !w-[95vw] !max-w-[1200px] !max-h-[85vh] !min-w-[300px] sm:!min-w-[800px] p-0 overflow-hidden">
        <DialogTitle className="sr-only">User Profile Settings</DialogTitle>
        <div className="flex h-full">
          {/* 左侧导航栏 */}
          <div className="w-64 lg:w-80 bg-gray-50 border-r flex flex-col flex-shrink-0">
            {/* 头部 */}
            <div className="p-6 border-b bg-white">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-black rounded-full flex items-center justify-center">
                    <User className="h-4 w-4 text-white" />
                  </div>
                  <span className="font-semibold text-gray-900">Atlas</span>
                </div>
                <Button variant="ghost" size="sm" onClick={onClose}>
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </div>

            {/* 导航菜单 */}
            <div className="flex-1 p-4">
              <nav className="space-y-1">
                {menuItems.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => setActiveSection(item.id)}
                    className={`w-full flex items-center gap-3 px-3 py-2.5 text-left rounded-lg transition-colors text-sm ${
                      activeSection === item.id 
                        ? 'bg-blue-50 text-blue-700 border border-blue-200' 
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <item.icon className="h-4 w-4" />
                    <span>{item.label}</span>
                  </button>
                ))}
              </nav>
            </div>

            {/* 底部帮助 */}
            <div className="p-4 border-t">
              <button className="w-full flex items-center gap-3 px-3 py-2.5 text-left rounded-lg transition-colors text-sm text-gray-700 hover:bg-gray-100">
                <HelpCircle className="h-4 w-4" />
                <span>Get help</span>
              </button>
            </div>
          </div>

          {/* 右侧内容区域 */}
          <div className="flex-1 bg-white overflow-y-auto">
            {activeSection === 'account' && (
              <div className="p-8">
                <div className="mb-8">
                  <h1 className="text-2xl font-semibold text-gray-900 mb-2">Account</h1>
                </div>

                {/* 用户信息卡片 */}
                <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-4">
                      <Avatar className="h-16 w-16">
                        <AvatarImage src="/default-avatar.png" alt="User" />
                        <AvatarFallback className="bg-orange-100 text-orange-600 text-lg font-semibold">
                          F
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <h2 className="text-xl font-semibold text-gray-900">Frank</h2>
                        <p className="text-gray-600">frank@autoagent.ai</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button variant="ghost" size="sm">
                        <User className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="sm">
                        <Mail className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>

                {/* 计划信息 */}
                <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">Free</h3>
                    </div>
                    <Badge variant="outline" className="bg-black text-white">
                      Upgrade
                    </Badge>
                  </div>

                  {/* Credits 信息 */}
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <CreditCard className="h-4 w-4 text-gray-500" />
                        <span className="text-sm text-gray-700">Credits</span>
                      </div>
                      <div className="text-right">
                        <div className="font-semibold">1,000</div>
                        <div className="text-xs text-gray-500">1,000</div>
                      </div>
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Calendar className="h-4 w-4 text-gray-500" />
                        <span className="text-sm text-gray-700">Daily refresh credits</span>
                      </div>
                      <div className="text-right">
                        <div className="font-semibold">300</div>
                      </div>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">Refresh to 300 at 00:00 every day</p>
                  </div>
                </div>
              </div>
            )}

            {activeSection === 'settings' && (
              <div className="p-8">
                <div className="mb-8">
                  <h1 className="text-2xl font-semibold text-gray-900 mb-2">Settings</h1>
                </div>
                
                <div className="space-y-6">
                  <div className="bg-white border border-gray-200 rounded-lg p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Preferences</h3>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <label className="text-sm font-medium text-gray-700">Theme</label>
                          <p className="text-xs text-gray-500">Choose your preferred theme</p>
                        </div>
                        <Select defaultValue="light">
                          <SelectTrigger className="w-[120px] h-8 text-sm">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="light">Light</SelectItem>
                            <SelectItem value="dark">Dark</SelectItem>
                            <SelectItem value="system">System</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="flex items-center justify-between">
                        <div>
                          <label className="text-sm font-medium text-gray-700">Language</label>
                          <p className="text-xs text-gray-500">Select interface language</p>
                        </div>
                        <Select 
                          value={actualLocale}
                          onValueChange={handleLanguageChange}
                          disabled={isPending}
                        >
                          <SelectTrigger className="w-[120px] h-8 text-sm">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="en">English</SelectItem>
                            <SelectItem value="zh">简体中文</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeSection === 'usage' && (
              <div className="p-8">
                <div className="mb-8">
                  <h1 className="text-2xl font-semibold text-gray-900 mb-2">Usage</h1>
                </div>
                <div className="bg-white border border-gray-200 rounded-lg p-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Current Usage</h3>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">API Calls</span>
                      <span className="font-semibold">0 / 1,000</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div className="bg-blue-600 h-2 rounded-full" style={{ width: '0%' }}></div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* 其他菜单项的默认内容 */}
            {!['account', 'settings', 'usage'].includes(activeSection) && (
              <div className="p-8">
                <div className="mb-8">
                  <h1 className="text-2xl font-semibold text-gray-900 mb-2 capitalize">
                    {menuItems.find(item => item.id === activeSection)?.label}
                  </h1>
                </div>
                <div className="bg-white border border-gray-200 rounded-lg p-6">
                  <p className="text-gray-600">
                    This section is under development. More features coming soon.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}