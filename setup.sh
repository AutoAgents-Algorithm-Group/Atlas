#!/bin/bash

# Modern Full-Stack Project Setup Script
# 现代全栈项目设置脚本

set -e  # 遇到错误时退出

echo "🚀 Project Setup Wizard"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查frontend目录是否存在
if [ ! -d "frontend" ]; then
    echo -e "${RED}❌ Error: frontend directory not found!${NC}"
    echo "Please run this script from the project root directory."
    exit 1
fi

# 检查package.json是否存在
if [ ! -f "frontend/package.json" ]; then
    echo -e "${RED}❌ Error: frontend/package.json not found!${NC}"
    exit 1
fi

# ========================================
# STEP 1: 项目名称配置
# ========================================
CURRENT_NAME=$(grep '"name":' frontend/package.json | sed 's/.*"name": *"\([^"]*\)".*/\1/')
echo -e "${BLUE}[STEP 1/4] Do you want to change the project name?${NC}"
echo -e "${BLUE}📦 Current project name: ${YELLOW}$CURRENT_NAME${NC}"
echo -e "${BLUE}💡 Enter new project name (or press Enter to keep current name):${NC}"
read -p "New name: " NEW_NAME

# 如果用户没有输入，保持当前名称
if [ -z "$NEW_NAME" ]; then
    echo -e "${YELLOW}⏭️  Keeping current name: $CURRENT_NAME${NC}"
    NEW_NAME="$CURRENT_NAME"
else
    # 验证项目名称格式（npm package name 规则）
    if [[ ! "$NEW_NAME" =~ ^[a-z0-9][a-z0-9._-]*$ ]]; then
        echo -e "${RED}❌ Error: Invalid project name!${NC}"
        echo "Project name should:"
        echo "  - Start with lowercase letter or number"
        echo "  - Only contain lowercase letters, numbers, dots, hyphens, and underscores"
        echo "  - Example: my-awesome-project, frontend-app, modern-template"
        exit 1
    fi
    
    echo -e "${YELLOW}🔄 Updating project name to: $NEW_NAME${NC}"
    
    # 使用sed替换项目名称
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/\"name\": *\"[^\"]*\"/\"name\": \"$NEW_NAME\"/" frontend/package.json
    else
        # Linux
        sed -i "s/\"name\": *\"[^\"]*\"/\"name\": \"$NEW_NAME\"/" frontend/package.json
    fi
    
    # 验证更改
    NEW_CURRENT_NAME=$(grep '"name":' frontend/package.json | sed 's/.*"name": *"\([^"]*\)".*/\1/')
    if [ "$NEW_CURRENT_NAME" = "$NEW_NAME" ]; then
        echo -e "${GREEN}✅ Project name successfully updated to: $NEW_NAME${NC}"
    else
        echo -e "${RED}❌ Error: Failed to update project name${NC}"
        exit 1
    fi
fi

echo ""

# ========================================
# STEP 2: 端口配置
# ========================================
# 读取当前端口配置
CURRENT_BACKEND_PORT=$(grep 'port=' backend/API/main.py | sed 's/.*port=\([0-9]*\).*/\1/' | head -1)
if [ -z "$CURRENT_BACKEND_PORT" ]; then
    CURRENT_BACKEND_PORT="8000"  # 默认后端端口
fi

# 从package.json或Makefile读取前端端口
CURRENT_FRONTEND_PORT=$(grep 'localhost:' Makefile | grep -o '[0-9]*' | head -1)
if [ -z "$CURRENT_FRONTEND_PORT" ]; then
    CURRENT_FRONTEND_PORT="3000"  # Next.js默认端口
fi

echo -e "${BLUE}[STEP 2/4] Do you want to configure ports?${NC}"
echo -e "${BLUE}📡 Current backend port: ${YELLOW}$CURRENT_BACKEND_PORT${NC}"
echo -e "${BLUE}📱 Current frontend port: ${YELLOW}$CURRENT_FRONTEND_PORT${NC}"
echo -e "${BLUE}🔧 Configure ports? (y/N)${NC}"
read -p "Configure ports: " CONFIGURE_PORTS

if [[ "$CONFIGURE_PORTS" =~ ^[Yy]$ ]]; then
    # 配置后端端口
    echo -e "${BLUE}📡 Enter backend port (or press Enter to keep $CURRENT_BACKEND_PORT):${NC}"
    read -p "Backend port: " NEW_BACKEND_PORT
    
    if [ -z "$NEW_BACKEND_PORT" ]; then
        NEW_BACKEND_PORT="$CURRENT_BACKEND_PORT"
        echo -e "${YELLOW}⏭️  Keeping current backend port: $CURRENT_BACKEND_PORT${NC}"
    else
        # 验证端口号
        if ! [[ "$NEW_BACKEND_PORT" =~ ^[1-9][0-9]{3,4}$ ]] || [ "$NEW_BACKEND_PORT" -lt 1024 ] || [ "$NEW_BACKEND_PORT" -gt 65535 ]; then
            echo -e "${RED}❌ Error: Invalid backend port! Please use a port between 1024-65535${NC}"
            exit 1
        fi
    fi
    
    # 配置前端端口
    echo -e "${BLUE}📱 Enter frontend port (or press Enter to keep $CURRENT_FRONTEND_PORT):${NC}"
    read -p "Frontend port: " NEW_FRONTEND_PORT
    
    if [ -z "$NEW_FRONTEND_PORT" ]; then
        NEW_FRONTEND_PORT="$CURRENT_FRONTEND_PORT"
        echo -e "${YELLOW}⏭️  Keeping current frontend port: $CURRENT_FRONTEND_PORT${NC}"
    else
        # 验证端口号
        if ! [[ "$NEW_FRONTEND_PORT" =~ ^[1-9][0-9]{3,4}$ ]] || [ "$NEW_FRONTEND_PORT" -lt 1024 ] || [ "$NEW_FRONTEND_PORT" -gt 65535 ]; then
            echo -e "${RED}❌ Error: Invalid frontend port! Please use a port between 1024-65535${NC}"
            exit 1
        fi
    fi
    
    # 检查端口冲突
    if [ "$NEW_BACKEND_PORT" = "$NEW_FRONTEND_PORT" ]; then
        echo -e "${RED}❌ Error: Backend and frontend ports cannot be the same!${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}🔄 Updating port configurations...${NC}"
    
    # 更新backend/API/main.py中的端口配置
    if [ "$NEW_BACKEND_PORT" != "$CURRENT_BACKEND_PORT" ]; then
        echo -e "${YELLOW}🔧 Updating backend port in API/main.py...${NC}"
        
        # 更新uvicorn端口
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s/port=[0-9]*/port=$NEW_BACKEND_PORT/" backend/API/main.py
        else
            sed -i "s/port=[0-9]*/port=$NEW_BACKEND_PORT/" backend/API/main.py
        fi
        
        echo -e "${GREEN}✅ Backend port updated to: $NEW_BACKEND_PORT${NC}"
    fi
    
    # 更新CORS配置中的前端端口
    if [ "$NEW_FRONTEND_PORT" != "$CURRENT_FRONTEND_PORT" ]; then
        echo -e "${YELLOW}🔧 Updating CORS configuration...${NC}"
        
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s/localhost:[0-9]*/localhost:$NEW_FRONTEND_PORT/g" backend/API/main.py
            sed -i '' "s/127\.0\.0\.1:[0-9]*/127.0.0.1:$NEW_FRONTEND_PORT/g" backend/API/main.py
        else
            sed -i "s/localhost:[0-9]*/localhost:$NEW_FRONTEND_PORT/g" backend/API/main.py
            sed -i "s/127\.0\.0\.1:[0-9]*/127.0.0.1:$NEW_FRONTEND_PORT/g" backend/API/main.py
        fi
        
        echo -e "${GREEN}✅ CORS configuration updated for frontend port: $NEW_FRONTEND_PORT${NC}"
    fi
    
    # 更新Makefile中的端口配置
    if [ "$NEW_BACKEND_PORT" != "$CURRENT_BACKEND_PORT" ] || [ "$NEW_FRONTEND_PORT" != "$CURRENT_FRONTEND_PORT" ]; then
        echo -e "${YELLOW}🔧 Updating Makefile...${NC}"
        
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # 更新backend端口
            sed -i '' "s/--port [0-9]*/--port $NEW_BACKEND_PORT/g" Makefile
            # 更新前端端口引用
            sed -i '' "s/localhost:3000/localhost:$NEW_FRONTEND_PORT/g" Makefile
            sed -i '' "s/localhost:$CURRENT_FRONTEND_PORT/localhost:$NEW_FRONTEND_PORT/g" Makefile
            # 更新后端端口引用
            sed -i '' "s/localhost:8000/localhost:$NEW_BACKEND_PORT/g" Makefile
            sed -i '' "s/localhost:$CURRENT_BACKEND_PORT/localhost:$NEW_BACKEND_PORT/g" Makefile
        else
            sed -i "s/--port [0-9]*/--port $NEW_BACKEND_PORT/g" Makefile
            # 更新前端端口引用
            sed -i "s/localhost:3000/localhost:$NEW_FRONTEND_PORT/g" Makefile
            sed -i "s/localhost:$CURRENT_FRONTEND_PORT/localhost:$NEW_FRONTEND_PORT/g" Makefile
            # 更新后端端口引用
            sed -i "s/localhost:8000/localhost:$NEW_BACKEND_PORT/g" Makefile
            sed -i "s/localhost:$CURRENT_BACKEND_PORT/localhost:$NEW_BACKEND_PORT/g" Makefile
        fi
        
        echo -e "${GREEN}✅ Makefile updated with new ports${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}🎯 Port Configuration Summary:${NC}"
    echo -e "  Backend Port: ${YELLOW}$NEW_BACKEND_PORT${NC}"
    echo -e "  Frontend Port: ${YELLOW}$NEW_FRONTEND_PORT${NC}"
    echo -e "  Backend URL: ${YELLOW}http://localhost:$NEW_BACKEND_PORT${NC}"
    echo -e "  Frontend URL: ${YELLOW}http://localhost:$NEW_FRONTEND_PORT${NC}"
    echo -e "  API Docs: ${YELLOW}http://localhost:$NEW_BACKEND_PORT/docs${NC}"
else
    NEW_BACKEND_PORT="$CURRENT_BACKEND_PORT"
    NEW_FRONTEND_PORT="$CURRENT_FRONTEND_PORT"
    echo -e "${YELLOW}⏭️  Keeping current port configuration${NC}"
fi

echo ""

# ========================================
# STEP 3: 依赖安装
# ========================================
echo -e "${BLUE}[STEP 3/4] Do you want to install dependencies?${NC}"
echo -e "${BLUE}📦 Install frontend and backend dependencies using 'make install'? (Y/n)${NC}"
read -p "Install dependencies: " INSTALL_DEPS

if [[ ! "$INSTALL_DEPS" =~ ^[Nn]$ ]]; then
    echo -e "${YELLOW}🔄 Installing dependencies using make install...${NC}"
    
    # 运行make install
    if make install; then
        echo -e "${GREEN}✅ Dependencies installed successfully${NC}"
    else
        echo -e "${RED}❌ Error: Failed to install dependencies${NC}"
        echo "Please check the error messages above and try again."
        exit 1
    fi
else
    echo -e "${YELLOW}⏭️  Skipping dependencies installation${NC}"
fi

echo ""

# ========================================
# STEP 4: 环境配置
# ========================================
echo -e "${BLUE}[STEP 4/4] Do you want to create environment configuration?${NC}"
if [ -f "frontend/.env.example" ]; then
    echo -e "${BLUE}📄 Found frontend/.env.example${NC}"
else
    echo -e "${BLUE}📄 No frontend/.env.example found (will create default)${NC}"
fi
if [ -f "backend/.env.example" ]; then
    echo -e "${BLUE}📄 Found backend/.env.example${NC}"
fi
echo -e "${BLUE}🔧 Create environment configuration files? (Y/n)${NC}"
read -p "Create env files: " CREATE_ENV

if [[ ! "$CREATE_ENV" =~ ^[Nn]$ ]]; then
    echo -e "${YELLOW}🔧 Creating environment configuration files...${NC}"

    # 为frontend创建环境配置
if [ -f "frontend/.env.example" ]; then
    # 如果存在.env.example，复制到.env
    cp frontend/.env.example frontend/.env
    echo -e "${BLUE}   - Copied from .env.example to .env${NC}"
else
    # 如果没有.env.example，创建基本的环境文件
    cat > frontend/.env << EOF
NEXT_PUBLIC_API_URL=http://localhost:$NEW_BACKEND_PORT
EOF
    echo -e "${BLUE}   - Created .env with default configuration${NC}"
fi

# 更新API URL配置
if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s|NEXT_PUBLIC_API_URL=.*|NEXT_PUBLIC_API_URL=http://localhost:$NEW_BACKEND_PORT|" frontend/.env
else
    sed -i "s|NEXT_PUBLIC_API_URL=.*|NEXT_PUBLIC_API_URL=http://localhost:$NEW_BACKEND_PORT|" frontend/.env
fi

    # 为backend创建环境配置（如果需要）
    if [ -f "backend/.env.example" ]; then
        cp backend/.env.example backend/.env
        echo -e "${BLUE}   - Copied backend/.env.example to backend/.env${NC}"
    fi
    
    echo -e "${GREEN}✅ Environment configuration completed${NC}"
else
    echo -e "${YELLOW}⏭️  Skipping environment configuration${NC}"
fi

echo ""

# ========================================
# 总结
# ========================================
echo -e "${GREEN}🎉 Setup completed successfully!${NC}"
echo ""
echo -e "${BLUE}📋 Configuration Summary:${NC}"
echo -e "  Project name: ${YELLOW}$NEW_NAME${NC}"
echo -e "  Backend port: ${YELLOW}$NEW_BACKEND_PORT${NC}"
echo -e "  Frontend port: ${YELLOW}$NEW_FRONTEND_PORT${NC}"
echo ""
echo -e "${BLUE}📁 Configuration files created/updated:${NC}"
echo -e "  ✅ frontend/package.json (project name)"
echo -e "  ✅ backend/API/main.py (ports and CORS)"
echo -e "  ✅ Makefile (ports)"
if [[ ! "$CREATE_ENV" =~ ^[Nn]$ ]]; then
    echo -e "  ✅ frontend/.env (environment variables)"
    if [ -f "backend/.env" ]; then
        echo -e "  ✅ backend/.env (environment variables)"
    fi
fi
echo ""
echo -e "${BLUE}🚀 Next steps:${NC}"
echo "  Terminal Run: make dev"

echo ""