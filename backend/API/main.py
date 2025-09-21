from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Agent.unified_agent import E2BUnifiedAgent

# 加载环境变量
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    # 尝试从backend目录加载.env文件
    backend_env_path = Path(__file__).parent.parent / '.env'
    # 也尝试从项目根目录加载.env文件作为备选
    root_env_path = Path(__file__).parent.parent.parent / '.env'
    
    if backend_env_path.exists():
        load_dotenv(backend_env_path)
        print(f"✅ 已加载环境变量文件: {backend_env_path}")
    elif root_env_path.exists():
        load_dotenv(root_env_path)
        print(f"✅ 已加载环境变量文件: {root_env_path}")
    else:
        print(f"⚠️ 未找到.env文件，查找路径:")
        print(f"   - {backend_env_path}")
        print(f"   - {root_env_path}")
        print("💡 您可以在backend目录下创建.env文件来配置环境变量")
except ImportError:
    print("⚠️ python-dotenv未安装，请运行: pip install python-dotenv")
except Exception as e:
    print(f"⚠️ 加载.env文件时出错: {e}")
from . import (
    session_router, init_session_router,
    chat_router, init_chat_router,
    files_router, init_files_router,
    desktop_router, init_desktop_router,
    system_router, init_system_router
)
from .routers.takeover import router as takeover_router, init_takeover_router
import uvicorn

# 创建FastAPI应用
app = FastAPI(
    title="E2B Browser Use API", 
    version="1.0.0",
    description="Modular API for E2B Browser Use with organized router structure"
)

# CORS设置，允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3100", 
        "http://127.0.0.1:3100", 
        "http://45.78.224.30:3100", 
        "https://atlas.agentspro.cn"
    ],  # Next.js默认端口
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局统一Agent实例 (整合了桌面管理和浏览器自动化)
# 使用标准Browser Use，启用highlight功能
unified_agent = E2BUnifiedAgent(
    resolution=(1440, 900), 
    dpi=96
)

# 初始化所有router的agent实例
init_session_router(unified_agent)
init_chat_router(unified_agent)
init_files_router(unified_agent)
init_desktop_router(unified_agent)
init_system_router(unified_agent)
init_takeover_router(unified_agent)

# 注册路由器
app.include_router(session_router)
app.include_router(chat_router)
app.include_router(files_router)
app.include_router(desktop_router)
app.include_router(system_router)
app.include_router(takeover_router)

# 根路由
@app.get("/")
async def root():
    return {
        "message": "E2B Browser Use API is running",
        "version": "2.0.0",
        "architecture": "Modular Router Structure",
        "available_endpoints": {
            "session": "/api/session/*",
            "chat": "/api/chat/*", 
            "files": "/api/files/*",
            "desktop": "/api/desktop/*",
            "system": "/api/status, /api/health, /api/info",
            "takeover": "/api/takeover/*"
        }
    }

if __name__ == "__main__":
    uvicorn.run("API.main:app", host="0.0.0.0", port=8100, reload=True)