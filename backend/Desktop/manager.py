import os
import time
from e2b_desktop import Sandbox


class E2BDesktopManager:
    """
    负责 E2B 桌面：创建沙盒、开启直播、在沙盒里启动可见的 Chrome（CDP:9222），
    并在 9223 起一个反向代理把 Host 改写为 127.0.0.1，供外网访问。
    """

    CHROME_PORT = 9222
    PROXY_PORT  = 9223

    CHROME_FLAGS = [
        "--remote-debugging-address=0.0.0.0",
        f"--remote-debugging-port={CHROME_PORT}",
        "--remote-allow-origins=*",
        "--user-data-dir=/home/user/chrome-profile",
        "--no-first-run",                   # 禁用首次运行检查
        "--no-default-browser-check",       # 禁用默认浏览器检查
        "--start-maximized",                # 让Chrome窗口启动时自动最大化
        "--kiosk",                          # 让Chrome窗口启动时自动全屏
        "--disable-infobars",               # 禁用Chrome的信息提示栏
        "--disable-extensions",             # 禁用扩展程序以减少界面元素
        "--disable-dev-shm-usage",          # 解决共享内存相关问题
    ]

    def __init__(self, resolution=(1440, 900), dpi=96):
        self.resolution = resolution
        self.dpi = dpi
        self.desk: Sandbox | None = None
        self.live_url: str | None = None
        self.chrome_bin: str | None = None
        # E2B API密钥
        self.api_key = "e2b_c6bbe444d963e8db1dc680d8a45a35cc13e0e47e"

    def start_desktop(self):
        """创建沙盒并开启直播（返回直播URL）。"""
        self.desk = Sandbox.create(
            api_key=self.api_key,
            resolution=self.resolution, 
            dpi=self.dpi, 
            timeout=60000
        )
        self.desk.stream.start(require_auth=True)
        self.live_url = self.desk.stream.get_url(auth_key=self.desk.stream.get_auth_key())
        print("\n=== 桌面直播地址（可观看整个过程） ===")
        print(self.live_url)
        print("=====================================\n")
        return self.live_url

    def _detect_chrome(self) -> str | None:
        """在沙盒里探测可用的 Chrome/Chromium 可执行名。"""
        assert self.desk is not None
        r = self.desk.commands.run(
            "bash -lc 'command -v google-chrome || command -v chromium || command -v chromium-browser || true'"
        )
        path = r.stdout.strip()
        return path or None

    def ensure_chrome_or_fail(self):
        """确保沙盒里有浏览器；若无则直接失败（避免每次安装）。"""
        self.chrome_bin = self._detect_chrome()
        if not self.chrome_bin:
            raise RuntimeError(
                "沙盒内未找到 Chrome/Chromium。请改用自带浏览器的基镜像，或在镜像制作阶段预装浏览器。"
            )
        print(f"检测到浏览器：{self.chrome_bin}")

    def launch_chrome_with_cdp(self, delay_seconds: int = 5):
        """启动'可见'的 Chrome，并监听 0.0.0.0:9222（CDP）。"""
        assert self.desk is not None and self.chrome_bin is not None
        flags = " ".join(self.CHROME_FLAGS)
        self.desk.commands.run(
            f"bash -lc '{self.chrome_bin} {flags} >/home/user/chrome.out 2>&1 &'",
            background=True,
        )
        print(f"已在沙盒内启动 Chrome（CDP 0.0.0.0:{self.CHROME_PORT}，窗口可在直播中看到）")
        
        # 等待Chrome启动并验证CDP端口
        print("等待Chrome启动...")
        for i in range(10):  # 最多等待10秒
            time.sleep(1)
            result = self.desk.commands.run("curl -s http://localhost:9222/json/version || echo 'FAILED'", timeout=5)
            if "FAILED" not in result.stdout and "Browser" in result.stdout:
                print(f"Chrome CDP验证成功 (尝试 {i+1}/10)")
                break
            print(f"Chrome尚未就绪，继续等待... (尝试 {i+1}/10)")
        else:
            print("警告：Chrome可能未完全启动，检查进程...")
            proc_result = self.desk.commands.run("ps aux | grep chrome | grep -v grep", timeout=5)
            print("Chrome进程:", proc_result.stdout)
            
        print("（内部自检）使用沙盒控制台访问：curl http://localhost:9222/json/version")
        
        # 显示Chrome日志以供调试
        print("检查Chrome日志...")
        log_result = self.desk.commands.run("tail -10 /home/user/chrome.out 2>/dev/null || echo '暂无日志'", timeout=5)
        print("Chrome日志:", log_result.stdout)

    def launch_cdp_proxy(self):
        """在沙盒内起代理：0.0.0.0:9223 → 127.0.0.1:9222（改写 Host，兼容 WS）。"""
        proxy_code = r"""
import aiohttp, asyncio
from aiohttp import web
import logging
import json

# 启用日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

UP = "http://127.0.0.1:9222"

async def proxy_http(request):
    url = f"{UP}{request.rel_url}"
    hdr = dict(request.headers)
    hdr["Host"] = "127.0.0.1"
    data = await request.read()
    try:
        async with aiohttp.ClientSession() as s:
            async with s.request(request.method, url, data=data, headers=hdr) as r:
                resp_data = await r.read()
                
                # 特殊处理 /json/version - 修复WebSocket URL
                if request.path == "/json/version":
                    try:
                        resp_json = json.loads(resp_data.decode('utf-8'))
                        if 'webSocketDebuggerUrl' in resp_json:
                            ws_url = resp_json['webSocketDebuggerUrl']
                            # 保持路径，但确保使用外网可访问的主机
                            if ws_url.startswith('ws://127.0.0.1'):
                                # 提取路径部分
                                path_part = ws_url.split('127.0.0.1')[-1]
                                if not path_part.startswith('/'):
                                    path_part = '/' + path_part
                                # 使用外网地址构建WebSocket URL，这里暂时保持127.0.0.1，客户端会修复
                                resp_json['webSocketDebuggerUrl'] = f"ws://127.0.0.1{path_part}"
                                resp_data = json.dumps(resp_json).encode('utf-8')
                                logger.info(f"修复WebSocket URL: {resp_json['webSocketDebuggerUrl']}")
                    except Exception as e:
                        logger.warning(f"处理/json/version时出错: {e}")
                
                resp = web.Response(body=resp_data, status=r.status, headers=r.headers)
                resp.headers.popall('Content-Length', None)
                return resp
    except Exception as e:
        logger.error(f"代理错误: {e}")
        raise

async def proxy_ws(request):
    # WebSocket URL转换为HTTP URL来连接Chrome
    ups_url = f"ws://127.0.0.1:9222{request.rel_url}"
    logger.info(f"WebSocket代理连接: {ups_url}")
    try:
        async with aiohttp.ClientSession() as s:
            async with s.ws_connect(ups_url, headers={"Host":"127.0.0.1"}) as ups:
                ws = web.WebSocketResponse()
                await ws.prepare(request)
                
                async def c2u():
                    try:
                        async for msg in ws:
                            if msg.type == aiohttp.WSMsgType.TEXT:   
                                await ups.send_str(msg.data)
                            elif msg.type == aiohttp.WSMsgType.BINARY: 
                                await ups.send_bytes(msg.data)
                            elif msg.type == aiohttp.WSMsgType.CLOSE:
                                break
                    except Exception as e:
                        logger.error(f"客户端到上游错误: {e}")
                
                async def u2c():
                    try:
                        async for msg in ups:
                            if msg.type == aiohttp.WSMsgType.TEXT:   
                                await ws.send_str(msg.data)
                            elif msg.type == aiohttp.WSMsgType.BINARY: 
                                await ws.send_bytes(msg.data)
                            elif msg.type == aiohttp.WSMsgType.CLOSE:
                                break
                    except Exception as e:
                        logger.error(f"上游到客户端错误: {e}")
                
                await asyncio.gather(c2u(), u2c(), return_exceptions=True)
                return ws
    except Exception as e:
        logger.error(f"WebSocket代理错误: {e}")
        raise

async def handler(request):
    logger.info(f"代理请求: {request.method} {request.path}")
    if request.headers.get("Upgrade","").lower() == "websocket":
        return await proxy_ws(request)
    return await proxy_http(request)

print("CDP代理启动中，监听端口 9223...")
app = web.Application()
app.router.add_route('*', '/{tail:.*}', handler)
web.run_app(app, host='0.0.0.0', port=9223)
"""
        print("安装 aiohttp 并启动 9223 代理…")
        
        # 检测 Python 命令
        python_check = self.desk.commands.run("which python3 || which python || echo 'NONE'", timeout=10)
        python_cmd = python_check.stdout.strip()
        if python_cmd == 'NONE' or not python_cmd:
            raise RuntimeError("沙盒内未找到 Python 解释器")
        print(f"使用 Python 解释器: {python_cmd}")
        
        # 安装依赖
        pip_check = self.desk.commands.run("which pip3 || which pip || echo 'NONE'", timeout=10)
        pip_cmd = pip_check.stdout.strip()
        if pip_cmd == 'NONE' or not pip_cmd:
            print("未找到 pip，尝试使用 python -m pip")
            pip_cmd = f"{python_cmd} -m pip"
        
        self.desk.commands.run(f"{pip_cmd} install -q aiohttp", timeout=600)
        self.desk.files.write("/home/user/cdp_proxy.py", proxy_code)
        self.desk.commands.run(
            f"{python_cmd} /home/user/cdp_proxy.py >/home/user/cdp_proxy.out 2>&1 &",
            background=True,
        )
        
        # 等待代理启动并验证
        print("等待代理启动...")
        proxy_started = False
        for i in range(15):  # 最多等待15秒
            time.sleep(1)
            
            # 检查代理进程是否运行
            proc_check = self.desk.commands.run("ps aux | grep cdp_proxy.py | grep -v grep | wc -l", timeout=5)
            proc_count = proc_check.stdout.strip()
            
            # 检查端口是否监听
            port_check = self.desk.commands.run("netstat -tlnp | grep 9223 | wc -l", timeout=5)
            port_count = port_check.stdout.strip()
            
            # 尝试连接
            result = self.desk.commands.run("curl -s -m 3 http://localhost:9223/json/version || echo 'FAILED'", timeout=5)
            
            print(f"代理状态检查 (尝试 {i+1}/15): 进程={proc_count}, 端口={port_count}")
            
            if "FAILED" not in result.stdout and "Browser" in result.stdout:
                print(f"✅ 代理验证成功 (尝试 {i+1}/15)")
                proxy_started = True
                break
            elif proc_count == "0":
                # 代理进程没有启动，检查错误
                log_result = self.desk.commands.run("cat /home/user/cdp_proxy.out 2>/dev/null || echo '暂无日志'", timeout=5)
                print(f"代理进程未启动，错误信息: {log_result.stdout}")
                break
            else:
                print(f"代理尚未就绪，继续等待... (尝试 {i+1}/15)")
        
        if not proxy_started:
            # 显示详细错误信息
            print("\n❌ 代理启动失败，详细诊断:")
            log_result = self.desk.commands.run("cat /home/user/cdp_proxy.out 2>/dev/null || echo '暂无日志文件'", timeout=5)
            print("代理完整日志:", log_result.stdout)
            
            proc_result = self.desk.commands.run("ps aux | grep python", timeout=5)
            print("Python进程:", proc_result.stdout)
            
            print("⚠️  代理未成功启动，但将继续尝试...")
        else:
            print(f"✅ CDP 代理已启动：0.0.0.0:{self.PROXY_PORT} → 127.0.0.1:{self.CHROME_PORT}")
        
        # 显示代理日志以供调试
        print("\n检查代理最新日志...")
        log_result = self.desk.commands.run("tail -5 /home/user/cdp_proxy.out 2>/dev/null || echo '暂无日志'", timeout=5)
        print("代理日志:", log_result.stdout)

    def get_external_cdp_base(self) -> str:
        """返回外网可访问的基础地址（给 /json/version 用）— 使用 9223。"""
        assert self.desk is not None
        
        # 确保端口被正确公开
        try:
            # 等待一下确保端口服务已经启动
            time.sleep(2)
            host = self.desk.get_host(self.PROXY_PORT)  # 公开代理端口
            base = f"https://{host}"
            print(f"使用 E2B 自动生成的 CDP 端点（代理）：{base}")
            
            # 测试端点是否可访问
            test_url = f"{base}/json/version"
            try:
                import urllib.request
                import ssl
                ssl._create_default_https_context = ssl._create_unverified_context
                with urllib.request.urlopen(test_url, timeout=5) as resp:
                    data = resp.read()
                    print(f"✅ 代理端点可访问，返回数据长度: {len(data)}")
            except Exception as e:
                print(f"⚠️  代理端点测试失败: {e}")
                
            return base
        except Exception as e:
            print(f"❌ 获取代理端点失败: {e}")
            raise
    
    def get_direct_chrome_base(self) -> str:
        """返回直接访问Chrome的外网地址（备用方案）"""
        assert self.desk is not None
        
        try:
            host = self.desk.get_host(self.CHROME_PORT)  # 公开Chrome端口
            base = f"https://{host}"
            print(f"备用方案 - 直接访问 Chrome CDP 端点：{base}")
            
            # 测试端点是否可访问
            test_url = f"{base}/json/version"
            try:
                import urllib.request
                import ssl
                ssl._create_default_https_context = ssl._create_unverified_context
                with urllib.request.urlopen(test_url, timeout=5) as resp:
                    data = resp.read()
                    print(f"✅ Chrome端点可访问，返回数据长度: {len(data)}")
            except Exception as e:
                print(f"⚠️  Chrome端点测试失败: {e}")
                
            return base
        except Exception as e:
            print(f"❌ 获取Chrome端点失败: {e}")
            raise
    
    def verify_services(self):
        """验证Chrome和代理服务是否正常运行。"""
        assert self.desk is not None
        
        print("\n=== 服务状态检查 ===")
        
        # 检查Chrome进程
        chrome_proc = self.desk.commands.run("ps aux | grep chrome | grep -v grep | wc -l", timeout=5)
        chrome_count = chrome_proc.stdout.strip()
        print(f"Chrome进程数: {chrome_count}")
        
        # 检查Chrome CDP端口
        chrome_port = self.desk.commands.run("netstat -tlnp | grep 9222 || echo 'Chrome CDP端口未监听'", timeout=5)
        print(f"Chrome CDP端口状态: {chrome_port.stdout.strip()}")
        
        # 检查代理进程
        proxy_proc = self.desk.commands.run("ps aux | grep cdp_proxy | grep -v grep | wc -l", timeout=5)
        proxy_count = proxy_proc.stdout.strip()
        print(f"代理进程数: {proxy_count}")
        
        # 检查代理端口
        proxy_port = self.desk.commands.run("netstat -tlnp | grep 9223 || echo '代理端口未监听'", timeout=5)
        print(f"代理端口状态: {proxy_port.stdout.strip()}")
        
        # 测试本地连接
        local_test = self.desk.commands.run("curl -s -m 5 http://localhost:9223/json/version || echo 'FAILED'", timeout=10)
        if "FAILED" not in local_test.stdout:
            print("✓ 本地代理连接正常")
        else:
            print("✗ 本地代理连接失败")
            
        print("==================\n")
