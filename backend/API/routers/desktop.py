from fastapi import APIRouter
from Agent.unified_agent import E2BUnifiedAgent

router = APIRouter(prefix="/api/desktop", tags=["desktop"])

# 全局Agent实例将在main.py中注入
unified_agent: E2BUnifiedAgent = None

def init_desktop_router(agent: E2BUnifiedAgent):
    """初始化desktop router的agent实例"""
    global unified_agent
    unified_agent = agent

@router.post("/takeover")
async def take_over_desktop():
    """接管桌面控制权"""
    try:
        result = unified_agent.take_over_desktop()
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to take over desktop"
        }

@router.post("/release")
async def release_desktop():
    """释放桌面控制权"""
    try:
        result = unified_agent.release_desktop()
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to release desktop"
        }