'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  Play, 
  Loader2, 
  Computer,
  ChevronDown,
  ChevronUp,
  Check,
  Globe,
  SkipBack,
  SkipForward,
  Power
} from 'lucide-react';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { useTranslations } from 'next-intl';

interface ArtifactsProps {
  streamUrl: string;
  isActive: boolean;
  isInitialized: boolean;
  isCreatingSession: boolean;
  currentStep: number;
  totalSteps: number;
  currentCommand: string;
  currentFilePath: string;
  currentBrowserUrl: string;
  createSession: () => void;
  resumeSession: () => void;
  terminateSession: () => void;
  handlePreviousStep: () => void;
  handleNextStep: () => void;
}

export default function Artifacts({
  streamUrl,
  isActive,
  isInitialized,
  isCreatingSession,
  currentStep,
  totalSteps,
  currentCommand,
  currentFilePath,
  currentBrowserUrl,
  createSession,
  resumeSession,
  terminateSession,
  handlePreviousStep,
  handleNextStep
}: ArtifactsProps) {
  const t = useTranslations();
  const [isTaskProgressOpen, setIsTaskProgressOpen] = useState(false);
  
  // Mock task list for demo
  const taskList = [
    "Clarify user requirements for the Starlink promotion",
    "Research information about Starlink's services, features, and benefits", 
    "Identify the target audience for the promotional content",
    "Create promotional content for Starlink",
    "Include highlights of Elon Musk's leadership in the content",
    "Review and finalize the promotional materials",
    "Deliver the promotional materials to the user",
    "Create a website for the Starlink promotional content",
    "Deploy the website permanently",
    "Notify the user of the website deployment"
  ];

  const currentTool = isActive ? "Browser" : "Waiting";
  const currentUrl = currentBrowserUrl || "";
  
  // 根据当前状态动态显示工具
  const getToolStatus = () => {
    if (!isActive) return t('common.waiting');
    if (streamUrl && isInitialized) return t('artifacts.browser');
    if (isInitialized) return t('common.ready');
    return t('common.loading');
  };

  return (
    <div className="w-full h-full bg-transparent">
      <Card className="h-full flex flex-col relative">
        {/* Header */}
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg">{t('artifacts.computerTitle')}</CardTitle>
            
            {/* 会话控制按钮 */}
            <div className="flex gap-2">
              {/* 启动会话按钮 */}
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    onClick={isActive ? resumeSession : createSession}
                    disabled={isCreatingSession}
                    size="sm"
                    className="bg-black text-white hover:bg-gray-800 border-black cursor-pointer"
                  >
                    {isCreatingSession ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Play className="h-4 w-4" />
                    )}
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>{t('header.startSessionTooltip')}</p>
                </TooltipContent>
              </Tooltip>

              {/* 终止会话按钮 */}
              {isActive && (
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button 
                      size="sm" 
                      onClick={terminateSession}
                      className="bg-black text-red-400 hover:bg-gray-800 hover:text-red-300 border-black cursor-pointer"
                    >
                      <Power className="h-4 w-4" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>{t('header.terminateTooltip')}</p>
                  </TooltipContent>
                </Tooltip>
              )}
            </div>
          </div>
        </CardHeader>
        
        {/* 工具状态显示 */}
        <div className="px-6 pb-3">
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <Computer className="h-4 w-4" />
            <span>
              {getToolStatus() === t('common.waiting') ? (
                <strong>{getToolStatus()}</strong>
              ) : (
                <>{t('artifacts.atlasUsing')} <strong>{getToolStatus()}</strong></>
              )}
            </span>
          </div>
          {currentUrl && (
            <div className="flex items-center gap-2 text-xs text-gray-500 mt-1 bg-[#f7f7f7] rounded-2xl p-2">
              <Globe className="h-3 w-3" />
              <span>{t('artifacts.browsing')} {currentUrl}</span>
            </div>
          )}
          {(currentCommand || currentFilePath) && (
            <div className="mt-2 p-2 bg-blue-50 rounded text-xs text-blue-700">
              {currentCommand && <div><strong>{t('artifacts.command')}:</strong> {currentCommand}</div>}
              {currentFilePath && <div><strong>{t('artifacts.file')}:</strong> {currentFilePath}</div>}
            </div>
          )}
        </div>
        
        {/* 预览区域 */}
        <CardContent className="flex-1 px-6 pb-8 flex flex-col">
          {/* 预览区域上方Header - 文件路径 */}
          <div className="bg-gray-100 border rounded-t-lg px-4 py-2 text-sm text-gray-600">
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1">
                <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              </div>
              <span className="flex-1 text-center font-mono text-xs">
                {currentBrowserUrl || currentFilePath || (streamUrl ? t('artifacts.loading') : t('artifacts.noPageLoaded'))}
              </span>
            </div>
          </div>

          {/* 预览区域主体 */}
          <div className="h-[calc(100%-120px)] border-l border-r overflow-hidden">
            {streamUrl ? (
              <iframe
                src={streamUrl}
                className="w-full h-full border-0"
                allow="camera; microphone; clipboard-read; clipboard-write"
                title="E2B Desktop VNC"
              />
            ) : (
              <div className="h-full flex items-center justify-center bg-[#f8f8f7]">
                <div className="text-center text-gray-500">
                  <Computer className="h-16 w-16 mx-auto mb-4 text-gray-300" />
                  <h3 className="text-lg font-medium mb-2">
                    {isActive ? t('artifacts.browserReady') : t('artifacts.noSessionActive')}
                  </h3>
                  <p className="text-sm">
                    {isActive ? t('artifacts.browserReadyToUse') : t('artifacts.startSessionDesktop')}
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* 预览区域下方Header - 进度条 */}
          <div className="bg-white border rounded-b-lg px-4 py-1">
            <div className="flex items-center gap-4">
              {/* 播放控制按钮 */}
              <div className="flex items-center gap-2">
                <Button
                  onClick={handlePreviousStep}
                  disabled={currentStep <= 1}
                  variant="ghost"
                  size="sm"
                  className="h-8 w-8 p-0 cursor-pointer"
                >
                  <SkipBack className="h-4 w-4" />
                </Button>
                <Button
                  onClick={handleNextStep}
                  disabled={currentStep >= totalSteps}
                  variant="ghost"
                  size="sm" 
                  className="h-8 w-8 p-0 cursor-pointer"
                >
                  <SkipForward className="h-4 w-4" />
                </Button>
              </div>

              {/* 进度条 */}
              <div className="flex-1">
                <div className="w-full bg-gray-300 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${(currentStep / totalSteps) * 100}%` }}
                  />
                </div>
              </div>

              {/* 步骤信息 */}
              <div className="text-xs text-gray-600 whitespace-nowrap">
                {currentStep} / {totalSteps}
              </div>
            </div>
          </div>
        </CardContent>
        
        {/* 可折叠的任务进度面板 - 作为overlay */}
        <div className="absolute bottom-0 left-0 right-0 z-10">
          <div className="px-6 pb-6">
            <Collapsible open={isTaskProgressOpen} onOpenChange={setIsTaskProgressOpen}>
              <CollapsibleTrigger className="w-full">
                <div className="bg-gray-50 rounded-lg p-4 cursor-pointer hover:bg-gray-100 transition-colors shadow-lg border">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="text-sm font-medium text-gray-700">
                        {t('artifacts.taskProgress')}
                      </span>
                      <span className="text-sm text-gray-500">
                        {Math.min(currentStep, taskList.length)} / {taskList.length}
                      </span>
                    </div>
                    {isTaskProgressOpen ? (
                      <ChevronDown className="h-4 w-4 text-gray-500" />
                    ) : (
                      <ChevronUp className="h-4 w-4 text-gray-500" />
                    )}
                  </div>
                </div>
              </CollapsibleTrigger>
              
              <CollapsibleContent className="overflow-hidden">
                <div className="mt-3 bg-white rounded-lg border shadow-lg p-4 max-h-[300px] overflow-y-auto">
                  <div className="space-y-3">
                    {taskList.map((task, index) => {
                      const isCompleted = index < Math.min(currentStep, taskList.length);
                      return (
                        <div key={index} className="flex items-start gap-3">
                          <div className="mt-0.5 flex-shrink-0">
                            {isCompleted ? (
                              <Check className="h-4 w-4 text-green-600" />
                            ) : (
                              <div className="h-4 w-4 border-2 border-gray-300 rounded-sm" />
                            )}
                          </div>
                          <span className={`text-sm flex-1 min-w-0 ${
                            isCompleted ? 'text-gray-700' : 'text-gray-400'
                          }`}>
                            {task}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </CollapsibleContent>
            </Collapsible>
          </div>
        </div>
      </Card>
    </div>
  );
}
