import os
import time
import json
import urllib.request
import ssl


class BrowseUseExecutor:
    """
    本地运行的 browser-use 执行器：连 E2B 公开的 9223（通过 /json/version 获取 ws 端点），
    然后用自然语言任务驱动浏览器。支持代理失败时的备用连接方案。
    """

    def __init__(self, task: str, external_cdp_base: str, backup_chrome_base: str = None, model: str | None = None):
        self.task = task
        self.external_cdp_base = external_cdp_base.rstrip("/")
        self.backup_chrome_base = backup_chrome_base.rstrip("/") if backup_chrome_base else None
        self.model = model or os.getenv("BROWSER_USE_MODEL", "gemini-2.5-pro")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.tu-zi.com/v1")
        self.api_key = os.getenv("OPENAI_API_KEY", "sk-9mRo0HPml7rUWwpQsal5Ve7CWx65Q7gxkF95a6QLxzfXarKi")

    @staticmethod
    def _http_get(url: str, timeout: int = 10) -> str:
        ssl._create_default_https_context = ssl._create_unverified_context  # demo 简化证书校验
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return resp.read().decode("utf-8")

    def _fix_websocket_url(self, ws_url: str, base_url: str) -> str:
        """修复WebSocket URL，确保包含正确的主机和端口。"""
        import urllib.parse
        
        # 解析原始WebSocket URL和基础URL
        ws_parsed = urllib.parse.urlparse(ws_url)
        base_parsed = urllib.parse.urlparse(base_url)
        
        # 构建正确的WebSocket URL
        if base_parsed.scheme == 'https':
            ws_scheme = 'wss'
        else:
            ws_scheme = 'ws'
            
        # 使用E2B的外网地址而不是127.0.0.1
        fixed_ws = f"{ws_scheme}://{base_parsed.netloc}{ws_parsed.path}"
        
        print(f"🔧 修复WebSocket URL: {ws_url} -> {fixed_ws}")
        return fixed_ws

    def fetch_ws_endpoint(self) -> str:
        """从公开的 /json/version 获取 webSocketDebuggerUrl，支持重试和备用方案。"""
        
        # 首先尝试代理端点
        meta_url = f"{self.external_cdp_base}/json/version"
        print(f"📡 尝试通过代理端点连接: {meta_url}")
        
        last_error = None
        for attempt in range(1, 4):  # 代理尝试3次
            try:
                print(f"代理连接尝试 {attempt}/3...")
                raw = self._http_get(meta_url, timeout=10)
                meta = json.loads(raw)
                
                ws = meta.get("webSocketDebuggerUrl")
                if not ws:
                    raise RuntimeError(f"未返回 webSocketDebuggerUrl，响应: {raw}")
                
                # 修复WebSocket URL
                fixed_ws = self._fix_websocket_url(ws, self.external_cdp_base)
                print("✅ 代理连接成功！CDP WebSocket:", fixed_ws)
                return fixed_ws
                
            except Exception as e:
                last_error = e
                print(f"代理连接失败 (尝试 {attempt}/3): {e}")
                if attempt < 3:
                    time.sleep(2)
        
        # 代理失败，尝试备用方案
        if self.backup_chrome_base:
            print(f"\n🔄 代理连接失败，尝试直接连接Chrome: {self.backup_chrome_base}")
            backup_url = f"{self.backup_chrome_base}/json/version"
            
            for attempt in range(1, 4):  # 直连尝试3次
                try:
                    print(f"直连尝试 {attempt}/3...")
                    raw = self._http_get(backup_url, timeout=10)
                    meta = json.loads(raw)
                    
                    ws = meta.get("webSocketDebuggerUrl")
                    if not ws:
                        raise RuntimeError(f"未返回 webSocketDebuggerUrl，响应: {raw}")
                    
                    # 修复WebSocket URL
                    fixed_ws = self._fix_websocket_url(ws, self.backup_chrome_base)
                    print("✅ 直连成功！CDP WebSocket:", fixed_ws)
                    return fixed_ws
                    
                except Exception as e:
                    print(f"直连失败 (尝试 {attempt}/3): {e}")
                    if attempt < 3:
                        time.sleep(2)
        
        # 所有方案都失败了
        error_msg = f"""
❌ 所有连接方案都失败了！

代理端点: {meta_url}
最后错误: {last_error}

请检查：
1. E2B 沙盒是否正常运行
2. 端口 9223 (代理) 或 9222 (Chrome) 是否已公开
3. 沙盒内的服务是否正常启动

建议：
- 检查 E2B 控制台的端口设置
- 确认沙盒没有被暂停或重启
- 查看服务启动日志
"""
        raise RuntimeError(error_msg)

    def run(self):
        """连接远端 CDP，执行写死任务。"""
        if not self.api_key or self.api_key.startswith("sk-your-") or len(self.api_key) < 20:
            raise RuntimeError(f"无效的 OPENAI_API_KEY: {self.api_key[:20]}... \n请在.env文件中设置有效的API密钥或使用: export OPENAI_API_KEY=sk-xxxx")

        # 延迟导入，避免无关环境报错
        from browser_use import Agent, Browser
        from browser_use import ChatOpenAI

        ws = self.fetch_ws_endpoint()
        llm = ChatOpenAI(
            model=self.model,
            base_url=self.base_url,
            api_key=self.api_key,
            temperature=0
        )
        
        # 创建Browser实例，启用highlight功能
        browser = Browser(
            cdp_url=ws,
            devtools=False,
            highlight_elements=True,  # 启用高亮功能，显示元素操作
            flash_mode=True
        )
        agent = Agent(
            task=self.task, 
            llm=llm, 
            browser=browser
        )

        print(f"\n>>> 开始执行任务：{self.task}\n")
        
        # 添加重试机制
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = agent.run_sync()
                print("\n【执行完成 | 文本摘要（前1000字）】\n", str(result)[:1000], "...\n")
                return str(result)  # 成功则返回结果
                
            except Exception as e:
                print(f"\n❌ 执行失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    print(f"等待 {(attempt + 1) * 5} 秒后重试...")
                    time.sleep((attempt + 1) * 5)
                    
                    # 重新获取WebSocket端点
                    try:
                        ws = self.fetch_ws_endpoint()
                        browser = Browser(
                            cdp_url=ws, 
                            highlight_elements=True, 
                            flash_mode=True
                        )
                        
                        agent = Agent(
                            task=self.task, 
                            llm=llm, 
                            browser=browser
                        )
                    except Exception as reconnect_error:
                        print(f"重连失败: {reconnect_error}")
                        continue
                else:
                    print(f"\n❌ 所有重试都失败了，最后错误: {e}")
                    raise e
