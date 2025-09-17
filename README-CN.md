<div align="center">

<img src="https://img.shields.io/badge/-Atlas-000000?style=for-the-badge&labelColor=faf9f6&color=faf9f6&logoColor=000000" alt="Atlas" width="280"/>

<h4>AI 驱动的浏览器自动化平台</h4>

[English](README.md) | 简体中文

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="media/dark_license.svg" />
  <img alt="License MIT" src="media/light_license.svg" />
</picture>

</div>

以希腊神话中擎天的泰坦阿特拉斯命名，这个平台为 AI 驱动的浏览器自动化提供了无与伦比的可靠性和控制能力的基础。

## 目录
- [目录](#目录)
- [为什么选择 Atlas？](#为什么选择-atlas)
- [快速开始](#快速开始)
- [部署指南](#部署指南)
- [参与贡献](#参与贡献)
- [开源许可](#开源许可)

## 为什么选择 Atlas？

Atlas 是一个革命性的 AI 浏览器自动化平台，让您可以通过自然语言对话来控制网页浏览器。基于 E2B 云桌面技术构建，Atlas 为复杂的网页自动化任务提供了安全、隔离的环境。

- **自然语言控制**：通过简单对话执行复杂的浏览器操作
- **零编程要求**：无需编写代码即可完成复杂任务
- **安全云环境**：使用 E2B 云桌面的隔离浏览器执行环境
- **实时监控**：实时观看自动化任务执行
- **专业界面**：现代响应式界面，支持双语

## 快速开始

**环境要求**
- Node.js 18+ 和 npm
- Python 3.11+
- Docker（可选，用于容器化部署）

**开始使用**
```bash
# 1. 克隆代码库
git clone https://github.com/your-org/Atlas.git
cd Atlas

# 2. 使设置脚本可执行并运行
chmod +x setup.sh
./setup.sh

# 3. 启动开发环境
make dev
```

## 部署指南

**Docker 部署**
```bash
cd Atlas
docker compose -f docker/docker-compose.yml up -d
```

**故障排除**
```bash
# 查看应用日志
docker compose -f docker/docker-compose.yml logs -f app

# 停止并删除旧容器
docker stop atlas && docker rm atlas
docker rmi atlas-app
```

## 参与贡献

1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 开源许可

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。