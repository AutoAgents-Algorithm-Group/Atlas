from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Agent.unified_agent import E2BUnifiedAgent
from . import (
    session_router, init_session_router,
    chat_router, init_chat_router,
    files_router, init_files_router,
    desktop_router, init_desktop_router,
    system_router, init_system_router
)
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
    allow_origins=["http://localhost:3100", "http://127.0.0.1:3100"],  # Next.js默认端口
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局统一Agent实例 (整合了桌面管理和浏览器自动化)
unified_agent = E2BUnifiedAgent(resolution=(1440, 900), dpi=96)

# 初始化所有router的agent实例
init_session_router(unified_agent)
init_chat_router(unified_agent)
init_files_router(unified_agent)
init_desktop_router(unified_agent)
init_system_router(unified_agent)

# 注册路由器
app.include_router(session_router)
app.include_router(chat_router)
app.include_router(files_router)
app.include_router(desktop_router)
app.include_router(system_router)

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
            "system": "/api/status, /api/health, /api/info"
        }
    }

if __name__ == "__main__":
    uvicorn.run("API.main:app", host="0.0.0.0", port=8100, reload=True)