from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from Agent.unified_agent import E2BUnifiedAgent

router = APIRouter(prefix="/api/session", tags=["session"])

# 数据模型定义
class SessionResponse(BaseModel):
    success: bool
    stream_url: str = None
    message: str
    error: str = None

# 全局Agent实例将在main.py中注入
unified_agent: E2BUnifiedAgent = None

def init_session_router(agent: E2BUnifiedAgent):
    """初始化session router的agent实例"""
    global unified_agent
    unified_agent = agent

@router.post("/create", response_model=SessionResponse)
async def create_session():
    """创建E2B浏览器会话"""
    try:
        result = unified_agent.create_desktop_session()
        if result["success"]:
            return SessionResponse(
                success=True,
                stream_url=result["stream_url"],
                message=result["message"]
            )
        else:
            raise HTTPException(status_code=500, detail=result.get("message", "Failed to create session"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/status")
async def get_session_status():
    """获取当前会话状态"""
    try:
        status = unified_agent.get_desktop_status()
        return {
            "success": status["success"],
            "active": status["active"],
            "initialized": status["initialized"],
            "stream_url": status["stream_url"],
            "message": "Session is active" if status["active"] else "No active session"
        }
    except Exception as e:
        return {
            "success": False,
            "active": False,
            "initialized": False,
            "message": f"Error checking status: {str(e)}"
        }

@router.delete("/close")
async def close_session():
    """暂停浏览器会话（保留沙盒）"""
    try:
        result = unified_agent.cleanup()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to pause session: {str(e)}")

@router.post("/resume")
async def resume_session():
    """恢复暂停的浏览器会话"""
    try:
        result = unified_agent.resume_session()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resume session: {str(e)}")

@router.delete("/terminate")
async def terminate_session():
    """彻底终止浏览器会话"""
    try:
        result = unified_agent.terminate_session()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to terminate session: {str(e)}")