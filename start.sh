#!/bin/bash

echo "🚀 Starting E2B Desktop + Browser Use Application..."

# 检查是否在正确的目录
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# 启动后端
echo "📦 Starting Backend (FastAPI + Browser Use)..."
cd backend
python3 -m pip install -r requirements.txt
python3 main.py &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"

# 等待后端启动
sleep 5

# 启动前端
echo "🎨 Starting Frontend (Next.js)..."
cd ../frontend

# 检查是否已安装依赖
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

npm run dev &
FRONTEND_PID=$!
echo "✅ Frontend started (PID: $FRONTEND_PID)"

echo ""
echo "🎉 Application is starting up!"
echo "📊 Backend API: http://localhost:8000"
echo "🌐 Frontend UI: http://localhost:3000"
echo ""
echo "🤖 Features:"
echo "  - E2B Desktop management"
echo "  - VNC preview in browser"
echo "  - Application launching (Firefox, Chrome)"
echo "  - Browser Use AI for natural language automation"
echo ""
echo "💡 Open http://localhost:3000 in your browser to use the application"
echo ""
echo "⚠️  Press Ctrl+C to stop all services"

# 等待用户中断
trap 'echo ""; echo "🛑 Stopping services..."; kill $BACKEND_PID $FRONTEND_PID; exit 0' INT
wait

