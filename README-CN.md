<div align="center">

<img src="https://img.shields.io/badge/-Atlas-000000?style=for-the-badge&labelColor=faf9f6&color=faf9f6&logoColor=000000" alt="Atlas" width="280"/>

<h4>AI 驱动的浏览器自动化平台</h4>

[English](README.md) | **简体中文**

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="media/dark_license.svg" />
  <img alt="License MIT" src="media/light_license.svg" />
</picture>

</div>

## 目录

- [为什么选择 Atlas？](#为什么选择-atlas)
- [快速开始](#快速开始)
- [架构说明](#架构说明)
- [部署指南](#部署指南)
- [参与贡献](#参与贡献)
- [开源许可](#开源许可)

## 为什么选择 Atlas？

Atlas 是一个革命性的 AI 浏览器控制器，让你可以通过自然语言对话来操控浏览器。基于 E2B 云桌面技术，Atlas 提供了安全、隔离的浏览器自动化环境，支持复杂的 Web 操作任务。

- **零编程门槛**：无需编写代码，通过对话即可完成复杂操作
- **安全可靠**：E2B 云桌面确保操作安全性和环境隔离
- **快速部署**：一键 Docker 部署，支持生产环境
- **灵活控制**：AI 自动化与手动控制无缝切换

## 架构说明

Atlas 采用现代化的前后端分离架构，结合 E2B 云桌面技术，提供稳定可靠的浏览器自动化服务。

### 后端 (FastAPI + Python)
- **入口点**: `backend/API/main.py` - FastAPI 应用主入口
- **核心代理**: `backend/Agent/unified_agent.py` - 集成桌面管理和浏览器自动化
- **桌面管理**: `backend/Desktop/manager.py` - E2B 桌面会话管理
- **浏览器引擎**: `backend/Engine/browser_runner.py` - 浏览器自动化引擎
- **模块化 API**: `backend/API/routers/` - 路由模块化设计

### 前端 (Next.js + TypeScript)
- **主布局**: `frontend/app/layout.tsx` - 应用主布局
- **组件库**: `frontend/components/` - 基于 Shadcn/UI 的现代组件
- **国际化**: `frontend/messages/` - 支持中英文切换
- **响应式设计**: ResizablePanel 布局，聊天界面 + 桌面预览

### 核心集成
- **E2B 云桌面**: 远程浏览器执行环境
- **Browser Use AI**: 自然语言浏览器自动化
- **Shadcn/UI**: 现代 React 组件库
- **FastAPI 路由**: 模块化 API 端点设计

## 快速开始

### 环境要求
- Node.js 18+ 和 npm
- Python 3.11+

### 安装与配置

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

### 环境变量配置

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


## 部署指南

### Docker 部署

#### 生产环境 Docker Compose 部署
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

#### 环境变量配置

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

#### 故障排除
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


## 参与贡献

我们欢迎社区贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详细的贡献指南。

### 开发流程
1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 开源许可

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

**享受 AI 驱动的浏览器自动化体验！**

如有问题或建议，请通过 [Issues](https://github.com/your-org/atlas/issues) 联系我们。
