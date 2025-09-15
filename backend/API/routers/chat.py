from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from Agent.unified_agent import E2BUnifiedAgent

router = APIRouter(prefix="/api/chat", tags=["chat"])

# 数据模型定义
class MessageRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

class MessageResponse(BaseModel):
    success: bool
    message: str
    result: Optional[str] = None
    task: str
    error: Optional[str] = None

# 全局Agent实例将在main.py中注入
unified_agent: E2BUnifiedAgent = None

def init_chat_router(agent: E2BUnifiedAgent):
    """初始化chat router的agent实例"""
    global unified_agent
    unified_agent = agent

@router.post("/", response_model=MessageResponse)
async def chat_with_browser(request: MessageRequest):
    """发送消息给Browser Use执行任务"""
    try:
        # 检查是否有活跃的会话
        if not unified_agent.get_stream_url():
            raise HTTPException(status_code=400, detail="No active session. Please create a session first.")
        
        # 执行browser use任务
        result = await unified_agent.execute_task(request.message, request.context)
        
        if result["success"]:
            return MessageResponse(
                success=True,
                message=result["message"],
                result=result.get("result", ""),
                task=request.message
            )
        else:
            return MessageResponse(
                success=False,
                message=result.get("message", "Task execution failed"),
                error=result.get("error", "Unknown error"),
                task=request.message
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")