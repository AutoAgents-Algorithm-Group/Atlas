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
            self.browser_runner = BrowseUseExecutor(
                task=task,
                external_cdp_base=self.external_cdp_base,
                backup_chrome_base=self.backup_chrome_base
            )
            
            # 执行任务 (在异步环境中运行同步的browser-use)
            import asyncio
            from concurrent.futures import ThreadPoolExecutor
            
            def run_browser_task():
                """在单独线程中运行browser-use任务"""
                try:
                    # 延迟导入，避免无关环境报错
                    from browser_use import Agent, Browser, ChatOpenAI

                    ws = self.browser_runner.fetch_ws_endpoint()
                    llm = ChatOpenAI(
                        model=self.browser_runner.model, 
                        temperature=0,
                        base_url=self.browser_runner.base_url,
                        api_key=self.browser_runner.api_key
                    )
                    
                    # 直接执行原始任务
                    task_to_execute = task
                    
                    # 使用重试机制执行任务
                    max_retries = 2  # 减少重试次数，避免长时间等待
                    last_error = None
                    
                    for attempt in range(max_retries):
                        try:
                            browser = Browser(cdp_url=ws)
                            agent = Agent(task=task_to_execute, llm=llm, browser=browser)
                            
                            print(f"🚀 开始执行任务 (尝试 {attempt + 1}/{max_retries}): {task_to_execute}")
                            result = agent.run_sync()
                            
                            return {
                                "success": True,
                                "message": "Task completed successfully",
                                "result": str(result)[:800] + "..." if len(str(result)) > 800 else str(result),
                                "task": task
                            }
                            
                        except Exception as e:
                            last_error = e
                            error_str = str(e)
                            print(f"❌ 任务执行失败 (尝试 {attempt + 1}/{max_retries}): {error_str[:200]}...")
                            
                            # 检查是否是连接问题
                            if "websocket" in error_str.lower() or "connection" in error_str.lower():
                                if attempt < max_retries - 1:
                                    print(f"🔄 检测到连接问题，等待 5 秒后重新连接...")
                                    time.sleep(5)
                                    
                                    # 重新获取WebSocket端点
                                    try:
                                        ws = self.browser_runner.fetch_ws_endpoint()
                                        print("✅ 重新获取WebSocket端点成功")
                                    except Exception as reconnect_error:
                                        print(f"❌ 重新获取端点失败: {reconnect_error}")
                                        continue
                            else:
                                # 其他错误，直接返回
                                break
                    
                    # 失败处理
                    if "websocket" in str(last_error).lower() or "connection" in str(last_error).lower():
                        return {
                            "success": False,
                            "error": "Connection timeout",
                            "message": "任务执行时连接超时。E2B WebSocket连接不稳定，请稍后重试或尝试更简单的任务。"
                        }
                    else:
                        return {
                            "success": False,
                            "error": str(last_error)[:200],
                            "message": f"任务执行失败: {str(last_error)[:200]}..."
                        }
                except Exception as e:
                    return {
                        "success": False,
                        "error": str(e),
                        "message": f"Failed to execute task: {task}"
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
        """列出沙盒中的文件"""
        try:
            # 如果没有沙盒会话，但有临时文件，仍然返回临时文件
            if not self.desktop_manager or not self.desktop_manager.desk:
                temp_files = []
                for temp_file in self._temp_files:
                    temp_files.append({
                        "name": temp_file["name"],
                        "path": temp_file["path"],
                        "size": temp_file["size"],
                        "type": temp_file["type"],
                        "is_temp": True
                    })
                
                if temp_files:
                    return {
                        "success": True,
                        "warning": "No active sandbox session, showing agent output files only",
                        "files": temp_files,
                        "directory": directory,
                        "temp_files_count": len(temp_files)
                    }
                else:
                    return {
                        "success": False,
                        "error": "No active sandbox session",
                        "files": []
                    }
            
            # E2B文件系统访问方式
            try:
                # 尝试使用E2B的文件API列出文件
                try:
                    file_items = self.desktop_manager.desk.files.list(directory)
                    files = []
                    
                    for item in file_items:
                        # 检查是否是文件且不是隐藏文件
                        if hasattr(item, 'is_dir') and not item.is_dir and not item.name.startswith('.'):
                            files.append({
                                "name": item.name,
                                "path": f"{directory.rstrip('/')}/{item.name}",
                                "size": getattr(item, 'size', 0),
                                "type": "file"
                            })
                    
                    # 添加临时文件到列表中（E2B文件API成功分支）
                    for temp_file in self._temp_files:
                        files.append({
                            "name": temp_file["name"],
                            "path": temp_file["path"],
                            "size": temp_file["size"],
                            "type": temp_file["type"],
                            "is_temp": True
                        })
                    
                    return {
                        "success": True,
                        "files": files,
                        "directory": directory,
                        "temp_files_count": len(self._temp_files)
                    }
                    
                except Exception as files_api_error:
                    print(f"E2B文件API失败，使用命令行方式: {files_api_error}")
                    
                    # 使用 commands.run 执行bash命令列出文件
                    result = self.desktop_manager.desk.commands.run(f"find {directory} -maxdepth 1 -type f -exec ls -la {{}} \\;")
                    files = []
                    
                    if result.exit_code == 0:
                        lines = result.stdout.strip().split('\n')
                        for line in lines:
                            if line.strip():
                                # 解析 ls -la 输出
                                parts = line.split()
                                if len(parts) >= 9:
                                    size = int(parts[4]) if parts[4].isdigit() else 0
                                    filename = ' '.join(parts[8:])
                                    filepath = f"{directory.rstrip('/')}/{filename}" if not filename.startswith('/') else filename
                                    
                                    # 只处理文件名不以.开头的文件
                                    if not filename.startswith('.'):
                                        files.append({
                                            "name": filename,
                                            "path": filepath,
                                            "size": size,
                                            "type": "file"
                                        })
                    
                    return {
                        "success": True,
                        "files": files,
                        "directory": directory
                    }
            
            except Exception as cmd_error:
                # 最后的备用方案：尝试简单的ls命令
                try:
                    result = self.desktop_manager.desk.commands.run(f"ls -la {directory}")
                    files = []
                    
                    if result.exit_code == 0:
                        lines = result.stdout.strip().split('\n')[1:]  # 跳过总计行
                        for line in lines:
                            if line.strip() and not line.startswith('d'):  # 不是目录
                                parts = line.split()
                                if len(parts) >= 9:
                                    filename = ' '.join(parts[8:])
                                    if not filename.startswith('.') and filename not in ['.', '..']:
                                        files.append({
                                            "name": filename,
                                            "path": f"{directory.rstrip('/')}/{filename}",
                                            "size": int(parts[4]) if parts[4].isdigit() else 0,
                                            "type": "file"
                                        })
                    
                    return {
                        "success": True,
                        "files": files,
                        "directory": directory
                    }
                    
                except Exception as fallback_error:
                    return {
                        "success": False,
                        "error": f"Failed to list files: {str(fallback_error)}",
                        "files": []
                    }
            
        except Exception as e:
            # 即使出错，也尝试返回临时文件
            temp_files = []
            for temp_file in self._temp_files:
                temp_files.append({
                    "name": temp_file["name"],
                    "path": temp_file["path"],
                    "size": temp_file["size"],
                    "type": temp_file["type"],
                    "is_temp": True
                })
            
            if temp_files:
                return {
                    "success": True,
                    "error": f"Sandbox files unavailable: {str(e)}",
                    "files": temp_files,
                    "directory": directory,
                    "temp_files_count": len(temp_files)
                }
            else:
                return {
                    "success": False,
                    "error": str(e),
                    "files": []
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
                return {"success": True, "message": "Desktop session terminated"}
            else:
                return {"success": True, "message": "No active session to terminate"}
        except Exception as e:
            return {"success": False, "error": str(e)}
