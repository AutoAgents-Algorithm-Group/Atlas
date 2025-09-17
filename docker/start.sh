#!/bin/bash

# Apollo 生产环境启动脚本

set -e  # 遇到错误立即退出

echo "🚀 启动 Apollo 生产环境服务..."
echo "📝 前端地址: http://localhost:3100"
echo "🔧 后端API: http://localhost:8100"
echo "📚 API文档: http://localhost:8100/docs"
echo ""

# 定义颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 错误处理函数
cleanup() {
    echo ""
    echo -e "${YELLOW}正在停止服务...${NC}"
    kill $(jobs -p) 2>/dev/null || true
    exit 0
}

# 捕获 SIGTERM 和 SIGINT 信号
trap cleanup SIGTERM SIGINT

# 启动后端API服务器
echo -e "${GREEN}⚙️  启动后端API服务器...${NC}"
cd /app/backend && python -m uvicorn API.main:app --host 0.0.0.0 --port 8100 --timeout-keep-alive 300 &
BACKEND_PID=$!

# 等待后端启动
sleep 3

# 检查后端是否启动成功
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "❌ 后端服务启动失败"
    exit 1
fi

echo -e "${GREEN}✅ 后端服务启动成功 (PID: $BACKEND_PID)${NC}"

# 启动前端生产服务器
echo -e "${GREEN}🎨 启动前端生产服务器...${NC}"
cd /app/frontend && PORT=3100 npx next start -H 0.0.0.0 &
FRONTEND_PID=$!

# 等待前端启动
sleep 5

# 检查前端是否启动成功
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo "❌ 前端服务启动失败"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo -e "${GREEN}✅ 前端服务启动成功 (PID: $FRONTEND_PID)${NC}"
echo ""
echo "🎉 Apollo 服务启动完成！"
echo "   前端: http://localhost:3100"
echo "   后端: http://localhost:8100"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 保持脚本运行，等待所有后台进程
wait
