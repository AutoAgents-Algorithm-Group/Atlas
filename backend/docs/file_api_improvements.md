# File API 改进 - 解决 "No active sandbox session" 错误

## 问题描述

之前当没有活动的沙盒会话时，前端调用 `/api/files` 会收到错误：
```
Error: Failed to fetch files: "No active sandbox session"
```

这个错误会在浏览器控制台中显示，影响用户体验。

## 解决方案

### 1. 优雅的错误处理

现在 `/api/files` 端点会：
- **总是返回 `success: true`**（除非发生系统级错误）
- 当没有活动会话时，返回临时文件（如果有的话）
- 提供详细的状态信息和警告消息

### 2. 新的响应格式

```json
{
  "success": true,
  "files": [],
  "directory": "/home/user",
  "temp_files_count": 0,
  "sandbox_files_count": 0,
  "session_active": false,
  "warning": "No active session and no files available",
  "message": "Found 0 files (0 temp, 0 sandbox)"
}
```

### 3. 新增文件状态端点

`GET /api/files/status` - 快速检查文件系统状态：

```json
{
  "success": true,
  "session_active": false,
  "temp_files_available": false,
  "temp_files_count": 0,
  "stream_url": null,
  "message": "Session inactive, 0 temp files available"
}
```

## API 端点更新

### `GET /api/files/`
- 列出所有可用文件（沙盒文件 + 临时文件）
- 即使没有活动会话也会成功返回
- 包含详细的状态信息

### `GET /api/files/status` (新增)
- 快速检查文件系统和会话状态
- 轻量级端点，用于状态检查

### `GET /api/files/download?file_path=<path>`
- 下载指定文件
- 支持沙盒文件和临时文件

### `POST /api/files/add` (改进)
- 手动添加临时文件到列表
- 改进了错误处理

## 前端兼容性

这些改动完全向后兼容，前端代码无需修改。原有的错误处理逻辑仍然有效，但现在会收到更有用的信息：

```javascript
// 之前会抛出异常的情况现在会正常返回
const response = await fetch('/api/files');
const data = await response.json();

if (data.success) {
  // 总是会进入这个分支（除非系统错误）
  if (data.session_active) {
    console.log(`Found ${data.sandbox_files_count} sandbox files`);
  } else {
    console.log(`Session inactive, showing ${data.temp_files_count} temp files`);
    if (data.warning) {
      console.warn(data.warning);
    }
  }
  
  // 处理文件列表
  setSandboxFiles(data.files || []);
}
```

## 测试验证

可以通过以下命令测试新的行为：

```bash
# 测试文件状态
curl http://localhost:8100/api/files/status

# 测试文件列表（即使没有活动会话）
curl http://localhost:8100/api/files/

# 测试会话创建后的文件列表
curl -X POST http://localhost:8100/api/session/create
curl http://localhost:8100/api/files/
```

## 日志输出

后端会输出详细的调试信息：

```
📁 没有活动沙盒会话，返回 0 个临时文件
📋 文件列表API调用结果: 临时文件=0, 沙盒文件=0, 会话活跃=false
```

这样可以帮助开发者更好地理解系统状态。

