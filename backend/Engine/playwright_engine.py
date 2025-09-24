import os
import json
import time
import urllib.request
import ssl
import asyncio
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, Page, BrowserContext


class PlaywrightEngine:
    """
    基于 Playwright 的浏览器自动化引擎，支持连接到 E2B CDP 端点。
    提供与 BrowseUseExecutor 兼容的接口，支持自然语言任务执行。
    """
    
    def __init__(
        self, 
        task: str, 
        external_cdp_base: str, 
        backup_chrome_base: str = None, 
        model: str = None,
        headless: bool = False
    ):
        self.task = task
        self.external_cdp_base = external_cdp_base.rstrip("/")
        self.backup_chrome_base = backup_chrome_base.rstrip("/") if backup_chrome_base else None
        self.model = model or os.getenv("BROWSER_USE_MODEL", "gpt-4o")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.headless = headless
        
        # Playwright 实例
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
        # 任务执行状态
        self.is_running = False
        self.max_steps = 50
        self.step_delay = 1.0
        
    @staticmethod
    def _http_get(url: str, timeout: int = 10) -> str:
        """HTTP GET 请求，简化证书校验"""
        ssl._create_default_https_context = ssl._create_unverified_context
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return resp.read().decode("utf-8")
    
    def _fix_websocket_url(self, ws_url: str, base_url: str) -> str:
        """修复 WebSocket URL，确保包含正确的主机和端口"""
        import urllib.parse
        
        ws_parsed = urllib.parse.urlparse(ws_url)
        base_parsed = urllib.parse.urlparse(base_url)
        
        if base_parsed.scheme == 'https':
            ws_scheme = 'wss'
        else:
            ws_scheme = 'ws'
            
        fixed_ws = f"{ws_scheme}://{base_parsed.netloc}{ws_parsed.path}"
        print(f"🔧 修复 WebSocket URL: {ws_url} -> {fixed_ws}")
        return fixed_ws
    
    def fetch_ws_endpoint(self) -> str:
        """从 /json/version 获取 webSocketDebuggerUrl，支持重试和备用方案"""
        
        # 首先尝试代理端点
        meta_url = f"{self.external_cdp_base}/json/version"
        print(f"📡 尝试通过代理端点连接: {meta_url}")
        
        last_error = None
        for attempt in range(1, 4):
            try:
                print(f"代理连接尝试 {attempt}/3...")
                raw = self._http_get(meta_url, timeout=10)
                meta = json.loads(raw)
                
                ws = meta.get("webSocketDebuggerUrl")
                if not ws:
                    raise RuntimeError(f"未返回 webSocketDebuggerUrl，响应: {raw}")
                
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
            
            for attempt in range(1, 4):
                try:
                    print(f"直连尝试 {attempt}/3...")
                    raw = self._http_get(backup_url, timeout=10)
                    meta = json.loads(raw)
                    
                    ws = meta.get("webSocketDebuggerUrl")
                    if not ws:
                        raise RuntimeError(f"未返回 webSocketDebuggerUrl，响应: {raw}")
                    
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
"""
        raise RuntimeError(error_msg)
    
    async def _connect_to_browser(self) -> Browser:
        """连接到远程 CDP 端点"""
        if not self.api_key or self.api_key.startswith("sk-your-") or len(self.api_key) < 20:
            raise RuntimeError(f"无效的 OPENAI_API_KEY: {self.api_key[:20]}... \n请设置有效的API密钥")
        
        # 获取 CDP 端点
        ws_endpoint = self.fetch_ws_endpoint()
        
        # 启动 Playwright
        self.playwright = await async_playwright().start()
        
        # 连接到远程浏览器
        # 从 WebSocket URL 提取 CDP 端点
        import urllib.parse
        parsed = urllib.parse.urlparse(ws_endpoint)
        cdp_endpoint = f"http://{parsed.netloc}"
        
        try:
            # 尝试连接到现有浏览器
            self.browser = await self.playwright.chromium.connect_over_cdp(cdp_endpoint)
            print(f"✅ 成功连接到远程浏览器: {cdp_endpoint}")
            
            # 创建新的浏览器上下文
            self.context = await self.browser.new_context(
                viewport={'width': 1440, 'height': 900},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            
            # 创建新页面
            self.page = await self.context.new_page()
            
            return self.browser
            
        except Exception as e:
            print(f"❌ 连接到 CDP 端点失败: {e}")
            # 清理资源
            if self.playwright:
                await self.playwright.stop()
            raise
    
    async def _analyze_page_content(self) -> Dict[str, Any]:
        """分析当前页面内容，提取关键信息供AI决策"""
        if not self.page:
            return {}
        
        try:
            # 获取页面基本信息
            title = await self.page.title()
            url = self.page.url
            
            # 获取页面文本内容 (限制长度)
            text_content = await self.page.evaluate("""
                () => {
                    const text = document.body.innerText || '';
                    return text.substring(0, 2000);
                }
            """)
            
            # 获取可交互元素
            interactive_elements = await self.page.evaluate("""
                () => {
                    const elements = [];
                    const selectors = [
                        'button', 'input', 'select', 'textarea', 'a[href]',
                        '[onclick]', '[role="button"]', '[role="link"]'
                    ];
                    
                    selectors.forEach(selector => {
                        document.querySelectorAll(selector).forEach((el, index) => {
                            if (el.offsetParent !== null) { // 元素可见
                                const rect = el.getBoundingClientRect();
                                if (rect.width > 0 && rect.height > 0) {
                                    elements.push({
                                        tag: el.tagName.toLowerCase(),
                                        type: el.type || '',
                                        text: (el.textContent || el.value || el.placeholder || '').substring(0, 100),
                                        selector: selector + ':nth-of-type(' + (index + 1) + ')',
                                        href: el.href || '',
                                        x: Math.round(rect.x),
                                        y: Math.round(rect.y)
                                    });
                                }
                            }
                        });
                    });
                    
                    return elements.slice(0, 20); // 限制数量
                }
            """)
            
            return {
                'title': title,
                'url': url,
                'text_content': text_content,
                'interactive_elements': interactive_elements
            }
            
        except Exception as e:
            print(f"分析页面内容时出错: {e}")
            return {}
    
    async def _get_ai_action(self, page_info: Dict[str, Any], step: int) -> Dict[str, Any]:
        """使用 AI 模型分析页面并决定下一步操作"""
        try:
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            
            # 构建提示词
            prompt = f"""
你是一个网页自动化助手。请分析当前页面状态并决定下一步操作来完成任务。

任务: {self.task}
当前步骤: {step}/{self.max_steps}

页面信息:
- 标题: {page_info.get('title', '')}
- URL: {page_info.get('url', '')}
- 页面文本: {page_info.get('text_content', '')[:500]}...

可交互元素:
{json.dumps(page_info.get('interactive_elements', []), indent=2, ensure_ascii=False)[:1000]}

请返回 JSON 格式的操作指令，格式如下:
{{
    "action": "click|type|navigate|scroll|wait|complete",
    "target": "CSS选择器或URL",
    "value": "输入的文本内容(仅type操作需要)",
    "reasoning": "操作原因",
    "completed": false|true
}}

可用操作类型:
- click: 点击元素
- type: 在输入框中输入文本  
- navigate: 导航到新URL
- scroll: 滚动页面
- wait: 等待页面加载
- complete: 任务完成

请确保返回有效的JSON格式。
"""
            
            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的网页自动化助手，请根据页面内容和任务要求返回最合适的操作指令。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # 尝试解析 JSON
            try:
                # 提取 JSON 部分
                if '```json' in ai_response:
                    json_start = ai_response.find('```json') + 7
                    json_end = ai_response.find('```', json_start)
                    ai_response = ai_response[json_start:json_end]
                elif '{' in ai_response:
                    json_start = ai_response.find('{')
                    json_end = ai_response.rfind('}') + 1
                    ai_response = ai_response[json_start:json_end]
                
                action_data = json.loads(ai_response)
                print(f"🤖 AI决策: {action_data.get('action')} - {action_data.get('reasoning', '')}")
                return action_data
                
            except json.JSONDecodeError as e:
                print(f"❌ 解析AI响应JSON失败: {e}")
                print(f"原始响应: {ai_response}")
                
                # 返回默认操作
                return {
                    "action": "wait",
                    "reasoning": "AI响应解析失败，等待后重试",
                    "completed": False
                }
                
        except Exception as e:
            print(f"❌ AI决策失败: {e}")
            return {
                "action": "wait", 
                "reasoning": f"AI调用失败: {str(e)}",
                "completed": False
            }
    
    async def _execute_action(self, action_data: Dict[str, Any]) -> bool:
        """执行具体的操作"""
        if not self.page:
            return False
        
        try:
            action = action_data.get('action', '').lower()
            target = action_data.get('target', '')
            value = action_data.get('value', '')
            
            print(f"🎯 执行操作: {action} {target} {value}")
            
            if action == 'click':
                if target:
                    await self.page.click(target, timeout=10000)
                    await asyncio.sleep(1)
                    
            elif action == 'type':
                if target and value:
                    await self.page.fill(target, value)
                    await asyncio.sleep(0.5)
                    
            elif action == 'navigate':
                if target:
                    await self.page.goto(target, wait_until='networkidle')
                    await asyncio.sleep(2)
                    
            elif action == 'scroll':
                scroll_amount = 500
                if target == 'up':
                    scroll_amount = -500
                await self.page.evaluate(f"window.scrollBy(0, {scroll_amount})")
                await asyncio.sleep(1)
                
            elif action == 'wait':
                await asyncio.sleep(2)
                
            elif action == 'complete':
                return True
                
            else:
                print(f"⚠️ 未知操作: {action}")
                
            return False
            
        except Exception as e:
            print(f"❌ 执行操作失败: {e}")
            return False
    
    async def _run_task(self) -> str:
        """执行主要的任务流程"""
        print(f"\n🚀 开始使用 Playwright 执行任务: {self.task}")
        
        try:
            # 连接到浏览器
            await self._connect_to_browser()
            
            # 导航到起始页面（可以是任何URL）
            start_url = "https://www.google.com"
            await self.page.goto(start_url, wait_until='networkidle')
            print(f"📍 导航到起始页面: {start_url}")
            
            # 执行任务步骤
            for step in range(1, self.max_steps + 1):
                if not self.is_running:
                    break
                
                print(f"\n--- 步骤 {step}/{self.max_steps} ---")
                
                # 分析当前页面
                page_info = await self._analyze_page_content()
                
                # 获取AI决策
                action_data = await self._get_ai_action(page_info, step)
                
                # 检查是否任务完成
                if action_data.get('completed') or action_data.get('action') == 'complete':
                    print("✅ 任务完成!")
                    break
                
                # 执行操作
                completed = await self._execute_action(action_data)
                if completed:
                    print("✅ 任务完成!")
                    break
                
                # 步骤间延迟
                await asyncio.sleep(self.step_delay)
            
            # 获取最终页面状态
            final_info = await self._analyze_page_content()
            
            result = f"""
✅ Playwright 任务执行完成

任务: {self.task}
执行步骤: {step}
最终页面: {final_info.get('title', '')} ({final_info.get('url', '')})
页面内容预览: {final_info.get('text_content', '')[:300]}...
"""
            print(result)
            return result
            
        except Exception as e:
            error_msg = f"❌ Playwright 任务执行失败: {str(e)}"
            print(error_msg)
            return error_msg
        
        finally:
            # 清理资源
            await self._cleanup()
    
    async def _cleanup(self):
        """清理 Playwright 资源"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
                
            print("🧹 Playwright 资源已清理")
            
        except Exception as e:
            print(f"⚠️ 清理资源时出错: {e}")
    
    def run(self) -> str:
        """同步接口：执行任务（兼容 BrowseUseExecutor.run()）"""
        self.is_running = True
        
        try:
            # 在新的事件循环中运行异步任务
            return asyncio.run(self._run_task())
            
        except Exception as e:
            error_msg = f"❌ Playwright 引擎运行失败: {str(e)}"
            print(error_msg)
            return error_msg
        
        finally:
            self.is_running = False
    
    def stop(self):
        """停止任务执行"""
        self.is_running = False
        print("⏹️ Playwright 任务已停止")


# 便于导入的别名
PlaywrightExecutor = PlaywrightEngine

