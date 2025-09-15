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
        # 添加调试信息
        temp_files_count = len(unified_agent._temp_files)
        print(f"调试：当前临时文件数量: {temp_files_count}")
        
        result = unified_agent.list_sandbox_files()
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "files": []
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

@router.post("/add")
async def add_temp_file(file_path: str):
    """手动添加临时文件到文件列表"""
    try:
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