from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from Agent.unified_agent import E2BUnifiedAgent

router = APIRouter(prefix="/api/files", tags=["files"])

# 全局Agent实例将在main.py中注入
unified_agent: E2BUnifiedAgent = None

def init_files_router(agent: E2BUnifiedAgent):
    """初始化files router的agent实例"""
    global unified_agent
    unified_agent = agent

@router.get("/")
async def list_files():
    """列出沙盒中的文件"""
    try:
        if not unified_agent:
            return {
                "success": False,
                "error": "Agent not initialized",
                "files": [],
                "temp_files_count": 0,
                "session_active": False
            }
        
        # 获取文件列表
        result = unified_agent.list_sandbox_files()
        
        # 添加调试信息
        temp_files_count = result.get("temp_files_count", 0)
        sandbox_files_count = result.get("sandbox_files_count", 0)
        session_active = result.get("session_active", False)
        
        print(f"📋 文件列表API调用结果: 临时文件={temp_files_count}, 沙盒文件={sandbox_files_count}, 会话活跃={session_active}")
        
        # 确保返回的格式是一致的
        return {
            "success": result.get("success", True),
            "files": result.get("files", []),
            "directory": result.get("directory", "/home/user"),
            "temp_files_count": temp_files_count,
            "sandbox_files_count": sandbox_files_count,
            "session_active": session_active,
            "warning": result.get("warning"),
            "message": f"Found {len(result.get('files', []))} files ({temp_files_count} temp, {sandbox_files_count} sandbox)"
        }
        
    except Exception as e:
        print(f"❌ 文件列表API异常: {e}")
        return {
            "success": False,
            "error": str(e),
            "files": [],
            "temp_files_count": 0,
            "sandbox_files_count": 0,
            "session_active": False,
            "message": f"Failed to list files: {str(e)}"
        }

@router.get("/download")
async def download_file(file_path: str):
    """下载沙盒中的文件"""
    try:
        result = unified_agent.download_sandbox_file(file_path)
        
        if result["success"]:
            content = result["content"]
            filename = result["filename"]
            
            # 根据文件扩展名设置Content-Type
            content_type = "text/plain"
            if filename.endswith(".md"):
                content_type = "text/markdown"
            elif filename.endswith(".json"):
                content_type = "application/json"
            elif filename.endswith(".csv"):
                content_type = "text/csv"
            elif filename.endswith(".html"):
                content_type = "text/html"
            
            return Response(
                content=content,
                media_type=content_type,
                headers={
                    "Content-Disposition": f"attachment; filename={filename}"
                }
            )
        else:
            raise HTTPException(status_code=404, detail=result["error"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_files_status():
    """获取文件系统状态"""
    try:
        if not unified_agent:
            return {
                "success": False,
                "error": "Agent not initialized",
                "session_active": False,
                "temp_files_available": False
            }
        
        # 检查沙盒会话状态
        session_active = bool(unified_agent.desktop_manager and unified_agent.desktop_manager.desk)
        temp_files_count = len(unified_agent._temp_files)
        
        return {
            "success": True,
            "session_active": session_active,
            "temp_files_available": temp_files_count > 0,
            "temp_files_count": temp_files_count,
            "stream_url": unified_agent.get_stream_url(),
            "message": f"Session {'active' if session_active else 'inactive'}, {temp_files_count} temp files available"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "session_active": False,
            "temp_files_available": False
        }

@router.post("/add")
async def add_temp_file(file_path: str):
    """手动添加临时文件到文件列表"""
    try:
        if not unified_agent:
            return {
                "success": False,
                "error": "Agent not initialized",
                "message": "Agent is not available"
            }
        
        success = unified_agent.add_temp_file_manually(file_path)
        if success:
            return {
                "success": True,
                "message": f"File added successfully: {file_path}"
            }
        else:
            return {
                "success": False,
                "error": "Failed to add file",
                "message": "File may not exist or already in the list"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to add temp file"
        }