from fastapi import APIRouter, HTTPException
from Agent.unified_agent import E2BUnifiedAgent

router = APIRouter(prefix="/api", tags=["system"])

# 全局Agent实例将在main.py中注入
unified_agent: E2BUnifiedAgent = None

def init_system_router(agent: E2BUnifiedAgent):
    """初始化system router的agent实例"""
    global unified_agent
    unified_agent = agent

@router.get("/status")
async def get_status():
    """获取系统整体状态"""
    try:
        has_session = unified_agent.get_stream_url() is not None
        is_initialized = unified_agent._initialized
        stream_url = unified_agent.get_stream_url()
        
        return {
            "success": True,
            "session_active": has_session,
            "agent_ready": is_initialized,
            "stream_url": stream_url,
            "message": "Browser Use agent is ready" if is_initialized else "Session required"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

@router.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy", 
        "message": "Browser Use API is running normally",
        "version": "2.0.0",
        "architecture": "Simplified Chat Interface",
        "features": [
            "Chat-based browser automation", 
            "E2B sandbox integration",
            "WebSocket CDP connection",
            "Natural language task execution"
        ]
    }

@router.get("/info")
async def system_info():
    """系统信息端点"""
    try:
        has_session = unified_agent.get_stream_url() is not None
        is_initialized = unified_agent._initialized
        
        return {
            "success": True,
            "system": "E2B Browser Use Platform",
            "architecture": "Chat-based Interface", 
            "status": {
                "session_active": has_session,
                "agent_ready": is_initialized,
                "stream_url": unified_agent.get_stream_url()
            },
            "workflow": [
                "1. Create session (/api/session/create)",
                "2. Send messages (/api/chat)",
                "3. View live desktop via stream_url",
                "4. Close session (/api/session/close)"
            ]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to get system information"
        }