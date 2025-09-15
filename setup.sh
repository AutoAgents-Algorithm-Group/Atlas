#!/bin/bash

# E2B Computer Use Setup Script
# 用于修改项目名称、端口配置和其他设置

set -e  # 遇到错误时退出

echo "🚀 E2B Computer Use Project Setup"
echo "=================================="
echo "📋 This setup will guide you through 4 main steps:"
echo "   1. Project name configuration"
echo "   2. Port configuration" 
echo "   3. Dependencies installation"
echo "   4. Summary"
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
echo -e "${BLUE}[STEP 1/4] 📦 Project Name Configuration${NC}"
echo "========================================"
echo ""

# 显示当前项目名称
CURRENT_NAME=$(grep '"name":' frontend/package.json | sed 's/.*"name": *"\([^"]*\)".*/\1/')
echo -e "${BLUE}📦 Current project name: ${YELLOW}$CURRENT_NAME${NC}"
echo ""

# 提示用户输入新的项目名称
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
        echo "  - Example: my-awesome-project, frontend-app, e2b-desktop"
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
echo -e "${BLUE}[STEP 2/4] 🔧 Port Configuration${NC}"
echo "=================================="
echo ""

# 读取当前端口配置
CURRENT_BACKEND_PORT=$(grep 'port=' backend/API/main.py | sed 's/.*port=\([0-9]*\).*/\1/')
if [ -z "$CURRENT_BACKEND_PORT" ]; then
    CURRENT_BACKEND_PORT="8000"  # 默认后端端口
fi

# 从package.json读取前端端口，如果没有配置则默认3000
CURRENT_FRONTEND_PORT=$(grep '"dev":' frontend/package.json | grep -o '\-p [0-9]*' | sed 's/-p //')
if [ -z "$CURRENT_FRONTEND_PORT" ]; then
    CURRENT_FRONTEND_PORT="3000"  # Next.js默认端口
fi

echo -e "${BLUE}📡 Current backend port: ${YELLOW}$CURRENT_BACKEND_PORT${NC}"
echo -e "${BLUE}📱 Current frontend port: ${YELLOW}$CURRENT_FRONTEND_PORT${NC}"
echo ""

# 询问是否要配置端口
echo -e "${BLUE}🔧 Do you want to configure ports? (y/N)${NC}"
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
            sed -i '' "s/localhost:8000/localhost:$NEW_BACKEND_PORT/g" Makefile
            sed -i '' "s/localhost:3000/localhost:$NEW_FRONTEND_PORT/g" Makefile
        else
            sed -i "s/--port [0-9]*/--port $NEW_BACKEND_PORT/g" Makefile
            sed -i "s/localhost:8000/localhost:$NEW_BACKEND_PORT/g" Makefile
            sed -i "s/localhost:3000/localhost:$NEW_FRONTEND_PORT/g" Makefile
        fi
        
        echo -e "${GREEN}✅ Makefile updated with new ports${NC}"
    fi
    
    # 为frontend创建环境配置
    echo -e "${YELLOW}🔧 Creating frontend environment configuration...${NC}"
    
    # 从.env.example复制到.env.local并更新值
    if [ -f "frontend/.env.example" ]; then
        cp frontend/.env.example frontend/.env.local
        echo -e "${BLUE}   - Copied from .env.example${NC}"
    else
        # 如果没有.env.example，创建一个基本的.env.local
        cat > frontend/.env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF
    fi
    
    # 更新API URL配置
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s|NEXT_PUBLIC_API_URL=.*|NEXT_PUBLIC_API_URL=http://localhost:$NEW_BACKEND_PORT|" frontend/.env.local
    else
        sed -i "s|NEXT_PUBLIC_API_URL=.*|NEXT_PUBLIC_API_URL=http://localhost:$NEW_BACKEND_PORT|" frontend/.env.local
    fi
    
    echo -e "${GREEN}✅ Frontend environment configuration created: frontend/.env.local${NC}"
    echo -e "${BLUE}   - Frontend port: $NEW_FRONTEND_PORT${NC}"
    echo -e "${BLUE}   - API URL: http://localhost:$NEW_BACKEND_PORT${NC}"
    
    # 更新package.json中的dev脚本端口
    echo -e "${YELLOW}🔧 Updating package.json dev script port...${NC}"
    
    # 使用sed替换dev脚本中的端口号
    sed -i.tmp "s/\"dev\": \"next dev --turbopack -p [0-9]*\"/\"dev\": \"next dev --turbopack -p $NEW_FRONTEND_PORT\"/g" frontend/package.json
    rm -f frontend/package.json.tmp
    echo -e "${GREEN}✅ Package.json dev script updated with port: $NEW_FRONTEND_PORT${NC}"
    
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
    
    # 即使不修改端口，也要确保.env.local文件存在
    echo -e "${YELLOW}🔧 Ensuring frontend environment configuration exists...${NC}"
    
    # 如果.env.local不存在，从.env.example复制
    if [ ! -f "frontend/.env.local" ]; then
        if [ -f "frontend/.env.example" ]; then
            cp frontend/.env.example frontend/.env.local
            echo -e "${BLUE}   - Copied from .env.example${NC}"
        else
            # 如果没有.env.example，创建一个基本的.env.local
            cat > frontend/.env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF
        fi
    fi
    
    # 确保API URL配置正确
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s|NEXT_PUBLIC_API_URL=.*|NEXT_PUBLIC_API_URL=http://localhost:$NEW_BACKEND_PORT|" frontend/.env.local
    else
        sed -i "s|NEXT_PUBLIC_API_URL=.*|NEXT_PUBLIC_API_URL=http://localhost:$NEW_BACKEND_PORT|" frontend/.env.local
    fi
    
    echo -e "${GREEN}✅ Frontend environment configuration ensured: frontend/.env.local${NC}"
    
    # 确保package.json中的dev脚本端口与当前配置一致
    echo -e "${YELLOW}🔧 Ensuring package.json dev script port consistency...${NC}"
    
    # 使用sed替换dev脚本中的端口号
    sed -i.tmp "s/\"dev\": \"next dev --turbopack -p [0-9]*\"/\"dev\": \"next dev --turbopack -p $NEW_FRONTEND_PORT\"/g" frontend/package.json
    rm -f frontend/package.json.tmp
    echo -e "${GREEN}✅ Package.json dev script port ensured: $NEW_FRONTEND_PORT${NC}"
fi

echo ""

# ========================================
# STEP 3: 依赖安装
# ========================================
echo -e "${BLUE}[STEP 3/4] 📦 Dependencies Installation${NC}"
echo "======================================"
echo ""

# 询问是否要安装依赖
echo -e "${BLUE}📦 Do you want to install frontend dependencies? (y/N)${NC}"
read -p "Install deps: " INSTALL_DEPS

if [[ "$INSTALL_DEPS" =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}🔄 Installing frontend dependencies...${NC}"
    cd frontend
    
    # 删除旧的node_modules和package-lock.json（如果存在）
    if [ -d "node_modules" ]; then
        rm -rf node_modules
        echo -e "${GREEN}✅ Removed old node_modules${NC}"
    fi
    
    if [ -f "package-lock.json" ]; then
        rm package-lock.json
        echo -e "${GREEN}✅ Removed old package-lock.json${NC}"
    fi
    
    # 安装依赖
    npm install
    echo -e "${GREEN}✅ Dependencies installed successfully${NC}"
    cd ..
else
    echo -e "${YELLOW}⏭️  Skipping dependencies installation${NC}"
fi

echo ""

# ========================================
# STEP 4: 总结
# ========================================
echo -e "${BLUE}[STEP 4/4] 📋 Summary${NC}"
echo "========================"
echo ""
echo -e "${GREEN}🎉 Setup completed successfully!${NC}"
echo ""
echo -e "${BLUE}📋 Configuration Summary:${NC}"
echo -e "  Project name: ${YELLOW}$NEW_NAME${NC}"
echo -e "  Backend port: ${YELLOW}$NEW_BACKEND_PORT${NC}"
echo -e "  Frontend port: ${YELLOW}$NEW_FRONTEND_PORT${NC}"
echo -e "  Frontend path: ${YELLOW}frontend/${NC}"
echo -e "  Package.json: ${YELLOW}frontend/package.json${NC}"
echo ""
echo -e "${BLUE}🌐 Service URLs:${NC}"
echo -e "  Frontend: ${YELLOW}http://localhost:$NEW_FRONTEND_PORT${NC}"
echo -e "  Backend API: ${YELLOW}http://localhost:$NEW_BACKEND_PORT${NC}"
echo -e "  API Documentation: ${YELLOW}http://localhost:$NEW_BACKEND_PORT/docs${NC}"
echo ""
echo -e "${BLUE}🚀 Next steps:${NC}"
echo "  1. Start development: make dev"
echo "  2. Or manually:"
echo "     Backend: cd backend && uvicorn API.main:app --host 0.0.0.0 --port $NEW_BACKEND_PORT --reload"
echo "     Frontend: cd frontend && npm run dev"
echo ""
echo -e "${BLUE}📁 Configuration files modified:${NC}"
echo -e "  ✅ frontend/package.json (dev script port)"
echo -e "  ✅ backend/API/main.py (ports and CORS)"
echo -e "  ✅ Makefile (ports)"
echo -e "  ✅ frontend/.env.local (environment variables)"
echo ""
