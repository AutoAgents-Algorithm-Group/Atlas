# Atlas - AI Browser Controller

一个基于 E2B 云桌面的智能浏览器自动化聊天应用，使用自然语言与 AI 进行交互来控制浏览器操作。

## 📋 Table of Contents

- [🤖 About & Features](#-about--features)
- [🚀 Quick Start](#-quick-start)
- [🏗️ Architecture](#️-architecture)
- [🐳 Deployment](#-deployment)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

## 🤖 About & Features

Atlas 是一个革命性的 AI 浏览器控制器，让你可以通过自然语言对话来操控浏览器。基于 E2B 云桌面技术，Atlas 提供了安全、隔离的浏览器自动化环境，支持复杂的 Web 操作任务。

### 🎯 核心特性

#### 🤖 AI-Powered Browser Automation
- **🗣️ 自然语言控制**：通过聊天对话控制浏览器操作，零编程门槛
- **🛡️ E2B 云桌面**：安全隔离的云环境进行浏览器自动化
- **👀 实时预览**：通过桌面流观看 AI 操作过程

#### 💬 Modern Chat Interface
- **✨ 直观界面**：类 ChatGPT 的对话体验
- **🌍 多语言支持**：支持中英文界面切换
- **📊 实时状态**：显示会话状态和连接状态

#### 🖥️ Desktop Management
- **⚙️ 会话控制**：创建、暂停、恢复和销毁会话
- **🔄 Take Over 模式**：在 AI 控制和手动控制之间切换
- **📁 文件管理**：下载和管理 AI 生成的文件

#### 🔧 Developer Features
- **🏗️ 模块化 API**：清晰的 FastAPI 路由架构
- **🐳 Docker 支持**：容器化部署就绪
- **📜 开源项目**：MIT 许可证，完整源码访问

### 💡 为什么选择 Atlas？

- **🎯 零编程门槛**：无需编写代码，通过对话即可完成复杂操作
- **🛡️ 安全可靠**：E2B 云桌面确保操作安全性和环境隔离
- **⚡ 快速部署**：一键 Docker 部署，支持生产环境
- **🔄 灵活控制**：AI 自动化与手动控制无缝切换

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+

### 📦 Installation & Setup

```bash
# 1. 克隆项目
git clone https://github.com/your-org/atlas.git
cd atlas

# 2. 安装依赖
cd frontend && npm install && cd ..
cd backend && pip install -r requirements.txt && cd ..

# 3. 配置环境变量（见下方 Environment Configuration）
# 创建 backend/.env 和 frontend/.env 文件

# 4. 启动开发服务
make dev
```

### 🔑 Environment Configuration

Atlas 采用前后端分离的环境变量配置方式，需要分别配置前端和后端的环境变量。

**目录结构**：
```
Atlas/
├── backend/
│   ├── .env              # 后端环境变量
│   └── .env.example      # 后端配置模板
└── frontend/
    ├── .env              # 前端环境变量
    └── .env.example      # 前端配置模板
```

**环境变量配置步骤**：
```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

**注意事项**：
- 将所有 `.env` 文件添加到 `.gitignore` 中，避免泄露 API 密钥
- 将 `.env.example` 文件提交到版本控制作为配置模板


## 🐳 Deployment

### 🐳 Docker

#### Production Deployment with Docker Compose
```bash
# 1. 创建部署目录
mkdir -p /path/to/deployment/frank
cd frank

# 2. 下载项目包
wget -P /root/frank https://your-cdn.com/Atlas.zip
unzip Atlas.zip -x "__MACOSX/*"

# 3. 进入项目目录
cd Atlas

# 4. 启动服务
docker compose -f docker/docker-compose.yml up -d

# 5. 查看应用日志
docker compose -f docker/docker-compose.yml logs -f app
```

#### Environment Variables

**配置方式：分别配置前后端环境变量**

**后端环境变量**（`backend/.env`）：
```bash
# backend/.env
# ==================== 必需配置 ====================
E2B_API_KEY=your_e2b_api_key
OPENAI_API_KEY=your_openai_api_key

# ==================== 可选配置 ====================
PORT=8100
PYTHONPATH=/app/backend
```

**前端环境变量**（`frontend/.env`）：
```bash
# frontend/.env
# ==================== 前端配置 ====================
NEXT_PUBLIC_API_URL=http://localhost:8100

# ==================== 可选配置 ====================
PORT=3100
NODE_ENV=production
```

**配置说明**：
- `E2B_API_KEY`: 从 [E2B](https://e2b.dev) 获取的 API 密钥
- `OPENAI_API_KEY`: 从 [OpenAI](https://platform.openai.com) 获取的 API 密钥
- `NEXT_PUBLIC_API_URL`: 前端连接后端的 API 地址

**注意事项**：
- `E2B_API_KEY` 和 `OPENAI_API_KEY` 是**必需的**，否则服务无法正常启动
- 前端需要 `NEXT_PUBLIC_API_URL` 来连接后端 API
- 生产环境建议使用 Docker Secrets 管理敏感信息
- 确保将所有 `.env` 文件添加到 `.gitignore` 中

#### 🚨 Troubleshooting
```bash
# 停止并删除旧容器
docker stop atlas && docker rm atlas

# 删除旧镜像
docker rmi atlas-app

# 清理所有未使用的容器和镜像
docker system prune -f

# 如果容器启动失败，查看日志
docker compose -f docker/docker-compose.yml logs app
```


## 🤝 Contributing

我们欢迎社区贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详细的贡献指南。

### 开发流程
1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 License

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

**享受 AI 驱动的浏览器自动化体验！** 🤖✨

如有问题或建议，请通过 [Issues](https://github.com/your-org/atlas/issues) 联系我们。