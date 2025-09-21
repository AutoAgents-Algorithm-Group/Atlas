# 人工接管功能使用指南

## 🎯 功能概述

当浏览器自动化过程中检测到需要输入密码、验证码等需要人工干预的情况时，系统会：
1. 在聊天区域显示提示消息
2. 提供 "Take Over" 按钮
3. 点击按钮后切换到可操作模式 (`view_only=True`)
4. 用户完成操作后可关闭接管模式 (`view_only=False`)

## 🔧 核心功能

### 1. 智能检测系统

系统会在以下情况触发人工干预提示：

#### 任务关键词检测
```python
intervention_keywords = [
    "password", "密码", "验证码", "captcha", "verification", 
    "two-factor", "2fa", "otp", "sms code", "email verification",
    "手机验证", "邮箱验证", "短信验证", "身份验证"
]
```

#### 执行结果检测
```python
intervention_phrases = [
    "enter password", "input password", "verification code",
    "captcha", "human verification", "please verify",
    "输入密码", "请输入密码", "验证码", "人机验证"
]
```

#### 错误信息检测
```python
verification_errors = [
    "login failed", "authentication", "verification", 
    "登录失败", "身份验证", "验证失败"
]
```

### 2. 状态管理

```python
# Agent状态属性
self.takeover_active = False      # 是否处于人工接管状态
self.intervention_needed = False  # 是否需要人工干预
self.intervention_reason = ""     # 需要干预的原因
self.automation_paused = False    # 自动化是否暂停
```

### 3. 桌面模式切换

```python
# 只读模式 (默认)
view_only = False  # 用户无法操作桌面

# 可操作模式 (接管时)
view_only = True   # 用户可以手动操作桌面
```

## 🚀 API 端点

### 启用人工接管
```http
POST /api/takeover/enable
```

**响应示例:**
```json
{
  "success": true,
  "message": "人工接管模式已启用，您现在可以手动操作桌面",
  "takeover_active": true,
  "stream_url": "https://...",
  "instruction": "请在桌面上完成密码输入或验证码验证，完成后点击 '结束接管' 恢复自动化"
}
```

### 禁用人工接管
```http
POST /api/takeover/disable
```

**响应示例:**
```json
{
  "success": true,
  "message": "已恢复自动化模式，人工接管结束",
  "takeover_active": false,
  "stream_url": "https://...",
  "instruction": "现在可以继续使用聊天界面发送自动化指令"
}
```

### 获取接管状态
```http
GET /api/takeover/status
```

**响应示例:**
```json
{
  "success": true,
  "data": {
    "takeover_active": false,
    "intervention_needed": true,
    "intervention_reason": "检测到需要输入密码或验证码",
    "automation_paused": true,
    "session_active": true,
    "stream_url": "https://...",
    "view_only": false,
    "mode": "只读"
  }
}
```

### 清除干预状态
```http
POST /api/takeover/clear-intervention
```

### 测试干预检测
```http
POST /api/takeover/test-intervention
Content-Type: application/json

"请输入密码登录账号"
```

**响应示例:**
```json
{
  "success": true,
  "message": "请输入密码登录账号",
  "needs_intervention": true,
  "triggered_keywords": ["密码"],
  "suggestion": "建议启用人工接管模式"
}
```

## 💬 聊天消息示例

### 检测到需要干预时的响应

```json
{
  "success": false,
  "intervention_needed": true,
  "intervention_reason": "检测到需要输入密码或验证码，建议切换到人工操作模式",
  "message": "🔐 检测到需要人工干预的操作（密码/验证码），请点击 Take Over 按钮进行手动操作",
  "suggested_action": "takeover",
  "task": "登录Gmail账号"
}
```

### 执行过程中遇到验证页面

```json
{
  "success": true,
  "result": "页面显示需要输入验证码...",
  "intervention_needed": true,
  "intervention_reason": "执行过程中遇到需要人工验证的页面",
  "message": "🔐 任务执行中遇到验证页面，建议切换到人工操作模式",
  "suggested_action": "takeover"
}
```

## 🔄 使用流程

### 1. 正常自动化流程
```bash
# 用户发送消息
POST /api/chat
{
  "message": "导航到Google首页"
}

# 系统正常执行
{
  "success": true,
  "message": "Task completed successfully",
  "intervention_needed": false
}
```

### 2. 触发人工干预流程

```bash
# 用户发送需要验证的任务
POST /api/chat
{
  "message": "登录Gmail并输入密码"
}

# 系统检测到需要干预
{
  "success": false,
  "intervention_needed": true,
  "message": "🔐 检测到需要人工干预的操作（密码/验证码），请点击 Take Over 按钮进行手动操作",
  "suggested_action": "takeover"
}

# 前端显示Take Over按钮，用户点击
POST /api/takeover/enable

# 系统切换到可操作模式
{
  "success": true,
  "message": "人工接管模式已启用，您现在可以手动操作桌面",
  "takeover_active": true
}

# 用户在桌面上手动完成密码输入
# 完成后点击结束接管按钮
POST /api/takeover/disable

# 系统恢复自动化模式
{
  "success": true,
  "message": "已恢复自动化模式，人工接管结束",
  "takeover_active": false
}
```

## 🎨 前端集成建议

### 1. 聊天消息处理
```javascript
// 处理聊天响应
if (response.intervention_needed) {
  // 显示特殊的干预提示消息
  showInterventionMessage(response.message, response.intervention_reason);
  
  // 显示Take Over按钮
  showTakeOverButton();
}
```

### 2. Take Over按钮
```javascript
// 启用接管
async function enableTakeover() {
  const response = await fetch('/api/takeover/enable', {
    method: 'POST'
  });
  const result = await response.json();
  
  if (result.success) {
    // 更新UI状态
    updateTakeoverStatus(true);
    // 更新stream URL
    updateDesktopStream(result.stream_url);
    // 显示结束接管按钮
    showEndTakeoverButton();
  }
}

// 禁用接管
async function disableTakeover() {
  const response = await fetch('/api/takeover/disable', {
    method: 'POST'
  });
  const result = await response.json();
  
  if (result.success) {
    // 更新UI状态
    updateTakeoverStatus(false);
    // 更新stream URL
    updateDesktopStream(result.stream_url);
    // 隐藏结束接管按钮
    hideEndTakeoverButton();
  }
}
```

### 3. 状态监控
```javascript
// 定期检查接管状态
setInterval(async () => {
  const response = await fetch('/api/takeover/status');
  const result = await response.json();
  
  if (result.success) {
    updateTakeoverUI(result.data);
  }
}, 5000);
```

## 🧪 测试命令

```bash
# 启动服务器
cd /Users/forhheart/AIGC/Atlas/backend
python -m API.main

# 测试干预检测
curl -X POST http://localhost:8100/api/takeover/test-intervention \
  -H "Content-Type: application/json" \
  -d '"请输入验证码"'

# 测试启用接管
curl -X POST http://localhost:8100/api/takeover/enable

# 查看状态
curl http://localhost:8100/api/takeover/status

# 测试禁用接管
curl -X POST http://localhost:8100/api/takeover/disable
```

## 📝 注意事项

1. **安全性**: 接管模式下用户可以完全控制桌面，需要确保只在必要时启用
2. **状态同步**: 前端需要实时监控接管状态变化
3. **错误处理**: 如果桌面会话不存在，接管功能将无法使用
4. **用户体验**: 建议在干预消息中提供清晰的操作指导

## 🔮 扩展可能性

1. **自定义关键词**: 允许用户配置触发干预的关键词
2. **智能暂停**: 检测到特定页面元素时自动暂停
3. **操作录制**: 记录用户的手动操作以供后续自动化
4. **多模式切换**: 支持半自动模式（部分操作需要确认）

这个人工接管功能为复杂的身份验证场景提供了完美的解决方案！🎉
