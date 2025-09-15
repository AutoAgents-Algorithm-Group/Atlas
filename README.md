# E2B Browser Use Chat

一个基于E2B云桌面的智能浏览器自动化聊天应用，使用自然语言与AI进行交互来控制浏览器操作。

## 🚀 功能特性

- **💬 聊天界面**: 现代化的聊天界面，通过对话控制浏览器
- **🖥️ 云桌面预览**: 实时预览E2B云桌面操作
- **🤖 Browser Use AI**: 使用自然语言控制浏览器自动化操作
- **🎯 智能任务执行**: AI自动理解并执行复杂的浏览器任务
- **🔄 Take Over功能**: 可切换只读模式和AI控制模式
- **📁 文件管理**: 查看和下载AI生成的文件
- **⏸️ 会话管理**: 支持暂停、恢复和销毁会话
- **🔧 自动配置**: 使用setup.sh脚本快速配置项目
- **📱 响应式布局**: 使用shadcn/ui的ResizablePanel设计

## 🏗️ 技术架构

### 后端 (FastAPI)
- **模块化API设计**: 使用APIRouter分离功能模块
- **统一Agent**: E2BUnifiedAgent整合桌面管理和浏览器自动化
- **会话管理**: 支持创建、暂停、恢复、销毁会话
- **文件操作**: browser-use生成文件的跟踪和下载

### 前端 (Next.js)
- **聊天界面**: 类ChatGPT的对话体验
- **分屏布局**: 左侧聊天，右侧桌面预览和文件管理
- **标签切换**: Computer和Files标签页
- **实时状态**: 显示会话状态和Take Over状态

### API模块结构
```
backend/API/
├── main.py              # 主应用和路由聚合
└── routers/
    ├── session.py       # 会话管理 (/api/session/*)
    ├── chat.py          # 聊天功能 (/api/chat)
    ├── files.py         # 文件操作 (/api/files/*)
    ├── desktop.py       # 桌面控制 (/api/desktop/*)
    └── system.py        # 系统信息 (/api/*)
```

## 📦 快速开始

### 1. 项目配置
```bash
# 使用setup.sh配置项目
./setup.sh
```

setup.sh脚本会引导您完成：
- 项目名称配置
- 前后端端口配置 (默认前端:3000, 后端:8000)
- 依赖安装

### 2. 启动开发环境
```bash
# 使用Makefile启动
make dev

# 或手动启动
cd backend && uvicorn API.main:app --host 0.0.0.0 --port 8000 --reload &
cd frontend && npm run dev
```

### 3. 访问应用
- 前端界面: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## 🎯 使用指南

### 基础操作流程
1. **启动会话**: 点击"Create Session"创建E2B桌面会话
2. **等待连接**: 右侧显示桌面预览画面
3. **发送消息**: 在聊天框中输入任务描述
4. **观察执行**: 在右侧预览窗口观看AI自动操作
5. **查看文件**: 切换到Files标签查看生成的文件
6. **Take Over**: 点击Take Over按钮可手动控制桌面

### Take Over 功能
- **View Only模式**: AI有完全控制权，用户只能观看
- **Controlled模式**: 用户接管控制，AI无法操作
- 状态切换通过Take Over/Release按钮控制

### 聊天示例
```
请帮我在Google上搜索"artificial intelligence"
打开GitHub，找到browser-use项目
访问www.example.com并截图保存
帮我下载这个页面的PDF文件
```

## 🔌 API端点

### 会话管理
- `POST /api/session/create` - 创建新会话
- `GET /api/session/status` - 获取会话状态
- `POST /api/session/pause` - 暂停会话
- `POST /api/session/resume` - 恢复会话
- `DELETE /api/session/destroy` - 销毁会话

### 聊天功能
- `POST /api/chat` - 发送聊天消息并执行任务

### 桌面控制
- `POST /api/desktop/takeover` - 接管桌面控制
- `POST /api/desktop/release` - 释放桌面控制

### 文件操作
- `GET /api/files/list` - 列出可用文件
- `GET /api/files/download/{file_path}` - 下载指定文件
- `POST /api/files/add` - 手动添加文件到跟踪列表

### 系统信息
- `GET /api/health` - 健康检查
- `GET /api/status` - 系统状态
- `GET /api/info` - 系统信息

## 🔧 配置文件

### 环境变量配置
项目使用 `frontend/.env.local` 配置环境变量：
```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### package.json端口配置
前端端口在 `frontend/package.json` 中配置：
```json
{
  "scripts": {
    "dev": "next dev --turbopack -p 3000"
  }
}
```

## 🛠️ 开发指南

### 目录结构
```
e2b-computer-use/
├── frontend/                # Next.js前端应用
│   ├── app/                # App Router页面
│   ├── components/         # UI组件库
│   ├── .env.example       # 环境变量模板
│   └── package.json       # 前端依赖和脚本
├── backend/                # FastAPI后端应用
│   ├── API/               # 模块化API结构
│   ├── Agent/             # 统一Agent实现
│   ├── Desktop/           # 桌面管理
│   ├── Engine/            # 浏览器运行引擎
│   └── requirements.txt   # 后端依赖
├── setup.sh               # 项目配置脚本
├── Makefile              # 构建和运行脚本
└── start.sh              # 启动脚本
```

### 添加新的API端点
1. 在 `backend/API/routers/` 中创建新的路由文件
2. 定义APIRouter和相关端点
3. 在 `backend/API/main.py` 中注册新路由

### 前端组件开发
- 使用shadcn/ui组件库
- 支持ResizablePanel布局
- 使用Next.js App Router

## 🌟 高级功能

### 文件跟踪机制
- 自动跟踪browser-use生成的临时文件
- 支持手动添加文件到跟踪列表
- 文件列表包含E2B沙箱文件和本地临时文件

### 会话持久化
- 支持暂停会话保留状态
- 可恢复之前暂停的会话
- 完全销毁会话释放资源

### 错误处理和重试
- WebSocket连接自动重连
- CDP协议异常处理
- 浏览器崩溃自动恢复

## 🐛 故障排除

### 常见问题
1. **502 Bad Gateway**: 检查CDP代理服务状态
2. **WebSocket超时**: 自动重连机制会处理
3. **端口冲突**: 使用setup.sh重新配置端口
4. **文件无法下载**: 检查文件权限和路径

### 调试模式
```bash
# 启动调试模式
cd backend && python -m uvicorn API.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

### 日志查看
- 后端日志: 控制台输出
- 前端日志: 浏览器开发者工具
- E2B沙箱日志: 通过API接口查看

## 🎉 快速启动

```bash
# 1. 克隆项目
git clone <repository>
cd e2b-computer-use

# 2. 配置项目
./setup.sh

# 3. 启动开发环境
make dev

# 4. 访问应用
open http://localhost:3000
```

享受AI驱动的浏览器自动化体验！🤖✨

## 📝 更新日志

### v2.0.0
- ✅ 重构为聊天界面
- ✅ 模块化API架构
- ✅ Take Over功能
- ✅ 文件管理和下载
- ✅ 会话管理优化
- ✅ setup.sh配置脚本
- ✅ 移除备份功能，简化配置

### v1.0.0
- ✅ 基础E2B桌面集成
- ✅ Browser Use AI集成
- ✅ VNC预览功能
- ✅ 应用启动按钮