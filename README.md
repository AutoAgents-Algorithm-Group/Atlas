# E2B Desktop + Browser Use AI Controller

一个集成了Browser Use AI的E2B云桌面Web应用，支持自然语言驱动的智能浏览器自动化。

## 🚀 功能特性

- **🖥️ 云桌面管理**: 创建和管理E2B云桌面会话
- **🌐 VNC预览**: 在Web界面右侧实时预览桌面
- **🤖 Browser Use AI**: 使用自然语言控制浏览器自动化操作
- **🎯 智能任务执行**: AI自动理解并执行复杂的浏览器任务
- **🔧 应用启动**: 一键启动Firefox、Chrome等应用
- **📱 响应式界面**: 现代化的UI设计，支持各种屏幕尺寸
- **⚡ 实时控制**: 支持鼠标、键盘等实时交互
- **📊 任务历史**: 跟踪和显示AI执行的任务历史

## 🏗️ 架构

- **Backend**: FastAPI + E2B Desktop SDK + Browser Use + OpenAI
- **Frontend**: Next.js + React + Tailwind CSS + ShadCN/UI
- **Desktop**: E2B云桌面环境
- **AI Agent**: Browser Use智能浏览器代理
- **Automation**: Playwright + 自然语言处理

## 📦 安装和运行

### 方法1：一键启动 (推荐)

```bash
# 给启动脚本执行权限 (如果还没有)
chmod +x start.sh

# 启动应用
./start.sh
```

### 方法2：手动启动

#### 启动后端
```bash
cd backend
pip install -r requirements.txt
python main.py
```

#### 启动前端
```bash
cd frontend
npm install
npm run dev
```

## 🎯 使用方法

### 基础操作
1. **启动应用**: 运行 `./start.sh` 或手动启动
2. **打开浏览器**: 访问 http://localhost:3000
3. **创建桌面**: 点击 "Create Desktop" 按钮
4. **等待加载**: 右侧将显示VNC桌面界面

### 应用启动
5. **启动应用**: 
   - 点击 "Launch Firefox" 启动Firefox浏览器
   - 点击 "Open Chrome (Google)" 启动Chrome并访问Google
   - 使用其他快捷按钮启动不同应用

### 🤖 Browser Use AI控制 (核心功能)
6. **自然语言任务执行**:
   - 在"Browser Use AI"区域输入任务描述
   - **智能搜索**: "Open Google and search for artificial intelligence"
   - **网站导航**: "Navigate to GitHub and browse repositories"
   - **直接访问**: "Open www.example.com"
   - 点击快捷任务或按Enter执行
7. **AI工作模式**:
   - **完整AI模式**: 使用browser_use进行智能浏览器控制
   - **Fallback模式**: 无OpenAI连接时，使用基础命令解析
8. **查看结果**: 
   - 观察右侧VNC窗口中的AI自动操作
   - 查看任务历史了解执行情况
   - AI会智能识别页面元素并执行相应操作

### 交互和清理
9. **交互操作**: 在右侧VNC窗口中进行鼠标、键盘操作
10. **关闭会话**: 点击 "Close Desktop" 结束会话

## 🔧 API端点

### 桌面管理
- `POST /api/desktop/create` - 创建桌面会话
- `GET /api/desktop/status` - 获取桌面状态
- `DELETE /api/desktop/close` - 关闭桌面会话

### 应用启动
- `POST /api/desktop/launch-firefox` - 启动Firefox
- `POST /api/desktop/launch-app` - 启动指定应用

### Browser Use AI
- `POST /api/browser/execute-task` - 执行自然语言任务
- `GET /api/browser/status` - 获取Browser Use状态

## 🌟 支持的功能

### 应用启动
- **Firefox**: 默认启动或指定URL启动
- **Google Chrome**: 可指定URL启动  
- **文本编辑器**: gedit等系统应用
- **自定义应用**: 通过API可启动任何已安装的应用

### Browser Use AI任务
- **智能搜索**: 自动打开搜索引擎并搜索指定内容
- **网站导航**: 智能导航到指定网站并浏览
- **页面交互**: AI自动识别并操作页面元素
- **表单填写**: 智能识别表单并填入数据
- **复杂任务**: 多步骤的浏览器自动化任务

## 📱 界面功能

### 左侧控制面板
- **Desktop Status**: 显示当前桌面状态和连接信息
- **Controls**: 桌面创建/关闭控制
- **Applications**: 应用启动控制(Firefox、Chrome等)
- **Browser Use AI**: 自然语言任务输入和执行
- **Task History**: 显示AI执行的任务历史
- **Instructions**: 完整的使用说明

### 右侧预览区域
- **实时VNC流**: 显示云桌面实时画面
- **鼠标键盘支持**: 完整的交互功能
- **全屏预览**: 最佳的操作体验

## 🔑 环境变量

确保在 `backend/desktop.py` 中配置了正确的E2B API Key:

```python
os.environ['E2B_API_KEY'] = 'your_e2b_api_key_here'
```

## 🎯 Browser Use测试示例

### 快速测试命令

1. **基础导航**:
   ```
   Open Google and search for artificial intelligence
   Navigate to GitHub and browse repositories
   Open www.example.com
   ```

2. **智能搜索**:
   ```
   Search for "browser automation tools" on Google
   Find information about E2B on their website
   ```

3. **网站导航**:
   ```
   Go to GitHub and look for browser-use repository
   Navigate to Stack Overflow and search for Python questions
   ```

### 测试步骤
1. 运行 `./start.sh` 启动应用
2. 访问 http://localhost:3000
3. 创建桌面会话
4. 在"Browser Use AI"中输入上述测试命令
5. 观察右侧VNC中的自动化操作
6. 查看任务历史了解执行结果

## 🐛 故障排除

1. **连接失败**: 检查E2B API Key是否正确
2. **应用启动失败**: 确保桌面会话已创建
3. **VNC显示问题**: 刷新页面或重新创建桌面
4. **端口占用**: 确保8000和3000端口未被占用
5. **Browser Use失败**: 检查OpenAI API配置，或使用fallback模式

## 🎉 开始使用

```bash
# 克隆或下载项目后
./start.sh

# 在浏览器中打开
open http://localhost:3000
```

享受AI驱动的云桌面自动化体验！🤖🚀

## 🌟 特性亮点

- ✅ **零配置启动**: 一键启动完整的AI桌面环境
- ✅ **自然语言控制**: 用简单的文字描述即可控制浏览器
- ✅ **实时预览**: 在Web界面中实时看到AI的操作过程
- ✅ **智能fallback**: 即使没有OpenAI API也能正常工作
- ✅ **任务历史**: 完整追踪所有AI执行的任务
- ✅ **现代UI**: 美观的界面设计，优秀的用户体验