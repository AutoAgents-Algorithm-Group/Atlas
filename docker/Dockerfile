# 多阶段构建 Dockerfile - 前后端统一构建

# ==================== 后端构建阶段 ====================
FROM python:3.11-slim AS backend-builder

# 设置工作目录
WORKDIR /app/backend

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 安装系统依赖
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        gfortran \
        liblapack-dev \
        libblas-dev \
        libgcc-s1 \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ==================== 前端构建阶段 ====================
FROM node:18-alpine AS frontend-builder

# 设置工作目录
WORKDIR /app/frontend

# 安装依赖
RUN apk add --no-cache libc6-compat

# 复制 package 文件并安装依赖（包含开发依赖，用于构建）
COPY frontend/package*.json ./
RUN npm ci && npm cache clean --force

# 复制前端代码并构建
COPY frontend/ .
RUN npm run build

# ==================== 生产环境镜像 ====================
FROM python:3.11-slim AS production

# 设置工作目录
WORKDIR /app

# 安装 Node.js 和 make（用于运行前端和构建工具）
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        gcc \
        g++ \
        gfortran \
        liblapack-dev \
        libblas-dev \
        libgcc-s1 \
        make \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# 从后端构建阶段复制 Python 依赖
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# 复制后端代码
COPY backend/ ./backend/

# 从前端构建阶段复制构建产物和依赖 (传统方式)
COPY --from=frontend-builder /app/frontend/.next ./frontend/.next
COPY --from=frontend-builder /app/frontend/package.json ./frontend/package.json
COPY --from=frontend-builder /app/frontend/public ./frontend/public
COPY --from=frontend-builder /app/frontend/node_modules ./frontend/node_modules

# 复制启动脚本
COPY docker/start.sh ./
RUN chmod +x start.sh

# 暴露端口
EXPOSE 3100 8100

# 设置环境变量
ENV PYTHONPATH=/app/backend
ENV NODE_ENV=production

# 启动命令
CMD ["./start.sh"]