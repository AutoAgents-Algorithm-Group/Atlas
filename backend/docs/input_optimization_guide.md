# 输入优化指南 - 解决文本输入超时问题

## 问题背景

在使用浏览器自动化时，经常遇到文本输入超时的问题，特别是：
- 在搜索框输入长文本时出现搜索建议下拉框导致的15秒超时
- TypeTextEvent的watchdog超时错误
- 网络延迟或DOM不稳定造成的输入中断

## 解决方案

我们开发了增强版的输入系统，提供多种输入策略来应对不同场景：

### 1. 增强默认策略 (`enhanced`)

**适用场景：** 大多数搜索框和表单输入

**特点：**
- 快速一次性输入完整文本
- 自动处理搜索建议下拉框干扰
- 优化的超时设置 (30秒动作超时，25秒watchdog超时)
- 输入完成后自动按ESC键关闭下拉框

### 2. 分段输入策略 (`chunked`)

**适用场景：** 超长文本输入，网络延迟较高的环境

**特点：**
- 将长文本分割成小段(默认10个字符)逐步输入
- 每段之间有短暂延迟避免触发超时
- 适合处理复杂表单和超长查询

### 3. 粘贴策略 (`paste`)

**适用场景：** 代码输入，格式化文本，多行文本

**特点：**
- 使用剪贴板粘贴整个文本
- 最快的输入方式
- 避免逐字符输入的所有问题

## 使用方法

### API接口

#### 1. 获取当前输入配置
```http
GET /api/input/config
```

响应示例：
```json
{
  "success": true,
  "data": {
    "use_enhanced_input": true,
    "input_strategy": "enhanced",
    "available_strategies": ["enhanced", "chunked", "paste"],
    "strategy_descriptions": {
      "enhanced": "增强默认策略，快速输入并处理搜索建议干扰",
      "chunked": "分段输入策略，将长文本分割成小段输入",
      "paste": "粘贴策略，使用剪贴板粘贴整个文本"
    }
  }
}
```

#### 2. 设置输入策略
```http
POST /api/input/strategy
Content-Type: application/json

{
  "strategy": "enhanced"
}
```

#### 3. 切换增强输入功能
```http
POST /api/input/toggle-enhanced
Content-Type: application/json

{
  "enabled": true
}
```

#### 4. 获取所有可用策略
```http
GET /api/input/strategies
```

#### 5. 测试输入策略
```http
POST /api/input/test-strategy?strategy=enhanced
```

### 代码使用示例

```python
from Agent.unified_agent import E2BUnifiedAgent

# 创建启用增强输入的Agent
agent = E2BUnifiedAgent(
    use_enhanced_input=True,
    input_strategy="enhanced"
)

# 动态切换输入策略
agent.set_input_strategy("chunked")

# 执行任务时会自动使用配置的输入策略
result = await agent.execute_task("在Google搜索框中输入 'artificial intelligence machine learning deep learning neural networks'")
```

## 策略选择建议

### 🎯 推荐使用场景

| 输入内容 | 推荐策略 | 原因 |
|---------|---------|------|
| 短查询词(1-20字符) | `enhanced` | 快速输入，处理下拉框 |
| 长查询句(20-100字符) | `enhanced` | 一次性输入，避免中断 |
| 超长文本(100+字符) | `chunked` | 分段输入避免超时 |
| 代码片段 | `paste` | 保持格式，避免语法错误 |
| 多行文本 | `paste` | 处理换行符，保持结构 |
| 表单填写 | `enhanced` | 快速完成，处理验证 |

### ⚠️ 故障排除

如果遇到输入问题：

1. **超时错误：** 切换到 `chunked` 策略
2. **下拉框干扰：** 使用 `enhanced` 策略
3. **格式丢失：** 选择 `paste` 策略
4. **网络延迟：** 降低分段大小或使用 `paste`

## 技术实现

### 增强配置参数

```python
{
    'action_timeout': 30,        # 动作超时时间(秒)
    'watchdog_timeout': 25,      # watchdog超时时间(秒)
    'input_delay': 50,           # 输入延迟(毫秒)
    'wait_for_stable_dom': True, # 等待DOM稳定
    'disable_web_security': True # 禁用web安全限制
}
```

### 自动策略切换

系统会根据错误类型自动调整策略：
- 检测到超时错误 → 切换到分段输入
- 分段输入仍失败 → 切换到粘贴策略
- 提供详细的错误反馈和建议

## 监控和调试

### 日志输出示例

```
🚀 使用增强输入策略: enhanced
🎯 使用增强输入策略输入文本: artificial intelligence...
📝 使用分段输入策略，文本长度: 50, 分段大小: 10
✅ 增强默认输入完成
```

### 错误处理

```json
{
  "success": false,
  "error": "Input timeout",
  "message": "文本输入超时。建议尝试切换输入策略：当前为 enhanced，可尝试 chunked 或 paste 策略。",
  "suggestion": "try_different_input_strategy"
}
```

## 更新日志

- **v1.0.0** - 基础增强输入系统
- **v1.1.0** - 添加分段和粘贴策略
- **v1.2.0** - 自动策略切换和错误处理
- **v1.3.0** - API接口和配置管理

通过这些优化，您现在可以可靠地进行一次性完整文本输入，而不再受到搜索建议下拉框或超时问题的困扰。

