import os
import time
import glob
import tempfile
from typing import Optional, Dict, Any

from Desktop.manager import E2BDesktopManager
from Engine.browser_runner import BrowseUseExecutor


class E2BUnifiedAgent:
    """
    统一的E2B Agent，整合了桌面管理和浏览器自动化功能，
    兼容原有的API接口，供FastAPI后端使用。
    """
    
    def __init__(self, resolution=(1440, 900), dpi=96):
        self.desktop_manager = E2BDesktopManager(resolution=resolution, dpi=dpi)
        self.browser_runner = None
        self.stream_url = None
        self.external_cdp_base = None
        self.backup_chrome_base = None
        self._initialized = False
        self._temp_files = []  # 跟踪browser-use agent生成的临时文件
        
        # 人工接管相关状态
        self.takeover_active = False  # 是否处于人工接管状态
        self.intervention_needed = False  # 是否需要人工干预
        self.intervention_reason = ""  # 需要干预的原因
        self.automation_paused = False  # 自动化是否暂停
    
    def create_desktop_session(self):
        """创建E2B desktop会话并返回stream URL (兼容原API)"""
        try:
            # 启动桌面和直播
            self.stream_url = self.desktop_manager.start_desktop()
            
            # 确保浏览器可用
            self.desktop_manager.ensure_chrome_or_fail()
            
            # 启动Chrome with CDP
            self.desktop_manager.launch_chrome_with_cdp()
            
            # 启动代理
            self.desktop_manager.launch_cdp_proxy()
            
            # 验证服务状态
            self.desktop_manager.verify_services()
            
            # 获取外网地址 - 重试机制
            max_retries = 3
            for retry in range(max_retries):
                try:
                    print(f"\n🌐 尝试获取外网端点 (第 {retry + 1}/{max_retries} 次)...")
                    
                    # 等待E2B端口映射完成
                    if retry > 0:
                        print(f"等待 {retry * 5} 秒让E2B端口映射稳定...")
                        time.sleep(retry * 5)
                    
                    self.external_cdp_base = self.desktop_manager.get_external_cdp_base()
                    self.backup_chrome_base = self.desktop_manager.get_direct_chrome_base()
                    self._initialized = True
                    
                    print("✅ 外网端点获取成功!")
                    break
                    
                except Exception as e:
                    print(f"❌ 第 {retry + 1} 次获取外网端点失败: {e}")
                    if retry == max_retries - 1:
                        # 最后一次尝试失败
                        print("⚠️  所有端口获取尝试都失败，但会话仍然创建")
                        print("💡 建议：请手动在E2B控制台中将端口9222和9223设置为Public")
                        # 设置为未初始化，但不阻止会话创建
                        self._initialized = False
                
            return {
                "success": True,
                "stream_url": self.stream_url,
                "message": "Desktop session created successfully" + 
                          (" with Browser-Use integration" if self._initialized else " (端口配置需要手动检查)")
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create desktop session: {str(e)}"
            }
    
    def get_stream_url(self):
        """获取当前的stream URL (兼容原API)"""
        return self.stream_url
    
    
    def get_desktop_status(self):
        """获取桌面状态"""
        return {
            "success": True,
            "active": bool(self.stream_url),
            "initialized": self._initialized,
            "stream_url": self.stream_url
        }
    
    async def execute_task(self, task: str, context=None):
        """
        执行Browser Use任务 (兼容原API)
        
        Args:
            task: 要执行的任务描述
            context: 额外的上下文信息
            
        Returns:
            Dict containing success status and results
        """
        try:
            if not self.stream_url:
                return {
                    "success": False,
                    "error": "No active session",
                    "message": "Please create a desktop session first"
                }
            
            if not self._initialized:
                return {
                    "success": False,
                    "error": "Browser Use not initialized", 
                    "message": "端口配置有问题，请检查E2B控制台中端口9222和9223是否设置为Public，或者重新创建会话"
                }
            
            # 确保有可用的CDP端点
            if not self.external_cdp_base and not self.backup_chrome_base:
                return {
                    "success": False,
                    "error": "No available CDP endpoints",
                    "message": "无法获取CDP端点。请到E2B控制台确保端口9222和9223已设置为Public"
                }
            
            # 创建Browser Use runner
            print("📝 使用标准Browser Use执行器")
            self.browser_runner = BrowseUseExecutor(
                task=task,
                external_cdp_base=self.external_cdp_base,
                backup_chrome_base=self.backup_chrome_base
            )
            
            # 执行任务 (在异步环境中运行同步的browser-use)
            import asyncio
            from concurrent.futures import ThreadPoolExecutor
            
            def run_browser_task():
                """在单独线程中运行browser-use任务，支持人工干预检测"""
                try:
                    # 检查是否需要暂停自动化
                    if self.automation_paused:
                        return {
                            "success": False,
                            "paused": True,
                            "message": "自动化已暂停，等待人工操作完成",
                            "intervention_needed": self.intervention_needed,
                            "intervention_reason": self.intervention_reason
                        }
                    
                    # 使用标准执行器
                    print(f"🚀 使用标准Browser Use执行器运行任务: {task[:50]}...")
                    
                    # 检测任务是否包含需要人工干预的关键词
                    intervention_keywords = [
                        "password", "密码", "验证码", "captcha", "verification", 
                        "two-factor", "2fa", "otp", "sms code", "email verification",
                        "手机验证", "邮箱验证", "短信验证", "身份验证", "两步验证", "双重验证"
                    ]
                    
                    task_lower = task.lower()
                    needs_intervention = any(keyword in task_lower for keyword in intervention_keywords)
                    
                    if needs_intervention and not self.takeover_active:
                        # 检测到需要人工干预的任务
                        self.intervention_needed = True
                        self.intervention_reason = "检测到需要输入密码或验证码，建议切换到人工操作模式"
                        self.automation_paused = True
                        
                        return {
                            "success": False,
                            "intervention_needed": True,
                            "intervention_reason": self.intervention_reason,
                            "message": "🔐 检测到需要人工干预的操作（密码/验证码），请点击 Take Over 按钮进行手动操作",
                            "suggested_action": "takeover",
                            "task": task
                        }
                    
                    # 正常执行任务
                    result = self.browser_runner.run()
                    
                    # 检查结果中是否包含需要人工干预的提示
                    result_str = str(result).lower()
                    intervention_phrases = [
                        "enter password", "input password", "verification code",
                        "captcha", "human verification", "please verify",
                        "输入密码", "请输入密码", "验证码", "人机验证"
                    ]
                    
                    if any(phrase in result_str for phrase in intervention_phrases):
                        self.intervention_needed = True
                        self.intervention_reason = "执行过程中遇到需要人工验证的页面"
                        
                        return {
                            "success": True,
                            "result": str(result)[:800] + "..." if len(str(result)) > 800 else str(result),
                            "intervention_needed": True,
                            "intervention_reason": self.intervention_reason,
                            "message": "🔐 任务执行中遇到验证页面，建议切换到人工操作模式",
                            "suggested_action": "takeover",
                            "task": task
                        }
                    
                    return {
                        "success": True,
                        "message": "Task completed successfully",
                        "result": str(result)[:800] + "..." if len(str(result)) > 800 else str(result),
                        "task": task,
                        "intervention_needed": False
                    }
                        
                except Exception as e:
                    error_str = str(e)
                    print(f"❌ 任务执行失败: {error_str[:200]}...")
                    
                    # 检查错误是否与验证相关
                    verification_errors = [
                        "login failed", "authentication", "verification", 
                        "登录失败", "身份验证", "验证失败"
                    ]
                    
                    if any(err in error_str.lower() for err in verification_errors):
                        self.intervention_needed = True
                        self.intervention_reason = "遇到身份验证相关错误，可能需要人工处理"
                        
                        return {
                            "success": False,
                            "error": str(e)[:200],
                            "intervention_needed": True,
                            "intervention_reason": self.intervention_reason,
                            "message": "🔐 执行失败：可能需要人工处理身份验证问题",
                            "suggested_action": "takeover"
                        }
                    
                    if "timeout" in error_str.lower() or "watchdog" in error_str.lower():
                        return {
                            "success": False,
                            "error": "Input timeout",
                            "message": "文本输入超时。E2B WebSocket连接可能不稳定，请稍后重试。"
                        }
                    elif "websocket" in error_str.lower() or "connection" in error_str.lower():
                        return {
                            "success": False,
                            "error": "Connection timeout",
                            "message": "连接超时。E2B WebSocket连接不稳定，请稍后重试或检查网络连接。"
                        }
                    else:
                        return {
                            "success": False,
                            "error": str(e)[:200],
                            "message": f"任务执行失败: {str(e)[:200]}..."
                        }
            
            # 在线程池中执行，避免阻塞异步事件循环
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                result = await loop.run_in_executor(executor, run_browser_task)
            
            # 如果任务执行成功，扫描新生成的临时文件
            if result.get("success"):
                self._scan_browser_use_files()
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Internal error executing task: {task}"
            }
    
    def _scan_browser_use_files(self):
        """扫描browser-use agent生成的临时文件"""
        try:
            # 扫描系统临时目录中的browser_use_agent文件
            temp_dir = tempfile.gettempdir()
            pattern = os.path.join(temp_dir, "browser_use_agent_*")
            agent_dirs = glob.glob(pattern)
            
            for agent_dir in agent_dirs:
                # 扫描browseruse_agent_data目录
                data_dir = os.path.join(agent_dir, "browseruse_agent_data")
                if os.path.exists(data_dir):
                    # 扫描所有文件
                    for root, dirs, files in os.walk(data_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            # 检查文件是否已经在列表中
                            if file_path not in [f['path'] for f in self._temp_files]:
                                try:
                                    file_stat = os.stat(file_path)
                                    self._temp_files.append({
                                        "name": file,
                                        "path": file_path,
                                        "size": file_stat.st_size,
                                        "type": "agent_output",
                                        "is_temp": True,
                                        "created_time": file_stat.st_ctime
                                    })
                                    print(f"📄 发现新的输出文件: {file}")
                                except OSError:
                                    continue
        except Exception as e:
            print(f"扫描临时文件时出错: {e}")
    
    def add_temp_file_manually(self, file_path):
        """手动添加临时文件到列表中"""
        try:
            if os.path.exists(file_path) and file_path not in [f['path'] for f in self._temp_files]:
                file_stat = os.stat(file_path)
                filename = os.path.basename(file_path)
                self._temp_files.append({
                    "name": filename,
                    "path": file_path,
                    "size": file_stat.st_size,
                    "type": "agent_output",
                    "is_temp": True,
                    "created_time": file_stat.st_ctime
                })
                print(f"📄 手动添加文件: {filename}")
                return True
        except Exception as e:
            print(f"添加临时文件失败: {e}")
        return False
    
    def launch_firefox(self):
        """在desktop中启动Firefox (兼容原API)"""
        return self.launch_application("firefox", "https://www.mozilla.org")
    
    def launch_application(self, app_name, url=None):
        """在desktop中启动指定应用 (兼容原API)"""
        try:
            if not self.desktop_manager.desk:
                return {
                    "success": False,
                    "error": "No active desktop session",
                    "message": "Please create a desktop session first"
                }
            
            # 构建命令
            if url and app_name in ['firefox', 'google-chrome']:
                command = f'{app_name} {url} &'
            else:
                command = f'{app_name} &'
            
            # 执行命令
            result = self.desktop_manager.desk.commands.run(command, background=True)
            
            return {
                "success": True,
                "message": f"{app_name} launched successfully",
                "result": result.stdout if hasattr(result, 'stdout') else str(result)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to launch {app_name}"
            }
    
    def list_sandbox_files(self, directory="/home/user"):
        """列出沙盒中的文件，优雅地处理没有活动会话的情况"""
        def prepare_temp_files():
            """准备临时文件列表的辅助函数"""
            temp_files = []
            for temp_file in self._temp_files:
                temp_files.append({
                    "name": temp_file["name"],
                    "path": temp_file["path"],
                    "size": temp_file["size"],
                    "type": temp_file["type"],
                    "is_temp": True
                })
            return temp_files
        
        temp_files = prepare_temp_files()
        
        try:
            # 如果没有沙盒会话，只返回临时文件
            if not self.desktop_manager or not self.desktop_manager.desk:
                print(f"📁 没有活动沙盒会话，返回 {len(temp_files)} 个临时文件")
                return {
                    "success": True,
                    "warning": "No active sandbox session, showing agent output files only" if temp_files else "No active session and no files available",
                    "files": temp_files,
                    "directory": directory,
                    "temp_files_count": len(temp_files),
                    "session_active": False
                }
            
            sandbox_files = []
            session_active = True
            
            # 尝试获取沙盒文件
            try:
                # 方法1：使用E2B的文件API
                try:
                    file_items = self.desktop_manager.desk.files.list(directory)
                    for item in file_items:
                        if hasattr(item, 'is_dir') and not item.is_dir and not item.name.startswith('.'):
                            sandbox_files.append({
                                "name": item.name,
                                "path": f"{directory.rstrip('/')}/{item.name}",
                                "size": getattr(item, 'size', 0),
                                "type": "file"
                            })
                    print(f"📂 通过E2B API获取到 {len(sandbox_files)} 个沙盒文件")
                    
                except Exception as files_api_error:
                    print(f"E2B文件API失败: {files_api_error}")
                    
                    # 方法2：使用find命令
                    try:
                        result = self.desktop_manager.desk.commands.run(f"find {directory} -maxdepth 1 -type f ! -name '.*'")
                        if result.exit_code == 0:
                            for line in result.stdout.strip().split('\n'):
                                if line.strip():
                                    filename = line.split('/')[-1]
                                    if filename:
                                        sandbox_files.append({
                                            "name": filename,
                                            "path": line.strip(),
                                            "size": 0,  # find命令不返回文件大小
                                            "type": "file"
                                        })
                        print(f"📂 通过find命令获取到 {len(sandbox_files)} 个沙盒文件")
                        
                    except Exception as find_error:
                        print(f"find命令失败: {find_error}")
                        
                        # 方法3：使用ls命令
                        try:
                            result = self.desktop_manager.desk.commands.run(f"ls -la {directory} 2>/dev/null")
                            if result.exit_code == 0:
                                lines = result.stdout.strip().split('\n')[1:]  # 跳过总计行
                                for line in lines:
                                    if line.strip() and not line.startswith('d'):  # 不是目录
                                        parts = line.split()
                                        if len(parts) >= 9:
                                            filename = ' '.join(parts[8:])
                                            if not filename.startswith('.') and filename not in ['.', '..']:
                                                sandbox_files.append({
                                                    "name": filename,
                                                    "path": f"{directory.rstrip('/')}/{filename}",
                                                    "size": int(parts[4]) if parts[4].isdigit() else 0,
                                                    "type": "file"
                                                })
                            print(f"📂 通过ls命令获取到 {len(sandbox_files)} 个沙盒文件")
                            
                        except Exception as ls_error:
                            print(f"ls命令也失败: {ls_error}")
                            session_active = False
                            
            except Exception as sandbox_error:
                print(f"沙盒文件访问完全失败: {sandbox_error}")
                session_active = False
            
            # 合并沙盒文件和临时文件
            all_files = sandbox_files + temp_files
            
            return {
                "success": True,
                "files": all_files,
                "directory": directory,
                "temp_files_count": len(temp_files),
                "sandbox_files_count": len(sandbox_files),
                "session_active": session_active,
                "warning": None if session_active else "Sandbox file access unavailable, showing temp files only"
            }
            
        except Exception as e:
            # 最终后备方案：总是返回临时文件
            print(f"文件列表获取异常: {e}")
            return {
                "success": True,
                "warning": f"File listing error: {str(e)}, showing temp files only",
                "files": temp_files,
                "directory": directory,
                "temp_files_count": len(temp_files),
                "sandbox_files_count": 0,
                "session_active": False
            }
    
    def download_sandbox_file(self, file_path):
        """下载沙盒中的文件或本地临时文件"""
        try:
            # 首先检查是否是本地临时文件
            for temp_file in self._temp_files:
                if temp_file["path"] == file_path:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        return {
                            "success": True,
                            "content": content,
                            "filename": temp_file["name"],
                            "path": file_path,
                            "is_temp": True
                        }
                    except Exception as e:
                        return {
                            "success": False,
                            "error": f"Failed to read temp file: {str(e)}",
                            "content": None
                        }
            
            # 如果不是临时文件，检查沙盒会话
            if not self.desktop_manager or not self.desktop_manager.desk:
                return {
                    "success": False,
                    "error": "No active sandbox session",
                    "content": None
                }
            
            # 尝试使用E2B的文件API读取文件
            try:
                content = self.desktop_manager.desk.files.read(file_path)
                return {
                    "success": True,
                    "content": content,
                    "filename": file_path.split('/')[-1],
                    "path": file_path
                }
            except Exception as files_error:
                # 如果文件API失败，回退到命令行方式
                print(f"文件API失败，使用命令行方式: {files_error}")
                result = self.desktop_manager.desk.commands.run(f"cat '{file_path}'")
                
                if result.exit_code == 0:
                    return {
                        "success": True,
                        "content": result.stdout,
                        "filename": file_path.split('/')[-1],
                        "path": file_path
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to read file: {result.stderr}",
                        "content": None
                    }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "content": None
            }

    def cleanup(self):
        """暂停资源而不删除沙盒 (兼容原API)"""
        try:
            if self.desktop_manager.desk:
                # 暂停直播流而不删除沙盒
                try:
                    self.desktop_manager.desk.stream.stop()
                    print("✅ 沙盒直播流已暂停")
                except Exception as e:
                    print(f"⚠️ 停止直播流时出错: {e}")
                
                # 重置状态但保留沙盒实例
                self.stream_url = None
                self._initialized = False
                
                return {"success": True, "message": "Desktop session paused (sandbox preserved)"}
            else:
                return {"success": True, "message": "No active session to pause"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def resume_session(self):
        """恢复沙盒会话"""
        try:
            if self.desktop_manager.desk:
                # 重新启动直播流
                try:
                    self.desktop_manager.desk.stream.start(require_auth=True)
                    self.stream_url = self.desktop_manager.desk.stream.get_url(
                        auth_key=self.desktop_manager.desk.stream.get_auth_key()
                    )
                    print("✅ 沙盒直播流已恢复")
                    print(f"📺 直播地址: {self.stream_url}")
                    return {
                        "success": True, 
                        "message": "Desktop session resumed",
                        "stream_url": self.stream_url
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "error": f"Failed to resume stream: {str(e)}"
                    }
            else:
                return {
                    "success": False,
                    "error": "No sandbox to resume"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def terminate_session(self):
        """彻底终止沙盒会话（原cleanup逻辑）"""
        try:
            if self.desktop_manager.desk:
                self.desktop_manager.desk.kill()
                self.desktop_manager.desk = None
                self.stream_url = None
                self._initialized = False
                # 清空临时文件列表
                self._temp_files = []
                # 重置接管状态
                self.takeover_active = False
                self.intervention_needed = False
                self.intervention_reason = ""
                self.automation_paused = False
                return {"success": True, "message": "Desktop session terminated"}
            else:
                return {"success": True, "message": "No active session to terminate"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def enable_takeover(self):
        """启用人工接管模式，设置view_only=True"""
        try:
            if not self.desktop_manager or not self.desktop_manager.desk:
                return {
                    "success": False,
                    "error": "No active desktop session",
                    "message": "请先创建桌面会话"
                }
            
            # 设置view_only=True，允许用户手动操作
            if hasattr(self.desktop_manager, 'set_view_only'):
                self.desktop_manager.set_view_only(True)
            
            # 更新状态
            self.takeover_active = True
            self.automation_paused = True
            
            # 获取新的stream URL（如果需要）
            try:
                new_stream_url = self.desktop_manager.desk.stream.get_url(
                    auth_key=self.desktop_manager.desk.stream.get_auth_key(),
                    view_only=True  # 用户可以操作
                )
                self.stream_url = new_stream_url
            except Exception as e:
                print(f"更新stream URL失败: {e}")
            
            print("🎮 人工接管模式已启用，用户可以手动操作")
            
            return {
                "success": True,
                "message": "人工接管模式已启用，您现在可以手动操作桌面",
                "takeover_active": True,
                "stream_url": self.stream_url,
                "instruction": "请在桌面上完成密码输入或验证码验证，完成后点击 '结束接管' 恢复自动化"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"启用人工接管失败: {str(e)}"
            }
    
    def disable_takeover(self):
        """禁用人工接管模式，设置view_only=False"""
        try:
            if not self.desktop_manager or not self.desktop_manager.desk:
                return {
                    "success": False,
                    "error": "No active desktop session",
                    "message": "没有活动的桌面会话"
                }
            
            # 设置view_only=False，切换回只读模式
            if hasattr(self.desktop_manager, 'set_view_only'):
                self.desktop_manager.set_view_only(False)
            
            # 更新状态
            self.takeover_active = False
            self.automation_paused = False
            self.intervention_needed = False
            self.intervention_reason = ""
            
            # 获取新的stream URL（只读模式）
            try:
                new_stream_url = self.desktop_manager.desk.stream.get_url(
                    auth_key=self.desktop_manager.desk.stream.get_auth_key(),
                    view_only=False  # 只读模式
                )
                self.stream_url = new_stream_url
            except Exception as e:
                print(f"更新stream URL失败: {e}")
            
            print("🤖 自动化模式已恢复，用户无法手动操作")
            
            return {
                "success": True,
                "message": "已恢复自动化模式，人工接管结束",
                "takeover_active": False,
                "stream_url": self.stream_url,
                "instruction": "现在可以继续使用聊天界面发送自动化指令"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"禁用人工接管失败: {str(e)}"
            }
    
    def get_takeover_status(self):
        """获取当前接管状态"""
        return {
            "takeover_active": self.takeover_active,
            "intervention_needed": self.intervention_needed,
            "intervention_reason": self.intervention_reason,
            "automation_paused": self.automation_paused,
            "session_active": bool(self.desktop_manager and self.desktop_manager.desk),
            "stream_url": self.stream_url
        }
    
    def clear_intervention_state(self):
        """清除干预状态，但保持接管模式"""
        self.intervention_needed = False
        self.intervention_reason = ""
        return {
            "success": True,
            "message": "干预状态已清除",
            "intervention_needed": False,
            "takeover_active": self.takeover_active
        }
    
