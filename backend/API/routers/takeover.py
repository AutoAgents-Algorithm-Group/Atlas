from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from Agent.unified_agent import E2BUnifiedAgent

router = APIRouter(prefix="/api/takeover", tags=["takeover"])

# 全局Agent实例将在main.py中注入
unified_agent: E2BUnifiedAgent = None

def init_takeover_router(agent: E2BUnifiedAgent):
    """初始化takeover router的agent实例"""
    global unified_agent
    unified_agent = agent

class TakeoverRequest(BaseModel):
    action: str  # "enable" or "disable"
    reason: Optional[str] = None

@router.post("/enable")
async def enable_takeover():
    """
    启用人工接管模式
    设置view_only=True，允许用户手动操作桌面
    """
    try:
        if not unified_agent:
            raise HTTPException(status_code=500, detail="Agent not initialized")
        
        result = unified_agent.enable_takeover()
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/disable")
async def disable_takeover():
    """
    禁用人工接管模式
    设置view_only=False，恢复只读模式
    """
    try:
        if not unified_agent:
            raise HTTPException(status_code=500, detail="Agent not initialized")
        
        result = unified_agent.disable_takeover()
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_takeover_status():
    """
    获取当前的接管状态
    """
    try:
        if not unified_agent:
            raise HTTPException(status_code=500, detail="Agent not initialized")
        
        status = unified_agent.get_takeover_status()
        
        # 添加额外的状态信息
        if unified_agent.desktop_manager and hasattr(unified_agent.desktop_manager, 'get_current_view_only_status'):
            view_status = unified_agent.desktop_manager.get_current_view_only_status()
            status.update(view_status)
        
        return {
            "success": True,
            "data": status
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clear-intervention")
async def clear_intervention():
    """
    清除干预状态，但保持当前的接管模式
    """
    try:
        if not unified_agent:
            raise HTTPException(status_code=500, detail="Agent not initialized")
        
        result = unified_agent.clear_intervention_state()
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/intervention-keywords")
async def get_intervention_keywords():
    """
    获取触发人工干预的关键词列表
    """
    try:
        keywords = {
            "password_keywords": [
                "password", "密码", "验证码", "captcha", "verification", 
                "two-factor", "2fa", "otp", "sms code", "email verification",
                "手机验证", "邮箱验证", "短信验证", "身份验证", "两步验证", "双重验证"
            ],
            "result_phrases": [
                "enter password", "input password", "verification code",
                "captcha", "human verification", "please verify",
                "输入密码", "请输入密码", "验证码", "人机验证"
            ],
            "error_phrases": [
                "login failed", "authentication", "verification", 
                "登录失败", "身份验证", "验证失败"
            ]
        }
        
        return {
            "success": True,
            "data": keywords,
            "message": "这些关键词会触发人工干预提示"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-intervention")
async def test_intervention(message: str):
    """
    测试消息是否会触发人工干预检测
    """
    try:
        intervention_keywords = [
            "password", "密码", "验证码", "captcha", "verification", 
            "two-factor", "2fa", "otp", "sms code", "email verification",
            "手机验证", "邮箱验证", "短信验证", "身份验证", "两步验证", "双重验证"
        ]
        
        message_lower = message.lower()
        triggered_keywords = [kw for kw in intervention_keywords if kw in message_lower]
        needs_intervention = len(triggered_keywords) > 0
        
        return {
            "success": True,
            "message": message,
            "needs_intervention": needs_intervention,
            "triggered_keywords": triggered_keywords,
            "suggestion": "建议启用人工接管模式" if needs_intervention else "可以使用自动化模式"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
