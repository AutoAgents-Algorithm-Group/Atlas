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

class EngineRequest(BaseModel):
    engine: str  # "browser-use" 或 "playwright"

class EngineResponse(BaseModel):
    success: bool
    engine: str
    message: Optional[str] = None
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

@router.get("/engine", response_model=EngineResponse)
async def get_browser_engine():
    """获取当前使用的浏览器引擎"""
    try:
        if not unified_agent:
            raise HTTPException(status_code=500, detail="Agent not initialized")
        
        engine_info = unified_agent.get_browser_engine()
        return EngineResponse(
            success=True,
            engine=engine_info["engine"],
            message=f"当前使用的浏览器引擎: {engine_info['engine']}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get engine: {str(e)}")

@router.post("/engine", response_model=EngineResponse)
async def set_browser_engine(request: EngineRequest):
    """设置浏览器引擎类型"""
    try:
        if not unified_agent:
            raise HTTPException(status_code=500, detail="Agent not initialized")
        
        result = unified_agent.set_browser_engine(request.engine)
        
        if result["success"]:
            return EngineResponse(
                success=True,
                engine=result["engine"],
                message=f"浏览器引擎已切换到: {result['engine']}"
            )
        else:
            return EngineResponse(
                success=False,
                engine=unified_agent.get_browser_engine()["engine"],
                error=result.get("error", "Unknown error")
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set engine: {str(e)}")

@router.post("/playwright", response_model=MessageResponse)
async def chat_with_playwright(request: MessageRequest):
    """使用Playwright引擎执行任务"""
    try:
        if not unified_agent:
            raise HTTPException(status_code=500, detail="Agent not initialized")
        
        # 检查是否有活跃的会话
        if not unified_agent.get_stream_url():
            raise HTTPException(status_code=400, detail="No active session. Please create a session first.")
        
        # 临时切换到Playwright引擎
        original_engine = unified_agent.get_browser_engine()["engine"]
        unified_agent.set_browser_engine("playwright")
        
        try:
            # 执行任务
            result = await unified_agent.execute_task(request.message, request.context)
            
            if result["success"]:
                return MessageResponse(
                    success=True,
                    message=f"[Playwright] {result['message']}",
                    result=result.get("result", ""),
                    task=request.message
                )
            else:
                return MessageResponse(
                    success=False,
                    message=f"[Playwright] {result.get('message', 'Task execution failed')}",
                    error=result.get("error", "Unknown error"),
                    task=request.message
                )
        finally:
            # 恢复原来的引擎
            unified_agent.set_browser_engine(original_engine)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/browser-use", response_model=MessageResponse)
async def chat_with_browser_use(request: MessageRequest):
    """使用Browser-Use引擎执行任务"""
    try:
        if not unified_agent:
            raise HTTPException(status_code=500, detail="Agent not initialized")
        
        # 检查是否有活跃的会话
        if not unified_agent.get_stream_url():
            raise HTTPException(status_code=400, detail="No active session. Please create a session first.")
        
        # 临时切换到Browser-Use引擎
        original_engine = unified_agent.get_browser_engine()["engine"]
        unified_agent.set_browser_engine("browser-use")
        
        try:
            # 执行任务
            result = await unified_agent.execute_task(request.message, request.context)
            
            if result["success"]:
                return MessageResponse(
                    success=True,
                    message=f"[Browser-Use] {result['message']}",
                    result=result.get("result", ""),
                    task=request.message
                )
            else:
                return MessageResponse(
                    success=False,
                    message=f"[Browser-Use] {result.get('message', 'Task execution failed')}",
                    error=result.get("error", "Unknown error"),
                    task=request.message
                )
        finally:
            # 恢复原来的引擎
            unified_agent.set_browser_engine(original_engine)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")