# Playwright Engine 使用指南

## 概述

Atlas 项目现在支持两种浏览器自动化引擎：

1. **Browser-Use** (默认) - 使用 browser-use 框架
2. **Playwright** (新增) - 使用 Microsoft Playwright 框架

## 功能特性

### Playwright Engine 优势

- 🚀 **更高的稳定性** - Playwright 提供更可靠的浏览器自动化
- 🎯 **精确的元素定位** - 支持多种选择器策略
- 🔧 **灵活的错误处理** - 内置重试和恢复机制
- 🌐 **跨浏览器支持** - 支持 Chrome、Firefox、Safari 等
- 🤖 **AI 驱动** - 集成 OpenAI 模型进行智能操作决策

### 核心特性

- **自然语言任务执行** - 支持中英文任务描述
- **智能页面分析** - 自动识别可交互元素
- **动态操作决策** - AI 分析页面状态并选择最佳操作
- **错误恢复机制** - 自动处理网络超时和连接问题
- **资源管理** - 自动清理浏览器资源

## 使用方法

### 1. 在 UnifiedAgent 中使用

```python
from Agent.unified_agent import E2BUnifiedAgent

# 创建使用 Playwright 的 agent
agent = E2BUnifiedAgent(browser_engine="playwright")

# 或在运行时切换
agent.set_browser_engine("playwright")
```

### 2. 直接使用 PlaywrightEngine

```python
from Engine.playwright_engine import PlaywrightEngine

engine = PlaywrightEngine(
    task="搜索 'OpenAI GPT-4' 并总结结果",
    external_cdp_base="https://your-e2b-session.e2b.dev:9223",
    backup_chrome_base="https://your-e2b-session.e2b.dev:9222",
    model="gpt-4o"
)

result = engine.run()
```

### 3. 通过 API 使用

#### 获取当前引擎

```bash
curl -X GET "http://localhost:8000/api/chat/engine"
```

#### 切换引擎

```bash
curl -X POST "http://localhost:8000/api/chat/engine" \
  -H "Content-Type: application/json" \
  -d '{"engine": "playwright"}'
```

#### 使用 Playwright 执行任务

```bash
curl -X POST "http://localhost:8000/api/chat/playwright" \
  -H "Content-Type: application/json" \
  -d '{"message": "访问百度并搜索人工智能"}'
```

#### 使用 Browser-Use 执行任务

```bash
curl -X POST "http://localhost:8000/api/chat/browser-use" \
  -H "Content-Type: application/json" \
  -d '{"message": "访问 GitHub 搜索 FastAPI"}'
```

## API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/chat/engine` | GET | 获取当前浏览器引擎 |
| `/api/chat/engine` | POST | 设置浏览器引擎 |
| `/api/chat/playwright` | POST | 使用 Playwright 执行任务 |
| `/api/chat/browser-use` | POST | 使用 Browser-Use 执行任务 |
| `/api/chat/` | POST | 使用默认引擎执行任务 |

## 配置选项

### 环境变量

```bash
# OpenAI API 配置
OPENAI_API_KEY=sk-your-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
BROWSER_USE_MODEL=gpt-4o
```

### PlaywrightEngine 参数

```python
PlaywrightEngine(
    task="任务描述",
    external_cdp_base="CDP代理端点",
    backup_chrome_base="直连Chrome端点",
    model="gpt-4o",          # AI模型
    headless=False,          # 是否无头模式
)
```

### 高级配置

```python
# 自定义步骤设置
engine.max_steps = 30        # 最大执行步骤
engine.step_delay = 1.0      # 步骤间延迟(秒)
```

## 故障排除

### 常见问题

1. **连接失败**
   ```
   ❌ 所有连接方案都失败了！
   ```
   **解决方案**: 
   - 检查 E2B 会话是否正常运行
   - 确保端口 9222 和 9223 设置为 Public
   - 验证 Chrome 和 CDP 代理服务已启动

2. **AI 调用失败**
   ```
   ❌ AI决策失败: Invalid API key
   ```
   **解决方案**: 
   - 检查 `OPENAI_API_KEY` 环境变量
   - 验证 API 密钥有效性
   - 检查 `OPENAI_BASE_URL` 配置

3. **任务执行超时**
   ```
   ❌ 执行操作失败: Timeout
   ```
   **解决方案**: 
   - 增加 `step_delay` 延迟
   - 检查网络连接稳定性
   - 简化任务描述

### 调试模式

```python
# 启用详细日志
engine = PlaywrightEngine(
    task="your task",
    external_cdp_base="...",
    backup_chrome_base="...",
)

# 手动设置最大步骤
engine.max_steps = 10
```

## 性能优化

### 建议配置

1. **网络优化**
   - 使用稳定的网络连接
   - 配置适当的超时时间
   - 启用 CDP 代理以提高稳定性

2. **任务设计**
   - 使用清晰、具体的任务描述
   - 将复杂任务分解为简单步骤
   - 避免需要大量交互的任务

3. **资源管理**
   - 及时调用 `stop()` 方法停止任务
   - 定期检查和清理浏览器资源
   - 避免长时间运行任务

## 与 Browser-Use 的比较

| 特性 | Playwright Engine | Browser-Use |
|------|------------------|-------------|
| 稳定性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 性能 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 易用性 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 可定制性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 错误处理 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

## 最佳实践

1. **引擎选择**
   - 对于稳定性要求高的任务，使用 Playwright
   - 对于快速原型和简单任务，使用 Browser-Use

2. **任务设计**
   - 使用自然语言描述任务
   - 提供具体的目标和期望结果
   - 避免模糊或歧义的指令

3. **错误处理**
   - 实现适当的重试机制
   - 监控任务执行状态
   - 提供用户友好的错误消息

## 更新日志

### v1.0.0 (2024-12-XX)
- ✨ 初始发布 Playwright Engine
- 🔧 集成到 UnifiedAgent 系统
- 📝 添加 API 端点支持
- 🤖 支持 AI 驱动的任务执行
- 🛡️ 完整的错误处理和重试机制

